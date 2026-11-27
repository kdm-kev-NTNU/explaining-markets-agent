"""FastAPI-presentasjonsside for Explaining Markets.

Ruter: /, /agent, /forskning, /admin, /healthz
Ekstern data går via Sources — feil gir Unavailable, aldri 500 fra GitHub.
Forskning krever admin-sesjon.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from . import content
from .auth import (
    AuthRequired,
    create_session_token,
    is_admin_request,
    load_admin_settings,
    require_admin,
    safe_next,
    session_cookie_kwargs,
    verify_credentials,
)
from .research_view import build_research_view, parse_filters
from .sources import Available, Sources

HERE = Path(__file__).resolve().parent
md = MarkdownIt("commonmark", {"html": False})


def render_markdown(text: str) -> str:
    """Render markdown med rå HTML slått av."""
    return md.render(text or "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    sources = Sources()
    app.state.sources = sources
    yield
    sources.close()


app = FastAPI(title="Explaining Markets", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")

templates = Jinja2Templates(directory=str(HERE / "templates"))
templates.env.filters["markdown"] = render_markdown
# Autoescape is on by default for .html in Jinja2Templates


@app.exception_handler(AuthRequired)
async def auth_required_handler(request: Request, exc: AuthRequired) -> RedirectResponse:
    return RedirectResponse(url=f"/admin?next={exc.next_path}", status_code=303)


def _base_context(request: Request, active: str) -> dict:
    return {
        "request": request,
        "active": active,
        "nav": content.NAV,
        "repo": content.REPO,
        "repo_url": content.REPO_URL,
        "competition_url": content.COMPETITION_URL,
        "is_admin": is_admin_request(request),
    }


def _cookie_secure(request: Request) -> bool:
    return request.url.scheme == "https" or os.environ.get("COOKIE_SECURE", "").lower() in {
        "1",
        "true",
        "yes",
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "service": "explaining-markets-site"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    chart_max = max(b.value for b in content.HOME_CHART) or 1.0
    ctx = _base_context(request, "Konkurransen")
    ctx.update(
        {
            "hero": content.HOME_HERO,
            "steps": content.HOME_STEPS,
            "why": content.HOME_WHY,
            "analogy_title": content.HOME_ANALOGY_TITLE,
            "analogy_body": content.HOME_ANALOGY_BODY,
            "chart": content.HOME_CHART,
            "chart_max": chart_max,
            "chart_caption": content.HOME_CHART_CAPTION,
            "tech_chips": content.HOME_TECH_CHIPS,
            "deep_dive": content.HOME_DEEP_DIVE,
        }
    )
    return templates.TemplateResponse(request, "index.html", ctx)


@app.get("/agent", response_class=HTMLResponse)
def agent_page(request: Request) -> HTMLResponse:
    ctx = _base_context(request, "Agenten")
    ctx.update(
        {
            "clocks": content.AGENT_CLOCKS,
            "rules": content.AGENT_RULES,
            "live_flow": content.LIVE_FLOW,
            "deploy_chain": content.DEPLOY_CHAIN,
            "learn_chain": content.LEARN_CHAIN,
            "formulas": content.AGENT_DEEP_DIVE_FORMULAS,
            "deep_dive": content.AGENT_DEEP_DIVE,
        }
    )
    return templates.TemplateResponse(request, "agent.html", ctx)


@app.get("/admin", response_model=None)
def admin_login_get(request: Request) -> Response:
    if is_admin_request(request):
        return RedirectResponse(url=safe_next(request.query_params.get("next")), status_code=303)
    settings = load_admin_settings()
    ctx = _base_context(request, "Forskning")
    ctx.update(
        {
            "next": safe_next(request.query_params.get("next")),
            "error": None,
            "auth_configured": settings is not None,
        }
    )
    return templates.TemplateResponse(request, "admin_login.html", ctx)


@app.post("/admin", response_model=None)
def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/forskning"),
) -> Response:
    settings = load_admin_settings()
    destination = safe_next(next)
    if settings is None:
        ctx = _base_context(request, "Forskning")
        ctx.update(
            {
                "next": destination,
                "error": "Innlogging er ikke konfigurert. Sett ADMIN_USERNAME, ADMIN_PASSWORD og SESSION_SECRET.",
                "auth_configured": False,
            }
        )
        return templates.TemplateResponse(request, "admin_login.html", ctx, status_code=503)

    if not verify_credentials(settings, username, password):
        ctx = _base_context(request, "Forskning")
        ctx.update(
            {
                "next": destination,
                "error": "Feil brukernavn eller passord.",
                "auth_configured": True,
            }
        )
        return templates.TemplateResponse(request, "admin_login.html", ctx, status_code=401)

    response = RedirectResponse(url=destination, status_code=303)
    response.set_cookie(
        value=create_session_token(settings),
        **session_cookie_kwargs(secure=_cookie_secure(request)),
    )
    return response


@app.post("/admin/logout")
def admin_logout(request: Request) -> RedirectResponse:
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="em_admin", path="/")
    return response


@app.get("/forskning", response_class=HTMLResponse)
def forskning_page(
    request: Request,
    _: None = Depends(require_admin),
) -> HTMLResponse:
    sources: Sources = request.app.state.sources
    result = sources.fetch_forskning()
    queue_result = sources.fetch_queue()
    filters = parse_filters(
        uke=request.query_params.get("uke"),
        status=request.query_params.get("status"),
        area=request.query_params.get("area"),
        linked=request.query_params.get("linked"),
    )
    ctx = _base_context(request, "Forskning")
    ctx.update(
        {
            "forskning_blob_url": content.FORSKNING_BLOB_URL,
            "queue_blob_url": content.QUEUE_BLOB_URL,
            "forskning": result,
            "forskning_available": isinstance(result, Available),
            "raw_md": None,
            "digest": None,
            "weeks": (),
            "view": None,
            "filters": filters,
        }
    )
    if isinstance(result, Available):
        raw_md, digest = result.value
        ctx["raw_md"] = raw_md
        ctx["digest"] = digest
        ctx["weeks"] = digest.weeks if digest.parse_ok else ()
        queue = queue_result.value if isinstance(queue_result, Available) else None
        queue_warning = None if isinstance(queue_result, Available) else (
            f"Kunne ikke hente kø: {queue_result.reason}"
        )
        if digest.parse_ok:
            ctx["view"] = build_research_view(
                digest, queue, filters, queue_warning=queue_warning
            )
    return templates.TemplateResponse(request, "forskning.html", ctx)
