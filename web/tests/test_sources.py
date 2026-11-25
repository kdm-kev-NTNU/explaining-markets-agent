"""Tester for Sources: feil → Unavailable, TTL-cache med injisert klokke."""

from __future__ import annotations

import httpx

from app.sources import Available, Sources, Unavailable


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _ok_forskning(request: httpx.Request) -> httpx.Response:
    body = (
        "## Ukentlige funn\n\n### Uke 2026-W99\n\n"
        "1 beholdt, 0 forkastet.\n\n"
        "**Safe Title**\nA, 2026-01-01 · https://arxiv.org/abs/9999.99999\n"
    )
    return httpx.Response(200, text=body)


def _ok_commits(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json=[
            {
                "sha": "abcdef1234567890",
                "commit": {
                    "message": "FEATURE: something\n\nbody",
                    "author": {"date": "2026-11-25T12:00:00Z"},
                },
            }
        ],
    )


def test_fetch_forskning_success_and_cache() -> None:
    clock = FakeClock()
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return _ok_forskning(request)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    sources = Sources(client=client, clock=clock, ttl_seconds=600)

    first = sources.fetch_forskning()
    assert isinstance(first, Available)
    text, digest = first.value
    assert digest.parse_ok
    assert "Safe Title" in text
    assert calls["n"] == 1

    clock.advance(100)
    second = sources.fetch_forskning()
    assert isinstance(second, Available)
    assert calls["n"] == 1  # cache hit

    clock.advance(501)
    third = sources.fetch_forskning()
    assert isinstance(third, Available)
    assert calls["n"] == 2  # TTL expired


def test_fetch_forskning_http_error_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    sources = Sources(client=client, ttl_seconds=600)
    result = sources.fetch_forskning()
    assert isinstance(result, Unavailable)
    assert "500" in result.reason or "HTTPStatusError" in result.reason


def test_fetch_forskning_timeout_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    sources = Sources(client=client, ttl_seconds=600)
    result = sources.fetch_forskning()
    assert isinstance(result, Unavailable)
    assert "Timeout" in result.reason


def test_latest_commits_success_and_cache() -> None:
    clock = FakeClock()
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return _ok_commits(request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    sources = Sources(client=client, clock=clock, ttl_seconds=10)

    first = sources.latest_commits()
    assert isinstance(first, Available)
    assert first.value[0].sha == "abcdef1"
    assert first.value[0].msg == "FEATURE: something"
    assert calls["n"] == 1

    clock.advance(5)
    assert isinstance(sources.latest_commits(), Available)
    assert calls["n"] == 1

    clock.advance(6)
    assert isinstance(sources.latest_commits(), Available)
    assert calls["n"] == 2


def test_latest_commits_error_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="rate limited")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    sources = Sources(client=client, ttl_seconds=600)
    result = sources.latest_commits()
    assert isinstance(result, Unavailable)
