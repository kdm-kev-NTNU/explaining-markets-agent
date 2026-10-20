"""Side 2. Agenten: arkitektur, produksjonsklokker, scoring og signal-design."""
import streamlit as st

st.set_page_config(page_title="Agenten · Explaining Markets", page_icon="🤖", layout="wide")

st.title("🤖 Agenten: webhook → prediksjon på 5 minutter")
st.caption("Av Kevin Dennis Mazali · Python · Modal · signerte webhooks · LLM-analyse med deterministisk fallback")

st.markdown(
    """
```mermaid
flowchart LR
  A[Selskap rapporterer] --> B[Signert webhook fra plattformen]
  B --> C["ACK 200 (klokke 1: 20 s)"]
  C --> D[Hent materials fra information_url]
  D --> E[LLM-analyse: preview + call facts + option-overflate]
  E --> F["POST /v1/predictions (klokke 2: 5 min)"]
  F --> G[Scoring mot realisert car1: delta-R2 over surprise]
```
"""
)

st.header("To produksjonsklokker")
clocks = {
    "Klokke": ["Delivery ACK", "Prediksjonsvindu"],
    "Budsjett": ["20 sekunder", "5 minutter"],
    "Starter": ["plattformen POSTer", "du ACKer 200"],
    "Miss den og …": [
        "retry inntil 5 ganger over ~30 min; gjentatte feil deaktiverer webhook-en",
        "prediksjonen tagges «late» og droppes fra scoring",
    ],
}
st.table(clocks)
st.info(
    "Strategi: **ACK umiddelbart, prediker deretter.** Kun den *første* gyldige "
    "prediksjonen per event scoret; late, tidlige og dupliserte poster aksepteres "
    "men ignoreres i rangeringen."
)

st.header("Scoring-identiteten")
st.markdown("Ett event, ett utfall: `car1` percentilrangert til `y ∈ [0, 1]`, surprise rangert til `surprise_pct`. Regresjonen:")
st.latex(r"y = \alpha + \beta_1 \cdot \text{predicted\_percentile} + \beta_2 \cdot \text{surprise\_pct}")
st.latex(r"\Delta R^2 = R^2(\text{full}) - R^2(\text{surprise-only})")
st.markdown("ΔR² er leaderboard-metrikken: forklart variasjon **utover** det markedsallerede vet om overraskelsen.")

s1, s2, s3 = st.columns(3)
with s1:
    st.error("**Konstant ⇒ ΔR² = 0, nøyaktig.** Flat 0,5-baseline tjener ingenting; den er kun siste utvei slik at et missed event ikke imputeres mot deg.")
with s2:
    st.error("**Affin remapping er uscoret.** p → a + b·p endrer ikke ΔR². Kalibrering og fortegnshypping hjelper ikke: kun rangering.")
with s3:
    st.error("**Å hoppe over events straffes.** Missed events imputeres med din egen prediksjonsmiddel. Alltid lever noe i vinduet.")

st.header("Signal-design: hva vi vekter")
st.markdown(
    "Benchmarken priser allerede rå surprise, «beat/miss» gir null ΔR². Vekten "
    "ligger på det surprise *ikke* fanger:"
)
g1, g2 = st.columns(2)
with g1:
    st.markdown(
        "- **Guidance og utsikter** mot den tidligere banen\n"
        "- **Framoverskuende call-innhold**: nytt vs gjentatt disclosure\n"
        "- **Optionsposisjonering**: 25-delta skew som retningsvinkt, implied move som konfidensmodulator\n"
        "- **Scenario-plassering**: realiserte fakta mot previewens bull/base/bear-grid"
    )
with g2:
    st.markdown(
        "**Innebygde forbehold i prompt-stien:**\n"
        "- Ikke dobbelttell implied move når previewen allerede bærer option-størrelsen\n"
        "- Tynne materials (ingen preview/optionstatistikk, vanlig på illikvide navn) får egen missing-data-gren\n"
        "- Når LLM-en er utilgjengelig: deterministisk skew-fallback varierer fortsatt per event; konstant 0,5 er kun siste leveringssti"
    )

st.header("Drift og kvalitet")
d1, d2, d3 = st.columns(3)
d1.metric("Runtime", "Modal", "serverless, auto-skalert")
d2.metric("Deploymetode", "git pull → pytest → deploy", "grønne tester påkrevd")
d3.metric("Repo", "offentlig", "github.com/kdm-kev-NTNU/explaining-markets-agent")
st.markdown(
    "Deploy-kjeden er automatisert: `git pull --ff-only` → pytest (grønne tester "
    "påkrevd) → `modal deploy` → verifisering av health-endepunkt → oppdatert "
    "deploy-state. Ukentlig research-cron kuraterer arXiv-funn inn i repoet."
)
