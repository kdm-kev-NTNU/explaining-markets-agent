"""Explaining Markets strategy — predict(event) → cross-sectional percentiles.

Scoring (see ../APPROACH.md and ../CONCEPTS.md):
  ΔR² beyond the earnings-surprise benchmark. Constant predictions ⇒ ΔR² = 0.
  Calibration is unscored (affine remapping invariance) — only ranking counts.

Per focal asset:
  1. Fetch the materials bundle from information_url (facts, preview, option stats).
  2. Deterministic option signal (skew + vol) as prompt context and fallback.
  3. One LLM call via an OpenAI-compatible endpoint
     (OPENAI_BASE_URL + OPENAI_API_KEY), returning
     JSON {"predicted_percentile": x, "reason": "..."}.
  4. On LLM failure: option signal alone; then 0.5 (delivery beats imputation;
     constant baselines earn nothing — last resort).

Time budgets against the 5-minute window: fetch 15 s, LLM 150 s + 1 retry.
"""

from __future__ import annotations

import json
import os
import re

import httpx
from openai import OpenAI

from explaining_markets.config import openai_model

_client: OpenAI | None = None  # lazy: importing this file must not require a key

SUMMARY_TIMEOUT_SECONDS = 15.0
LLM_TIMEOUT_SECONDS = 150.0
LLM_MAX_RETRIES = 1
LLM_MAX_TOKENS = 3000  # reasoning models need headroom for the chain of thought

FACTS_ID = "earnings-call-facts"
PREVIEW_ID = "earnings-preview"
OPTION_STATS_ID = "option-implied-stats"

PREVIEW_MAX_CHARS = 8000
OTHER_ITEM_MAX_CHARS = 2000


def predict(event: dict) -> list[dict]:
    """Return predictions for one Explaining Markets event.

    `event` is the verified webhook payload. Useful fields:
      event["event_type"]          e.g. "EARNINGS_RELEASE"
      event["focal_assets"]        list of {"identifier_type", "identifier_value"}
      event["information_url"]     short-lived signed URL to the event's materials
                                   (a JSON bundle of items; see `format_materials`)
      event["prediction_deadline"] ISO timestamp; submit before this fires

    Required return: a list of dicts, one per focal asset:
      [{"identifier_value": "AAPL", "predicted_percentile": 0.71}, ...]

    `predicted_percentile` is a float in [0, 1] — where you predict the asset's
    next-day abnormal (market-adjusted) return will rank across all of the
    quarter's event outcomes: 0 = the quarter's most negative reaction,
    0.50 = median, 1 = its most positive. It's a cross-sectional rank across
    the quarter's events, not a percentile within the asset's own history.
    """
    summary = httpx.get(event["information_url"], timeout=SUMMARY_TIMEOUT_SECONDS)
    summary.raise_for_status()
    bundle = summary.json()

    materials = format_materials(bundle)
    option_signal = option_stats_signal(bundle)

    # One model call per focal asset, in series — so the LLM budget below is
    # per asset, not per event. Today every event carries a single asset; if
    # that changes and you need several, run them concurrently rather than
    # raising the timeout.
    return [
        {
            "identifier_value": asset["identifier_value"],
            "predicted_percentile": _predict_one(
                ticker=asset["identifier_value"],
                event_type=event.get("event_type", ""),
                materials=materials,
                option_signal=option_signal,
                bundle=bundle,
            ),
        }
        for asset in event.get("focal_assets", [])
    ]


# ---------------------------------------------------------------- materials ---

def _percent(block: object) -> str | None:
    """A `{value, status}` statistic as a percentage, or None if unavailable."""
    if not isinstance(block, dict) or block.get("status") != "ok":
        return None
    value = block.get("value")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return f"{value * 100:+.1f}" if value < 0 else f"{value * 100:.1f}"


def _format_option_stats(stats: dict) -> str | None:
    volatility = _percent(stats.get("implied_earnings_volatility"))
    if volatility is None:
        return None
    lines = [
        f"- Implied earnings volatility: {volatility}% (the standard deviation of the "
        "stock's move on this release that option prices imply)",
    ]
    move = _percent(stats.get("implied_absolute_earnings_move"))
    if move is not None:
        lines.append(
            f"- Implied absolute move: {move}% (the size of move options price in; "
            "it says nothing about direction)"
        )
    skew = _percent(stats.get("skew_25_delta"))
    if skew is not None:
        lines.append(
            f"- 25-delta skew: {skew} volatility points (call minus put implied "
            "volatility; negative means downside protection is priced richer)"
        )
    else:
        lines.append("- 25-delta skew: unavailable (options too thinly traded)")
    as_of = stats.get("as_of")
    header = "Option-market expectations, measured before the release"
    if isinstance(as_of, str) and as_of:
        header += f" (as of {as_of})"
    return header + ":\n" + "\n".join(lines)


def _stat_value(bundle: dict, field: str) -> float | None:
    """Raw numeric value for an option-stats field, None if missing/not-ok."""
    items = bundle.get("items") if isinstance(bundle, dict) else None
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict) and item.get("id") == OPTION_STATS_ID:
            stats = item.get("content")
            if isinstance(stats, dict):
                block = stats.get(field)
                if isinstance(block, dict) and block.get("status") == "ok":
                    v = block.get("value")
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        return float(v)
    return None


def option_stats_signal(bundle: dict) -> str:
    """Deterministic one-line summary of the option signal for the prompt."""
    vol = _stat_value(bundle, "implied_earnings_volatility")
    move = _stat_value(bundle, "implied_absolute_earnings_move")
    skew = _stat_value(bundle, "skew_25_delta")
    parts = []
    if vol is not None:
        parts.append(f"implied earnings volatility {vol * 100:.1f}%")
    if move is not None:
        parts.append(f"implied absolute move {move * 100:.1f}%")
    if skew is not None:
        direction = "negatively loaded (market prices richer downside protection)" if skew < 0 else "positively loaded"
        parts.append(f"25-delta skew {skew * 100:+.1f} vol-points — {direction}")
    if not parts:
        return "Option data: unavailable for this event."
    return "Option-market expectations, measured BEFORE the release: " + "; ".join(parts) + "."


def format_materials(bundle: object) -> str:
    """Turn the event's bundle into the text the model reads.

    Items are found by `id`, so arrival order does not matter. Unknown text
    items are included; non-text unknowns are skipped. Order is prior first
    (option surface, then preview), then realization (call facts), so the
    model sees the priced distribution before what was said.
    """
    if not isinstance(bundle, dict):
        return ""
    raw_items = bundle.get("items")
    items = [i for i in raw_items if isinstance(i, dict)] if isinstance(raw_items, list) else []
    by_id = {i.get("id"): i for i in items}
    sections: list[str] = []

    stats = (by_id.get(OPTION_STATS_ID) or {}).get("content")
    if isinstance(stats, dict):
        formatted = _format_option_stats(stats)
        if formatted:
            sections.append(formatted)

    preview = (by_id.get(PREVIEW_ID) or {}).get("content")
    if isinstance(preview, str) and preview.strip():
        text = preview[:PREVIEW_MAX_CHARS]
        if len(preview) > PREVIEW_MAX_CHARS:
            text += "\n[preview truncated]"
        sections.append(
            "Research note written BEFORE the release (expectations, not results):\n" + text
        )

    for item in items:
        if item.get("id") in (FACTS_ID, PREVIEW_ID, OPTION_STATS_ID):
            continue
        content = item.get("content")
        if isinstance(content, list) and all(isinstance(c, str) for c in content):
            content = "\n".join(content)
        if isinstance(content, str) and content.strip():
            label = item.get("id") or item.get("kind") or "item"
            sections.append(f"Additional material ({label}):\n{content[:OTHER_ITEM_MAX_CHARS]}")

    facts = (by_id.get(FACTS_ID) or {}).get("content")
    if isinstance(facts, list) and facts:
        sections.append(
            "Facts from the earnings call:\n"
            + "\n".join(f"{n}. {fact}" for n, fact in enumerate(facts, start=1))
        )

    return "\n\n".join(sections)


# ---------------------------------------------------------------- LLM-kallet ---

SYSTEM_PROMPT = """\
Rank the residual equity reaction given a priced earnings surprise and a
pre-release option-implied distribution.

Predict a single percentile in [0, 1] for how the focal asset's next-day
abnormal (market-adjusted) return will rank across ALL of the quarter's
earnings events: 0 = the quarter's most negative reaction, 0.50 = median,
1 = its most positive. A great-but-fully-priced-in beat is NOT a top-decile
event — the benchmark already captures the raw earnings surprise. Your value
is in what the surprise does NOT capture: guidance shifts vs the prior
trajectory, forward-looking call content, strategic changes, expectations vs.
realized results, and divergence from option-market positioning.

Weigh, in roughly this order:
  1. Guidance / outlook — raises, holds, cuts vs the prior trajectory.
  2. Forward-looking call content that is novel vs restating the surprise.
  3. Strategic shifts — product launches, M&A, capital allocation, leadership.
  4. Option-market positioning — skew direction; treat implied move as size/
     confidence (do not double-count it if the preview already embeds it).
  5. Quantitative surprise vs expectations — only the part not already implied.
  6. Tone and confidence in management commentary (small weight).
  7. Risks called out — regulatory, supply chain, demand, competition.

If preview or option stats are missing, say so in the reason and rely on call
facts alone — do not invent a ticker prior.

Calibration discipline:
- Long-run base rates: about 25% of events land "up" (>0.75), 50% "neutral"
  (0.25-0.75), 25% "down" (<0.25). Default toward 0.40-0.60 when signals are
  mixed or modest.
- Reserve values above 0.80 or below 0.20 for unambiguous, multi-signal
  evidence. Do not exceed 0.90 or fall below 0.10 without overwhelming,
  lopsided evidence.
- Your number MUST vary between events — a constant answer scores exactly zero.
- Tone alone (confident vs hedging language) should move you no more than
  ~0.03 absent quantitative confirmation.

Respond with STRICT JSON only, no markdown fence, no extra text:
{"predicted_percentile": <float 0..1>, "reason": "<one short sentence>"}
"""


def _llm_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def _ask_llm(*, ticker: str, event_type: str, materials: str, option_signal: str) -> float | None:
    """One OpenAI-compatible chat call. None on failure."""
    global _client
    if not _llm_available():
        return None
    if _client is None:
        # OPENAI_BASE_URL + OPENAI_API_KEY select the endpoint; OpenAI client protocol.
        _client = OpenAI(timeout=LLM_TIMEOUT_SECONDS, max_retries=LLM_MAX_RETRIES)

    if not materials:
        # Not a bundle this code recognises. Show the model what arrived rather
        # than nothing.
        materials = json.dumps({"note": "no recognizable materials"})[:PREVIEW_MAX_CHARS]

    user_prompt = (
        f"Event type: {event_type}\n"
        f"Ticker: {ticker}\n\n"
        f"{option_signal}\n\n"
        f"Event materials:\n{materials}\n\n"
        f"Predict the next-day abnormal-return percentile for {ticker}. "
        'Strict JSON: {"predicted_percentile": <float>, "reason": "..."}'
    )

    resp = _client.chat.completions.create(
        model=openai_model(),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=LLM_MAX_TOKENS,
        temperature=0.3,
    )
    try:
        content = (resp.choices[0].message.content or "").strip()
    except Exception:
        return None
    m = re.search(r"\{[^{}]*\}", content, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        p = float(obj["predicted_percentile"])
    except Exception:
        return None
    if not 0.0 <= p <= 1.0:
        p = min(1.0, max(0.0, p))  # clamp defective JSON, don't discard a valid signal
    return p


def _option_fallback(bundle: dict) -> float | None:
    """Deterministic fallback from the option signal alone.

    Skew is the most directional of the three: negative skew (richer put
    protection) → downward expectation. Weak but VARYING signal — better
    than a constant 0.5 (which scores exactly ΔR² 0).
    """
    skew = _stat_value(bundle, "skew_25_delta")
    if skew is None:
        return None
    capped = max(-0.10, min(0.10, skew))
    return 0.5 - capped * 1.5  # negative skew → below 0.5; positive → above


def _predict_one(*, ticker: str, event_type: str, materials: str, option_signal: str,
                 bundle: dict | None = None) -> float:
    if event_type == "TEST":
        return 0.5  # portal test deliveries: neutral, never scored

    p = None
    try:
        p = _ask_llm(ticker=ticker, event_type=event_type, materials=materials, option_signal=option_signal)
    except Exception as exc:
        print(f"[WARN] LLM call failed for {ticker}: {exc}")

    if p is None:
        p = _option_fallback(bundle or {})
        if p is not None:
            print(f"[WARN] Using option-stats fallback for {ticker}: {p:.3f}")
    if p is None:
        print(f"[WARN] No signals — submitting 0.5 for {ticker} (avoids imputation; ΔR² contribution 0)")
        p = 0.5
    return p
