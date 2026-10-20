"""Felles presentasjonslag for Explaining Markets Streamlit-siden.

Ene eier av CSS og visuelle komponenter. Sidene kaller bare disse
funksjonene — ingen side har CSS eller HTML inline.
Fargetema matcher explainingmarkets.ai (--em-accent #c84a1f).
"""
from __future__ import annotations

import streamlit as st
import requests

REPO = "kdm-kev-NTNU/explaining-markets-agent"
REPO_URL = f"https://github.com/{REPO}"

# Design tokens (explainingmarkets.ai light theme)
ACCENT = "#c84a1f"
FG = "#161616"
BG = "#fafaf8"
MUTED = "#6e6e6e"
RULE = "#ebebe7"
WASH = "#faede9"
WHITE = "#ffffff"
WASH_LINK = "#9e3a17"


def inject_css() -> None:
    """Injiser global CSS én gang per side lasting."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
.stApp {{
  background: {BG};
}}
section[data-testid="stSidebar"] {{
  background: {WHITE};
  border-right: 1px solid {RULE};
}}

.em-hero {{
  background: {FG};
  border-radius: 16px;
  padding: 2.5rem 2rem;
  margin-bottom: 1.75rem;
  color: {WHITE};
}}
.em-hero .em-eyebrow {{
  color: {ACCENT};
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}}
.em-hero h1 {{
  color: {WHITE} !important;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.25;
  margin: 0 0 0.75rem 0;
}}
.em-hero p {{
  color: rgba(255,255,255,0.72);
  font-size: 1.05rem;
  line-height: 1.55;
  margin: 0;
  max-width: 42rem;
}}
.em-hero-metrics {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.5rem;
}}
.em-hero-metric {{
  background: rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 0.85rem 1.1rem;
  min-width: 9rem;
}}
.em-hero-metric .v {{
  color: {WHITE};
  font-size: 1.1rem;
  font-weight: 700;
}}
.em-hero-metric .l {{
  color: rgba(255,255,255,0.5);
  font-size: 0.75rem;
  margin-top: 0.2rem;
}}

.em-section-title {{
  color: {FG};
  font-size: 1.5rem;
  font-weight: 700;
  margin: 1.5rem 0 0.35rem 0;
}}
.em-section-sub {{
  color: {MUTED};
  font-size: 1rem;
  margin-bottom: 1rem;
}}
.em-label {{
  color: {ACCENT};
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}}

.em-card {{
  background: {WHITE};
  border: 1px solid {RULE};
  border-radius: 12px;
  padding: 1.25rem 1.35rem;
  height: 100%;
}}
.em-card .em-num {{
  color: {ACCENT};
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}}
.em-card h3 {{
  color: {FG};
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  line-height: 1.35;
}}
.em-card p {{
  color: {MUTED};
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}}

.em-stat {{
  background: {WHITE};
  border: 1px solid {RULE};
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
}}
.em-stat .v {{
  color: {FG};
  font-size: 1.75rem;
  font-weight: 700;
}}
.em-stat .l {{
  color: {MUTED};
  font-size: 0.85rem;
  margin-top: 0.25rem;
}}

.em-clock {{
  background: {FG};
  border-radius: 12px;
  padding: 1.5rem;
  color: {WHITE};
}}
.em-clock .v {{
  font-size: 2.25rem;
  font-weight: 700;
  color: {WHITE};
}}
.em-clock .l {{
  color: {ACCENT};
  font-size: 1rem;
  font-weight: 600;
  margin: 0.35rem 0;
}}
.em-clock .d {{
  color: rgba(255,255,255,0.65);
  font-size: 0.85rem;
  line-height: 1.45;
}}

.em-rule {{
  background: {WASH};
  border-radius: 12px;
  padding: 1.2rem 1.3rem;
  height: 100%;
}}
.em-rule h3 {{
  color: {FG};
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.4rem 0;
}}
.em-rule p {{
  color: {MUTED};
  font-size: 0.85rem;
  line-height: 1.45;
  margin: 0;
}}

.em-analogy {{
  background: {WASH};
  border-radius: 10px;
  padding: 1.1rem 1.25rem;
}}
.em-analogy .t {{
  color: {ACCENT};
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
}}
.em-analogy p {{
  color: {FG};
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
  white-space: pre-line;
}}

.em-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.75rem 0 1.25rem 0;
}}
.em-chip {{
  background: {WASH};
  color: {WASH_LINK};
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
}}

.em-cta a {{
  display: inline-block;
  background: {FG};
  color: {WHITE} !important;
  text-decoration: none !important;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 0.7rem 1.25rem;
  border-radius: 10px;
}}
.em-cta a:hover {{
  opacity: 0.9;
}}

.em-paper {{
  background: {WHITE};
  border: 1px solid {RULE};
  border-radius: 12px;
  padding: 1.2rem 1.35rem;
  margin-bottom: 0.75rem;
}}
.em-paper h3 {{
  color: {FG};
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  line-height: 1.4;
}}
.em-paper .meta {{
  color: {MUTED};
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}}

.em-why {{
  background: {WHITE};
  border: 1px solid {RULE};
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}}
.em-why h3 {{
  color: {FG};
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}}
.em-why p {{
  color: {MUTED};
  font-size: 0.95rem;
  line-height: 1.55;
  margin: 0;
}}

.em-footer {{
  color: {MUTED};
  font-size: 0.8rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid {RULE};
}}

/* Architecture diagram */
.em-arch {{
  margin: 1rem 0 1.5rem 0;
}}
.em-lane {{
  background: {WHITE};
  border: 1px solid {RULE};
  border-radius: 12px;
  padding: 1.25rem 1.35rem;
  margin-bottom: 1rem;
}}
.em-lane.em-lane-bg {{
  background: {BG};
  border-style: dashed;
}}
.em-lane-tag {{
  color: {ACCENT};
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}}
.em-lane-title {{
  color: {FG};
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}}
.em-lane-cap {{
  color: {MUTED};
  font-size: 0.85rem;
  margin-bottom: 1rem;
}}
.em-flow {{
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: 0.5rem;
}}
.em-flow-step {{
  flex: 1 1 140px;
  min-width: 120px;
  border-radius: 10px;
  padding: 0.9rem 0.85rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.6rem;
  border: 1px solid {RULE};
  background: {WHITE};
}}
.em-flow-step.dark {{
  background: {FG};
  border-color: {FG};
}}
.em-flow-step .owner {{
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: {ACCENT};
}}
.em-flow-step.dark .owner {{
  color: rgba(255,255,255,0.55);
}}
.em-flow-step .title {{
  font-size: 0.9rem;
  font-weight: 600;
  color: {FG};
  margin: 0.2rem 0;
}}
.em-flow-step.dark .title {{
  color: {WHITE};
}}
.em-flow-step .body {{
  font-size: 0.75rem;
  line-height: 1.4;
  color: {MUTED};
  margin: 0;
}}
.em-flow-step.dark .body {{
  color: rgba(255,255,255,0.65);
}}
.em-flow-step .time {{
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  color: {ACCENT};
  background: {WASH};
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  align-self: flex-start;
}}
.em-flow-step.dark .time {{
  color: {WHITE};
  background: rgba(255,255,255,0.12);
}}
.em-arrow {{
  display: flex;
  align-items: center;
  color: {ACCENT};
  font-weight: 700;
  font-size: 1.1rem;
  flex: 0 0 auto;
}}
.em-chains {{
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}}
.em-chain {{
  flex: 1 1 280px;
}}
.em-chain-title {{
  font-size: 0.9rem;
  font-weight: 600;
  color: {FG};
  margin: 0 0 0.15rem 0;
}}
.em-chain-sub {{
  font-size: 0.75rem;
  color: {MUTED};
  margin-bottom: 0.75rem;
}}
.em-legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: {MUTED};
}}
.em-legend-item {{
  display: flex;
  align-items: center;
  gap: 0.4rem;
}}
.em-swatch {{
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid {RULE};
  display: inline-block;
}}
.em-swatch.dark {{ background: {FG}; border-color: {FG}; }}
.em-swatch.mine {{ background: {WHITE}; }}
.em-swatch.bg {{ background: {BG}; border-style: dashed; }}
</style>
""",
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=600, show_spinner=False)
def latest_commits() -> list[dict]:
    """Siste commits fra det offentlige repoet (cachet 10 min)."""
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/commits?per_page=4",
            timeout=8,
            headers={"Accept": "application/vnd.github+json"},
        )
        r.raise_for_status()
        return [
            {
                "sha": c["sha"][:7],
                "msg": (c["commit"]["message"].splitlines() or [""])[0][:64],
                "date": c["commit"]["author"]["date"][:10],
            }
            for c in r.json()
        ]
    except Exception:
        return []


def sidebar() -> None:
    """Felles sidebar på alle sider (navigasjon + live-status)."""
    with st.sidebar:
        st.markdown("## Explaining Markets")
        st.caption(
            "Presentert av [Kevin Dennis Mazali](https://github.com/kdm-kev-NTNU) · Q4 2026"
        )
        st.page_link("app.py", label="Konkurransen")
        st.page_link("pages/1_agent.py", label="Agenten")
        st.page_link("pages/2_forskning.py", label="Forskning")
        st.divider()
        st.markdown("**Live-status**")
        commits = latest_commits()
        if commits:
            st.success("Agenten er deployet på Modal")
            st.markdown(
                f"Siste commit: [`{commits[0]['sha']}`]({REPO_URL}/commit/{commits[0]['sha']}) "
                f"({commits[0]['date']})"
            )
            st.caption(commits[0]["msg"])
        else:
            st.info("Agenten er deployet på Modal.")
        st.divider()
        st.markdown(
            f"[explainingmarkets.ai](https://explainingmarkets.ai/) · "
            f"[Repo]({REPO_URL})"
        )


def hero(
    eyebrow: str,
    title: str,
    subtitle: str,
    metrics: list[tuple[str, str]] | None = None,
) -> None:
    """Mørk hero-blokk med valgfrie nøkkeltall."""
    metrics_html = ""
    if metrics:
        pills = "".join(
            f'<div class="em-hero-metric"><div class="v">{v}</div>'
            f'<div class="l">{l}</div></div>'
            for l, v in metrics
        )
        metrics_html = f'<div class="em-hero-metrics">{pills}</div>'
    st.markdown(
        f"""
<div class="em-hero">
  <div class="em-eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
  {metrics_html}
</div>
""",
        unsafe_allow_html=True,
    )


def section_heading(title: str, subtitle: str | None = None, label: str | None = None) -> None:
    """Seksjonstittel + valgfri undertekst."""
    lab = f'<div class="em-label">{label}</div>' if label else ""
    sub = f'<p class="em-section-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'{lab}<div class="em-section-title">{title}</div>{sub}',
        unsafe_allow_html=True,
    )


def step_cards(steps: list[tuple[str, str, str]]) -> None:
    """Rad med stegkort: (nummer, tittel, brødtekst)."""
    cols = st.columns(len(steps))
    for col, (num, title, body) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
<div class="em-card">
  <div class="em-num">{num}</div>
  <h3>{title}</h3>
  <p>{body}</p>
</div>
""",
                unsafe_allow_html=True,
            )


def stat_cards(items: list[tuple[str, str]]) -> None:
    """Rad med tallkort: (verdi, etikett)."""
    cols = st.columns(len(items))
    for col, (value, label) in zip(cols, items):
        with col:
            st.markdown(
                f"""
<div class="em-stat">
  <div class="v">{value}</div>
  <div class="l">{label}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def clock_cards(items: list[tuple[str, str, str]]) -> None:
    """Mørke klokkekort: (verdi, etikett, detalj)."""
    cols = st.columns(len(items))
    for col, (value, label, detail) in zip(cols, items):
        with col:
            st.markdown(
                f"""
<div class="em-clock">
  <div class="v">{value}</div>
  <div class="l">{label}</div>
  <div class="d">{detail}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def rule_cards(items: list[tuple[str, str]]) -> None:
    """Spilleregelkort: (tittel, brødtekst)."""
    cols = st.columns(len(items))
    for col, (title, body) in zip(cols, items):
        with col:
            st.markdown(
                f"""
<div class="em-rule">
  <h3>{title}</h3>
  <p>{body}</p>
</div>
""",
                unsafe_allow_html=True,
            )


def tech_chips(labels: list[str]) -> None:
    """Teknologi-chips for rekruttererseksjonen."""
    chips = "".join(f'<span class="em-chip">{l}</span>' for l in labels)
    st.markdown(f'<div class="em-chips">{chips}</div>', unsafe_allow_html=True)


def cta(label: str, url: str) -> None:
    """Primær call-to-action-knapp."""
    st.markdown(
        f'<div class="em-cta"><a href="{url}" target="_blank">{label}</a></div>',
        unsafe_allow_html=True,
    )


def deep_dive(label: str = "For de spesielt interesserte"):
    """Wrapper rundt st.expander for teknisk dybde."""
    return st.expander(label)


def footer() -> None:
    st.markdown(
        f"""
<div class="em-footer">
  Bygget av <a href="https://github.com/kdm-kev-NTNU">Kevin Dennis Mazali</a>
  · kode: <a href="{REPO_URL}">{REPO}</a>
  · ingen hemmeligheter i denne appen; alt innhold er offentlige kilder.
</div>
""",
        unsafe_allow_html=True,
    )


def paper_card(title: str, meta: str) -> None:
    """Kort for ett research-paper (tittel + metadata)."""
    st.markdown(
        f"""
<div class="em-paper">
  <h3>{title}</h3>
  <div class="meta">{meta}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _flow_step(owner: str, title: str, body: str, time: str | None = None, dark: bool = False) -> str:
    cls = "em-flow-step dark" if dark else "em-flow-step"
    time_html = f'<span class="time">{time}</span>' if time else ""
    return f"""
<div class="{cls}">
  <div>
    <div class="owner">{owner}</div>
    <div class="title">{title}</div>
    <p class="body">{body}</p>
  </div>
  {time_html}
</div>
"""


def architecture_diagram() -> None:
    """To-baners arkitekturdiagram: live-flyt + bakgrunnsløkker."""
    live_steps = [
        ("Konkurransen", "Selskap rapporterer", "Plattformen sender et signert varsel til agenten.", "0 s", True),
        ("Min agent", "Mottak", "Sjekker at varselet er ekte og svarer «mottatt».", "under 20 s", False),
        ("Min agent", "Hent data", "Rapport, forhåndsanalyse og opsjonsmarkedets «værmelding».", "sekunder", False),
        ("Min agent", "AI-vurdering", "GPT rangerer aksjen fra 0 (fall) til 1 (hopp). Reserve: enkel opsjonsregel.", "under 5 min", False),
        ("Konkurransen", "Poeng", "Rangeringen sendes inn og sammenlignes med fasit.", "neste børsdag", True),
    ]
    flow_parts: list[str] = []
    for i, (owner, title, body, time, dark) in enumerate(live_steps):
        flow_parts.append(_flow_step(owner, title, body, time, dark))
        if i < len(live_steps) - 1:
            flow_parts.append('<div class="em-arrow">→</div>')

    deploy = [
        ("GitHub", "Ny kode", "Endringen pushes til repoet."),
        ("pytest", "Tester", "Må være grønne, ellers stopper alt."),
        ("Modal", "Live", "Ny versjon av Mottak og AI-vurdering."),
    ]
    learn = [
        ("Cron-jobb", "Skann arXiv", "Søker etter ny forskning."),
        ("LLM-filter", "Sorter", "Beholder bare det som kan gi poeng."),
        ("FORSKNING.md", "Idébank", "Neste forbedring av AI-vurderingen."),
    ]

    def chain_html(label: str, sub: str, steps: list[tuple[str, str, str]]) -> str:
        parts: list[str] = []
        for i, (owner, title, body) in enumerate(steps):
            parts.append(_flow_step(owner, title, body))
            if i < len(steps) - 1:
                parts.append('<div class="em-arrow">→</div>')
        return f"""
<div class="em-chain">
  <div class="em-chain-title">{label}</div>
  <div class="em-chain-sub">{sub}</div>
  <div class="em-flow">{''.join(parts)}</div>
</div>
"""

    st.markdown(
        f"""
<div class="em-arch">
  <div class="em-lane">
    <div class="em-lane-tag">Live · hver rapport</div>
    <div class="em-lane-title">Når et selskap legger frem tall</div>
    <div class="em-lane-cap">Fem steg, helt automatisk. Agenten har fem minutter fra varselet kommer til rangeringen er sendt inn.</div>
    <div class="em-flow">{''.join(flow_parts)}</div>
  </div>
  <div class="em-lane em-lane-bg">
    <div class="em-lane-tag">I bakgrunnen</div>
    <div class="em-lane-title">Slik holdes agenten oppdatert</div>
    <div class="em-lane-cap">To separate løkker som ikke påvirker en pågående prediksjon.</div>
    <div class="em-chains">
      {chain_html("Utrulling", "Ved hver kodeendring", deploy)}
      {chain_html("Læring", "Hver fredag kl. 09:15", learn)}
    </div>
  </div>
  <div class="em-legend">
    <div class="em-legend-item"><span class="em-swatch dark"></span> Konkurransens plattform</div>
    <div class="em-legend-item"><span class="em-swatch mine"></span> Min kode</div>
    <div class="em-legend-item"><span class="em-swatch bg"></span> Skjer i bakgrunnen</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
