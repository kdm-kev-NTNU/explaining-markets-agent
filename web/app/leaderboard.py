"""Leaderboard på explainingmarkets.ai: velg periode og finn egen rad.

Kun standardbiblioteket, slik at snapshot-scriptet i scripts/ kan gjenbruke
samme logikk uten å installere web-avhengighetene.

Dataen er statiske JSON-snapshots på CloudFront (samme kilde som nettsiden):
  {base}/leaderboards/v1/{board}/index.json      -> perioder
  {base}/leaderboards/v1/{board}/{PERIOD}.json   -> rows med rank og metrics
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

LEADERBOARD_BASE_URL = "https://df48ooei1lq8t.cloudfront.net"
LEADERBOARD_ID = "lb_global"
PUBLIC_NAME = "Tokenmaxxer"


def index_url(board: str = LEADERBOARD_ID, base: str = LEADERBOARD_BASE_URL) -> str:
    return f"{base}/leaderboards/v1/{board}/index.json"


def standings_url(
    period: str, board: str = LEADERBOARD_ID, base: str = LEADERBOARD_BASE_URL
) -> str:
    return f"{base}/leaderboards/v1/{board}/{period.upper()}.json"


@dataclass(frozen=True)
class Standing:
    """Én deltakers plassering i én periode."""

    period: str
    frozen: bool
    public_name: str
    submission_id: str
    rank: int
    rank_common: int | None
    rank_own: int | None
    total: int  # alle rader, inkl. baselines (slik arrangøren rangerer)
    participants: int  # rader som ikke er baselines
    participant_rank: int  # plass blant ekte deltakere (baselines trukket fra)
    ranking_metric: str
    score: float | None  # verdien av ranking_metric
    r_squared: float | None
    n_obs: int | None
    generated_at: str

    def as_row(self) -> dict[str, Any]:
        return asdict(self)


def featured_period(index: dict[str, Any]) -> str | None:
    """Periode forsiden bør vise: inneværende konkurranse hvis den er rangert.

    Speiler arrangørens logikk: siste rangerte «-CONTEST»-periode, ellers
    current_period.
    """
    periods = index.get("periods") or []
    current = index.get("current_period")
    contests = [
        p["period"]
        for p in periods
        if str(p.get("period", "")).endswith("-CONTEST") and p.get("status") == "ranked"
    ]
    if current and f"{current}-CONTEST" in contests:
        return f"{current}-CONTEST"
    if contests:
        return contests[-1]
    return current


def find_standing(standings: dict[str, Any], public_name: str = PUBLIC_NAME) -> Standing | None:
    """Finn raden med gitt public_name (uavhengig av store/små bokstaver)."""
    rows = standings.get("rows") or []
    target = public_name.strip().casefold()
    mine = next(
        (r for r in rows if str(r.get("public_name", "")).strip().casefold() == target),
        None,
    )
    if mine is None:
        return None

    rank = int(mine["rank"])
    baselines_ahead = sum(
        1 for r in rows if r.get("baseline") and r.get("rank") is not None and int(r["rank"]) < rank
    )
    metric = str(standings.get("ranking_metric") or "delta_r_squared_imputed")
    metrics = mine.get("metrics") or {}
    r2_key = "r_squared_imputed" if metric.endswith("_imputed") else "r_squared"
    return Standing(
        period=str(standings.get("period", "")),
        frozen=bool(standings.get("frozen", False)),
        public_name=str(mine.get("public_name", "")),
        submission_id=str(mine.get("submission_id", "")),
        rank=rank,
        rank_common=mine.get("rank_common"),
        rank_own=mine.get("rank_own"),
        total=len(rows),
        participants=sum(1 for r in rows if not r.get("baseline")),
        participant_rank=rank - baselines_ahead,
        ranking_metric=metric,
        score=metrics.get(metric),
        r_squared=metrics.get(r2_key),
        n_obs=mine.get("n_obs"),
        generated_at=str(standings.get("generated_at", "")),
    )
