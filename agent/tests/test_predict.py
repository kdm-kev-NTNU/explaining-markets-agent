"""predict() returns the right shape on the no-OpenAI-key fallback path.

With OPENAI_API_KEY unset, predict() must still return one well-formed prediction
per focal asset (the 0.5 baseline) without making any network calls. We stub the
disclosure fetch so the test is fully offline.
"""

from __future__ import annotations

import pytest

import predict as predict_module


SAMPLE_EVENT = {
    "id": "evt_test_1",
    "event_id": "11111111-1111-1111-1111-111111111111",
    "event_type": "EARNINGS_RELEASE",
    "timing_category": "SCHEDULED",
    "event_datetime": "2026-01-15T21:00:00Z",
    "focal_assets": [
        {"identifier_type": "TICKER", "identifier_value": "AAPL"},
        {"identifier_type": "TICKER", "identifier_value": "MSFT"},
    ],
    "information_url": "https://example.test/disclosure",
    "prediction_deadline": "2026-01-15T21:05:00Z",
}


PREVIEW = "# Acme (ACME) — Q3 FY2026 Earnings Preview\n\n## Consensus Estimates\nEPS $1.20\n"
STATS = {
    "as_of": "2026-10-05T19:36:12Z",
    "methodology": "v1",
    "implied_earnings_volatility": {"value": 0.0847, "status": "ok"},
    "implied_absolute_earnings_move": {"value": 0.0676, "status": "ok"},
    "skew_25_delta": {"value": -0.0412, "status": "ok"},
}
FACTS_ITEM = {
    "id": "earnings-call-facts",
    "kind": "facts",
    "source": "earnings_call",
    "media_type": "application/json",
    "content": ["Revenue rose 12% year over year.", "Full-year guidance was raised."],
}
PREVIEW_ITEM = {
    "id": "earnings-preview",
    "kind": "text",
    "source": "claude_code_web_research",
    "media_type": "text/markdown",
    "content": PREVIEW,
}
STATS_ITEM = {
    "id": "option-implied-stats",
    "kind": "stats",
    "source": "option_market",
    "media_type": "application/json",
    "content": STATS,
}
# The real shape behind `information_url`.
BUNDLE = {
    "schema_version": "1.0",
    "event_id": "11111111-1111-1111-1111-111111111111",
    "generated_at": "2026-10-05T21:30:00Z",
    "items": [FACTS_ITEM, PREVIEW_ITEM, STATS_ITEM],
}


def _bundle(*items) -> dict:
    return {**BUNDLE, "items": list(items)}


class _FakeResponse:
    def __init__(self, json_value: dict | None = None) -> None:
        self._json = json_value if json_value is not None else BUNDLE

    def raise_for_status(self) -> None:  # noqa: D401 - stub
        return None

    def json(self) -> dict:
        return self._json


def test_predict_fallback_shape(monkeypatch) -> None:
    """Without an LLM key the deterministic option-stats fallback fires
    (a VARYING signal — a constant 0.5 scores exactly ΔR² 0).
    With no option stats either, the flat 0.5 delivery fallback applies."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(predict_module.httpx, "get", lambda *a, **k: _FakeResponse())

    preds = predict_module.predict(SAMPLE_EVENT)

    assert isinstance(preds, list)
    assert len(preds) == len(SAMPLE_EVENT["focal_assets"])
    returned = {p["identifier_value"] for p in preds}
    assert returned == {"AAPL", "MSFT"}
    for p in preds:
        assert set(p) == {"identifier_value", "predicted_percentile"}
        assert 0.0 <= p["predicted_percentile"] <= 1.0
        # STATS carries skew_25_delta = -0.0412 → fallback = 0.5 - (-0.0412)*1.5 ≈ 0.562
        assert abs(p["predicted_percentile"] - 0.5618) < 1e-3

    # No option stats at all → flat 0.5 delivery fallback (avoids imputation).
    monkeypatch.setattr(
        predict_module.httpx, "get", lambda *a, **k: _FakeResponse(json_value={"items": []})
    )
    preds2 = predict_module.predict(SAMPLE_EVENT)
    assert all(p["predicted_percentile"] == 0.5 for p in preds2)


def test_every_item_reaches_the_prompt_under_its_own_label() -> None:
    text = predict_module.format_materials(BUNDLE)
    assert "1. Revenue rose 12% year over year." in text
    assert "2. Full-year guidance was raised." in text
    assert "Implied earnings volatility: 8.5%" in text
    assert "Implied absolute move: 6.8%" in text
    assert "25-delta skew: -4.1 volatility points" in text
    assert "as of 2026-10-05T19:36:12Z" in text
    assert "## Consensus Estimates" in text
    # The raw envelope is not pasted in.
    for noise in ("schema_version", "media_type", "generated_at", '"kind"'):
        assert noise not in text


def test_items_are_found_by_id_not_by_position() -> None:
    shuffled = predict_module.format_materials(_bundle(STATS_ITEM, PREVIEW_ITEM, FACTS_ITEM))
    assert shuffled == predict_module.format_materials(BUNDLE)


def test_a_long_preview_never_costs_the_facts_or_the_statistics() -> None:
    """A long preview is truncated in place; option stats and call facts still
    reach the prompt. Prior (stats, preview) comes before realization (facts)."""
    long_preview = {**PREVIEW_ITEM, "content": "# Preview\n" + "x" * 50_000}
    text = predict_module.format_materials(_bundle(FACTS_ITEM, long_preview, STATS_ITEM))
    assert "1. Revenue rose 12% year over year." in text
    assert "Implied earnings volatility: 8.5%" in text
    assert "[preview truncated]" in text
    assert text.index("Implied earnings volatility") < text.index("[preview truncated]")
    assert text.index("[preview truncated]") < text.index("Facts from the earnings call")
    kept = predict_module.PREVIEW_MAX_CHARS - len("# Preview\n")
    assert "x" * kept in text and "x" * (kept + 1) not in text


def _preview_section(title: str, sentinel: str, filler: int) -> str:
    return f"{title}\n{sentinel}\n" + "z" * filler + "\n"


LONG_STRUCTURED_PREVIEW = (
    "# ACME (ACME) — Q3 FY2026 Earnings Preview\nWritten by Claude Code before the release\n\n"
    + _preview_section("## 1. Consensus Estimates", "CONSENSUS_SENTINEL", 3000)
    + _preview_section("## 2. Key Metrics to Watch (ranked)", "KEY_METRICS_SENTINEL", 2000)
    + _preview_section("## 3. Scenario Analysis", "SCENARIO_SENTINEL", 2000)
    + _preview_section("## 4. Catalyst Checklist", "CATALYST_SENTINEL", 1500)
    + _preview_section("## 5. Trading Setup", "TRADING_SENTINEL", 1500)
    + _preview_section("### Caveats", "CAVEATS_SENTINEL", 800)
)


def test_a_long_structured_preview_spends_the_budget_where_the_signal_lives() -> None:
    """Every section header survives compression; the scenario grid and
    catalyst checklist — the ranking anchors — keep (near-)full length
    while the consensus table (which restates what the surprise benchmark
    already scores) is cut hardest, and the budget holds exactly."""
    compressed = predict_module._compress_preview(LONG_STRUCTURED_PREVIEW)
    assert len(compressed) <= predict_module.PREVIEW_MAX_CHARS
    for header in (
        "## 1. Consensus Estimates",
        "## 2. Key Metrics to Watch",
        "## 3. Scenario Analysis",
        "## 4. Catalyst Checklist",
        "## 5. Trading Setup",
        "### Caveats",
    ):
        assert header in compressed
    for sentinel in ("SCENARIO_SENTINEL", "CATALYST_SENTINEL", "TRADING_SENTINEL"):
        assert sentinel in compressed
    assert "[section trimmed]" in compressed  # consensus went under the knife
    consensus = compressed[compressed.index("## 1.") : compressed.index("## 2.")]
    scenario = compressed[compressed.index("## 3.") : compressed.index("## 4.")]
    assert len(scenario) > len(consensus)


def test_when_budgets_overflow_low_value_sections_floor_before_high_value_ones() -> None:
    """With every section over its budget, the deficit is shaved off the
    least valuable sections first (caveats before trading setup), so the
    scenario grid keeps its ranking head start."""
    heavy = (
        "# ACME — Q3 FY2026 Earnings Preview\n\n"
        + _preview_section("## 1. Consensus Estimates", "CONSENSUS_SENTINEL", 6000)
        + _preview_section("## 2. Key Metrics to Watch (ranked)", "KEY_METRICS_SENTINEL", 2500)
        + _preview_section("## 3. Scenario Analysis", "SCENARIO_SENTINEL", 2500)
        + _preview_section("## 4. Catalyst Checklist", "CATALYST_SENTINEL", 2500)
        + _preview_section("## 5. Trading Setup", "TRADING_SENTINEL", 2500)
        + _preview_section("### Caveats", "CAVEATS_SENTINEL", 2500)
    )
    compressed = predict_module._compress_preview(heavy)
    assert len(compressed) <= predict_module.PREVIEW_MAX_CHARS
    assert "SCENARIO_SENTINEL" in compressed
    assert "TRADING_SENTINEL" in compressed
    caveats = compressed[compressed.index("### Caveats") :]
    trading = compressed[compressed.index("## 5. Trading Setup") : compressed.index("### Caveats")]
    assert len(caveats) < len(trading)


def test_a_preview_within_the_budget_passes_through_unchanged() -> None:
    short = PREVIEW_ITEM["content"]
    assert predict_module._compress_preview(short) == short


def test_optional_items_may_be_absent() -> None:
    facts_only = predict_module.format_materials(_bundle(FACTS_ITEM))
    assert facts_only.startswith("Facts from the earnings call:")
    assert "Option-market" not in facts_only and "Research note" not in facts_only


def test_an_unavailable_skew_is_said_plainly() -> None:
    stats = {**STATS, "skew_25_delta": {"value": None, "status": "illiquid_wings"}}
    text = predict_module.format_materials(_bundle(FACTS_ITEM, {**STATS_ITEM, "content": stats}))
    assert "Implied earnings volatility: 8.5%" in text
    assert "25-delta skew: unavailable" in text


def test_statistics_without_a_usable_volatility_are_left_out() -> None:
    for broken in (
        {**STATS, "implied_earnings_volatility": {"value": None, "status": "illiquid_atm"}},
        {**STATS, "implied_earnings_volatility": {"value": "0.08", "status": "ok"}},
        {},
        {"as_of": "2026-10-05T19:36:12Z"},
    ):
        text = predict_module.format_materials(
            _bundle(FACTS_ITEM, {**STATS_ITEM, "content": broken})
        )
        assert "Option-market" not in text and "Facts from the earnings call" in text


def test_an_option_stats_object_does_not_reject_the_bundle() -> None:
    """Queue 1: stats content is an object. A str|list[str] read must not drop the rest."""
    text = predict_module.format_materials(
        _bundle(
            {**STATS_ITEM, "content": STATS},
            PREVIEW_ITEM,
            {**FACTS_ITEM, "content": "Guidance was raised."},
            {"id": "bullets", "kind": "list", "content": ["keep me", {"rows": [[1]]}, None, True, 3]},
            {"id": "future-table", "kind": "table", "content": {"rows": [[1, 2]]}},
            "not even an object",
        )
    )
    assert "Implied earnings volatility: 8.5%" in text
    assert "Research note written BEFORE the release" in text
    assert "1. Guidance was raised." in text
    assert "Additional material (bullets):\nkeep me\n3" in text
    assert "future-table" not in text
    assert "rows" not in text


def test_scenario_grid_is_extracted_from_tables_and_bullets() -> None:
    """Queue 3: grid rows reach the model even if compression drops the section."""
    table = (
        "## Scenario Analysis\n| Scenario | EPS | Reaction |\n|---|---|---|\n"
        "| **Bear** | $1.05 | -8% |\n| Base | $1.20 | +1% |\n| Bull | $1.35 | +7% |\n"
        "Bull case risk is priced.\n"
    )
    assert predict_module.extract_scenario_grid(table) == [
        "Bull | $1.35 | +7%",
        "Base | $1.20 | +1%",
        "Bear | $1.05 | -8%",
    ]
    bullets = "- **Bull case:** beat and raise, +6%\n- Basement project delayed\n"
    assert predict_module.extract_scenario_grid(bullets) == ["Bull case: beat and raise, +6%"]
    assert predict_module.extract_scenario_grid(PREVIEW) == []

    grid_item = {**PREVIEW_ITEM, "content": PREVIEW + table}
    text = predict_module.format_materials(_bundle(grid_item))
    assert text.index("Scenario grid from the research note") < text.index("Research note written")


def test_coverage_names_missing_inputs_and_blocks_a_ticker_prior() -> None:
    """Queue 6: an absent prior is stated, not silently replaced."""
    full = predict_module.materials_coverage(BUNDLE)
    assert full.startswith("Materials missing: none.")
    facts_only = predict_module.materials_coverage(_bundle(FACTS_ITEM))
    assert "pre-release research note" in facts_only
    assert "option-market statistics" in facts_only
    assert "earnings-call facts" not in facts_only
    assert "Do not substitute general knowledge" in facts_only
    assert predict_module.materials_coverage(None).startswith("Materials missing:")


def test_coverage_warns_against_double_counting_the_implied_move() -> None:
    """Queue 2: preview that quotes the implied move gets a direction-only note."""
    quoting = {**PREVIEW_ITEM, "content": PREVIEW + "\n## Trading Setup\nImplied move ±6.8%.\n"}
    note = predict_module.materials_coverage(_bundle(FACTS_ITEM, quoting, STATS_ITEM))
    assert "do not count the size of the move again" in note
    plain = predict_module.materials_coverage(_bundle(FACTS_ITEM, PREVIEW_ITEM, STATS_ITEM))
    assert "do not count the size" not in plain


def test_a_kind_this_code_has_never_seen_is_never_an_error() -> None:
    text = predict_module.format_materials(
        _bundle(
            FACTS_ITEM,
            {"id": "analyst-note", "kind": "text", "content": "Street is cautious."},
            {"id": "bullets", "kind": "list", "content": ["one", "two"]},
            {"id": "future-table", "kind": "table", "content": {"rows": [[1, 2]]}},
            {"id": "by-reference", "kind": "document", "url": "https://example.test/x.pdf"},
            "not even an object",
        )
    )
    assert "Additional material (analyst-note):\nStreet is cautious." in text
    assert "Additional material (bullets):\none\ntwo" in text
    assert "future-table" not in text and "by-reference" not in text


def test_anything_that_is_not_a_bundle_formats_to_nothing() -> None:
    for odd in (None, [], "text", {"summary": "legacy shape"}, {"items": "nope"}, {"items": []}):
        assert predict_module.format_materials(odd) == ""


def test_reasoning_effort_is_a_separate_first_form(monkeypatch) -> None:
    """Unset effort leaves the existing chain untouched. Set effort is the
    first GPT-6 form: max_completion_tokens plus that effort, no temperature,
    and the old forms stay behind it so an unsupported effort still falls through."""
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    assert predict_module._completion_param_sets() == predict_module._COMPLETION_PARAM_SETS

    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "max")
    sets = predict_module._completion_param_sets()
    assert sets[0] == {
        "max_completion_tokens": predict_module.LLM_MAX_TOKENS,
        "reasoning_effort": "max",
    }
    assert "temperature" not in sets[0]
    assert sets[1:] == predict_module._COMPLETION_PARAM_SETS


class _CapturingCompletions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        class _Message:
            content = '{"predicted_percentile": 0.61, "reason": "guidance raised"}'

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        return _Response()


class _CapturingClient:
    def __init__(self) -> None:
        self.completions = _CapturingCompletions()
        self.chat = self


def test_ask_llm_sends_luna_max_without_temperature(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-6-luna")
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "max")
    client = _CapturingClient()
    monkeypatch.setattr(predict_module, "_client", client)

    value = predict_module._ask_llm(
        ticker="AAPL",
        event_type="EARNINGS_RELEASE",
        materials="facts",
        option_signal="skew",
    )

    assert value == 0.61
    sent = client.completions.calls[0]
    assert sent["model"] == "gpt-6-luna"
    assert sent["reasoning_effort"] == "max"
    assert sent["max_completion_tokens"] == predict_module.LLM_MAX_TOKENS
    assert "temperature" not in sent


def test_truncated_output_is_logged(monkeypatch, capsys) -> None:
    """Queue 8: finish_reason=length is visible in the logs."""
    class _Truncated:
        def create(self, **_):
            class _Choice:
                finish_reason = "length"

                class message:
                    content = '{"predicted_percentile": 0.5'

            class _Response:
                choices = [_Choice()]

            return _Response()

    client = _CapturingClient()
    client.completions = _Truncated()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(predict_module, "_client", client)
    predict_module._ask_llm(ticker="AAPL", event_type="EARNINGS_RELEASE", materials="f", option_signal="s")
    assert "truncated for AAPL" in capsys.readouterr().out


def test_samples_are_averaged_and_disagreement_halves_the_tilt() -> None:
    """Queue 15a and 11: mean of samples; wide spread pulls toward 0.5."""
    assert predict_module.combine_samples([]) is None
    assert predict_module.combine_samples([0.7]) == 0.7
    assert predict_module.combine_samples([0.6, 0.7]) == pytest.approx(0.65)
    assert predict_module.combine_samples([0.4, 0.9]) == pytest.approx(0.575)
    a, b = predict_module.combine_samples([0.8, 0.85]), predict_module.combine_samples([0.5, 0.95])
    assert a > b > 0.5


def test_predict_one_runs_parallel_samples_and_drops_failures(monkeypatch) -> None:
    monkeypatch.setenv("PREDICTION_SAMPLES", "3")
    answers = iter([0.6, None, RuntimeError("boom")])
    calls = []

    def fake_ask(**kwargs):
        calls.append(kwargs["ticker"])
        answer = next(answers)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(predict_module, "_ask_llm", fake_ask)
    p = predict_module._predict_one(
        ticker="AAPL", event_type="EARNINGS_RELEASE", materials="m", option_signal="s"
    )
    assert calls == ["AAPL"] * 3
    assert p == 0.6


def test_all_samples_failing_falls_back_to_option_stats(monkeypatch) -> None:
    monkeypatch.setattr(predict_module, "_ask_llm", lambda **_: None)
    p = predict_module._predict_one(
        ticker="AAPL", event_type="EARNINGS_RELEASE", materials="m", option_signal="s",
        bundle=_bundle(STATS_ITEM),
    )
    assert p == pytest.approx(0.5 + 0.0412 * 1.5)


@pytest.mark.parametrize("raw,expected", [("", 2), ("1", 1), ("5", 5), ("0", 2), ("9", 2), ("x", 2)])
def test_prediction_samples_is_bounded(monkeypatch, raw, expected) -> None:
    from explaining_markets.config import prediction_samples

    monkeypatch.setenv("PREDICTION_SAMPLES", raw)
    assert prediction_samples() == expected
