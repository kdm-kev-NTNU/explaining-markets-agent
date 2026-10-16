# FORSKNING — Explaining Markets: kuratert research for systemforbedring

> Vedlikeholdes ukentlig av explaining-markets-research-cron (fredag 09:15).
> Hvert paper er filtrert mot scoring-mekanikken i ../NOTES.md: ΔR² over
> surprise-benchmarken; kalibrering scorees ikke, kun rangeringsinformasjon.

## Ukentlige funn

### Uke 2026-W42 (16. okt 2026)

Collect OK: 7 nye arXiv-papers, 0 feilede søk (state.json verifisert: alle 7
persistert med last_seen 2026-10-16; sete 21 dedup-papers). 2 beholdt, 5
forkastet. Web-sjekk: ingen nye bloggposter (siste fortsatt «earnings-previews»,
29. sep) og GitHub-org uendret — men scoring.py-snutter bekrefter
ranking/tie-break-reglene, og en tredjepartsgjennomgang av arrangørens
NVDA-eksempel validerer scenario-mapping (kø 3). Detaljer under
«Plattform-endringer» 2026-10-16.

**Momentum, Commentary Tone, and Earnings Surprise in LLM Financial Forecasts**
Khaybullina, 2026-10-15 · https://arxiv.org/abs/2610.22043 · cs.LG, cs.AI, cs.CL, q-fin.GN
Syntetiske earnings-annonser der 20-dagers momentum, non-informational
kommentar-tone og EPS-beat-mot-manipulert konsensus varieres uavhengig; 2 016
prompts per modell over seks checkpoints fra fire familier (0,49–7,61B, lokalt
Q8_0). Funn: primær EPS-kontrakt spenner fra −0,19 til 86,80 prosentpoeng (én
modell reagerer knapt på selve overraskelsen), signert tone-kontrast skygger
over EPS i 5 av 6 modeller og momentum i 5 av 6; numerisk diagnostisk
nøyaktighet 51,0–95,8 %. Måler betingede answer-prefix-skårer — ikke
kalibrerte sannsynligheter, og etablerer ingen realisert
avkastningspredikerbarhet. Forbehold: små checkpoints (≤7,6B) — gpt-6-astra
kan oppføre seg annerledes. Bruk (3c, mate kø 4/5): la ikke tone drive
prediksjonen — ekstraher konkrete tallfelt (guidance-tall, scenarioplassering)
i stedet for tone-ratings; verifiser tallene i steg 1 av to-trinns-designen
slik at lesefeil ikke forveksles med rangeringsinformasjon. Momentum/posisjon
(previewens trading-setup) ligger utenfor benchmarken, men papiret gir ingen
evidens for at momentum predikerer car1 — aktuell som 3b-ablasjon, med
arkiv-forbeholdet i kø 7.

**When Does "Post-Call" Begin? An Availability Contract for Earnings-Call NLP Benchmarks**
Ma, Koa, Liu & Huang, 2026-10-15 · https://arxiv.org/abs/2610.21659 · q-fin.CP, cs.CL, cs.LG
Innfører en «Availability Contract» for earnings-call-benchmarks: oppgi
input-grense, bevis for input-tilgjengelighet, start på utfallsklokken og
hvilke claims beviset bærer; anvendt på 552 earnings calls fra 24 selskaper.
Funn: labels og tap avhenger vesentlig av deklarert utfallsklokke selv når
modellrangeringer ser stabile ut — within-event timing-mismatch overlever
kronologiske train–test-splits fordi den oppstår inne i enkeltevents, ikke
på tvers av utvalg. Bruk (3b-hygiene): eksplisitt tilgjengelighetskontrakt per
inputkilde i arkiv-backtester — facts = levert post-cutoff (lov som levert),
preview = «illustrative, not strictly point-in-time», arkiverte option-stats
= én sesjon gamle — så ablasjonstall ikke sammenlignes på tvers av ulike
tilgjengelighetsregimer (forsterker arkiv-forbeholdet i kø 7). Live-drift er
urørt: kun leverte materials er post-cutoff-lovlige, eget hentet materiale
må holde knowledge_cutoff.

(Forkastet: 2610.18435 LLM-peer-review i finans/regnskap — referee-arbeid,
ikke avkastningsprediksjon; 2610.18052 memory-unlearning i agenter —
agent-minne utenfor earnings; 2610.17856 MMTA tri-modal
tidsserie/visjon-benchmark — ingen implementasjonsvei for vår tekst+stats-
input; 2610.17214 density-matrix-RL — RL-teori; 2610.13432 EWC/mini-KFAC på
earnings-call-ASR — vi får call facts levert som tekst, ingen ASR-pipeline.)

### Uke 2026-W41 (9. okt 2026 — ukentlig cron: collect-timeout, web-kompensasjon)

Collect: 0 nye arXiv-papers (søket «earnings-reaksjon» timeoutet; setet står
på 21 dedup-papers). Kompensert med web-søk mot arXiv/SSRN/NBER: 23 kandidater
vurdert, 4 beholdt. Ingen nye bloggposter; nye plattform-detaljer funnet i
examples-repoet — se «Plattform-endringer» 2026-10-09.

**Measuring What is Repeated and Novel in Earnings Disclosures Using Optimal Transport**
Wu, Tao, Martineau, Grégoire & Veneris, 2026-10-02 · https://arxiv.org/abs/2610.04094 · cs.CE
Optimal transport deler 105 000 dokumentpar (pressemedling vs. konferansekall,
2008–2023) i aligned/unaligned innhold. Funn: det unike call-innholdet
(fremoverrettet info som ikke står i pressemedlingen) har substansiell
inkrementell forklaringskraft for announcement-dagsavkastningen, soft-
informasjonen slår earnings-surprise målt i Shapley-verdier, og markedet
overreagerer på gjentatt innhold mens det underreagerer på unikt call-innhold.
Bruk (3c): treffer residualiseringskravet vårt direkte — be modellen skille
fakta som gjenforteller overraskelsen (allerede i benchmarken → nedveies) fra
fremoverrettet nyinformasjon i call facts (oppveies). Kø-item 4.

**Which Voices Move Markets? Speaker Identity and the Cross-Section of Post-Earnings Returns**
Sidhu, Fan & Pishgar, 2026-04-14 · https://arxiv.org/abs/2604.13260 · q-fin.TR
FinBERT-sentiment over 16 428 S&P 500-calltranskript (2015–2025) med empirisk
utledede talervekter: analyst 49 %, CFO 30 %, exec 16 %. Gir OOS Spearman IC
0,142 og 2,03 % månedlig long-short-alpha uforklart av FF5 (t = 6,49),
signifikant etter kontroll for SUE, og subsumerer Loughran-McDonald
fullstendig (FinBERT t = 5,90 vs. LM t = 0,86). Bruk (3c): hvis call facts
inneholder Q&A-deriverte elementer, vektlegg analyst-/CFO-uttalelser høyere enn
forberedte exec-tekster. Kø-item 4.

**LLMs and Systematic Measurement Error**
Grieser, Cookson, Fathollahi & Venugopal, 2026-05-04 (SSRN-postet jul 2026) · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7177500
LLM-utledde mål har ikke-klassisk målefeil fra to distortions: utelatelse
(omission) og injeksjon (injection) — målene forsømmer meningsfull terminologi
og reshaper tone. Verst for konstrukt-ratings av lange dokumenter (10-K risk
factors), mildere på korte call-tekster, mest attenuert for direkte spørsmål.
Bruk (3b/3c): be ikke om holistisk «preview-sentiment 1–10» på den 8000-tegns
previewen — ekstraher direkte, konkrete felt (guidance-retning,
scenarioplassering, katalysatorstatus). Kø-item 5.

**Seeing the Goal, Missing the Truth: Human Accountability for AI Bias**
Cao, Jiang & Xu, NBER WP 35142, apr 2026 · https://www.nber.org/papers/w35142
Å avsløre nedstrømsbruken («dette skal predikere aksjeavkastning») i prompten
skifter LLM-mellommålene systematisk mot det avslørte målet — purpose-
conditioned bias med in-sample-overfitting før knowledge cutoff og ingen
fordel etter cutoff; prompt-regulering fjerner ikke effekten. Bruk
(3c-arkitektur): to-trinnsdesign — (1) formålsnøytral ekstraksjon av
strukturerte felt fra materials (ingen omtale av prediksjon/avkastning),
(2) separat mapping til percentile. Kø-item 5.

(Forkastet bl.a.: analyst-forecast-papirene 2511.15214 og manager-non-respons,
MM-FinEval-benchmarket 2609.38523, nyhets-«priced in»-corpuset 2608.14014,
LLM-embedding-alfa SSRN 6351439 (~546 arkivevents er for lite treningsgrunnlag
+ embedding-cutoff-lekkasje), AlphaAgents 2508.11152, lokale-LLM-evalueringen
SSRN 4627143, samt eldre oversikter.)

### Uke 2026-W41 (8. okt 2026 — etableringskjøring)

**SOTA: Stock Options Trading Agents Guided by Option-Implied Return Distributions**
Xie & Liu, 2026-10-07 · https://arxiv.org/abs/2610.10407 · cs.AI, q-fin.TR
LLM-agenter for opsjonshandel styrt av opsjonsimplisitte avkastningsfordelinger.
Relevans: vi får `option-implied-stats` (implied vol, abs move, 25-delta skew)
levert per event — dette paperet viser hvordan slike fordelinger kan guide
agent-beslutninger direkte. Bruk: la opsjonsstatistikken veie tyngre i
prediksjonsmodulen (3c), ikke bare som prompt-tekst.

**Thin Evidence, Thick Priors: How Language Models Substitute Identity for Missing Financial Facts**
Khetan & Balasubramanian, 2026-10-06 · https://arxiv.org/abs/2610.07798 · cs.AI
LLMer substituerer identitet/priorer når fakta mangler — målt over 96 600 prompts.
Relevans: advarsel for vår agent. Når materials er tynne (ingen preview, ingen
opsjonsstats — >50 % av events!), vil LLM-en falle tilbake på ticker-priorer.
Det kan være greit (fortsatt rangeringsinfo) men må bevisst designes:
håndter «missing data»-casen eksplisitt i prompten (3c).

(Se collect-utskrift 2026-10-08 for 19 ytterligere kandidater vurdert og
forkastet denne uken — utenfor earnings/abnormal-return/LLM-finans-kjernen.)

**Andre kjøring 8. okt 16:37:** 0 nye arXiv-papers (dedup mot etableringskjøringens
21). Ingen nye bloggposter; web-sjekken fant nye plattform-detaljer — notert
under «Plattform-endringer» 2026-10-08 (2) og ny kø-item 4.

## Implementeringskø (prioritert idébank)

1. **Parser-robusthet i 2c (blokkerende)**: `item.content` må akseptere vilkårlig
   JSON-type — option-implied-stats er et objekt, og examples-repoet hadde selv
   en schema-bug der en `str | list[str]`-annotasjon avviste HELE bundlen ved
   første stats-item. Feil her = missed events = common-sample-
   imputeringsstraff. (Plattform-funn 2026-10-09.)
2. **Opsjonsimplisitt veiing i 3c**: mappede signaler (skew-negativ → ned-justert
   percentile; implied abs move som konfidens-modulator) — se SOTA-paperet fra
   8. okt. Caveat 2026-10-09: previewen inneholder ofte implied move fra
   opsjoner allerede — unngå dobbelttelling for aksjer med likvide opsjoner.
3. **Scenario-mapping i 3c**: plasser realiserte call facts i previewens
   bull/base/bear-scenariogrid (Anthropic-skillen inkluderer forventet
   aksjereaksjon per scenario) og rangér etter scenarioplassering, ikke bare
   etter fakta alene. (Plattform-funn 2026-10-09.)
   *Status 2026-10-13: implementert som prompt-instruksjon (vekt-punkt 2);
   gjenstår: deterministisk grid-ekstraksjon + validering mot arkiv/live.*
   *Status 2026-10-16: tredjepartsgjennomgang (quantide.cn) av arrangørens
   eget NVDA-eksempel treffer metoden punkt for punkt — realiserte tall (rev
   $96B, guide $108B, DC $89B) falt i bull-rutene, og realisert +8,1 % landet
   innenfor bull-rangens estimerte +6 til +11 %; deterministisk
   grid-ekstraksjon gjenstår som arbeidspunkt.*
4. **Surprise-residualisering + novelty-/taler-vekting i 3c**: prompt-føring:
   fakta som gjenforteller overraskelsen er allerede i benchmarken (nedveies);
   unikt fremoverrettet call-innhold og analyst-/CFO-uttalelser oppveies.
   (OT-paperet + Sidhu et al., 9. okt.)
   *Tillegg 2026-10-16 (Khaybullina 2610.22043): vektlegg innhold med påvist
   alpha — men la ikke non-informational tone drive forecasten; tone-kontrast
   skygger over EPS i 5/6 modeller og er ingen signalvei for oss. Tallfelt >
   tone-ratings i ekstraksjonen.*
5. **Formålsnøytral to-trinns-ekstraksjon i 3c**: steg 1 ekstraherer strukturerte
   felt uten å nevne prediksjonsformålet; steg 2 mappere til percentile.
   Foretrekk direkte spørsmål fremfor konstrukt-ratings, særlig på den
   8000-tegns previewen. (NBER w35142 + SSRN 7177500, 9. okt.)
   *Tillegg 2026-10-16 (Khaybullina 2610.22043): steg 1 må hente konkrete
   tallfelt (guidance-tall, scenarioplassering) og verifisere dem mot
   kildeteksten — numerisk diagnostisk nøyaktighet er 51–96 %, og lesefeil i
   steg-2-innputten blir støy i rangeringen.*
6. **Missing-data-grener**: eksplisitte fallback-regler når preview/opsjonsstats
   mangler (LLM-prior-advarsel fra Khetan & Balasubramanian, 8. okt).
7. **Preview-håndtering etter arrangørens eget mønster** (plattform-funn
   2026-10-08): baseline-repoet sender preview FØR call facts (Luna max effort)
   — gjør det samme i 3c-prompten, slik at trunkering treffer facts, ikke
   preview. Arkiv-caveat for 3b: arkiverte previews er attached etter faktum
   (ikke strengt point-in-time) — ikke overvurder preview-signalet i
   arkiv-backtests; valider heller mot live events.
   *Status 2026-10-13: gjort — stats → preview → facts-rekkefølge + verdibasert
   seksjonskomprimering i predict.py; arkiv-caveat gjelder fortsatt for 3b.*
8. **Modell/innsats-valg (3c)**: bloggen viser reasoning-innsats betaler
   FØRST med preview (Luna medium 0,245 → max 0,288, <$3/1000).
   *Status 2026-10-13: delvis løst i commit c7c99b6 — OPENAI_MODEL=gpt-6-astra
   direkte mot OpenAI + adaptive completion-params (max_completion_tokens med
   fallback-former); bloggen viser Astra 0,309–0,312, så effort-parameter er
   margenal. Gjenstår: overvåk om LLM_MAX_TOKENS=3000 kapper resonneringen
   (tegn: hyppige «[WARN] Using option-stats fallback» i Modal-loggen).*
9. *(følger fra ny research hver uke)*

## Plattform-endringer

- 2026-10-16 — ukentlig web-sjekk (cron: web_extract er blokkert mot
  explainingmarkets.ai, søkesnutter kun):
  - Blogg: ingen nye poster (siste fortsatt «earnings-previews», 29. sep).
    Hjemmesiden bekrefter at Q4-scoring kjører 12. okt–15. des — vi er inne i
    live-vinduet. Ingen nye modell-benchmarks denne uken → OPENAI_MODEL=
    gpt-6-astra står (R²-tabellen fra 13. okt gjelder fortsatt).
  - GitHub: org uendret (examples, starter-modal, starter-railway,
    baseline-earnings-summary + offisielle baselines). scoring.py-snutter
    bekrefter ranking-reglene: primærmetrikk `delta_r_squared_imputed`
    (common-sample), første tie-break = høyest `n_obs` (timely coverage FØR
    imputering), deretter submission-id. Konsekvens: dekning teller dobbelt —
    imputeringsstraff OG tie-break — kø 1 (parser-robusthet) er dobbelt
    begrunnet som blokkerende.
  - Tredjeparts: quantide.cn gjennomgår arrangørens NVDA-eksempel
    (scenario-plassering → reaksjonsrange; «beat and retreat»: 4 strake
    beats på rev/EPS/guide, falt påfølgende dag hver gang, snitt ~4,8 %);
    noah-news dekker kun arbeidsartikkelen. Ingen nye tekniske detaljer
    utover NOTES.md.

- 2026-10-13 — fulltekstlesing av «earnings-previews»-bloggen (arrangørens
  egne R²-målinger, 546 Q3-2026-events, leaderboard-regresjonen; SE ≈ 0,034–0,036):
  - **R²-tabellen:** surprise alene 0,099. Call facts alene: Luna 0,218–0,222,
    Sol 0,208–0,223, Astra 0,230–0,231 — reasoning-innsats (medium/xhigh/max)
    flytter ingenting. MED preview: Luna 0,245/0,272/0,288, Sol 0,281/0,299/0,305,
    Astra 0,309/0,312 (medium/xhigh/max; Astra max ikke rapportert).
  - **Nøkkelinnsikt — interaksjon:** preview er verdt +0,02–0,09 R² avhengig av
    modell/innsats, og innsats betaler FØRST med preview. Kost/effekt-topp:
    billig modell på max innsats (Luna max 0,288 for $2,57 per 1000 events);
    Astra xhigh 0,312 for $126,93 = 49x pris for +0,024 (innenfor 1 SE).
  - **Handling 3c (implementert 2026-10-13):** SYSTEM_PROMPT oppgradert —
    scenario-plassering (kø 3), buy-side/whisper-bar, reaksjonshistorikk
    («beats repeatedly sold»-mønster). Preview-trunkering byttet fra head-cut
    (som kuttet scenario/trading-slutt for lange previews) til verdibasert
    seksjonskomprimering: consensus kappes først, scenario/katalysator/trading
    bevarer budsjettet. 28 tester grønne.
  - Arkiverte opsjonsstats er én sesjon eldre enn live-verdier (forbehold for
    3b-backtester).

- 2026-10-09 — ingen nye bloggposter (siste er fortsatt 29. sep: previews +
  opsjonsdata for Q4) og GitHub-org uendret (5 repos). Nye detaljer fra
  examples-repo-README:
  - **Previewen bygges med Anthropics offentlige «Earnings Preview Skill»**
    (github.com/anthropics/financial-services → earnings-reviewer/skills/
    earnings-preview): output = konsensus-estimater, rangert katalysator-
    checkliste, bull/base/bear-scenariotabell MED forventet aksjereaksjon,
    trading setup inkl. implied move fra opsjoner. Gir oss et ferdig
    scenario-raster å mappa facts mot (kø 3) — og betyr at preview delvis
    koder opsjonsinfo allerede (caveat i kø 2).
  - **Parser-advarsel**: et items `content` må ta vilkårlig JSON-type
    (stats-itemen er et objekt); examples-repoets egen `DisclosureItem`-
    annotasjon avviste hele bundlen inntil denne releasen. Kø 1.
  - Nytt hjelpemodul i examples: `option_stats` (`option_implied_stats_from_
    disclosure`, `statistic_value`) — ingen option-stats-notebook enda; lev
    mot live arkiv.
- 2026-10-08: Q4-materials bekreftet i docs: earnings preview (Claude,
  pre-cutoff) + option-implied-stats på events med likvide opsjoner. Blogg:
  GPT-6 Astra >30 % R² med preview. Starter-repo: starter-modal (Modal),
  starter-railway. Eksempler-repo har offentlig scoring-transform
  (src/examples/scoring.py) — verbatim port av produksjonsscoreren.
- 2026-10-08 (2) — detaljer fra earnings-previews-posten + repos (andre kjøring):
  - Examples-repo: ny notebook `03_earnings_previews.ipynb` — preview-itemet vs
    call vs faktisk markedsreaksjon. Les i 3a/3b.
  - Baseline (baseline-earnings-summary): preview sendes til modellen FØR call
    facts; GPT-6 Luna kjører på max effort → arrangøren behandler preview som
    høyverdi-input.
  - Preview-dekning Q3 2026: 542/546 contest-events (~99 %) hadde preview;
    itemet forblir valgfritt (TEST-events har aldri) — behold fallback.
  - Arkiv-forbehold: previews finnes bare delvis i Q3-arkivet, attached etter
    faktum (skrevet før release, men ikke alltid før knowledge cutoff) →
    «illustrative, not strictly point-in-time». Preview inngår i alle
    submissions fra 3. okt 2026; nye events er skrevet før cutoff.

## Kilder overvåket

- arXiv: earnings announcement/return, earnings calls, option-implied,
  PEAD, LLM-finans, abnormal return prediction (6 søk, 21-dagers vindu)
- explainingmarkets.ai/blog (via ukentlig web-sjekk i agent-turnen)
- github.com/explaining-markets/* (SDK/starter-endringer)
