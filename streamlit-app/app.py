"""Explaining Markets · presentasjonsnettside (Streamlit).

Hjem-side: konkurransen, tallene fra arbeidsartikkelen, vår deltakelse.
Andre sider: pages/1_agent.py (arkitektur + scoring), pages/2_forskning.py.
Kjør lokalt:  streamlit run app.py  (fra denne mappen)
"""
import streamlit as st
import pandas as pd
import requests

REPO = "kdm-kev-NTNU/explaining-markets-agent"
REPO_URL = f"https://github.com/{REPO}"

st.set_page_config(
    page_title="Explaining Markets · AI-agenten",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(ttl=600, show_spinner=False)
def latest_commits() -> list[dict]:
    """Siste commits fra det offentlige repoet (GitHub API, cachet 10 min)."""
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


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Explaining Markets")
    st.caption("Presentert av [Kevin Dennis Mazali](https://github.com/kdm-kev-NTNU) · Q4 2026")
    st.page_link("app.py", label="🏠 Konkurransen")
    st.page_link("pages/1_agent.py", label="🤖 Agenten")
    st.page_link("pages/2_forskning.py", label="🔬 Forskning")
    st.divider()
    st.markdown("**Live-status**")
    commits = latest_commits()
    if commits:
        st.success("Agenten er deployet på Modal ✅")
        st.markdown(
            f"Siste commit: [`{commits[0]['sha']}`]({REPO_URL}/commit/{commits[0]['sha']}) "
            f"({commits[0]['date']})"
        )
        st.caption(commits[0]["msg"])
    else:
        st.info("Agenten er deployet på Modal (deploy-logg: em_deploy_state.json).")
    st.divider()
    st.markdown(
        f"[🌐 explainingmarkets.ai](https://explainingmarkets.ai/) · "
        f"[💻 Repo]({REPO_URL})"
    )

# ── Hjem ───────────────────────────────────────────────────────────────────
st.title("Explaining Markets — en AI-agent i live-konkurranse")
st.markdown(
    "Kvartalsvis, **live out-of-sample benchmark** for AI-systemer som forklarer "
    "aksjeavkastning rundt earnings, arrangert av **Ralph Koijen & Bradford Levy "
    "(University of Chicago Booth) i samarbeid med Optiver**. Deltakelsen: en "
    "autonom webhook-agent bygget av [Kevin Dennis Mazali]"
    "(https://github.com/kdm-kev-NTNU), deployet på Modal."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Q4 2026-vindu", "12. okt – 15. des", "scoring pågår nå")
c2.metric("Målingen", "ΔR²", "utover earnings-surprise")
c3.metric("Agentstatus", "Live på Modal", "webhook + 5-min prediksjon")
c4.metric("Kuraterte papers", "21+", "ukentlig arXiv-scan")

st.divider()

st.header("Spørsmålet agenten svarer på")
st.markdown(
    "> Etter en earningsmelding: **hvor lander denne aksjens neste-dags "
    "markedsjusterte avkastning i kvartalets tverrsnitt** — fra 0 (mest negative) "
    "til 1 (mest positive)?"
)
st.markdown(
    "Ett event gir ett utfall: `car1` (neste-dags kumulativ avviksavkastning), "
    "percentilrangert på tvers av alle earnings i kvartalet. Scoren er "
    "**ΔR² — forklart variasjon utover earnings-surprise-benchmarken**. En konstant "
    "0,5-prediksjon scorer nøyaktig null: det er kun *rangeringsinformasjon* som teller."
)

st.header("Hvorfor en live benchmark?")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        "**Look-ahead bias.** Historiske backtester trenes på data som inkluderer "
        "utfallet — informasjon man ikke hadde i beslutningsøyeblikket. Konkurransen "
        "håndhever et *knowledge cutoff* per event."
    )
with col_b:
    st.markdown(
        "**Refleksivitet.** Markeder er refleksive: når AI-adopsjon skalerer, "
        "eroderer mønsterne modellene ble trent på. Den ene ærlige testen er "
        "prediksjon i sanntid mot realiserte utfall."
    )
st.markdown(
    "Arbeidsartikkelen (*Assessing the Benefits of Optimized Agentic AI Systems "
    "for Asset Pricing*): de beste optimaliserte systemene **mer enn dobler "
    "forklart variasjon — R² ca. 8 % → nær 20 %**."
)

st.header("Tallene fra arrangørens Q3-måling")
st.markdown(
    "546 Q3-2026-events. Nye i Q4: hvert event bærer en **earnings preview** "
    "(agentic research skrevet *før* call-et) og **optionsmarkedsdata**."
)
chart_df = pd.DataFrame(
    {
        "Oppsett": ["Surprise alene", "Call facts alene", "Call facts + preview"],
        "R²": [0.099, 0.231, 0.312],
    }
).set_index("Oppsett")
st.bar_chart(chart_df, height=320)
st.caption(
    "Kilde: arrangørens blogg «earnings-previews» (29. sep 2026). Preview flytter "
    "mest, og innsats (reasoning effort) betyr noe *først med* preview. Beste måling: "
    "GPT-6 Astra xhigh > 0,30."
)

st.header("Optiver-overflaten — hva markedet allerede har priset inn")
st.markdown(
    "Før et selskap rapporterer tall, priser optionsmarkedet inn markedets "
    "samlede forventning til kvantehoppet. For de mest handlede selskapene "
    "leverer konkurransen tre slike tall, målt **rett før release**:"
)
opt_df = pd.DataFrame(
    {
        "Statistikk": ["Implied earnings vol", "Implied absolute move", "25-delta skew"],
        "Hva den forteller": [
            "Hvor usikkert markedet er om utfallet — spredningen options priser inn",
            "Hvor stor bevegelse markedet priser inn — retningsløs: ±X %, ikke opp eller ned",
            "Om nedsidebeskyttelse er dyrere enn oppsidsspill — negativ skew = markedet frykter fall",
        ],
    }
)
st.table(opt_df)
st.markdown(
    "**Hvorfor det betyr noe:** Se for deg at optionsmarkedet har priset inn "
    "«±8 % bevegelse» på et selskap før tallene kommer. Da vet alle allerede at "
    "bevegelsen blir stor — en prediksjon som bare sier «det kommer et stort "
    "kvantehopp» gir null forklaringskraft, uansett hvor riktig den er.\n\n"
    "Poenget er å lese av *hva markedet forventer* (disse tre tallene), og så "
    "forklare hvor utfallet ender **i forhold til den forventningen**: svakere "
    "eller sterkere enn priset inn — og hvorfor. Overraskende guidance, nytt "
    "innhold fra call-et, eller signaler optionsmarkedet ikke fanget opp. "
    "Forklaringskraften som står igjen når det alle allerede vet er tatt høyde "
    "for, er nøyaktig det ΔR² belønner."
)

st.divider()
st.caption(
    "Bygget av [Kevin Dennis Mazali](https://github.com/kdm-kev-NTNU) · "
    f"kode: [{REPO}]({REPO_URL}) · "
    "ingen hemmeligheter i denne appen — alt innhold er offentlige kilder."
)
