"""Logg egen plassering på explainingmarkets.ai over tid.

Kjøres daglig av .github/workflows/leaderboard-snapshot.yml og legger til
rader i data/leaderboard_history.csv. Kun standardbiblioteket.

Regler:
- Hver periode i leaderboard-indeksen sjekkes (kvartaler og -CONTEST).
- En ny rad skrives bare når arrangøren har publisert nye tall
  (ny generated_at for perioden), så CSV-en ikke fylles med duplikater.
- Frosne perioder skrives én gang og aldri igjen (sluttplassering).

Bruk:
  python scripts/snapshot_leaderboard.py
  python scripts/snapshot_leaderboard.py --name Tokenmaxxer --out data/leaderboard_history.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "web"))

from app.leaderboard import (  # noqa: E402
    LEADERBOARD_ID,
    PUBLIC_NAME,
    find_standing,
    index_url,
    standings_url,
)

DEFAULT_OUT = REPO_ROOT / "data" / "leaderboard_history.csv"
COLUMNS = (
    "captured_at",
    "period",
    "frozen",
    "rank",
    "total",
    "participant_rank",
    "participants",
    "rank_common",
    "rank_own",
    "ranking_metric",
    "score",
    "r_squared",
    "n_obs",
    "submission_id",
    "public_name",
    "generated_at",
)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "leaderboard-snapshot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def read_history(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", default=PUBLIC_NAME)
    parser.add_argument("--board", default=LEADERBOARD_ID)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    history = read_history(args.out)
    seen = {(r["period"], r["generated_at"]) for r in history}
    frozen_done = {r["period"] for r in history if r.get("frozen") == "True"}

    index = get_json(index_url(args.board))
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    new_rows: list[dict] = []

    for p in index.get("periods") or []:
        period = p.get("period")
        if not period or p.get("status") != "ranked" or period in frozen_done:
            continue
        try:
            standings = get_json(standings_url(period, args.board))
        except urllib.error.HTTPError as exc:
            print(f"{period}: hoppet over ({exc.code})")
            continue
        standing = find_standing(standings, args.name)
        if standing is None:
            print(f"{period}: {args.name} ikke med")
            continue
        if (standing.period, standing.generated_at) in seen:
            print(f"{period}: ingen nye tall (#{standing.rank})")
            continue
        row = {"captured_at": captured_at, **standing.as_row()}
        new_rows.append({k: row.get(k) for k in COLUMNS})
        print(f"{period}: #{standing.rank} av {standing.total} (score {standing.score})")

    if not new_rows:
        print("Ingenting nytt å skrive.")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_header = not args.out.exists()
    with args.out.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)
    print(f"Skrev {len(new_rows)} rad(er) til {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
