"""Unit-tester for admin-autentisering."""

from __future__ import annotations

import time

import pytest

from app.auth import (
    AdminSettings,
    create_session_token,
    read_session_token,
    safe_next,
    verify_credentials,
)


@pytest.fixture
def settings() -> AdminSettings:
    return AdminSettings(
        username="ADMIN",
        password="FUTURE",
        session_secret="unit-test-secret",
    )


def test_verify_credentials_ok(settings: AdminSettings) -> None:
    assert verify_credentials(settings, "ADMIN", "FUTURE") is True


def test_verify_credentials_wrong_password(settings: AdminSettings) -> None:
    assert verify_credentials(settings, "ADMIN", "wrong") is False


def test_verify_credentials_wrong_username(settings: AdminSettings) -> None:
    assert verify_credentials(settings, "other", "FUTURE") is False


def test_session_token_roundtrip(settings: AdminSettings) -> None:
    token = create_session_token(settings)
    assert read_session_token(settings, token) is True


def test_session_token_tampered(settings: AdminSettings) -> None:
    token = create_session_token(settings)
    assert read_session_token(settings, token + "x") is False


def test_session_token_expired(
    settings: AdminSettings, monkeypatch: pytest.MonkeyPatch
) -> None:
    token = create_session_token(settings)
    issued_at = time.time()
    monkeypatch.setattr(time, "time", lambda: issued_at + 100_000)
    assert read_session_token(settings, token) is False


def test_session_token_none(settings: AdminSettings) -> None:
    assert read_session_token(settings, None) is False


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, "/forskning"),
        ("", "/forskning"),
        ("/forskning", "/forskning"),
        ("//evil.com", "/forskning"),
        ("https://evil.com", "/forskning"),
        ("/admin", "/forskning"),
        ("http://localhost/forskning", "/forskning"),
        ("/forskning?x=1", "/forskning"),  # path only; query stripped by urlparse.path
    ],
)
def test_safe_next(raw: str | None, expected: str) -> None:
    assert safe_next(raw) == expected
