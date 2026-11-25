"""Queue 10: build the three frozen identity-ablation arms.

The module describes what each arm would see. It does not call a model,
does not read an archive, and does not change the live prompt.

Masking is not an arm. Arm B drops facts, preview, and option stats instead
of redacting names inside them.
"""

from __future__ import annotations

import argparse
import copy
import sys
from collections.abc import Mapping
from typing import Any

ARM_IDS = ("A_full", "B_ticker_date", "C_materials_only")
TRIAL_IDS = ("10A", "10B", "10C")

FACTS_ID = "earnings-call-facts"
PREVIEW_ID = "earnings-preview"
OPTION_STATS_ID = "option-implied-stats"
DROPPED_ON_B = frozenset({FACTS_ID, PREVIEW_ID, OPTION_STATS_ID})

C_INSTRUCTION = (
    "Justify the percentile only from the materials in this input. "
    "Do not use prior knowledge of the company."
)

CUTOFF_ASSUMPTION = "unknown"


def quarter_key(event: Mapping[str, Any]) -> str | None:
    """Calendar quarter of event_datetime, or None when the timestamp is missing."""
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


def event_date(event: Mapping[str, Any]) -> str | None:
    raw = event.get("event_datetime")
    if not isinstance(raw, str) or len(raw) < 10 or raw[4] != "-" or raw[7] != "-":
        return None
    try:
        year = int(raw[0:4])
        month = int(raw[5:7])
        day = int(raw[8:10])
    except ValueError:
        return None
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def tickers(event: Mapping[str, Any]) -> list[str]:
    assets = event.get("focal_assets")
    if not isinstance(assets, list):
        return []
    names: list[str] = []
    for asset in assets:
        if isinstance(asset, dict) and asset.get("identifier_value"):
            names.append(str(asset["identifier_value"]))
    return names


def _bundle_copy(bundle: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        return {"items": []}
    return copy.deepcopy(bundle)


def arm_input(arm: str, event: Mapping[str, Any], bundle: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return the frozen input for one arm. The caller's bundle is not mutated."""
    if arm not in ARM_IDS:
        raise ValueError(f"unknown arm {arm!r}; masking is not an arm")
    base: dict[str, Any] = {
        "arm": arm,
        "trial_id": TRIAL_IDS[ARM_IDS.index(arm)],
        "event_id": event.get("event_id"),
        "tickers": tickers(event),
        "quarter": quarter_key(event),
        "event_date": event_date(event),
    }
    if arm == "B_ticker_date":
        return base
    copied = _bundle_copy(bundle)
    if arm == "A_full":
        return {**base, "bundle": copied}
    return {**base, "bundle": copied, "instruction": C_INSTRUCTION}


def _contains_dropped_material(payload: Mapping[str, Any]) -> bool:
    """True when arm B accidentally kept facts, preview, or option stats."""
    if "bundle" in payload or "instruction" in payload:
        return True
    blob = repr(payload)
    return any(item_id in blob for item_id in DROPPED_ON_B)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Queue 10 identity arms. Does not run them.")
    parser.add_argument("--check", action="store_true", help="Print the frozen arm list")
    parser.add_argument("--run", action="store_true", help="Refused")
    args = parser.parse_args(argv)
    if args.run:
        print("refusing: this script does not run archive predictions", file=sys.stderr)
        return 2
    print("arms=" + ",".join(ARM_IDS))
    print("trials=" + ",".join(TRIAL_IDS))
    print(f"cutoff_assumption={CUTOFF_ASSUMPTION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
