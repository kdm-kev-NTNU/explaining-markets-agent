"""Sidekontrakt: alle ruter gir 200, også når GitHub er nede."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from app import content
from app.main import app as real_app
from app.sources import Sources


def _failing_transport(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503, text="unavailable")


def test_healthz() -> None:
    with TestClient(real_app) as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["ok"] is True


def test_home_and_agent_contain_key_copy() -> None:
    with TestClient(real_app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert "Kan en AI forutsi" in home.text
        assert "FastAPI" in home.text
        assert "Railway" in home.text

        agent = client.get("/agent")
        assert agent.status_code == 200
        assert "Fra webhook til prediksjon" in agent.text
        assert "20 s" in agent.text


def test_pages_survive_unavailable_sources() -> None:
    transport = httpx.MockTransport(_failing_transport)
    http_client = httpx.Client(transport=transport)
    sources = Sources(client=http_client, ttl_seconds=600)

    with TestClient(real_app) as client:
        client.app.state.sources = sources

        home = client.get("/")
        assert home.status_code == 200
        assert "Kan en AI forutsi" in home.text

        agent = client.get("/agent")
        assert agent.status_code == 200

        forskning = client.get("/forskning")
        assert forskning.status_code == 200
        assert "Kunne ikke hente" in forskning.text
        assert content.FORSKNING_BLOB_URL in forskning.text


def test_forskning_renders_parsed_weeks() -> None:
    body = (
        "## Ukentlige funn\n\n### Uke 2026-W50 (10. des 2026)\n\n"
        "Collect OK: 3 nye arXiv-papers. 1 beholdt, 2 forkastet.\n\n"
        "**A Great Paper**\nSmith, 2026-12-01 · https://arxiv.org/abs/2612.00001\n"
        "Useful finding.\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if "raw.githubusercontent" in str(request.url):
            return httpx.Response(200, text=body)
        if "api.github.com" in str(request.url):
            return httpx.Response(
                200,
                json=[
                    {
                        "sha": "deadbeef",
                        "commit": {
                            "message": "test",
                            "author": {"date": "2026-11-25T00:00:00Z"},
                        },
                    }
                ],
            )
        return httpx.Response(404)

    sources = Sources(client=httpx.Client(transport=httpx.MockTransport(handler)), ttl_seconds=600)
    with TestClient(real_app) as client:
        client.app.state.sources = sources
        r = client.get("/forskning")
        assert r.status_code == 200
        assert "A Great Paper" in r.text
        assert "2612.00001" in r.text
        assert "Uke 2026-W50" in r.text
