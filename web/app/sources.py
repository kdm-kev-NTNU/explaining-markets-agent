"""Ekstern data: GitHub raw FORSKNING.md og siste commits.

Returnerer eksplisitte resultattyper — kaster aldri unntak ut til rutene.
Cache-tilstand eies her; klokken injiseres for deterministiske tester.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

import httpx

from .content import COMMITS_API_URL, FORSKNING_RAW_URL
from .research_parser import ResearchDigest, parse_forskning

T = TypeVar("T")

DEFAULT_TTL_SECONDS = 600.0
FORSKNING_TIMEOUT = 12.0
COMMITS_TIMEOUT = 8.0


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


@dataclass(frozen=True)
class CommitInfo:
    sha: str
    msg: str
    date: str


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
        self._commits_cache: TTLCache[Available[tuple[CommitInfo, ...]]] = TTLCache(
            ttl_seconds=ttl_seconds, clock=clock
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

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

    def latest_commits(self) -> Result[tuple[CommitInfo, ...]]:
        cached = self._commits_cache.get()
        if cached is not None:
            return cached
        try:
            resp = self._client.get(COMMITS_API_URL, timeout=COMMITS_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            commits = tuple(
                CommitInfo(
                    sha=c["sha"][:7],
                    msg=(c["commit"]["message"].splitlines() or [""])[0][:64],
                    date=c["commit"]["author"]["date"][:10],
                )
                for c in data
            )
            result: Available[tuple[CommitInfo, ...]] = Available(commits)
            self._commits_cache.set(result)
            return result
        except Exception as exc:
            return Unavailable(reason=f"{type(exc).__name__}: {exc}")
