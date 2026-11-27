"""Sidekontrakt: offentlige sider 200; Forskning krever admin-sesjon."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app import content
from app.auth import SESSION_COOKIE, load_admin_settings
from app.main import app as real_app
from app.sources import Sources

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_YAML = (REPO_ROOT / "research" / "queue.yaml").read_text(encoding="utf-8")


def _failing_transport(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503, text="unavailable")


def _login(client: TestClient) -> None:
    r = client.post(
        "/admin",
        data={"username": "ADMIN", "password": "FUTURE", "next": "/forskning"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert SESSION_COOKIE in r.cookies or SESSION_COOKIE in client.cookies


def test_healthz() -> None:
    with TestClient(real_app) as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["ok"] is True


def test_home_and_agent_contain_key_copy(admin_env: None) -> None:
    with TestClient(real_app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert "Kan en AI forutsi" in home.text
        assert "FastAPI" in home.text
        assert "Railway" in home.text
        assert "Presentert av" not in home.text
        assert "Siste commit" not in home.text
        assert "ingen hemmeligheter" not in home.text
        assert "Kevin Dennis Mazali" not in home.text

        agent = client.get("/agent")
        assert agent.status_code == 200
        assert "Fra webhook til prediksjon" in agent.text
        assert "20 s" in agent.text
        assert "Presentert av" not in agent.text
        assert "Siste commit" not in agent.text
        assert "ingen hemmeligheter" not in agent.text


def test_forskning_requires_login(admin_env: None) -> None:
    with TestClient(real_app) as client:
        r = client.get("/forskning", follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"].startswith("/admin")


def test_admin_login_success_then_forskning(admin_env: None) -> None:
    with TestClient(real_app) as client:
        _login(client)
        r = client.get("/forskning")
        assert r.status_code == 200
        assert "Hva agenten lærer" in r.text or "Forskning" in r.text
        assert "Presentert av" not in r.text
        assert "Siste commit" not in r.text
        assert "ingen hemmeligheter" not in r.text


def test_admin_login_wrong_password(admin_env: None) -> None:
    with TestClient(real_app) as client:
        r = client.post(
            "/admin",
            data={"username": "ADMIN", "password": "WRONG", "next": "/forskning"},
        )
        assert r.status_code == 401
        assert "Feil brukernavn eller passord" in r.text


def test_admin_login_disabled_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("SESSION_SECRET", raising=False)
    assert load_admin_settings() is None
    with TestClient(real_app) as client:
        page = client.get("/admin")
        assert page.status_code == 200
        assert "ikke konfigurert" in page.text

        r = client.post(
            "/admin",
            data={"username": "ADMIN", "password": "FUTURE", "next": "/forskning"},
        )
        assert r.status_code == 503
        assert "ikke konfigurert" in r.text

        blocked = client.get("/forskning", follow_redirects=False)
        assert blocked.status_code == 303


def test_pages_survive_unavailable_sources(admin_env: None) -> None:
    transport = httpx.MockTransport(_failing_transport)
    http_client = httpx.Client(transport=transport)
    sources = Sources(client=http_client, ttl_seconds=600)

    with TestClient(real_app) as client:
        client.app.state.sources = sources
        _login(client)

        home = client.get("/")
        assert home.status_code == 200
        assert "Kan en AI forutsi" in home.text

        agent = client.get("/agent")
        assert agent.status_code == 200

        forskning = client.get("/forskning")
        assert forskning.status_code == 200
        assert "Kunne ikke hente" in forskning.text
        assert content.FORSKNING_BLOB_URL in forskning.text


def test_forskning_renders_parsed_weeks_and_queue(admin_env: None) -> None:
    body = (
        "## Ukentlige funn\n\n### Uke 2026-W50 (10. des 2026)\n\n"
        "Collect OK: 3 nye arXiv-papers. 1 beholdt, 2 forkastet.\n\n"
        "**A Great Paper**\nSmith, 2026-12-01 · https://arxiv.org/abs/2611.22177\n"
        "Useful finding.\n\n"
        "(Forkastet: 2612.00099 «Nope» — reason.)\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "queue.yaml" in url:
            return httpx.Response(200, text=QUEUE_YAML)
        if "raw.githubusercontent" in url:
            return httpx.Response(200, text=body)
        return httpx.Response(404)

    sources = Sources(client=httpx.Client(transport=httpx.MockTransport(handler)), ttl_seconds=600)
    with TestClient(real_app) as client:
        client.app.state.sources = sources
        _login(client)
        r = client.get("/forskning")
        assert r.status_code == 200
        assert "A Great Paper" in r.text
        assert "2611.22177" in r.text
        assert "Uke 2026-W50" in r.text
        assert "Implementeringskø" in r.text
        assert "Funnet-tidslinje" in r.text
        assert "Forkastet" in r.text
        assert "Nope" in r.text
        assert "#10" in r.text or "Identitets-ablation" in r.text


def test_forskning_filters_and_queue_unavailable(admin_env: None) -> None:
    body = (
        "## Ukentlige funn\n\n### Uke 2026-W50 (10. des 2026)\n\n"
        "1 beholdt, 0 forkastet.\n\n"
        "**Safe Title**\nSmith, 2026-12-01 · https://arxiv.org/abs/2611.22177\n"
        "Body with <script>alert(1)</script>.\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "queue.yaml" in url:
            return httpx.Response(503, text="no queue")
        if "raw.githubusercontent" in url:
            return httpx.Response(200, text=body)
        return httpx.Response(404)

    sources = Sources(client=httpx.Client(transport=httpx.MockTransport(handler)), ttl_seconds=600)
    with TestClient(real_app) as client:
        client.app.state.sources = sources
        _login(client)
        r = client.get("/forskning?uke=2026-W50&status=bogus")
        assert r.status_code == 200
        assert "Ukjent status-filter" in r.text
        assert "Kunne ikke hente kø" in r.text
        assert "<script>alert(1)</script>" not in r.text
        assert "Safe" in r.text


def test_logout_clears_session(admin_env: None) -> None:
    with TestClient(real_app) as client:
        _login(client)
        assert client.get("/forskning").status_code == 200
        out = client.post("/admin/logout", follow_redirects=False)
        assert out.status_code == 303
        blocked = client.get("/forskning", follow_redirects=False)
        assert blocked.status_code == 303
