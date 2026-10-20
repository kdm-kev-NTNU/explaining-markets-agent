"""Explaining Markets · presentasjonsnettside (Streamlit).

Hjem: lite tekst, enkle forklaringer, rekrutterervennlig.
Teknisk dybde ligger i expandere.
Kjør lokalt:  streamlit run app.py  (fra denne mappen)
"""
import streamlit as st
import pandas as pd

from ui import (
    REPO,
    REPO_URL,
    inject_css,
    sidebar,
    hero,
    section_heading,
    step_cards,
    tech_chips,
    cta,
    deep_dive,
    footer,
)

st.set_page_config(
    page_title="Explaining Markets · AI-agenten",
    page_icon="📈",
    layout="wide",
)

inject_css()
sidebar()

hero(
    eyebrow="Live AI-agent  ·  Q4 2026  ·  Chicago Booth × Optiver",
    title="Kan en AI forutsi hvordan en aksje reagerer på kvartalstall?",
    subtitle=(
        "Markedet gjetter på forhånd. Agenten min prøver å se det markedet overså "
        "— og rangerer utfallet før børsen åpner neste dag."
    ),
    metrics=[
        ("Scoringvindu", "12. okt – 15. des"),
        ("Status", "Live på Modal"),
        ("Kuraterte papers", "21+"),
    ],
)

section_heading("Slik fungerer det", "Tre steg. Ingen finansjargon nødvendig.")
step_cards(
    [
        (
            "01",
            "Selskapet legger frem tall",
            "Kvartalsrapporten er klar. Markedet har allerede gjettet hvor stor "
            "bevegelsen blir — som en værmelding.",
        ),
        (
            "02",
            "Agenten rangerer utfallet",
            "Innen fem minutter plasserer den aksjen i en kø fra største fall (0) "
            "til største hopp (1).",
        ),
        (
            "03",
            "Fasit dagen etter",
            "Neste børsdag avslører hvor aksjen faktisk endte. Poeng gis bare hvis "
            "rangeringen var bedre enn «bare overraskelsen».",
        ),
    ]
)

st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

section_heading("Hvorfor er dette vanskelig?")
col_a, col_b = st.columns([3, 2], gap="large")
with col_a:
    st.markdown(
        """
<div class="em-why">
  <p>Opsjonsmarkedet er værmeldingen: alle vet allerede at det kan bli storm.
  Å si «det blir stor bevegelse» gir null poeng. Agenten må forklare hvor aksjen
  lander <strong>i forhold til</strong> det markedet allerede priste inn.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        """
<div class="em-analogy">
  <div class="t">Analogien</div>
  <p>Værmelding = markedets gjetning
Agent = det værmeldingen overså</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

section_heading(
    "Hva fungerer best?",
    "Jo mer kontekst agenten får før og under call-et, jo mer forklarer den.",
)
chart_df = pd.DataFrame(
    {
        "Oppsett": [
            "Bare overraskelsen",
            "AI leser call-et",
            "AI + forhåndsanalyse",
        ],
        "Forklart variasjon": [0.099, 0.231, 0.312],
    }
).set_index("Oppsett")
st.bar_chart(chart_df, height=280)
st.caption(
    "Kilde: arrangørens Q3-2026-måling (546 events). Tallene er R² — "
    "hvor mye av aksjebevegelsen som forklares."
)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

section_heading(
    "Hva jeg bygde",
    "Kevin Dennis Mazali — autonom webhook-agent i live konkurranse.",
)
tech_chips(["Python", "Modal", "LLM", "Webhooks", "pytest", "Cron"])
cta("Se koden på GitHub →", REPO_URL)

with deep_dive("For de spesielt interesserte: scoring, look-ahead og Optiver-overflaten"):
    st.markdown(
        "**Spørsmålet formelt.** Etter en earningsmelding: hvor lander aksjens "
        "neste-dags markedsjusterte avkastning (`car1`) i kvartalets tverrsnitt, "
        "fra 0 (mest negativ) til 1 (mest positiv)? Scoren er **ΔR²** — forklart "
        "variasjon utover earnings-surprise-benchmarken. En konstant 0,5 scorer "
        "nøyaktig null."
    )
    st.markdown(
        "**Hvorfor live?** Historiske backtester lekker utfall (look-ahead bias). "
        "Markeder er refleksive: når AI-adopsjon skalerer, eroderer mønstrene. "
        "Den ærlige testen er prediksjon i sanntid. Arbeidsartikkelen viser at "
        "optimaliserte systemer mer enn dobler forklart variasjon (R² ca. 8 % → nær 20 %)."
    )
    st.markdown(
        "**Optiver-overflaten** (før release, likvide navn): implied earnings vol, "
        "implied absolute move, 25-delta skew. Det er markedets pre-release-fordeling. "
        "Agentens jobb er residualet: guidance, nytt call-innhold, divergens fra "
        "det options allerede priste."
    )
    st.markdown(
        f"Arrangør: [explainingmarkets.ai](https://explainingmarkets.ai/) · "
        f"repo: [{REPO}]({REPO_URL})"
    )

footer()
