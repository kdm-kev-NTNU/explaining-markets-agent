"""Pytest path setup: web/ er root for `app`-pakken."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

WEB_ROOT = Path(__file__).resolve().parents[1]
if str(WEB_ROOT) not in sys.path:
    sys.path.insert(0, str(WEB_ROOT))


@pytest.fixture
def admin_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sett admin-credentials for tester som trenger innlogging."""
    monkeypatch.setenv("ADMIN_USERNAME", "ADMIN")
    monkeypatch.setenv("ADMIN_PASSWORD", "FUTURE")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-not-for-prod")
