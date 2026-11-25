"""CLI/mutasjonskontrakt for queue.yaml."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.queue_mutate import add_item, next_id, save_queue, set_status
from app.research_registry import load_queue_yaml, parse_queue_yaml

MINIMAL = """
version: 1
items:
  - id: 1
    title: Existing
    area: 3c
    status: queued
    rank: 1
    risk: docs
    automation: auto_pr
    added: 2026-W47
    sources: []
    history:
      - {date: 2026-11-20, status: queued, note: start}
"""


def test_add_and_set_status_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "queue.yaml"
    path.write_text(MINIMAL, encoding="utf-8")
    reg = load_queue_yaml(path)
    assert next_id(reg) == 2

    updated = add_item(
        reg,
        title="New work",
        area="3b",
        risk="offline_analysis",
        automation="auto_pr",
        added="2026-W48",
        note="from cron",
        arxiv_refs=["2611.22177"],
        today="2026-11-27",
    )
    assert updated.items[-1].id == 2
    assert updated.items[-1].rank == 2
    save_queue(path, updated)
    reloaded = load_queue_yaml(path)
    assert len(reloaded.items) == 2

    progressed = set_status(
        reloaded,
        item_id=2,
        status="in_progress",
        note="PR opened",
        pr="https://github.com/example/pull/1",
        today="2026-11-27",
    )
    save_queue(path, progressed)
    final = load_queue_yaml(path)
    item = final.by_id()[2]
    assert item.status == "in_progress"
    assert item.history[-1].pr.endswith("/1")


def test_live_risk_forced_manual() -> None:
    reg = parse_queue_yaml(MINIMAL)
    updated = add_item(
        reg,
        title="Live change",
        area="3c",
        risk="live_prompt",
        automation="auto_pr",  # skal tvinges til manual
        added="2026-W48",
        note="must be manual",
        today="2026-11-27",
    )
    assert updated.items[-1].automation == "manual"


def test_set_status_unknown_id() -> None:
    reg = parse_queue_yaml(MINIMAL)
    with pytest.raises(KeyError):
        set_status(reg, item_id=99, status="done", note="nope", today="2026-11-27")
