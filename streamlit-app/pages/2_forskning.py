"""Side 3 — Forskning: ukentlig kuratert arXiv-scan, rendret fra repoet."""
import streamlit as st
import requests

REPO = "kdm-kev-NTNU/explaining-markets-agent"
RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main/research/FORSKNING.md"

st.set_page_config(page_title="Forskning · Explaining Markets", page_icon="🔬", layout="wide")

st.title("🔬 Ukentlig kuratert research")
st.markdown(
    "En cron-jobb kjører hver **fredag kl. 09:15**: seks arXiv-søk, dedup mot "
    "state, og et LLM-filter som vurderer hvert paper mot scoring-mekanikken "
    "(ΔR² over surprise-benchmarken; kalibrering scoret ikke). Det som holder, "
    "lander i `research/FORSKNING.md` i repoet — samme fil denne siden leser live."
)


@st.cache_data(ttl=600, show_spinner="Henter Forskning.md fra GitHub …")
def hent_forskning() -> str:
    r = requests.get(RAW_URL, timeout=12)
    r.raise_for_status()
    return r.text


try:
    tekst = hent_forskning()
    st.success(f"Live fra repoet · {len(tekst):,} tegn · cachet i 10 min")
    st.markdown(tekst)
except Exception:
    st.warning(
        "Kunne ikke hente research/FORSKNING.md fra GitHub akkurat nå. "
        f"Se filen direkte: [lenke](https://github.com/{REPO}/blob/main/research/FORSKNING.md)."
    )
