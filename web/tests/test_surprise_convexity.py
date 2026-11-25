"""Queue 13A: the frozen surprise map is monotone and stays off the live prompt."""

from __future__ import annotations

import sys
from pathlib import Path

ABLATIONS = Path(__file__).resolve().parents[2] / "research" / "ablations"
if str(ABLATIONS) not in sys.path:
    sys.path.insert(0, str(ABLATIONS))

import surprise_convexity as convexity

GRID = [i / 20 for i in range(21)]


def test_trial_is_frozen_and_run_is_refused() -> None:
    assert convexity.TRIAL_ID == "13A"
    assert convexity.CURVATURE_K == 2.0
    assert convexity.CUTOFF_ASSUMPTION == "unknown"
    assert convexity.main(["--check"]) == 0
    assert convexity.main(["--run"]) == 2


def test_missing_option_stats_are_linear() -> None:
    assert convexity.uncertainty(None, 0.08) == 0.0
    assert convexity.uncertainty(0.08, 0.0) == 0.0
    assert convexity.uncertainty(0.08, 0.08) == 0.0
    assert convexity.uncertainty(0.16, 0.08) == 1.0
    assert convexity.uncertainty(0.12, 0.08) == 0.5
    for s in GRID:
        assert convexity.surprise_reaction(s, 0.0) == s


def test_high_uncertainty_is_steeper_at_the_median_and_flatter_in_the_tail() -> None:
    steep = (convexity.surprise_reaction(0.55, 1.0) - 0.5) / 0.05
    flat = (1.0 - convexity.surprise_reaction(0.95, 1.0)) / 0.05
    assert steep > 1.0
    assert flat < 1.0
    assert convexity.surprise_reaction(0.6, 1.0) > 0.6


def test_map_stays_in_unit_interval_and_is_monotone() -> None:
    for u in (0.0, 0.5, 1.0):
        values = [convexity.surprise_reaction(s, u) for s in GRID]
        assert values[0] == 0.0
        assert values[-1] == 1.0
        assert abs(convexity.surprise_reaction(0.5, u) - 0.5) < 1e-12
        assert values == sorted(values)
        assert all(0.0 <= value <= 1.0 for value in values)
