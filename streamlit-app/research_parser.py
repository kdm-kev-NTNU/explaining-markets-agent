"""Parser for research/FORSKNING.md → strukturerte kort.

Kontrakt: ### Uke-overskrifter, **Tittel**-linjer, deretter metadata-linje
med forfattere, dato og arXiv-URL. Ved parsefeil returneres tomme lister
(eksplisitt, ikke stille unntak) slik at siden kan falle tilbake til rå markdown.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Paper:
    title: str
    authors: str
    date: str
    url: str
    arxiv_id: str
    body: str


@dataclass(frozen=True)
class Week:
    heading: str
    summary: str
    new_count: int | None
    kept_count: int | None
    rejected_count: int | None
    papers: tuple[Paper, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResearchDigest:
    weeks: tuple[Week, ...]
    parse_ok: bool


_WEEK_RE = re.compile(r"^###\s+(Uke\s+.+)$", re.MULTILINE)
_PAPER_TITLE_RE = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
_ARXIV_RE = re.compile(r"https://arxiv\.org/abs/([\w.]+)")
_META_RE = re.compile(
    r"^(?P<authors>.+?),\s*(?P<date>\d{4}-\d{2}-\d{2})\s*·\s*"
    r"(?P<url>https://arxiv\.org/abs/[\w.]+)",
)


def _parse_counts(summary: str) -> tuple[int | None, int | None, int | None]:
    m3 = re.search(
        r"(?P<new>\d+)\s+nye.*?\.?\s*(?P<kept>\d+)\s+beholdt,\s*(?P<rejected>\d+)\s+forkastet",
        summary,
        re.IGNORECASE | re.DOTALL,
    )
    if m3:
        return int(m3.group("new")), int(m3.group("kept")), int(m3.group("rejected"))
    m2 = re.search(
        r"(?P<kept>\d+)\s+beholdt.*?,\s*(?P<rejected>\d+)\s+forkastet",
        summary,
        re.IGNORECASE | re.DOTALL,
    )
    if m2:
        return None, int(m2.group("kept")), int(m2.group("rejected"))
    return None, None, None


def _parse_paper_block(block: str) -> Paper | None:
    lines = [ln for ln in block.strip().splitlines() if ln.strip()]
    if not lines:
        return None
    title_m = re.match(r"^\*\*(.+?)\*\*$", lines[0].strip())
    if not title_m:
        return None
    title = title_m.group(1).strip()
    authors, date, url, arxiv_id = "", "", "", ""
    body_start = 1
    if len(lines) > 1:
        meta_m = _META_RE.match(lines[1].strip())
        if meta_m:
            authors = meta_m.group("authors").strip()
            date = meta_m.group("date")
            url = meta_m.group("url")
            arxiv_m = _ARXIV_RE.search(url)
            arxiv_id = arxiv_m.group(1) if arxiv_m else ""
            body_start = 2
        else:
            arxiv_m = _ARXIV_RE.search(lines[1])
            if arxiv_m:
                url = arxiv_m.group(0)
                arxiv_id = arxiv_m.group(1)
                authors = lines[1].split("·")[0].strip().rstrip(",")
                date_m = re.search(r"\d{4}-\d{2}-\d{2}", lines[1])
                date = date_m.group(0) if date_m else ""
                body_start = 2
    body = "\n".join(lines[body_start:]).strip()
    return Paper(
        title=title,
        authors=authors,
        date=date,
        url=url,
        arxiv_id=arxiv_id,
        body=body,
    )


def _split_papers(section_body: str) -> tuple[str, list[Paper]]:
    """Del uketekst i sammendrag + paper-blokker som starter med **Tittel**."""
    first = _PAPER_TITLE_RE.search(section_body)
    if not first:
        return section_body.strip(), []

    summary = section_body[: first.start()].strip()
    rest = section_body[first.start() :]

    stop = re.search(r"^\(Forkastet:", rest, re.MULTILINE)
    if stop:
        rest = rest[: stop.start()]

    titles = list(_PAPER_TITLE_RE.finditer(rest))
    papers: list[Paper] = []
    for i, match in enumerate(titles):
        end = titles[i + 1].start() if i + 1 < len(titles) else len(rest)
        block = rest[match.start() : end]
        paper = _parse_paper_block(block)
        if paper:
            papers.append(paper)
    return summary, papers


def parse_forskning(md: str) -> ResearchDigest:
    """Parse FORSKNING.md til ResearchDigest.

    Invariant: returnerer alltid ResearchDigest (aldri raise for formatfeil).
    parse_ok er False hvis ingen uker ble funnet.
    """
    if not md or not md.strip():
        return ResearchDigest(weeks=(), parse_ok=False)

    funn = re.search(r"^##\s+Ukentlige funn\s*$", md, re.MULTILINE)
    if funn:
        rest_start = funn.end()
        next_h2 = re.search(r"^##\s+", md[rest_start:], re.MULTILINE)
        section = md[rest_start : rest_start + next_h2.start()] if next_h2 else md[rest_start:]
    else:
        section = md

    week_matches = list(_WEEK_RE.finditer(section))
    if not week_matches:
        return ResearchDigest(weeks=(), parse_ok=False)

    weeks: list[Week] = []
    for i, match in enumerate(week_matches):
        heading = match.group(1).strip()
        end = week_matches[i + 1].start() if i + 1 < len(week_matches) else len(section)
        body = section[match.end() : end]
        summary, papers = _split_papers(body)
        new_c, kept_c, rej_c = _parse_counts(summary)
        weeks.append(
            Week(
                heading=heading,
                summary=summary,
                new_count=new_c,
                kept_count=kept_c,
                rejected_count=rej_c,
                papers=tuple(papers),
            )
        )

    return ResearchDigest(weeks=tuple(weeks), parse_ok=True)
