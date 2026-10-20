"""Kontrakttester for parse_forskning — fanger formatendringer i FORSKNING.md."""
from __future__ import annotations

from pathlib import Path

import pytest

from research_parser import parse_forskning

FIXTURE = """# FORSKNING — test

## Ukentlige funn

### Uke 2026-W42 (16. okt 2026)

Collect OK: 7 nye arXiv-papers, 0 feilede søk. 2 beholdt, 5 forkastet.
Web-sjekk: ingen nye bloggposter.

**Momentum, Commentary Tone, and Earnings Surprise in LLM Financial Forecasts**
Khaybullina, 2026-10-15 · https://arxiv.org/abs/2610.22043 · cs.LG
Syntetiske earnings-annonser. Bruk (3c): la ikke tone drive prediksjonen.

**When Does "Post-Call" Begin? An Availability Contract for Earnings-Call NLP Benchmarks**
Ma, Koa, Liu & Huang, 2026-10-15 · https://arxiv.org/abs/2610.21659 · q-fin.CP
Innfører Availability Contract. Bruk (3b-hygiene).

(Forkastet: 2610.18435 LLM-peer-review.)

### Uke 2026-W41 (9. okt 2026)

Collect: 0 nye arXiv-papers. Kompensert: 4 beholdt, 0 forkastet.

**Measuring What is Repeated and Novel in Earnings Disclosures Using Optimal Transport**
Wu, Tao, Martineau, Grégoire & Veneris, 2026-10-02 · https://arxiv.org/abs/2610.04094 · cs.CE
Optimal transport. Bruk (3c).

## Implementeringskø

Noe annet som ikke skal parses.
"""


def test_parses_weeks_and_papers() -> None:
    digest = parse_forskning(FIXTURE)
    assert digest.parse_ok
    assert len(digest.weeks) == 2

    w42 = digest.weeks[0]
    assert w42.heading.startswith("Uke 2026-W42")
    assert w42.new_count == 7
    assert w42.kept_count == 2
    assert w42.rejected_count == 5
    assert len(w42.papers) == 2
    assert w42.papers[0].title.startswith("Momentum")
    assert w42.papers[0].arxiv_id == "2610.22043"
    assert w42.papers[0].authors == "Khaybullina"
    assert "arxiv.org/abs/2610.22043" in w42.papers[0].url
    assert w42.papers[1].arxiv_id == "2610.21659"

    w41 = digest.weeks[1]
    assert len(w41.papers) == 1
    assert w41.papers[0].arxiv_id == "2610.04094"


def test_empty_and_garbage_do_not_raise() -> None:
    assert parse_forskning("").parse_ok is False
    assert parse_forskning("").weeks == ()
    assert parse_forskning("bare tekst uten uker").parse_ok is False
    assert parse_forskning("## Annet\n### Ikke uke").parse_ok is False


def test_missing_uke_section_still_finds_weeks() -> None:
    md = "### Uke 2026-W99\n\n1 beholdt, 0 forkastet.\n\n**Tittel**\nA, 2026-01-01 · https://arxiv.org/abs/9999.99999\n"
    digest = parse_forskning(md)
    assert digest.parse_ok
    assert len(digest.weeks) == 1
    assert digest.weeks[0].papers[0].title == "Tittel"


def test_real_forskning_md_if_present() -> None:
    """Regression mot repoets FORSKNING.md når den finnes."""
    path = Path(__file__).resolve().parents[2] / "research" / "FORSKNING.md"
    if not path.exists():
        pytest.skip("FORSKNING.md ikke i repoet")
    digest = parse_forskning(path.read_text(encoding="utf-8"))
    assert digest.parse_ok
    assert len(digest.weeks) >= 1
    assert any(w.papers for w in digest.weeks)
    first = next(p for w in digest.weeks for p in w.papers)
    assert first.title
    assert first.arxiv_id or first.url
