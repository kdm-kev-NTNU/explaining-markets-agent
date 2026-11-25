"""Invariants for the passive submitted-percentile spread log.

The log describes the cross-section that was submitted. It must not invent an
alert cutoff, must ignore unscored test deliveries, and must not append the
same event twice.
"""

from __future__ import annotations

import math

from explaining_markets.dispersion import (
    WINDOW,
    dispersion_of,
    observe_submitted,
    quarter_key,
)

EVENT = {
    "event_id": "evt-1",
    "event_type": "EARNINGS_RELEASE",
    "event_datetime": "2026-11-02T21:00:00Z",
}


def _event(event_id: str, when: str = "2026-11-02T21:00:00Z") -> dict:
    return {
        "event_id": event_id,
        "event_type": "EARNINGS_RELEASE",
        "event_datetime": when,
    }


def _pred(ticker: str, percentile: float) -> dict:
    return {"identifier_value": ticker, "predicted_percentile": percentile}


def test_population_sd_and_band_edges() -> None:
    """sd divides by n. Band edges are inclusive; tails are strict."""
    stats = dispersion_of([0.0, 0.1, 0.3, 0.7, 0.9, 1.0])
    assert stats.n == 6
    mean = sum([0.0, 0.1, 0.3, 0.7, 0.9, 1.0]) / 6
    expected = math.sqrt(sum((p - mean) ** 2 for p in [0.0, 0.1, 0.3, 0.7, 0.9, 1.0]) / 6)
    assert stats.sd is not None
    assert abs(stats.sd - expected) < 1e-12
    # 0.3 and 0.7 are inside the mid band. 0.1 and 0.9 are not tails.
    assert stats.mid_band_share == 2 / 6
    assert stats.tail_share == 2 / 6


def test_single_point_has_no_sd_and_flat_series_has_zero_sd() -> None:
    assert dispersion_of([]).sd is None
    assert dispersion_of([0.4]).sd is None
    flat = dispersion_of([0.5, 0.5, 0.5])
    assert flat.sd == 0.0
    assert flat.mid_band_share == 1.0
    assert flat.tail_share == 0.0


def test_observe_logs_quarter_spread_and_keeps_predictions() -> None:
    store: dict = {}
    predictions = [_pred("AAPL", 0.2), _pred("MSFT", 0.8)]
    snapshot = [dict(p) for p in predictions]
    lines = observe_submitted(EVENT, predictions, store)
    assert predictions == snapshot
    assert len(lines) == 2
    assert "quarter=2026Q4" in lines[0]
    assert "n=1 sd=na" in lines[0]
    assert "n=2" in lines[1]
    assert "alert=uncalibrated" in lines[0]
    assert "alert=uncalibrated" in lines[1]
    assert store["2026Q4"]["percentiles"] == [0.2, 0.8]


def test_same_event_is_not_appended_twice() -> None:
    store: dict = {}
    observe_submitted(EVENT, [_pred("AAPL", 0.2)], store)
    again = observe_submitted(EVENT, [_pred("AAPL", 0.9)], store)
    assert again == []
    assert store["2026Q4"]["percentiles"] == [0.2]


def test_window_is_the_last_ten_points() -> None:
    store: dict = {}
    for i in range(WINDOW + 1):
        observe_submitted(
            _event(f"evt-{i}"),
            [_pred("AAPL", 0.0 if i == 0 else 0.5)],
            store,
        )
    series = store["2026Q4"]["percentiles"]
    assert len(series) == WINDOW + 1
    full = dispersion_of(series)
    window = dispersion_of(series[-WINDOW:])
    assert window.n == WINDOW
    assert 0.0 not in series[-WINDOW:]
    assert full.sd is not None and window.sd is not None
    assert window.sd < full.sd


def test_test_delivery_and_missing_quarter_do_not_touch_the_store() -> None:
    store: dict = {}
    test_event = dict(EVENT, event_type="TEST")
    assert observe_submitted(test_event, [_pred("AAPL", 0.5)], store) == []
    undated = {"event_id": "evt-2", "event_type": "EARNINGS_RELEASE"}
    assert observe_submitted(undated, [_pred("AAPL", 0.5)], store) == []
    assert store == {}
    assert quarter_key(undated) is None
    assert quarter_key({"event_datetime": "2026-01-15T00:00:00Z"}) == "2026Q1"


def test_invalid_points_are_skipped_and_corrupt_store_is_replaced() -> None:
    store: dict = {"2026Q4": {"keys": ["old"], "percentiles": ["nope"]}}
    warnings: list[str] = []
    lines = observe_submitted(
        EVENT,
        [
            {"identifier_value": "AAPL", "predicted_percentile": True},
            {"identifier_value": "MSFT", "predicted_percentile": 1.2},
            _pred("NVDA", 0.4),
        ],
        store,
        log=warnings.append,
    )
    assert len(lines) == 1
    assert store["2026Q4"]["percentiles"] == [0.4]
    assert any(line.startswith("[WARN]") for line in warnings)
    assert warnings[-1] == lines[0]
