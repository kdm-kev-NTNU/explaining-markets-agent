"""Passive cross-sectional spread log for submitted percentiles.

Queue 15, part (b) only. This module records the percentile that was already
submitted and logs the quarter's dispersion. It does not call a model, does
not draw extra samples, and does not change the number that was submitted.

The logged ``sd`` is the population standard deviation of the observed
percentiles in that quarter (divisor ``n``). It describes the set submitted
so far, not an estimate of a larger population. ``n < 2`` has no sd.

Bands, fixed by the research note, are not thresholds:

- mid band: percentile in ``[0.3, 0.7]`` (inclusive)
- tail: percentile strictly outside ``[0.1, 0.9]``

``alert`` is always ``uncalibrated``. The rolling 10-observation window is
logged so a threshold can be set later from measured archive dispersion.
This module does not invent that cutoff and does not emit an alert.

State is one record per quarter in the store the caller passes. A read-
modify-write of that record can drop one concurrent observation if two
submits in the same quarter overlap. Each log line includes the point just
recorded, so the series can be rebuilt from logs. Re-recording the same
``event_id`` and ticker does not append a second point.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, Callable

MID_LOW = 0.3
MID_HIGH = 0.7
TAIL_LOW = 0.1
TAIL_HIGH = 0.9
WINDOW = 10

Log = Callable[[str], None]


@dataclass(frozen=True)
class Dispersion:
    """Dispersion of one observed cross-section. Shares are fractions in [0, 1]."""

    n: int
    sd: float | None
    mid_band_share: float | None
    tail_share: float | None


def dispersion_of(percentiles: Sequence[float]) -> Dispersion:
    """Population sd and band shares of ``percentiles``, in the given order."""
    values = [float(p) for p in percentiles]
    n = len(values)
    if n == 0:
        return Dispersion(0, None, None, None)
    mid = sum(1 for p in values if MID_LOW <= p <= MID_HIGH) / n
    tail = sum(1 for p in values if p < TAIL_LOW or p > TAIL_HIGH) / n
    if n < 2:
        return Dispersion(n, None, mid, tail)
    mean = sum(values) / n
    variance = sum((p - mean) ** 2 for p in values) / n
    return Dispersion(n, math.sqrt(variance), mid, tail)


def quarter_key(event: Mapping[str, Any]) -> str | None:
    """Calendar quarter of ``event_datetime``, or None when it is missing."""
    raw = event.get("event_datetime")
    if not isinstance(raw, str) or len(raw) < 7 or raw[4] != "-":
        return None
    try:
        year = int(raw[0:4])
        month = int(raw[5:7])
    except ValueError:
        return None
    if not 1 <= month <= 12:
        return None
    return f"{year}Q{(month - 1) // 3 + 1}"


def _percentile(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not 0.0 <= number <= 1.0:
        return None
    return number


def _series(raw: Any) -> tuple[list[str], list[float]] | None:
    """Return the stored series, an empty series, or None when the record is corrupt."""
    if raw is None:
        return [], []
    if not isinstance(raw, dict):
        return None
    keys = raw.get("keys")
    values = raw.get("percentiles")
    if (
        not isinstance(keys, list)
        or not isinstance(values, list)
        or len(keys) != len(values)
        or not all(isinstance(key, str) for key in keys)
    ):
        return None
    parsed: list[float] = []
    for value in values:
        number = _percentile(value)
        if number is None:
            return None
        parsed.append(number)
    return list(keys), parsed


def _format(value: float | None) -> str:
    return "na" if value is None else f"{value:.4f}"


def _line(
    *,
    quarter: str,
    event_id: str,
    ticker: str,
    point: float,
    full: Dispersion,
    window: Dispersion,
) -> str:
    return (
        f"[DISPERSION] quarter={quarter} event={event_id} ticker={ticker} "
        f"point={point:.4f} n={full.n} sd={_format(full.sd)} "
        f"mid_band_share={_format(full.mid_band_share)} "
        f"tail_share={_format(full.tail_share)} "
        f"window_n={window.n} window_sd={_format(window.sd)} "
        f"window_mid_band_share={_format(window.mid_band_share)} "
        f"window_tail_share={_format(window.tail_share)} "
        f"alert=uncalibrated"
    )


def observe_submitted(
    event: Mapping[str, Any],
    predictions: Sequence[Mapping[str, Any]],
    store: MutableMapping[str, Any],
    *,
    log: Log = print,
) -> list[str]:
    """Append submitted percentiles and log the quarter's spread.

    Test deliveries are ignored. The ``predictions`` sequence is not modified.
    Returns the log lines written, one per newly recorded point.
    """
    if event.get("event_type") == "TEST":
        return []
    quarter = quarter_key(event)
    if quarter is None:
        return []
    event_id = str(event.get("event_id") or "")
    raw = store.get(quarter)
    loaded = _series(raw)
    if loaded is None:
        keys, values = [], []
        log(f"[WARN] dispersion store for {quarter} was unreadable; starting a new series")
    else:
        keys, values = loaded

    lines: list[str] = []
    for prediction in predictions:
        ticker = str(prediction.get("identifier_value") or "")
        point = _percentile(prediction.get("predicted_percentile"))
        if point is None or not event_id or not ticker:
            continue
        key = f"{event_id}:{ticker}"
        if key in keys:
            continue
        keys.append(key)
        values.append(point)
        full = dispersion_of(values)
        window = dispersion_of(values[-WINDOW:])
        lines.append(
            _line(
                quarter=quarter,
                event_id=event_id,
                ticker=ticker,
                point=point,
                full=full,
                window=window,
            )
        )
    if lines:
        store[quarter] = {"keys": keys, "percentiles": values}
        for line in lines:
            log(line)
    return lines
