"""Invarianter for queue.yaml-kontrakten."""
from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.research_parser import parse_forskning
from app.research_registry import (
    QueueRegistry,
    check_cross_file_links,
    load_queue_yaml,
    parse_queue_yaml,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = REPO_ROOT / "research" / "queue.yaml"
FORSKNING_PATH = REPO_ROOT / "research" / "FORSKNING.md"

MINIMAL = """
version: 1
items:
  - id: 1
    title: Test item
    area: 3c
    status: queued
    rank: 1
    risk: observability
    automation: auto_pr
    added: 2026-W47
    sources: []
    history:
      - {date: 2026-11-20, status: queued, note: start}
"""


def test_parse_minimal_ok() -> None:
    reg = parse_queue_yaml(MINIMAL)
    assert reg.version == 1
    assert reg.items[0].id == 1
    assert reg.next_auto_pr() is not None
    assert reg.next_auto_pr().id == 1


def test_live_risk_requires_manual() -> None:
    bad = MINIMAL.replace("observability", "live_prompt")
    with pytest.raises(ValidationError, match="requires automation"):
        parse_queue_yaml(bad)


def test_history_must_match_status() -> None:
    bad = MINIMAL.replace("status: queued\n    rank", "status: done\n    rank", 1)
    # item.status=done but last history still queued
    with pytest.raises(ValidationError, match="last history status"):
        parse_queue_yaml(bad)


def test_duplicate_ids_rejected() -> None:
    dup = """
version: 1
items:
  - id: 1
    title: A
    area: 3c
    status: queued
    rank: 1
    risk: docs
    automation: manual
    added: 2026-W01
    history: [{date: 2026-01-01, status: queued, note: x}]
  - id: 1
    title: B
    area: 3c
    status: queued
    rank: 2
    risk: docs
    automation: manual
    added: 2026-W01
    history: [{date: 2026-01-01, status: queued, note: y}]
"""
    with pytest.raises(ValidationError, match="duplicate item ids"):
        parse_queue_yaml(dup)


def test_duplicate_active_ranks_rejected() -> None:
    dup = """
version: 1
items:
  - id: 1
    title: A
    area: 3c
    status: queued
    rank: 1
    risk: docs
    automation: manual
    added: 2026-W01
    history: [{date: 2026-01-01, status: queued, note: x}]
  - id: 2
    title: B
    area: 3c
    status: partial
    rank: 1
    risk: docs
    automation: manual
    added: 2026-W01
    history: [{date: 2026-01-01, status: partial, note: y}]
"""
    with pytest.raises(ValidationError, match="duplicate ranks"):
        parse_queue_yaml(dup)


def test_real_queue_yaml_validates() -> None:
    if not QUEUE_PATH.exists():
        pytest.skip("queue.yaml mangler")
    reg = load_queue_yaml(QUEUE_PATH)
    assert len(reg.items) == 15
    nxt = reg.next_auto_pr()
    if nxt is not None:
        assert nxt.status == "queued"
        assert nxt.automation == "auto_pr"
    # live-risiko skal aldri være auto_pr
    for it in reg.items:
        if it.risk in ("live_prompt", "live_infra"):
            assert it.automation == "manual"


def test_cross_file_arxiv_links() -> None:
    if not QUEUE_PATH.exists() or not FORSKNING_PATH.exists():
        pytest.skip("research-filer mangler")
    reg = load_queue_yaml(QUEUE_PATH)
    md = FORSKNING_PATH.read_text(encoding="utf-8")
    errors = check_cross_file_links(reg, md)
    assert errors == [], errors
    digest = parse_forskning(md)
    assert digest.parse_ok
