"""Admin-autentisering for Forskning-siden.

Ene eier av credentials, sesjonscookie og next-validering.
Fail closed: mangler miljøvariabler → innlogging deaktivert.
"""

from __future__ import annotations

import hmac
import os
from dataclasses import dataclass
from typing import Annotated
from urllib.parse import urlparse

from fastapi import Cookie, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SESSION_COOKIE = "em_admin"
SESSION_MAX_AGE = 8 * 60 * 60  # 8 timer
ALLOWED_NEXT = frozenset({"/forskning"})
DEFAULT_NEXT = "/forskning"


@dataclass(frozen=True)
class AdminSettings:
    username: str
    password: str
    session_secret: str


class AuthRequired(Exception):
    """Kastes når admin-sesjon mangler. Håndteres i main med 303-redirect."""

    def __init__(self, next_path: str) -> None:
        self.next_path = next_path
        super().__init__(next_path)


def load_admin_settings() -> AdminSettings | None:
    """Les credentials fra miljø. Returnerer None hvis noe mangler."""
    username = os.environ.get("ADMIN_USERNAME", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "").strip()
    secret = os.environ.get("SESSION_SECRET", "").strip()
    if not username or not password or not secret:
        return None
    return AdminSettings(username=username, password=password, session_secret=secret)


def verify_credentials(settings: AdminSettings, username: str, password: str) -> bool:
    """Konstant-tid sammenligning av brukernavn og passord."""
    user_ok = hmac.compare_digest(username.encode("utf-8"), settings.username.encode("utf-8"))
    pass_ok = hmac.compare_digest(password.encode("utf-8"), settings.password.encode("utf-8"))
    return user_ok and pass_ok


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="em-admin-session")


def create_session_token(settings: AdminSettings) -> str:
    return _serializer(settings.session_secret).dumps({"role": "admin"})


def read_session_token(settings: AdminSettings, token: str | None) -> bool:
    if not token:
        return False
    try:
        data = _serializer(settings.session_secret).loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return False
    return isinstance(data, dict) and data.get("role") == "admin"


def safe_next(raw: str | None) -> str:
    """Whitelist interne stier. Blokker open redirects."""
    if not raw:
        return DEFAULT_NEXT
    candidate = raw.strip()
    if not candidate.startswith("/") or candidate.startswith("//"):
        return DEFAULT_NEXT
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        return DEFAULT_NEXT
    path = parsed.path
    if path not in ALLOWED_NEXT:
        return DEFAULT_NEXT
    return path


def is_admin_request(request: Request) -> bool:
    settings = load_admin_settings()
    if settings is None:
        return False
    return read_session_token(settings, request.cookies.get(SESSION_COOKIE))


def require_admin(
    request: Request,
    em_admin: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> None:
    """FastAPI-dependency: krever gyldig admin-sesjon."""
    settings = load_admin_settings()
    if settings is not None and read_session_token(settings, em_admin):
        return None
    raise AuthRequired(safe_next(request.url.path))


def session_cookie_kwargs(*, secure: bool) -> dict:
    return {
        "key": SESSION_COOKIE,
        "httponly": True,
        "samesite": "lax",
        "secure": secure,
        "max_age": SESSION_MAX_AGE,
        "path": "/",
    }
