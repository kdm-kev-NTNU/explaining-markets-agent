"""View-modell: join, gruppering, filtre."""
from __future__ import annotations

from app.research_parser import parse_forskning
from app.research_registry import parse_queue_yaml
from app.research_view import build_research_view, parse_filters

MD = """## Ukentlige funn

### Uke 2026-W47 (20. nov 2026)

Collect OK: 2 nye. 2 beholdt, 1 forkastet.

**Paper Alpha**
A, 2026-11-17 · https://arxiv.org/abs/2611.22177
Body.

**Paper Beta**
B, 2026-11-14 · https://arxiv.org/abs/2611.19530
Body.

(Forkastet: 2611.25951 «No» — reason.)

### Uke 2026-W46 (13. nov 2026)

1 beholdt, 0 forkastet.

**Paper Gamma**
C, 2026-11-11 · https://arxiv.org/abs/2611.15747
Body.
"""

QUEUE = """
version: 1
items:
  - id: 10
    title: Identitet
    area: 3b
    status: queued
    rank: 1
    risk: offline_analysis
    automation: auto_pr
    added: 2026-W45
    sources: [{kind: arxiv, ref: "2611.22177"}]
    history: [{date: 2026-11-06, status: queued, note: start}]
  - id: 15
    title: Støy
    area: F4
    status: queued
    rank: 2
    risk: observability
    automation: auto_pr
    added: 2026-W47
    sources: [{kind: arxiv, ref: "2611.19530"}]
    history: [{date: 2026-11-20, status: queued, note: start}]
  - id: 13
    title: Surprise
    area: 3c
    status: partial
    rank: 3
    risk: live_prompt
    automation: manual
    added: 2026-W46
    sources: [{kind: arxiv, ref: "2611.15747"}]
    history:
      - {date: 2026-11-13, status: queued, note: start}
      - {date: 2026-11-20, status: partial, note: half}
"""


def test_join_papers_to_queue() -> None:
    digest = parse_forskning(MD)
    queue = parse_queue_yaml(QUEUE)
    view = build_research_view(digest, queue)
    assert view.stats.kept_papers == 3
    assert view.stats.rejected_papers == 1
    assert view.stats.queue_queued == 2
    assert view.stats.next_auto_pr_id == 10

    w47 = view.weeks[0]
    assert w47.week_id == "2026-W47"
    alpha = w47.papers[0]
    assert alpha.queue_links[0].id == 10
    assert alpha.queue_links[0].status_label == "Kø"
    assert w47.rejected[0].arxiv_id == "2611.25951"

    assert len(view.board["queued"]) == 2
    assert len(view.board["partial"]) == 1
    assert view.board["partial"][0].source_papers[0].arxiv_id == "2611.15747"


def test_filter_uke_and_invalid_status() -> None:
    digest = parse_forskning(MD)
    queue = parse_queue_yaml(QUEUE)
    filters = parse_filters(uke="2026-W47", status="bogus")
    assert filters.uke == "2026-W47"
    assert filters.status is None
    assert filters.warnings
    view = build_research_view(digest, queue, filters)
    assert len(view.weeks) == 1
    assert view.weeks[0].week_id == "2026-W47"


def test_filter_linked_only() -> None:
    digest = parse_forskning(MD)
    queue = parse_queue_yaml(QUEUE)
    filters = parse_filters(linked="1", area="3c")
    view = build_research_view(digest, queue, filters)
    # Only gamma links to kø 13 (3c), and board filtered to area 3c
    assert all(c.item.area == "3c" for c in view.all_queue)
    paper_ids = [p.paper.arxiv_id for w in view.weeks for p in w.papers]
    assert paper_ids == ["2611.15747"]


def test_queue_none_still_renders_weeks() -> None:
    digest = parse_forskning(MD)
    view = build_research_view(digest, None, queue_warning="missing")
    assert view.queue_available is False
    assert view.queue_warning == "missing"
    assert len(view.weeks) == 2
    assert view.weeks[0].papers[0].queue_links == ()
