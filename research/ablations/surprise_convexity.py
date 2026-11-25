"""Queue 13, trial 13A: monotone surprise reaction given valuation uncertainty.

The benchmark treats surprise as one linear term. This arm is a pre-registered
shape on top of the surprise percentile: steeper near the median and flatter
toward the tails when uncertainty is high, and linear when uncertainty is low.

It does not call a model, does not read an archive, and is not wired into the
live prompt. The prompt change waits for a positive paired result.
"""

from __future__ import annotations

import argparse
import math
import sys

# Frozen before any archive run. Not estimated.
CURVATURE_K = 2.0
TRIAL_ID = "13A"
CUTOFF_ASSUMPTION = "unknown"


def uncertainty(implied_vol: float | None, implied_abs_move: float | None) -> float:
    """Map option stats to u in [0, 1]. Missing or non-positive inputs are u = 0.

    u = clip(vol / abs_move - 1, 0, 1). A ratio of 1 is the linear case.
    A ratio of 2 is the most curved case. Preview fields are not used.
    """
    if (
        implied_vol is None
        or implied_abs_move is None
        or isinstance(implied_vol, bool)
        or isinstance(implied_abs_move, bool)
        or implied_vol <= 0
        or implied_abs_move <= 0
    ):
        return 0.0
    return max(0.0, min(1.0, implied_vol / implied_abs_move - 1.0))


def surprise_reaction(surprise_percentile: float, u: float, *, k: float = CURVATURE_K) -> float:
    """Monotone map of a surprise percentile. Endpoints and the median stay fixed.

    t = 2s - 1. High u mixes t with tanh(k t) / tanh(k), which is steeper at
    0 and flatter near ±1. u = 0 returns s unchanged.
    """
    if isinstance(surprise_percentile, bool) or isinstance(u, bool):
        raise TypeError("surprise percentile and uncertainty must be numbers")
    s = min(1.0, max(0.0, float(surprise_percentile)))
    weight = min(1.0, max(0.0, float(u)))
    if weight == 0.0:
        return s
    t = 2.0 * s - 1.0
    if weight == 0.0 or t == 0.0:
        curved = t
    else:
        curved = math.tanh(k * t) / math.tanh(k)
    mixed = (1.0 - weight) * t + weight * curved
    return 0.5 + 0.5 * mixed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Queue 13 surprise-convexity arm. Does not run it.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--run", action="store_true", help="Refused")
    args = parser.parse_args(argv)
    if args.run:
        print("refusing: this script does not run archive predictions", file=sys.stderr)
        return 2
    print(f"trial={TRIAL_ID}")
    print(f"k={CURVATURE_K}")
    print(f"cutoff_assumption={CUTOFF_ASSUMPTION}")
    print("prompt=unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
