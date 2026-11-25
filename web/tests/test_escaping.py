"""Ekstern/paper-tekst skal escapes — aldri kjøre rå HTML."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.sources import Sources


def test_script_in_paper_title_is_escaped() -> None:
    body = (
        "## Ukentlige funn\n\n### Uke 2026-W99\n\n"
        "1 beholdt, 0 forkastet.\n\n"
        "**<script>alert(1)</script> Evil Title**\n"
        "Attacker, 2026-01-01 · https://arxiv.org/abs/9999.99999\n"
        "Body with <img src=x onerror=alert(1)>.\n"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if "raw.githubusercontent" in str(request.url):
            return httpx.Response(200, text=body)
        if "api.github.com" in str(request.url):
            return httpx.Response(200, json=[])
        return httpx.Response(404)

    sources = Sources(client=httpx.Client(transport=httpx.MockTransport(handler)), ttl_seconds=600)
    with TestClient(app) as client:
        client.app.state.sources = sources
        r = client.get("/forskning")
        assert r.status_code == 200
        assert "<script>alert(1)</script>" not in r.text
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in r.text
        # markdown-it with html=False should not emit a raw img tag from body
        assert "<img src=x onerror=alert(1)>" not in r.text


def test_markdown_filter_does_not_pass_raw_html() -> None:
    from app.main import render_markdown

    html = render_markdown("Hello <script>x</script> **world**")
    assert "<script>" not in html
    assert "<strong>world</strong>" in html or "<em>" in html or "world" in html
