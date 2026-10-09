#!/usr/bin/env python3
"""Explaining Markets — research-collector (pre-run for ukentlig cron).

Søker arXiv etter nye papers relevant for konkurransesystemet, deduper mot
state.json og skriver ut de NYE (tittel, forfattere, dato, abstract-snutt,
lenke). Stdlib only — ingen deps, trygt i cron-terminal.

Kjør:  python3 ~/explaining-markets/research/collect.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state.json"
NS = {"a": "http://www.w3.org/2005/Atom"}

# Søketemaer = innsatsområdene i konkurransen. Holdt fokusert for signal/støy.
QUERIES = [
    # (id, arXiv search_query)
    ("earnings-reaksjon", 'abs:"earnings announcement" AND (abs:return OR abs:stock price OR abs:drift)'),
    ("llm-finans", 'abs:"large language model" AND (abs:"asset pricing" OR abs:finance OR abs:"stock return" OR abs:earnings)'),
    ("earnings-calls", 'abs:"earnings call" OR abs:"earnings calls"'),
    ("opsjonsimplisitt", 'abs:"option-implied" AND (abs:earnings OR abs:"announcement" OR abs:skew)'),
    ("pead", 'abs:"post-earnings announcement drift" OR abs:PEAD'),
    ("abnormal-return", 'abs:"abnormal return" AND (abs:prediction OR abs:forecast OR abs:machine)'),
]
MAX_PER_QUERY = 20
WINDOW_DAYS = 21  # ukentlig jobb → 3 ukers vindu som sikkerhetsmargin
API = "https://export.arxiv.org/api/query"


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            return {"seen": {}}
    return {"seen": {}}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False))


def arxiv_search(query: str, max_results: int = MAX_PER_QUERY) -> list[dict]:
    params = urllib.parse.urlencode({
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
    })
    url = f"{API}?{params}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "cogito-research/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            root = ET.fromstring(data)
            out = []
            for entry in root.findall("a:entry", NS):
                arxiv_id = entry.find("a:id", NS).text.strip().split("/abs/")[-1]
                # versjonsløs id for dedup
                base_id = re.sub(r"v\d+$", "", arxiv_id)
                title = re.sub(r"\s+", " ", entry.find("a:title", NS).text.strip())
                authors = ", ".join(a.find("a:name", NS).text for a in entry.findall("a:author", NS))
                published = entry.find("a:published", NS).text[:10]
                summary = re.sub(r"\s+", " ", entry.find("a:summary", NS).text.strip())[:400]
                cats = ", ".join(c.get("term") for c in entry.findall("a:category", NS))
                # Withdrawn?
                low = summary.lower()
                if "withdrawn" in low or "retract" in low:
                    continue
                out.append({
                    "id": base_id, "title": title, "authors": authors,
                    "published": published, "summary": summary, "cats": cats,
                    "url": f"https://arxiv.org/abs/{base_id}",
                })
            return out
        except Exception as exc:
            if attempt == 2:
                print(f"FEILET arXiv-søk ({query[:40]}...): {type(exc).__name__}: {exc}")
                return []
            time.sleep(4 * (attempt + 1))  # arXiv vil ha ~3s mellom kall
    return []


def main() -> int:
    state = load_state()
    seen: dict = state.setdefault("seen", {})
    now = time.time()
    new_papers: dict[str, dict] = {}   # id -> paper
    failed: list[str] = []

    for tema, q in QUERIES:
        papers = arxiv_search(q)
        if not papers:
            failed.append(tema)
        for p in papers:
            # tidsvindu
            try:
                age_days = (now - time.mktime(time.strptime(p["published"], "%Y-%m-%d"))) / 86400
            except ValueError:
                continue
            if age_days > WINDOW_DAYS:
                continue
            pid = p["id"]
            if pid in seen:
                continue
            if pid not in new_papers:
                p["temaer"] = [tema]
                new_papers[pid] = p
            elif tema not in new_papers[pid]["temaer"]:
                new_papers[pid]["temaer"].append(tema)
        time.sleep(3.1)  # arXiv rate-limit

    # Skriv ut i cron-vennlig format
    print(f"=== RESEARCH-COLLECT {time.strftime('%Y-%m-%d %H:%M')} ===")
    print(f"Nye papers siste {WINDOW_DAYS} dager: {len(new_papers)}")
    print(f"Sete papers totalt: {len(seen)} | Feilede søk: {len(failed)}")
    if failed:
        print("FEILET-temaer: " + ", ".join(failed) + " (kompensér med web-søk)")
    print()
    for pid, p in sorted(new_papers.items(), key=lambda kv: kv[1]["published"], reverse=True):
        print(f"[{p['published']}] {p['title']}")
        print(f"  Forfattere: {p['authors'][:150]}")
        print(f"  Tema: {'+'.join(p['temaer'])} | Kat: {p['cats']}")
        print(f"  {p['summary']}")
        print(f"  {p['url']}")
        print()

    # Oppdater state: de utleverte er nå sett
    for pid in new_papers:
        seen[pid] = {"last_seen": time.strftime("%Y-%m-%d")}
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
