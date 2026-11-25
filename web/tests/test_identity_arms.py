"""Queue 10 arm contract: three frozen inputs, no masking, no execution."""

from __future__ import annotations

import sys
from pathlib import Path

ABLATIONS = Path(__file__).resolve().parents[2] / "research" / "ablations"
if str(ABLATIONS) not in sys.path:
    sys.path.insert(0, str(ABLATIONS))

import identity_arms as arms

EVENT = {
    "event_id": "evt-1",
    "event_type": "EARNINGS_RELEASE",
    "event_datetime": "2026-11-02T21:00:00Z",
    "focal_assets": [{"identifier_type": "TICKER", "identifier_value": "ACME"}],
}

BUNDLE = {
    "items": [
        {"id": "option-implied-stats", "content": {"skew_25_delta": {"value": -0.04, "status": "ok"}}},
        {"id": "earnings-preview", "content": "unique-preview-sentence about ACME"},
        {"id": "earnings-call-facts", "content": ["unique-call-fact about margins"]},
    ]
}


def test_three_arms_and_run_is_refused() -> None:
    assert arms.ARM_IDS == ("A_full", "B_ticker_date", "C_materials_only")
    assert arms.TRIAL_IDS == ("10A", "10B", "10C")
    assert arms.CUTOFF_ASSUMPTION == "unknown"
    assert arms.main(["--check"]) == 0
    assert arms.main(["--run"]) == 2


def test_arm_b_keeps_identity_fields_and_drops_materials() -> None:
    built = arms.arm_input("B_ticker_date", EVENT, BUNDLE)
    assert built["tickers"] == ["ACME"]
    assert built["quarter"] == "2026Q4"
    assert built["event_date"] == "2026-11-02"
    assert built["trial_id"] == "10B"
    assert "bundle" not in built
    assert "unique-preview-sentence" not in repr(built)
    assert "unique-call-fact" not in repr(built)
    assert not arms._contains_dropped_material(built)


def test_arm_a_keeps_bundle_and_arm_c_adds_only_the_frozen_instruction() -> None:
    full = arms.arm_input("A_full", EVENT, BUNDLE)
    constrained = arms.arm_input("C_materials_only", EVENT, BUNDLE)
    assert full["bundle"]["items"][2]["content"] == ["unique-call-fact about margins"]
    assert "instruction" not in full
    assert constrained["instruction"] == arms.C_INSTRUCTION
    assert constrained["bundle"] == full["bundle"]
    constrained["bundle"]["items"].clear()
    assert BUNDLE["items"][2]["content"] == ["unique-call-fact about margins"]


def test_masking_is_not_an_arm() -> None:
    try:
        arms.arm_input("masked", EVENT, BUNDLE)
    except ValueError as exc:
        assert "masking" in str(exc)
    else:
        raise AssertionError("masked arm was accepted")
