"""Leaderboard: periodevalg, egen rad og visning på forsiden."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from app.leaderboard import featured_period, find_standing
from app.main import app as real_app
from app.sources import Available, Sources, Unavailable

INDEX = {
    "current_period": "2026Q4",
    "periods": [
        {"period": "2026Q3", "status": "ranked", "frozen": True},
        {"period": "2026Q4", "status": "ranked", "frozen": False},
        {"period": "2026Q3-CONTEST", "status": "ranked", "frozen": True},
        {"period": "2026Q4-CONTEST", "status": "ranked", "frozen": False},
    ],
}


def _row(name: str, rank: int, *, baseline: bool = False, score: float = 0.1) -> dict:
    return {
        "public_name": name,
        "rank": rank,
        "rank_common": rank,
        "rank_own": rank + 1,
        "baseline": baseline,
        "submission_id": f"s_{rank}",
        "n_obs": 2669,
        "metrics": {"delta_r_squared_imputed": score, "r_squared_imputed": score + 0.07},
    }


STANDINGS = {
    "period": "2026Q4-CONTEST",
    "frozen": False,
    "generated_at": "2026-11-26T23:54:13+00:00",
    "ranking_metric": "delta_r_squared_imputed",
    "rows": [
        _row("leader", 1, score=0.2),
        _row("GPT baseline", 2, baseline=True),
        _row("Tokenmaxxer", 3, score=0.046),
        _row("GPT baseline 2", 4, baseline=True),
        _row("someone", 5),
    ],
}


def test_featured_period_prefers_current_contest() -> None:
    assert featured_period(INDEX) == "2026Q4-CONTEST"


def test_featured_period_falls_back_to_current() -> None:
    assert featured_period({"current_period": "2027Q1", "periods": []}) == "2027Q1"


def test_find_standing_counts_baselines_separately() -> None:
    s = find_standing(STANDINGS, "tokenmaxxer")
    assert s is not None
    assert s.rank == 3
    assert s.total == 5
    assert s.participants == 3
    assert s.participant_rank == 2  # én baseline foran
    assert s.score == 0.046
    assert s.r_squared == 0.046 + 0.07
    assert s.period == "2026Q4-CONTEST"


def test_find_standing_missing_name() -> None:
    assert find_standing(STANDINGS, "nobody") is None


def _handler(request: httpx.Request) -> httpx.Response:
    assert "authorization" not in request.headers
    if request.url.path.endswith("/index.json"):
        return httpx.Response(200, json=INDEX)
    if request.url.path.endswith("/2026Q4-CONTEST.json"):
        return httpx.Response(200, json=STANDINGS)
    return httpx.Response(404)


def test_fetch_standing_and_home_page_shows_rank() -> None:
    sources = Sources(client=httpx.Client(transport=httpx.MockTransport(_handler)))
    result = sources.fetch_standing()
    assert isinstance(result, Available)
    assert result.value.rank == 3

    with TestClient(real_app) as client:
        client.app.state.sources = sources
        home = client.get("/")
        assert home.status_code == 200
        assert "#3 av 5" in home.text
        assert "Min plassering (Tokenmaxxer)" in home.text


def test_fetch_standing_failure_hides_rank() -> None:
    failing = httpx.MockTransport(lambda r: httpx.Response(403, text="denied"))
    sources = Sources(client=httpx.Client(transport=failing))
    assert isinstance(sources.fetch_standing(), Unavailable)

    with TestClient(real_app) as client:
        client.app.state.sources = sources
        home = client.get("/")
        assert home.status_code == 200
        assert "Min plassering" not in home.text
