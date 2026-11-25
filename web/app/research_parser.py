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
class RejectedPaper:
    arxiv_id: str
    title: str
    reason: str


@dataclass(frozen=True)
class Week:
    heading: str
    summary: str
    new_count: int | None
    kept_count: int | None
    rejected_count: int | None
    papers: tuple[Paper, ...] = field(default_factory=tuple)
    rejected: tuple[RejectedPaper, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResearchDigest:
    weeks: tuple[Week, ...]
    parse_ok: bool


_WEEK_RE = re.compile(r"^###\s+(Uke\s+.+)$", re.MULTILINE)
# Tillat trailing parentetisk merknad etter lukkende ** (OLIVIA-protokollen).
_PAPER_TITLE_RE = re.compile(r"^\*\*(.+?)\*\*(?:\s+\([^)]*\))?\s*$", re.MULTILINE)
_ARXIV_RE = re.compile(r"https://arxiv\.org/abs/([\w.]+)")
_META_RE = re.compile(
    r"^(?P<authors>.+?),\s*(?P<date>\d{4}-\d{2}-\d{2})\s*·\s*"
    r"(?P<url>https://arxiv\.org/abs/[\w.]+)",
)
_FORKASTET_BLOCK_RE = re.compile(
    r"^\(Forkastet:\s*(?P<body>.*?)\)\s*$",
    re.MULTILINE | re.DOTALL,
)
# arXiv-ID YYMM.NNNNN(vN)? midt i forkastet-tekst
_REJECTED_ID_RE = re.compile(r"(?<![\w.])(\d{4}\.\d{4,5})(?![\w.])")


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


def _parse_meta_lines(lines: list[str]) -> tuple[str, str, str, str, int]:
    """Parse forfattere/dato/URL fra én eller to linjer etter tittelen.

    Returnerer (authors, date, url, arxiv_id, body_start_index).
    body_start_index er relativ til `lines` (0 = tittel).
    """
    if len(lines) < 2:
        return "", "", "", "", 1

    # Én linje: "Authors, YYYY-MM-DD · https://arxiv.org/abs/...."
    meta_m = _META_RE.match(lines[1].strip())
    if meta_m:
        url = meta_m.group("url")
        arxiv_m = _ARXIV_RE.search(url)
        return (
            meta_m.group("authors").strip(),
            meta_m.group("date"),
            url,
            arxiv_m.group(1) if arxiv_m else "",
            2,
        )

    # To linjer: forfattere/dato på L1, URL på L2 (OLIVIA-format)
    if len(lines) >= 3:
        arxiv_m = _ARXIV_RE.search(lines[2])
        date_m = re.search(r"\d{4}-\d{2}-\d{2}", lines[1])
        if arxiv_m and date_m:
            authors = lines[1].split("·")[0].strip().rstrip(",")
            return (
                authors,
                date_m.group(0),
                arxiv_m.group(0),
                arxiv_m.group(1),
                3,
            )

    # Fallback: URL et sted på metadata-linjen
    arxiv_m = _ARXIV_RE.search(lines[1])
    if arxiv_m:
        authors = lines[1].split("·")[0].strip().rstrip(",")
        date_m = re.search(r"\d{4}-\d{2}-\d{2}", lines[1])
        return (
            authors,
            date_m.group(0) if date_m else "",
            arxiv_m.group(0),
            arxiv_m.group(1),
            2,
        )
    return "", "", "", "", 1


def _parse_paper_block(block: str) -> Paper | None:
    lines = [ln for ln in block.strip().splitlines() if ln.strip()]
    if not lines:
        return None
    title_m = re.match(r"^\*\*(.+?)\*\*(?:\s+\([^)]*\))?\s*$", lines[0].strip())
    if not title_m:
        return None
    title = title_m.group(1).strip()
    authors, date, url, arxiv_id, body_start = _parse_meta_lines(lines)
    body = "\n".join(lines[body_start:]).strip()
    return Paper(
        title=title,
        authors=authors,
        date=date,
        url=url,
        arxiv_id=arxiv_id,
        body=body,
    )


def _strip_rejected_wrappers(chunk: str) -> tuple[str, str]:
    """Fra '«Title» — reason' eller 'Title — reason' → (title, reason)."""
    text = " ".join(chunk.split()).strip(" .;")
    if not text:
        return "", ""

    guillemet = re.match(r"^[«\"](.+?)[»\"]\s*[—–-]\s*(.+)$", text)
    if guillemet:
        return guillemet.group(1).strip(), guillemet.group(2).strip()

    dash = re.search(r"\s+[—–]\s+", text)
    if dash:
        title = text[: dash.start()].strip(" «»\"")
        reason = text[dash.end() :].strip()
        return title, reason

    # Kort form uten dash: hele resten er tittel
    return text.strip(" «»\""), ""


def parse_rejected_block(text: str) -> tuple[RejectedPaper, ...]:
    """Parse innholdet i en (Forkastet: ...)-blokk til RejectedPaper-er."""
    body_m = _FORKASTET_BLOCK_RE.search(text)
    if not body_m:
        # Tillat rå body uten wrapping
        body = text.strip()
        if body.lower().startswith("forkastet:"):
            body = body.split(":", 1)[1].strip()
    else:
        body = body_m.group("body")

    body = " ".join(body.split())
    matches = list(_REJECTED_ID_RE.finditer(body))
    if not matches:
        return ()

    out: list[RejectedPaper] = []
    for i, match in enumerate(matches):
        arxiv_id = match.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[match.end() : end]
        title, reason = _strip_rejected_wrappers(chunk)
        if not title:
            title = arxiv_id
        out.append(RejectedPaper(arxiv_id=arxiv_id, title=title, reason=reason))
    return tuple(out)


def _extract_rejected_from_section(section_body: str) -> tuple[RejectedPaper, ...]:
    block = re.search(r"^\(Forkastet:.*$", section_body, re.MULTILINE | re.DOTALL)
    if not block:
        return ()
    # Finn avsluttende ) på egen nesting — ta til siste ) før neste ### eller slutt
    raw = block.group(0)
    # Begrens til første balanserte parentes-blokk som starter med (Forkastet:
    depth = 0
    end_idx = None
    for i, ch in enumerate(raw):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end_idx = i + 1
                break
    if end_idx is None:
        return ()
    return parse_rejected_block(raw[:end_idx])


def _split_papers(section_body: str) -> tuple[str, list[Paper], tuple[RejectedPaper, ...]]:
    """Del uketekst i sammendrag + paper-blokker + forkastede."""
    rejected = _extract_rejected_from_section(section_body)

    first = _PAPER_TITLE_RE.search(section_body)
    if not first:
        return section_body.strip(), [], rejected

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
        # Avvis bold-linjer midt i body («**Bruk (...):**») — krev arXiv-ID.
        if paper and paper.arxiv_id:
            papers.append(paper)
    return summary, papers, rejected


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
        summary, papers, rejected = _split_papers(body)
        new_c, kept_c, rej_c = _parse_counts(summary)
        weeks.append(
            Week(
                heading=heading,
                summary=summary,
                new_count=new_c,
                kept_count=kept_c,
                rejected_count=rej_c,
                papers=tuple(papers),
                rejected=rejected,
            )
        )

    return ResearchDigest(weeks=tuple(weeks), parse_ok=True)
