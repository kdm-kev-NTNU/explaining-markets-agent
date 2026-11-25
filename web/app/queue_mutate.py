"""Mutasjoner av research/queue.yaml for research-cron og auto-PR.

CLI (kjør fra web/):
  python -m app.queue_mutate next-id --path ../research/queue.yaml
  python -m app.queue_mutate add --path ../research/queue.yaml \\
      --title "…" --area 3c --risk live_prompt --automation manual \\
      --added 2026-W48 --note "…" --arxiv 2611.12345
  python -m app.queue_mutate set-status --path ../research/queue.yaml \\
      --id 13 --status partial --note "…" [--commit abc1234] [--pr URL]
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .research_registry import (
    LIVE_RISKS,
    Automation,
    QueueItem,
    QueueRegistry,
    Risk,
    Status,
    load_queue_yaml,
    parse_queue_yaml,
)


def _dump(registry: QueueRegistry) -> str:
    """Serialiser registry til YAML. Kommentar-header bevares ikke (maskinfil)."""
    data = registry.model_dump(mode="json", exclude_none=True)
    header = (
        "# Implementeringskø — sannhetskilde for status/automatisering.\n"
        "# Prosa og paper-sammendrag lever i FORSKNING.md.\n"
        "# Valider: python -m app.research_registry --check research/queue.yaml\n"
        "# Muter: python -m app.queue_mutate … (fra web/)\n\n"
    )
    body = yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    )
    return header + body


def save_queue(path: Path, registry: QueueRegistry) -> None:
    path.write_text(_dump(registry), encoding="utf-8")
    # Round-trip: avvis hvis vi nettopp skrev noe ugyldig
    load_queue_yaml(path)


def next_id(registry: QueueRegistry) -> int:
    return max((it.id for it in registry.items), default=0) + 1


def next_rank(registry: QueueRegistry) -> int:
    active = [it.rank for it in registry.items if not it.is_finished]
    return max(active, default=0) + 1


def add_item(
    registry: QueueRegistry,
    *,
    title: str,
    area: str,
    risk: Risk,
    automation: Automation,
    added: str,
    note: str,
    arxiv_refs: list[str] | None = None,
    status: Status = "queued",
    item_id: int | None = None,
    rank: int | None = None,
    due: str | None = None,
    today: str | None = None,
) -> QueueRegistry:
    today = today or date.today().isoformat()
    new_id = item_id if item_id is not None else next_id(registry)
    new_rank = rank if rank is not None else next_rank(registry)
    if risk in LIVE_RISKS:
        automation = "manual"

    sources = [{"kind": "arxiv", "ref": r} for r in (arxiv_refs or [])]
    raw: dict[str, Any] = {
        "id": new_id,
        "title": title,
        "area": area,
        "status": status,
        "rank": new_rank,
        "risk": risk,
        "automation": automation,
        "added": added,
        "sources": sources,
        "history": [{"date": today, "status": status, "note": note}],
    }
    if due:
        raw["due"] = due

    item = QueueItem.model_validate(raw)
    items = list(registry.items) + [item]
    return QueueRegistry.model_validate(
        {
            "version": registry.version,
            "updated": today,
            "recommended_order": list(registry.recommended_order),
            "items": [it.model_dump(mode="json") for it in items],
        }
    )


def set_status(
    registry: QueueRegistry,
    *,
    item_id: int,
    status: Status,
    note: str,
    commit: str | None = None,
    pr: str | None = None,
    today: str | None = None,
) -> QueueRegistry:
    today = today or date.today().isoformat()
    found = False
    new_items: list[dict[str, Any]] = []
    for it in registry.items:
        data = it.model_dump(mode="json")
        if it.id == item_id:
            found = True
            data["status"] = status
            hist = list(data.get("history") or [])
            entry: dict[str, Any] = {"date": today, "status": status, "note": note}
            if commit:
                entry["commit"] = commit
            if pr:
                entry["pr"] = pr
            hist.append(entry)
            data["history"] = hist
        new_items.append(data)
    if not found:
        raise KeyError(f"no queue item with id={item_id}")
    return QueueRegistry.model_validate(
        {
            "version": registry.version,
            "updated": today,
            "recommended_order": list(registry.recommended_order),
            "items": new_items,
        }
    )


def _cmd_next_id(args: argparse.Namespace) -> int:
    reg = load_queue_yaml(args.path)
    print(next_id(reg))
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    reg = load_queue_yaml(args.path)
    arxiv = [a.strip() for a in (args.arxiv or []) if a.strip()]
    try:
        updated = add_item(
            reg,
            title=args.title,
            area=args.area,
            risk=args.risk,
            automation=args.automation,
            added=args.added,
            note=args.note,
            arxiv_refs=arxiv,
            status=args.status,
            item_id=args.id,
            rank=args.rank,
            due=args.due,
        )
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    save_queue(args.path, updated)
    new = updated.items[-1]
    print(f"OK: added id={new.id} rank={new.rank} status={new.status}")
    return 0


def _cmd_set_status(args: argparse.Namespace) -> int:
    reg = load_queue_yaml(args.path)
    try:
        updated = set_status(
            reg,
            item_id=args.id,
            status=args.status,
            note=args.note,
            commit=args.commit,
            pr=args.pr,
        )
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    save_queue(args.path, updated)
    print(f"OK: id={args.id} → {args.status}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mutate research/queue.yaml")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("../research/queue.yaml"),
        help="Path to queue.yaml",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_next = sub.add_parser("next-id", help="Print next free item id")
    p_next.set_defaults(func=_cmd_next_id)

    p_add = sub.add_parser("add", help="Append a new queue item")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--area", required=True, choices=["2c", "3b", "3c", "F4", "ops"])
    p_add.add_argument(
        "--risk",
        required=True,
        choices=["live_prompt", "live_infra", "offline_analysis", "observability", "docs"],
    )
    p_add.add_argument("--automation", default="manual", choices=["manual", "auto_pr"])
    p_add.add_argument("--added", required=True, help="ISO week, e.g. 2026-W48")
    p_add.add_argument("--note", required=True)
    p_add.add_argument("--arxiv", action="append", default=[], help="Repeatable arXiv id")
    p_add.add_argument("--status", default="queued", choices=["queued", "in_progress", "partial", "done", "parked", "rejected"])
    p_add.add_argument("--id", type=int, default=None)
    p_add.add_argument("--rank", type=int, default=None)
    p_add.add_argument("--due", default=None)
    p_add.set_defaults(func=_cmd_add)

    p_set = sub.add_parser("set-status", help="Append history + update status")
    p_set.add_argument("--id", type=int, required=True)
    p_set.add_argument(
        "--status",
        required=True,
        choices=["queued", "in_progress", "partial", "done", "parked", "rejected"],
    )
    p_set.add_argument("--note", required=True)
    p_set.add_argument("--commit", default=None)
    p_set.add_argument("--pr", default=None)
    p_set.set_defaults(func=_cmd_set_status)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
