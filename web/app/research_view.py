"""Ren view-modell: join papers ↔ kø, gruppering og filtre.

Ingen I/O. Deterministisk og testbar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from .research_parser import Paper, RejectedPaper, ResearchDigest
from .research_registry import Area, QueueItem, QueueRegistry, Status

BoardColumn = Literal["queued", "in_progress", "partial", "done", "parked"]
BOARD_COLUMNS: tuple[BoardColumn, ...] = (
    "queued",
    "in_progress",
    "partial",
    "done",
    "parked",
)

STATUS_LABELS: dict[str, str] = {
    "queued": "Kø",
    "in_progress": "Pågår",
    "partial": "Delvis",
    "done": "Implementert",
    "parked": "Parkert",
    "rejected": "Forkastet",
}

AREA_LABELS: dict[str, str] = {
    "2c": "2c parser",
    "3b": "3b arkiv",
    "3c": "3c prediksjon",
    "F4": "F4 / eligibility",
    "ops": "Ops",
}


@dataclass(frozen=True)
class ResearchFilters:
    """Query-parametre for /forskning. Ugyldige verdier → None + warning."""

    uke: str | None = None
    status: Status | None = None
    area: Area | None = None
    linked_only: bool = False
    warnings: tuple[str, ...] = ()


_UKE_ID_RE = re.compile(r"2026-W\d{2}")
_VALID_STATUS = frozenset(STATUS_LABELS)
_VALID_AREA = frozenset(AREA_LABELS)


def parse_filters(
    *,
    uke: str | None = None,
    status: str | None = None,
    area: str | None = None,
    linked: str | None = None,
) -> ResearchFilters:
    warnings: list[str] = []
    uke_v: str | None = None
    if uke:
        m = _UKE_ID_RE.search(uke)
        if m:
            uke_v = m.group(0)
        else:
            warnings.append(f"Ukjent uke-filter {uke!r} — ignorert")

    status_v: Status | None = None
    if status:
        if status in _VALID_STATUS:
            status_v = status  # type: ignore[assignment]
        else:
            warnings.append(f"Ukjent status-filter {status!r} — ignorert")

    area_v: Area | None = None
    if area:
        if area in _VALID_AREA:
            area_v = area  # type: ignore[assignment]
        else:
            warnings.append(f"Ukjent område-filter {area!r} — ignorert")

    linked_only = linked in ("1", "true", "yes", "on")
    return ResearchFilters(
        uke=uke_v,
        status=status_v,
        area=area_v,
        linked_only=linked_only,
        warnings=tuple(warnings),
    )


@dataclass(frozen=True)
class LinkedQueueRef:
    id: int
    title: str
    status: Status
    status_label: str


@dataclass(frozen=True)
class PaperCard:
    paper: Paper
    week_heading: str
    week_id: str
    queue_links: tuple[LinkedQueueRef, ...] = ()


@dataclass(frozen=True)
class WeekCard:
    week_heading: str
    week_id: str
    summary: str
    new_count: int | None
    kept_count: int | None
    rejected_count: int | None
    papers: tuple[PaperCard, ...]
    rejected: tuple[RejectedPaper, ...]


@dataclass(frozen=True)
class QueueCard:
    item: QueueItem
    status_label: str
    area_label: str
    source_papers: tuple[Paper, ...] = ()
    auto_eligible: bool = False


@dataclass(frozen=True)
class ResearchStats:
    kept_papers: int
    rejected_papers: int
    weeks: int
    queue_total: int
    queue_queued: int
    queue_partial: int
    queue_done: int
    queue_in_progress: int
    next_auto_pr_id: int | None


@dataclass(frozen=True)
class ResearchView:
    stats: ResearchStats
    weeks: tuple[WeekCard, ...]
    board: dict[BoardColumn, tuple[QueueCard, ...]]
    next_in_queue: tuple[QueueCard, ...]
    week_options: tuple[str, ...]
    filters: ResearchFilters
    queue_available: bool
    queue_warning: str | None = None
    all_queue: tuple[QueueCard, ...] = field(default_factory=tuple)


def _week_id(heading: str) -> str:
    m = _UKE_ID_RE.search(heading)
    return m.group(0) if m else heading


def _queue_card(item: QueueItem, papers_by_arxiv: dict[str, Paper]) -> QueueCard:
    linked = tuple(
        papers_by_arxiv[ref] for ref in item.arxiv_refs if ref in papers_by_arxiv
    )
    return QueueCard(
        item=item,
        status_label=STATUS_LABELS.get(item.status, item.status),
        area_label=AREA_LABELS.get(item.area, item.area),
        source_papers=linked,
        auto_eligible=item.automation == "auto_pr",
    )


def _item_matches(item: QueueItem, filters: ResearchFilters) -> bool:
    if filters.status is not None and item.status != filters.status:
        return False
    if filters.area is not None and item.area != filters.area:
        return False
    return True


def _links_for(
    paper: Paper,
    arxiv_to_queue: dict[str, list[QueueItem]],
    filters: ResearchFilters,
) -> tuple[LinkedQueueRef, ...]:
    if not paper.arxiv_id:
        return ()
    links: list[LinkedQueueRef] = []
    for qi in arxiv_to_queue.get(paper.arxiv_id, []):
        if not _item_matches(qi, filters):
            continue
        links.append(
            LinkedQueueRef(
                id=qi.id,
                title=qi.title,
                status=qi.status,
                status_label=STATUS_LABELS.get(qi.status, qi.status),
            )
        )
    return tuple(links)


def build_research_view(
    digest: ResearchDigest,
    queue: QueueRegistry | None,
    filters: ResearchFilters | None = None,
    *,
    queue_warning: str | None = None,
) -> ResearchView:
    filters = filters or ResearchFilters()
    papers_by_arxiv: dict[str, Paper] = {}
    for week in digest.weeks:
        for paper in week.papers:
            if paper.arxiv_id:
                papers_by_arxiv[paper.arxiv_id] = paper

    arxiv_to_queue: dict[str, list[QueueItem]] = {}
    all_queue_cards: list[QueueCard] = []
    board_lists: dict[BoardColumn, list[QueueCard]] = {c: [] for c in BOARD_COLUMNS}
    next_in_queue: list[QueueCard] = []
    queue_available = queue is not None

    if queue is not None:
        arxiv_to_queue = {k: list(v) for k, v in queue.by_arxiv().items()}
        for item in sorted(queue.items, key=lambda it: it.rank):
            if not _item_matches(item, filters):
                continue
            card = _queue_card(item, papers_by_arxiv)
            all_queue_cards.append(card)
            if item.status in BOARD_COLUMNS:
                board_lists[item.status].append(card)  # type: ignore[index]
            if item.status == "queued":
                next_in_queue.append(card)

    week_options = tuple(_week_id(w.heading) for w in digest.weeks)
    week_cards: list[WeekCard] = []
    for week in digest.weeks:
        wid = _week_id(week.heading)
        if filters.uke and wid != filters.uke:
            continue

        paper_cards: list[PaperCard] = []
        for paper in week.papers:
            links = _links_for(paper, arxiv_to_queue, filters)
            if filters.linked_only and not links:
                continue
            # Status/area-filter uten linked_only: behold papers, men bare matching chips
            paper_cards.append(
                PaperCard(
                    paper=paper,
                    week_heading=week.heading,
                    week_id=wid,
                    queue_links=links,
                )
            )

        rejected = () if filters.linked_only else week.rejected
        if filters.linked_only and not paper_cards:
            continue

        week_cards.append(
            WeekCard(
                week_heading=week.heading,
                week_id=wid,
                summary=week.summary,
                new_count=week.new_count,
                kept_count=week.kept_count,
                rejected_count=week.rejected_count,
                papers=tuple(paper_cards),
                rejected=rejected,
            )
        )

    kept = sum(len(w.papers) for w in digest.weeks)
    rejected_n = sum(len(w.rejected) for w in digest.weeks)
    next_auto = queue.next_auto_pr() if queue else None
    stats = ResearchStats(
        kept_papers=kept,
        rejected_papers=rejected_n,
        weeks=len(digest.weeks),
        queue_total=len(queue.items) if queue else 0,
        queue_queued=sum(1 for i in queue.items if i.status == "queued") if queue else 0,
        queue_partial=sum(1 for i in queue.items if i.status == "partial") if queue else 0,
        queue_done=sum(1 for i in queue.items if i.status == "done") if queue else 0,
        queue_in_progress=(
            sum(1 for i in queue.items if i.status == "in_progress") if queue else 0
        ),
        next_auto_pr_id=next_auto.id if next_auto else None,
    )

    return ResearchView(
        stats=stats,
        weeks=tuple(week_cards),
        board={c: tuple(board_lists[c]) for c in BOARD_COLUMNS},
        next_in_queue=tuple(next_in_queue[:5]),
        week_options=week_options,
        filters=filters,
        queue_available=queue_available,
        queue_warning=queue_warning,
        all_queue=tuple(all_queue_cards),
    )
