"""Queue 12: the metric and the frozen trial list, without an archive run."""

from __future__ import annotations

import sys
from pathlib import Path

ABLATIONS = Path(__file__).resolve().parents[2] / "research" / "ablations"
if str(ABLATIONS) not in sys.path:
    sys.path.insert(0, str(ABLATIONS))

import validation_hygiene as hygiene

Y = [0.1, 0.2, 0.4, 0.7, 0.9]
SURPRISE = [0.2, 0.4, 0.5, 0.6, 0.8]


def test_frozen_trials_and_unknown_cutoff() -> None:
    assert hygiene.trial_count() == 3
    assert [trial.trial_id for trial in hygiene.FROZEN_TRIALS] == ["10A", "10B", "10C"]
    assert hygiene.CUTOFF_ASSUMPTION == "unknown"
    assert hygiene.main(["--check"]) == 0
    assert hygiene.main(["--run"]) == 2


def test_constant_and_affine_predictions_score_zero() -> None:
    assert abs(hygiene.delta_r_squared(Y, SURPRISE, [0.5] * len(Y))) < 1e-9
    affine = [0.1 + 0.3 * value for value in SURPRISE]
    assert abs(hygiene.delta_r_squared(Y, SURPRISE, affine)) < 1e-9


def test_prediction_that_matches_outcome_beats_a_flat_surprise() -> None:
    flat_surprise = [0.5] * len(Y)
    score = hygiene.delta_r_squared(Y, flat_surprise, Y)
    assert abs(score - 1.0) < 1e-8


def test_paired_contrast_uses_one_shared_sample() -> None:
    same = hygiene.paired_delta_delta(Y, SURPRISE, Y, Y, n_boot=40, seed=1)
    assert same.delta_delta == 0.0
    assert same.ci_low == 0.0 and same.ci_high == 0.0
    assert same.trials == 3
    assert same.cutoff_assumption == "unknown"

    contrast = hygiene.paired_delta_delta(Y, SURPRISE, Y, [0.5] * len(Y), n_boot=40, seed=1)
    again = hygiene.paired_delta_delta(Y, SURPRISE, Y, [0.5] * len(Y), n_boot=40, seed=1)
    assert contrast.delta_delta > 0
    assert contrast.ci_low == again.ci_low
    assert contrast.n == len(Y)
    assert contrast.n_boot == 40
