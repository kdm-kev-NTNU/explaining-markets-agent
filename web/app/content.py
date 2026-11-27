"""Statisk innhold for presentasjonssiden.

Ene eier av alle tekster og tall. Ingen HTML her, malene eier presentasjonen.
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
    subtitle="Markedet gjetter på forhånd. Agenten prøver å se det markedet overså.",
    metrics=(
        Metric("Konkurranseperiode", "12. okt til 15. des"),
        Metric("Status", "Live"),
        Metric("Forskningsartikler lest", "21+"),
    ),
)

HOME_STEPS = (
    Step("01", "Et selskap legger frem tall", "Kvartalsrapporten kommer ut."),
    Step(
        "02",
        "Agenten tipper plasseringen",
        "For eksempel: «Denne aksjen havner blant de 20 % beste reaksjonene dette kvartalet.»",
    ),
    Step("03", "Fasit neste dag", "Børsen viser hvem som traff best."),
)

HOME_WHY_LEAD = "Markedet vet allerede at kursen kan svinge mye."
HOME_WHY_BODY = (
    "Tenk på en værmelding. Alle vet at det kan bli storm. "
    "Poengene får du bare for å se noe værmeldingen ikke så."
)

HOME_RULES = (
    Rule("Alltid svar", "Et forsiktig svar er bedre enn ingen."),
    Rule(
        "Bare plasseringen teller",
        "Det handler om hvor aksjen havner blant de andre, ikke hvor mye den stiger.",
    ),
    Rule("Å si «midt på» hver gang gir null", "Du må tørre å skille selskapene fra hverandre."),
)

HOME_CHART = (
    ChartBar("Bare overraskelsen", 0.099),
    ChartBar("AI leser investormøtet", 0.231),
    ChartBar("AI + analyse på forhånd", 0.312),
)
HOME_CHART_CAPTION = (
    "Hvor stor del av kursbevegelsen som blir forklart. "
    "Kilde: arrangørens måling av 546 rapporter, Q3 2026."
)

HOME_TECH_CHIPS = ("Python", "Modal", "FastAPI", "Railway", "LLM", "Webhooks", "pytest", "Cron")

HOME_DEEP_DIVE_FORMULAS = (
    "y = α + β₁ · predicted_percentile + β₂ · surprise_pct",
    "ΔR² = R²(full) − R²(surprise-only)",
)

HOME_DEEP_DIVE = (
    (
        "Hva måles?",
        "Utfallet er aksjens avkastning dagen etter rapporten, justert for resten av "
        "markedet (car1). Alle selskapene i kvartalet rangeres fra 0 (dårligst) til 1 "
        "(best). Scoren er ΔR²: hvor mye mer av variasjonen agenten forklarer enn "
        "overraskelsen i tallene alene. Å svare 0,5 hver gang gir nøyaktig null.",
    ),
    (
        "Hvorfor live?",
        "Tester på gamle data lekker lett fasit inn i modellen (look-ahead bias). "
        "Mønstre i markedet forsvinner også når mange bruker dem. Den ærlige testen er "
        "å spå i sanntid. Arrangørens arbeidsartikkel viser at gode systemer mer enn "
        "dobler forklart variasjon, fra ca. 8 % til nær 20 %.",
    ),
    (
        "Optiver-dataene.",
        "For likvide aksjer får agenten opsjonsmarkedets forventning før rapporten: "
        "forventet svingning, forventet størrelse på bevegelsen og 25-delta skew. "
        "Agentens jobb er å finne det som ikke allerede ligger i disse tallene, "
        "som ny guidance og nytt innhold fra investormøtet.",
    ),
)

AGENT_CLOCKS = (
    Clock("20 s", "Si fra med en gang", "Bekreft at varselet er mottatt."),
    Clock("5 min", "Lever svaret", "Les, tenk og send inn plasseringen."),
)

LIVE_FLOW = (
    FlowStep("Konkurransen", "Varsel kommer", "Et selskap har rapportert.", "0 s", True),
    FlowStep("Min agent", "Sjekk og bekreft", "Er varselet ekte?", "under 20 s"),
    FlowStep("Min agent", "Hent data", "Rapport, analyse og opsjonsdata.", "sekunder"),
    FlowStep("Min agent", "AI vurderer", "Plasserer aksjen og sender svar.", "under 5 min"),
    FlowStep("Konkurransen", "Poeng", "Svaret sammenlignes med fasit.", "neste børsdag", True),
)

DEPLOY_CHAIN = (
    ChainStep("GitHub", "Ny kode", "Endringen lastes opp."),
    ChainStep("pytest", "Tester", "Må bli grønne."),
    ChainStep("Modal", "Live", "Ny versjon kjører."),
)

LEARN_CHAIN = (
    ChainStep("Cron-jobb", "Søk", "Ny forskning på arXiv."),
    ChainStep("LLM-filter", "Sorter", "Beholder det nyttige."),
    ChainStep("queue.yaml", "Idébank", "Ideer venter på test."),
)

AGENT_DEEP_DIVE = (
    (
        "Signaldesign.",
        "Benchmarken fanger allerede selve overraskelsen i tallene. Agenten ser derfor "
        "etter det den ikke fanger: guidance sammenlignet med tidligere kvartaler, hva "
        "ledelsen sier om fremtiden i investormøtet, 25-delta skew som hint om retning, "
        "og hvor resultatet lander mot analytikernes bull/base/bear-scenarier.",
    ),
    (
        "Mottak.",
        "Varselet er signert, så agenten sjekker signaturen først. Den svarer «mottatt» "
        "med en gang og jobber videre etterpå. Bare den første gyldige prediksjonen per "
        "rapport teller.",
    ),
    (
        "Reserveplan.",
        "Er materialet tynt, brukes en egen gren for manglende data. Er AI-tjenesten "
        "nede, brukes en enkel regel basert på opsjonsmarkedet. 0,5 sendes bare som "
        "aller siste utvei.",
    ),
    (
        "Drift.",
        "Agenten kjører serverløst på Modal. Ny kode går gjennom git pull, pytest og "
        "modal deploy. Forskningssøket kjører som en ukentlig cron-jobb. Denne siden er "
        "FastAPI på Railway.",
    ),
)

NAV = (
    ("/", "Konkurransen"),
    ("/agent", "Agenten"),
    ("/forskning", "Forskning"),
)
