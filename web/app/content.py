"""Statisk innhold for presentasjonssiden.

Ene eier av alle tekster og tall. Ingen HTML her — malene eier presentasjonen.
"""

from __future__ import annotations

from dataclasses import dataclass


REPO = "kdm-kev-NTNU/explaining-markets-agent"
REPO_URL = f"https://github.com/{REPO}"
FORSKNING_RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main/research/FORSKNING.md"
FORSKNING_BLOB_URL = f"https://github.com/{REPO}/blob/main/research/FORSKNING.md"
QUEUE_RAW_URL = f"https://raw.githubusercontent.com/{REPO}/main/research/queue.yaml"
QUEUE_BLOB_URL = f"https://github.com/{REPO}/blob/main/research/queue.yaml"
COMPETITION_URL = "https://explainingmarkets.ai/"


@dataclass(frozen=True)
class Metric:
    label: str
    value: str


@dataclass(frozen=True)
class Step:
    number: str
    title: str
    body: str


@dataclass(frozen=True)
class Clock:
    value: str
    label: str
    detail: str


@dataclass(frozen=True)
class Rule:
    title: str
    body: str


@dataclass(frozen=True)
class ChartBar:
    label: str
    value: float  # R², e.g. 0.099


@dataclass(frozen=True)
class FlowStep:
    owner: str
    title: str
    body: str
    time: str | None = None
    dark: bool = False


@dataclass(frozen=True)
class ChainStep:
    owner: str
    title: str
    body: str


@dataclass(frozen=True)
class Hero:
    eyebrow: str
    title: str
    subtitle: str
    metrics: tuple[Metric, ...]


HOME_HERO = Hero(
    eyebrow="Live AI-agent  ·  Q4 2026  ·  Chicago Booth × Optiver",
    title="Kan en AI forutsi hvordan en aksje reagerer på kvartalstall?",
    subtitle=(
        "Markedet gjetter på forhånd. Agenten min prøver å se det markedet overså "
        "— og rangerer utfallet før børsen åpner neste dag."
    ),
    metrics=(
        Metric("Scoringvindu", "12. okt – 15. des"),
        Metric("Status", "Live på Modal"),
        Metric("Kuraterte papers", "21+"),
    ),
)

HOME_STEPS = (
    Step(
        "01",
        "Selskapet legger frem tall",
        "Kvartalsrapporten er klar. Markedet har allerede gjettet hvor stor "
        "bevegelsen blir — som en værmelding.",
    ),
    Step(
        "02",
        "Agenten rangerer utfallet",
        "Innen fem minutter plasserer den aksjen i en kø fra største fall (0) "
        "til største hopp (1).",
    ),
    Step(
        "03",
        "Fasit dagen etter",
        "Neste børsdag avslører hvor aksjen faktisk endte. Poeng gis bare hvis "
        "rangeringen var bedre enn «bare overraskelsen».",
    ),
)

HOME_WHY = (
    "Opsjonsmarkedet er værmeldingen: alle vet allerede at det kan bli storm. "
    "Å si «det blir stor bevegelse» gir null poeng. Agenten må forklare hvor aksjen "
    "lander i forhold til det markedet allerede priste inn."
)

HOME_ANALOGY_TITLE = "Analogien"
HOME_ANALOGY_BODY = "Værmelding = markedets gjetning\nAgent = det værmeldingen overså"

HOME_CHART = (
    ChartBar("Bare overraskelsen", 0.099),
    ChartBar("AI leser call-et", 0.231),
    ChartBar("AI + forhåndsanalyse", 0.312),
)
HOME_CHART_CAPTION = (
    "Kilde: arrangørens Q3-2026-måling (546 events). Tallene er R² — "
    "hvor mye av aksjebevegelsen som forklares."
)

HOME_TECH_CHIPS = ("Python", "Modal", "FastAPI", "Railway", "LLM", "Webhooks", "pytest", "Cron")

HOME_DEEP_DIVE = (
    (
        "Spørsmålet formelt.",
        "Etter en earningsmelding: hvor lander aksjens neste-dags markedsjusterte "
        "avkastning (car1) i kvartalets tverrsnitt, fra 0 (mest negativ) til 1 "
        "(mest positiv)? Scoren er ΔR² — forklart variasjon utover "
        "earnings-surprise-benchmarken. En konstant 0,5 scorer nøyaktig null.",
    ),
    (
        "Hvorfor live?",
        "Historiske backtester lekker utfall (look-ahead bias). Markeder er "
        "refleksive: når AI-adopsjon skalerer, eroderer mønstrene. Den ærlige "
        "testen er prediksjon i sanntid. Arbeidsartikkelen viser at optimaliserte "
        "systemer mer enn dobler forklart variasjon (R² ca. 8 % → nær 20 %).",
    ),
    (
        "Optiver-overflaten",
        "(før release, likvide navn): implied earnings vol, implied absolute move, "
        "25-delta skew. Det er markedets pre-release-fordeling. Agentens jobb er "
        "residualet: guidance, nytt call-innhold, divergens fra det options allerede priste.",
    ),
)

AGENT_CLOCKS = (
    Clock(
        "20 s",
        "Svar med en gang",
        "Bekreft at meldingen er mottatt. Ellers prøver plattformen igjen.",
    ),
    Clock(
        "5 min",
        "Prediksjonsvindu",
        "Les materialene, tenk, og send rangeringen før tiden går ut.",
    ),
)

AGENT_RULES = (
    Rule(
        "Alltid lever noe",
        "Hopper du over, får du din egen snitt-score. Bedre å sende en forsiktig gjetning.",
    ),
    Rule(
        "Bare rekkefølge teller",
        "Å skalere tallene om hjelper ikke. Det er plasseringen i køen som scoreres.",
    ),
    Rule(
        "Konstant = null poeng",
        "Å alltid si «midt på treet» gir nøyaktig null. Du må skille selskapene.",
    ),
)

LIVE_FLOW = (
    FlowStep(
        "Konkurransen",
        "Selskap rapporterer",
        "Plattformen sender et signert varsel til agenten.",
        "0 s",
        True,
    ),
    FlowStep(
        "Min agent",
        "Mottak",
        "Sjekker at varselet er ekte og svarer «mottatt».",
        "under 20 s",
    ),
    FlowStep(
        "Min agent",
        "Hent data",
        "Rapport, forhåndsanalyse og opsjonsmarkedets «værmelding».",
        "sekunder",
    ),
    FlowStep(
        "Min agent",
        "AI-vurdering",
        "GPT rangerer aksjen fra 0 (fall) til 1 (hopp). Reserve: enkel opsjonsregel.",
        "under 5 min",
    ),
    FlowStep(
        "Konkurransen",
        "Poeng",
        "Rangeringen sendes inn og sammenlignes med fasit.",
        "neste børsdag",
        True,
    ),
)

DEPLOY_CHAIN = (
    ChainStep("GitHub", "Ny kode", "Endringen pushes til repoet."),
    ChainStep("pytest", "Tester", "Må være grønne, ellers stopper alt."),
    ChainStep("Modal", "Live", "Ny versjon av Mottak og AI-vurdering."),
)

LEARN_CHAIN = (
    ChainStep("Cron-jobb", "Skann arXiv", "Søker etter ny forskning."),
    ChainStep("LLM-filter", "Sorter", "Beholder bare det som kan gi poeng."),
    ChainStep("FORSKNING.md + queue.yaml", "Idébank", "Prosa i FORSKNING; status og auto-PR i queue.yaml."),
)

AGENT_DEEP_DIVE_FORMULAS = (
    "y = α + β₁ · predicted_percentile + β₂ · surprise_pct",
    "ΔR² = R²(full) − R²(surprise-only)",
)

AGENT_DEEP_DIVE = (
    (
        "Scoring.",
        "ΔR² er leaderboard-metrikken. Affin remapping (p → a + b·p) endrer ikke "
        "scoren. Strategi: ACK umiddelbart, prediker deretter. Kun første gyldige "
        "prediksjon per event scores.",
    ),
    (
        "Signal-design.",
        "Benchmarken priser allerede rå surprise. Vekten ligger på guidance vs "
        "tidligere bane, framoverskuende call-innhold, 25-delta skew som "
        "retningsvinkt, og scenario-plassering mot previewens bull/base/bear-grid.",
    ),
    (
        "Fallback.",
        "Tynne materials får egen missing-data-gren. Når LLM er nede: "
        "deterministisk skew-fallback. Konstant 0,5 er kun siste leveringssti.",
    ),
    (
        "Drift.",
        "Modal (serverless) · git pull → pytest → modal deploy · "
        "ukentlig research-cron. Presentasjonssiden: FastAPI på Railway.",
    ),
)

NAV = (
    ("/", "Konkurransen"),
    ("/agent", "Agenten"),
    ("/forskning", "Forskning"),
)
