"""Side 2. Agenten: arkitektur, klokker, spilleregler. Teknisk dybde i expandere."""
import streamlit as st

from ui import (
    inject_css,
    sidebar,
    section_heading,
    clock_cards,
    rule_cards,
    architecture_diagram,
    deep_dive,
    footer,
)

st.set_page_config(
    page_title="Agenten · Explaining Markets",
    page_icon="🤖",
    layout="wide",
)

inject_css()
sidebar()

section_heading(
    "Fra webhook til prediksjon på fem minutter",
    "Når et selskap rapporterer, får agenten beskjed. "
    "Den svarer med en gang, tenker, og sender inn rangeringen.",
    label="Agenten",
)

section_heading(
    "Slik er agenten bygget",
    "Øverste rad skjer automatisk hver gang et selskap rapporterer. "
    "Nederste rad holder agenten oppdatert.",
)
architecture_diagram()

section_heading("To klokker")
clock_cards(
    [
        (
            "20 s",
            "Svar med en gang",
            "Bekreft at meldingen er mottatt. Ellers prøver plattformen igjen.",
        ),
        (
            "5 min",
            "Prediksjonsvindu",
            "Les materialene, tenk, og send rangeringen før tiden går ut.",
        ),
    ]
)

st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

section_heading("Tre spilleregler")
rule_cards(
    [
        (
            "Alltid lever noe",
            "Hopper du over, får du din egen snitt-score. Bedre å sende en forsiktig gjetning.",
        ),
        (
            "Bare rekkefølge teller",
            "Å skalere tallene om hjelper ikke. Det er plasseringen i køen som scoreres.",
        ),
        (
            "Konstant = null poeng",
            "Å alltid si «midt på treet» gir nøyaktig null. Du må skille selskapene.",
        ),
    ]
)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

with deep_dive("For de spesielt interesserte: scoring-formel, signal-design og fallback"):
    st.markdown(
        "Ett event, ett utfall: `car1` percentilrangert til `y ∈ [0, 1]`, "
        "surprise rangert til `surprise_pct`. Regresjonen:"
    )
    st.latex(
        r"y = \alpha + \beta_1 \cdot \text{predicted\_percentile} + \beta_2 \cdot \text{surprise\_pct}"
    )
    st.latex(r"\Delta R^2 = R^2(\text{full}) - R^2(\text{surprise-only})")
    st.markdown(
        "ΔR² er leaderboard-metrikken. Affin remapping (`p → a + b·p`) endrer ikke scoren. "
        "Strategi: **ACK umiddelbart, prediker deretter.** Kun første gyldige prediksjon "
        "per event scores."
    )
    st.markdown(
        "**Signal-design.** Benchmarken priser allerede rå surprise. Vekten ligger på "
        "guidance vs tidligere bane, framoverskuende call-innhold, 25-delta skew som "
        "retningsvinkt, og scenario-plassering mot previewens bull/base/bear-grid."
    )
    st.markdown(
        "**Fallback.** Tynne materials får egen missing-data-gren. Når LLM er nede: "
        "deterministisk skew-fallback. Konstant 0,5 er kun siste leveringssti."
    )
    st.markdown(
        "**Drift.** Modal (serverless) · `git pull → pytest → modal deploy` · "
        "ukentlig research-cron."
    )

footer()
