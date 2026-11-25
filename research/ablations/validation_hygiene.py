"""Queue 12: frozen trial list, cutoff statement, and paired ΔΔR².

The statistic can be computed on arrays the caller already has. This module
does not load an archive, does not call a model, and does not interpret arm B
while the Astra cutoff assumption is unknown.
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass

CUTOFF_ASSUMPTION = "unknown"
DEFAULT_BOOTSTRAP = 1000


@dataclass(frozen=True)
class Trial:
    trial_id: str
    arm: str
    description: str


# Pre-registered before any archive run. A new arm is a new entry.
FROZEN_TRIALS: tuple[Trial, ...] = (
    Trial("10A", "A_full", "full materials"),
    Trial("10B", "B_ticker_date", "ticker, quarter, and event date only"),
    Trial("10C", "C_materials_only", "full materials plus a materials-only instruction"),
)


@dataclass(frozen=True)
class PairedDelta:
    """Paired contrast of two arms, with the frozen trial count and cutoff."""

    delta_r2_a: float
    delta_r2_b: float
    delta_delta: float
    n: int
    n_boot: int
    ci_low: float
    ci_high: float
    trials: int
    cutoff_assumption: str


def trial_count() -> int:
    return len(FROZEN_TRIALS)


def _solve(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Solve a square system. Raises ValueError when a pivot vanishes."""
    size = len(rhs)
    augmented = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-10:
            raise ValueError("singular design")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        for j in range(col, size + 1):
            augmented[col][j] /= scale
        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            for j in range(col, size + 1):
                augmented[row][j] -= factor * augmented[col][j]
    return [augmented[i][size] for i in range(size)]


def _is_full_rank(columns: list[list[float]]) -> bool:
    width = len(columns)
    height = len(columns[0])
    gram = [[0.0] * width for _ in range(width)]
    for i in range(width):
        for j in range(i, width):
            dot = sum(columns[i][k] * columns[j][k] for k in range(height))
            gram[i][j] = gram[j][i] = dot
    try:
        _solve(gram, [1.0] + [0.0] * (width - 1))
    except ValueError:
        return False
    return True


def _r2(y: list[float], features: list[list[float]]) -> float:
    """R² of y on an intercept plus whichever features increase rank, in order."""
    n = len(y)
    accepted: list[list[float]] = [[1.0] * n]
    for feature in features:
        trial = accepted + [feature]
        if _is_full_rank(trial):
            accepted = trial
    width = len(accepted)
    gram = [[0.0] * width for _ in range(width)]
    xty = [0.0] * width
    for i in range(width):
        xty[i] = sum(accepted[i][k] * y[k] for k in range(n))
        for j in range(i, width):
            dot = sum(accepted[i][k] * accepted[j][k] for k in range(n))
            gram[i][j] = gram[j][i] = dot
    beta = _solve(gram, xty)
    fitted = [sum(beta[j] * accepted[j][i] for j in range(width)) for i in range(n)]
    mean = sum(y) / n
    ss_tot = sum((value - mean) ** 2 for value in y)
    if ss_tot == 0.0:
        return 0.0
    ss_res = sum((y[i] - fitted[i]) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / ss_tot
    if abs(r2) < 1e-12:
        return 0.0
    return r2


def _as_floats(name: str, values: list[float], n: int) -> list[float]:
    if len(values) != n:
        raise ValueError(f"{name} must have length {n}")
    return [float(value) for value in values]


def delta_r_squared(y: list[float], surprise: list[float], prediction: list[float]) -> float:
    """ΔR² of one prediction beyond the surprise benchmark. Constant predictions score 0."""
    if len(y) < 3:
        raise ValueError("need at least 3 aligned events")
    outcome = _as_floats("y", y, len(y))
    benchmark = _as_floats("surprise", surprise, len(y))
    forecast = _as_floats("prediction", prediction, len(y))
    return _r2(outcome, [benchmark, forecast]) - _r2(outcome, [benchmark])


def paired_delta_delta(
    y: list[float],
    surprise: list[float],
    pred_a: list[float],
    pred_b: list[float],
    *,
    n_boot: int = DEFAULT_BOOTSTRAP,
    seed: int = 0,
) -> PairedDelta:
    """ΔR²(A) − ΔR²(B) on one shared bootstrap of the same events."""
    if n_boot < 1:
        raise ValueError("n_boot must be positive")
    point_a = delta_r_squared(y, surprise, pred_a)
    point_b = delta_r_squared(y, surprise, pred_b)
    n = len(y)
    rng = random.Random(seed)
    diffs: list[float] = []
    for _ in range(n_boot):
        index = [rng.randrange(n) for _ in range(n)]
        outcome = [y[i] for i in index]
        benchmark = [surprise[i] for i in index]
        arm_a = [pred_a[i] for i in index]
        arm_b = [pred_b[i] for i in index]
        diffs.append(delta_r_squared(outcome, benchmark, arm_a) - delta_r_squared(outcome, benchmark, arm_b))
    diffs.sort()
    last = len(diffs) - 1
    return PairedDelta(
        delta_r2_a=point_a,
        delta_r2_b=point_b,
        delta_delta=point_a - point_b,
        n=n,
        n_boot=n_boot,
        ci_low=diffs[int(0.025 * last)],
        ci_high=diffs[int(0.975 * last)],
        trials=trial_count(),
        cutoff_assumption=CUTOFF_ASSUMPTION,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Queue 12 validation hygiene. Does not run an archive.")
    parser.add_argument("--check", action="store_true", help="Print the frozen trial list and cutoff")
    parser.add_argument("--run", action="store_true", help="Refused")
    args = parser.parse_args(argv)
    if args.run:
        print("refusing: this script does not run archive predictions", file=sys.stderr)
        return 2
    print(f"trials={trial_count()}")
    for trial in FROZEN_TRIALS:
        print(f"{trial.trial_id} {trial.arm}")
    print(f"cutoff_assumption={CUTOFF_ASSUMPTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
