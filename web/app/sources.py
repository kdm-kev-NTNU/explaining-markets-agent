"""Ekstern data: GitHub raw FORSKNING.md, queue.yaml og leaderboard-plassering.

Returnerer eksplisitte resultattyper — kaster aldri unntak ut til rutene.
Cache-tilstand eies her; klokken injiseres for deterministiske tester.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

import httpx

from .content import FORSKNING_RAW_URL, QUEUE_RAW_URL
from .leaderboard import PUBLIC_NAME, Standing, featured_period, find_standing, index_url, standings_url
from .research_parser import ResearchDigest, parse_forskning
from .research_registry import QueueRegistry, parse_queue_yaml

T = TypeVar("T")

DEFAULT_TTL_SECONDS = 600.0
FORSKNING_TIMEOUT = 12.0
LEADERBOARD_TIMEOUT = 6.0


@dataclass(frozen=True)
class Available(Generic[T]):
    value: T


@dataclass(frozen=True)
class Unavailable:
    reason: str


Result = Available[T] | Unavailable


@dataclass
class TTLCache(Generic[T]):
    """Enkel TTL-cache med injiserbar klokke."""

    ttl_seconds: float
    clock: Callable[[], float] = time.monotonic
    _value: T | None = None
    _expires_at: float = 0.0

    def get(self) -> T | None:
        if self._value is None:
            return None
        if self.clock() >= self._expires_at:
            return None
        return self._value

    def set(self, value: T) -> None:
        self._value = value
        self._expires_at = self.clock() + self.ttl_seconds

    def clear(self) -> None:
        self._value = None
        self._expires_at = 0.0


class Sources:
    """Henter og cacher eksterne kilder. Én instans per app."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        clock: Callable[[], float] = time.monotonic,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        github_token: str | None = None,
    ) -> None:
        self._owns_client = client is None
        headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
        token = github_token if github_token is not None else os.environ.get("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = client or httpx.Client(timeout=FORSKNING_TIMEOUT, headers=headers)
        self._forskning_cache: TTLCache[Available[tuple[str, ResearchDigest]]] = TTLCache(
            ttl_seconds=ttl_seconds, clock=clock
        )
        self._queue_cache: TTLCache[Available[QueueRegistry]] = TTLCache(
            ttl_seconds=ttl_seconds, clock=clock
        )
        # Egen klient uten GitHub-token: tokenet skal aldri sendes til CloudFront.
        self._lb_client = client or httpx.Client(timeout=LEADERBOARD_TIMEOUT)
        self._standing_cache: TTLCache[Available[Standing]] = TTLCache(
            ttl_seconds=ttl_seconds, clock=clock
        )
        self._public_name = os.environ.get("LEADERBOARD_NAME", "").strip() or PUBLIC_NAME

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
            self._lb_client.close()

    def fetch_standing(self) -> Result[Standing]:
        """Egen plassering i inneværende konkurranseperiode."""
        cached = self._standing_cache.get()
        if cached is not None:
            return cached
        try:
            resp = self._lb_client.get(index_url(), timeout=LEADERBOARD_TIMEOUT)
            resp.raise_for_status()
            period = featured_period(resp.json())
            if not period:
                return Unavailable(reason="Ingen rangert periode")
            resp = self._lb_client.get(standings_url(period), timeout=LEADERBOARD_TIMEOUT)
            resp.raise_for_status()
            standing = find_standing(resp.json(), self._public_name)
            if standing is None:
                return Unavailable(reason=f"{self._public_name} finnes ikke i {period}")
            result: Available[Standing] = Available(standing)
            self._standing_cache.set(result)
            return result
        except Exception as exc:
            return Unavailable(reason=f"{type(exc).__name__}: {exc}")

    def fetch_forskning(self) -> Result[tuple[str, ResearchDigest]]:
        cached = self._forskning_cache.get()
        if cached is not None:
            return cached
        try:
            resp = self._client.get(FORSKNING_RAW_URL, timeout=FORSKNING_TIMEOUT)
            resp.raise_for_status()
            text = resp.text
            digest = parse_forskning(text)
            result: Available[tuple[str, ResearchDigest]] = Available((text, digest))
            self._forskning_cache.set(result)
            return result
        except Exception as exc:
            return Unavailable(reason=f"{type(exc).__name__}: {exc}")

    def fetch_queue(self) -> Result[QueueRegistry]:
        cached = self._queue_cache.get()
        if cached is not None:
            return cached
        try:
            resp = self._client.get(QUEUE_RAW_URL, timeout=FORSKNING_TIMEOUT)
            resp.raise_for_status()
            registry = parse_queue_yaml(resp.text)
            result: Available[QueueRegistry] = Available(registry)
            self._queue_cache.set(result)
            return result
        except Exception as exc:
            return Unavailable(reason=f"{type(exc).__name__}: {exc}")
