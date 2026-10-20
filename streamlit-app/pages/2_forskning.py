"""Side 3. Forskning: ukentlige funn som kort, fulltekst bak expandere."""
import streamlit as st
import requests

from ui import (
    REPO,
    inject_css,
    sidebar,
    section_heading,
    stat_cards,
    paper_card,
    deep_dive,
    footer,
)
from research_parser import parse_forskning

RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main/research/FORSKNING.md"

st.set_page_config(
    page_title="Forskning · Explaining Markets",
    page_icon="🔬",
    layout="wide",
)

inject_css()
sidebar()

section_heading(
    "Hva agenten lærer hver uke",
    "Hver fredag skanner en cron arXiv. Det som kan forbedre agenten, lander her som korte kort.",
    label="Forskning",
)


@st.cache_data(ttl=600, show_spinner="Henter Forskning.md fra GitHub …")
def hent_forskning() -> str:
    r = requests.get(RAW_URL, timeout=12)
    r.raise_for_status()
    return r.text


def _fmt_date(iso: str) -> str:
    """2026-10-15 → 15. okt 2026."""
    months = {
        "01": "jan", "02": "feb", "03": "mar", "04": "apr",
        "05": "mai", "06": "jun", "07": "jul", "08": "aug",
        "09": "sep", "10": "okt", "11": "nov", "12": "des",
    }
    parts = iso.split("-")
    if len(parts) != 3:
        return iso
    y, m, d = parts
    return f"{int(d)}. {months.get(m, m)} {y}"


try:
    tekst = hent_forskning()
    digest = parse_forskning(tekst)

    if not digest.parse_ok or not digest.weeks:
        st.warning(
            "Kunne ikke parse Forskning.md til kort. Viser rå markdown under."
        )
        with deep_dive("Rå FORSKNING.md"):
            st.markdown(tekst)
    else:
        latest = digest.weeks[0]
        stats: list[tuple[str, str]] = []
        if latest.new_count is not None:
            stats.append((str(latest.new_count), "Nye papers denne uken"))
        if latest.kept_count is not None:
            stats.append((str(latest.kept_count), "Beholdt for agenten"))
        if latest.rejected_count is not None:
            stats.append((str(latest.rejected_count), "Forkastet"))
        if stats:
            stat_cards(stats)
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        for week in digest.weeks[:2]:
            section_heading(week.heading)
            if not week.papers:
                st.caption("Ingen papers beholdt denne uken.")
                continue
            for paper in week.papers:
                meta_parts = []
                if paper.authors:
                    meta_parts.append(paper.authors)
                if paper.date:
                    meta_parts.append(_fmt_date(paper.date))
                if paper.arxiv_id:
                    link = (
                        f"[arXiv:{paper.arxiv_id}]({paper.url})"
                        if paper.url
                        else f"arXiv:{paper.arxiv_id}"
                    )
                    meta_parts.append(link)
                paper_card(paper.title, " · ".join(meta_parts))
                if paper.body:
                    with st.expander("Les mer"):
                        st.markdown(paper.body)

        with deep_dive("Se hele FORSKNING.md fra repoet"):
            st.markdown(tekst)

except Exception:
    st.warning(
        "Kunne ikke hente research/FORSKNING.md fra GitHub akkurat nå. "
        f"Se filen direkte: [lenke](https://github.com/{REPO}/blob/main/research/FORSKNING.md)."
    )

footer()
