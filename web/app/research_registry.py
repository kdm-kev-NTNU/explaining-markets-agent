"""Validert kontrakt for research/queue.yaml.

Invarianter (håndheves her, ikke i kommentarer):
- status/risk/area/automation er lukkede Literal-sett
- risk in {live_prompt, live_infra} ⇒ automation == manual
- id unik; rank unik blant ikke-ferdige punkter
- history ikke-tom, sortert stigende på date; siste.status == item.status
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

Area = Literal["2c", "3b", "3c", "F4", "ops"]
Status = Literal["queued", "in_progress", "partial", "done", "parked", "rejected"]
Risk = Literal["live_prompt", "live_infra", "offline_analysis", "observability", "docs"]
Automation = Literal["manual", "auto_pr"]
SourceKind = Literal["arxiv", "platform", "other"]

FINISHED_STATUSES: frozenset[Status] = frozenset({"done", "rejected"})
LIVE_RISKS: frozenset[Risk] = frozenset({"live_prompt", "live_infra"})


class HistoryEntry(BaseModel):
    model_config = {"extra": "forbid"}

    date: str
    status: Status
    note: str = ""
    commit: str | None = None
    pr: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def _iso_date(cls, v: Any) -> str:
        if isinstance(v, datetime):
            v = v.date().isoformat()
        elif isinstance(v, date):
            v = v.isoformat()
        elif not isinstance(v, str):
            raise ValueError(f"date must be YYYY-MM-DD, got {v!r}")
        if len(v) != 10 or v[4] != "-" or v[7] != "-":
            raise ValueError(f"date must be YYYY-MM-DD, got {v!r}")
        return v


class SourceRef(BaseModel):
    model_config = {"extra": "forbid"}

    kind: SourceKind
    ref: str

    @field_validator("ref")
    @classmethod
    def _nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("source.ref must be non-empty")
        return v.strip()


class QueueItem(BaseModel):
    model_config = {"extra": "forbid"}

    id: int = Field(ge=1)
    title: str
    area: Area
    status: Status
    rank: int = Field(ge=1)
    risk: Risk
    automation: Automation
    added: str
    sources: list[SourceRef] = Field(default_factory=list)
    history: list[HistoryEntry]
    due: str | None = None

    @field_validator("due", mode="before")
    @classmethod
    def _coerce_due(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.date().isoformat()
        if isinstance(v, date):
            return v.isoformat()
        return str(v)

    @model_validator(mode="after")
    def _invariants(self) -> QueueItem:
        if self.risk in LIVE_RISKS and self.automation != "manual":
            raise ValueError(
                f"item {self.id}: risk={self.risk!r} requires automation='manual', "
                f"got {self.automation!r}"
            )
        if not self.history:
            raise ValueError(f"item {self.id}: history must be non-empty")
        dates = [h.date for h in self.history]
        if dates != sorted(dates):
            raise ValueError(f"item {self.id}: history must be sorted ascending by date")
        if self.history[-1].status != self.status:
            raise ValueError(
                f"item {self.id}: last history status {self.history[-1].status!r} "
                f"!= item.status {self.status!r}"
            )
        if not self.title.strip():
            raise ValueError(f"item {self.id}: title must be non-empty")
        return self

    @property
    def is_finished(self) -> bool:
        return self.status in FINISHED_STATUSES

    @property
    def arxiv_refs(self) -> tuple[str, ...]:
        return tuple(s.ref for s in self.sources if s.kind == "arxiv")


class QueueRegistry(BaseModel):
    model_config = {"extra": "forbid"}

    version: Literal[1]
    updated: str | None = None
    recommended_order: list[int] = Field(default_factory=list)
    items: list[QueueItem]

    @field_validator("updated", mode="before")
    @classmethod
    def _coerce_updated(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.date().isoformat()
        if isinstance(v, date):
            return v.isoformat()
        return str(v)

    @model_validator(mode="after")
    def _collection_invariants(self) -> QueueRegistry:
        ids = [it.id for it in self.items]
        if len(ids) != len(set(ids)):
            dupes = sorted({i for i in ids if ids.count(i) > 1})
            raise ValueError(f"duplicate item ids: {dupes}")

        active_ranks = [it.rank for it in self.items if not it.is_finished]
        if len(active_ranks) != len(set(active_ranks)):
            dupes = sorted({r for r in active_ranks if active_ranks.count(r) > 1})
            raise ValueError(f"duplicate ranks among unfinished items: {dupes}")

        known = set(ids)
        for qid in self.recommended_order:
            if qid not in known:
                raise ValueError(f"recommended_order references unknown id {qid}")
        return self

    def by_id(self) -> dict[int, QueueItem]:
        return {it.id: it for it in self.items}

    def by_arxiv(self) -> dict[str, list[QueueItem]]:
        out: dict[str, list[QueueItem]] = {}
        for it in self.items:
            for ref in it.arxiv_refs:
                out.setdefault(ref, []).append(it)
        return out

    def next_auto_pr(self) -> QueueItem | None:
        """Laveste rank blant queued + automation=auto_pr."""
        candidates = [
            it for it in self.items if it.status == "queued" and it.automation == "auto_pr"
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda it: it.rank)


def load_queue_yaml(path: Path | str) -> QueueRegistry:
    text = Path(path).read_text(encoding="utf-8")
    return parse_queue_yaml(text)


def parse_queue_yaml(text: str) -> QueueRegistry:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("queue.yaml root must be a mapping")
    return QueueRegistry.model_validate(data)


def arxiv_ids_from_forskning(md: str) -> set[str]:
    """Alle arXiv-ID-er som er sitert i beholdte paper-blokker (ikke forkastet-listen)."""
    from .research_parser import parse_forskning

    digest = parse_forskning(md)
    ids: set[str] = set()
    for week in digest.weeks:
        for paper in week.papers:
            if paper.arxiv_id:
                ids.add(paper.arxiv_id)
    return ids


def check_cross_file_links(registry: QueueRegistry, forskning_md: str) -> list[str]:
    """Returner liste over feilmeldinger (tom = OK)."""
    known = arxiv_ids_from_forskning(forskning_md)
    errors: list[str] = []
    for it in registry.items:
        for ref in it.arxiv_refs:
            if ref not in known:
                errors.append(
                    f"item {it.id}: arxiv ref {ref!r} not found among kept papers in FORSKNING.md"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate research/queue.yaml")
    parser.add_argument(
        "--check",
        type=Path,
        required=True,
        help="Path to queue.yaml",
    )
    parser.add_argument(
        "--forskning",
        type=Path,
        default=None,
        help="Optional FORSKNING.md for cross-file arxiv link check",
    )
    args = parser.parse_args(argv)

    try:
        registry = load_queue_yaml(args.check)
    except (OSError, yaml.YAMLError, ValidationError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    forskning_path = args.forskning
    if forskning_path is None:
        # Default: sibling of queue.yaml → ../FORSKNING.md or research/FORSKNING.md
        sibling = args.check.resolve().parent / "FORSKNING.md"
        if sibling.exists():
            forskning_path = sibling
    if forskning_path is not None and forskning_path.exists():
        errors.extend(check_cross_file_links(registry, forskning_path.read_text(encoding="utf-8")))

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(registry.items)} items, "
        f"next auto_pr={getattr(registry.next_auto_pr(), 'id', None)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
