# FORSKNING — Explaining Markets: kuratert research for systemforbedring

> Vedlikeholdes ukentlig av explaining-markets-research-cron (fredag 09:15).
> Hvert paper er filtrert mot scoring-mekanikken i ../NOTES.md: ΔR² over
> surprise-benchmarken; kalibrering scorees ikke, kun rangeringsinformasjon.

## Ukentlige funn

### Uke 2026-W46 (13. nov 2026)

Collect OK: 6 nye arXiv-papers, 0 feilede søk. 3 beholdt, 3 forkastet.
Ukens viktigste treff er det første paperet vi har funnet som gir et *direkte*
ΔR²-håndtak: heterogen og konveks surprise-følsomhet, altså en ikke-lineær
bruk av surprise som benchmarken (lineær β₂) ikke fanger. De to andre er
metodiske: én overførbar ICL-idé (referanseklasse i prompten) og én
kvantitativ måling av hvor mye tekst-look-ahead blåser opp arkivtall.
Web-sjekk: bloggen uendret (29. sep), GitHub-org uendret på 6 repos — men
commit-historikken i `examples` ga to nye scoring-detaljer (se
«Plattform-endringer» 2026-11-13).

**Huge If True: Learning from the Size of the Surprise**
Graeber, Roth, Sammon & Schesch, 2026-11-11 · https://arxiv.org/abs/2611.15747 · econ.GN
Modellerer at reaksjonen på en earnings-surprise går via en ukjent multiplikator
λ som mapper earnings-tall til verdi (r ≈ λ·s). Investorene lærer om både nyheten
og λ fra **samme tall**: store surprises kan signalisere lav λ og små høy λ.
Større usikkerhet om λ demper gjennomsnittsfølsomheten, men gjør den *brattere
nær null-surprise*. Bekreftet i incentivert eksperiment (prosesseringsbegrensninger
senker snittfølsomhet, hever den nær null) og i ekte earnings-announcements:
aksjer med høy verdsettelsesusikkerhet (deres proxy for λ-usikkerhet) reagerer
mindre i snitt, men brattere nær null. **Bruk (3c, ny kø 13):** benchmarken
fatter surprise som én lineær β₂ over hele tverrsnittet. Er λ heterogen og
fallende i verdsettelsesusikkerhet, er E[car1|s] ikke-lineær — og en ikke-lineær,
monoton transform av surprise kan gi ΔR² > 0 selv om surprise selv ligger i
benchmarken (ΔR² måles mot den *lineære* surprise-regressoren). Konkret: la
prediksjonen komprimere surprise-percentilen i halene og ekspandere den nær
midten for selskaper med høy verdsettelsesusikkerhet u, med omvendt (nærmest
lineær) behandling for lav u. u må approksimeres fra det vi får: opsjonsstats
(høy `implied_earnings_volatility` relativt til `implied_absolute_earnings_move`),
og preview-felt (multipler/verdsettelsesdiskusjon, «hvor mye er priset inn»,
analytikerspredning i konsensustabellen). Ekstraksjonssteget (kø 5) bør hente
verdsettelsesusikkerhet som eget tallfelt, ikke som narrativ. Forbehold:
λ-modellen er formulert på announcement-dagsavkastning = samme målvariabel som
car1 (god match), men 546 arkiv-events er lite for en interaksjonskoeffisient —
kjør som arkiv-ablasjon etter kø 12-formatet (frosset plan) før den rører live.

**Tabular Foundation Models in Financial Predictions**
deHaan & Huang, 2026-11-10 · https://arxiv.org/abs/2611.13550 · cs.LG, q-fin.CP, q-fin.ST
Teknisk note som introduserer tabular foundation models (TFM) i regnskapsforskning:
Google Research' TabFM gir numeriske prediksjoner via **in-context learning** uten
trening eller tuning, og er mer nøyaktig enn både en finstilt open-weight-LLM fra
nyere regnskapsforskning og flere trebaserte modeller — på oppgaven «prediker
selskapets earnings-endring neste år». Viktig designpoeng: TFM-ene er forhåndstrent
på **syntetiske** tabulardata og unngår dermed look-ahead-bias fra å memorere
selskapenes utfall. **Bruk (3c, ny kø 14):** to overførbare ting. (1) Selve
ICL-mekanikken trenger ikke en TFM: gi prediksjonskallet et lite sett historiske
referanseeventer (features + realisert car1-percentil) og be modellen *interpolere
i referanseklassen* i stedet for å resonnere fritt om selskapet — samme «les av
naboene»-operasjon som tabellmodellen gjør, og den flytter rangeringsarbeidet fra
selskapsminne til leverte data (jf. kø 10). (2) Argumentet om syntetiske
treningsdata er et alternativ til identitetsmaskering når vi skal måle hvor mye av
ΔR² som er memorering: en modell som aldri har sett selskapets utfall kan ikke
lekke det. Forbehold: (a) målvariabelen er neste års earnings-endring, ikke
car1 — designevidens, ikke metode; (b) vi har ikke TabFM i 5-min-vinduet, kun
prinsippet; (c) referanse-rader må være vintage-begrenset (neste paper) og små
(5–15 rader) for ikke å sprenge tegnbudsjettet i prompten.

**Point-in-Time Encoders for Earnings Calls**
Brini, 2026-11-10 · https://arxiv.org/abs/2611.14325 · cs.CL, cs.IR, q-fin.ST
(IEEE BigData 2026-workshop; kode: github.com/Alessiobrini/point-in-time-encoders-for-earnings-calls)
Trener «vintage»-encodere på 412 248 calls med årlige cutoffs 2010–2024, der hver
vintage bare har lest tekst datert ≤ cutoff — kur mot look-ahead-bias i backtester.
33,8M-parameters encodere trent på calls alene slår de generelle retrieverne de
testet i hvert testkvartal, og vektorene **hever rangkorrelasjonen mellom neste
dags avkastning og prognoser bygget på tidligere avkastning + selskapsstørrelse
med ca. 50 %**. Men konklusjonen er todelt: 2024-vintagen prognoserer
earnings-surprises bedre (intervallet inkluderer null på calls ingen vintage leste),
og **avkastning «no better» — point-in-time vintages betyr mest for retrieval og
lite for avkastningsprognoser**. **Bruk (3b, forsterker kø 12):** (i) dette er den
første kvantitative målingen vi har av hvor mye tekst-look-ahead blåser opp en
arkiv-backtest, og den sier at oppblåsningen er stor for retrieval-/
surprise-prognoser men liten for avkastning. For vår 3b: ΔR² fra arkivkjøringer
er ikke systematisk oppblåst av at gpt-6-astra leste tekst etter cutoff — men
*alle tekstforbedringer vi måler i arkivet* skal leses som retrieval-gevinst, ikke
som avkastningsgevinst. (ii) Det setter et tak på hva bedre tekst-encoding/
retrieval kan gi oss: tekst hjelper mest der benchmarken allerede står (surprise) —
samme advarsel som Efe/OLIVIA, nå med tall. (iii) Praktisk hygiene hvis vi en gang
bruker embeddings/retrieval i 3c: indeksen må være vintage-begrenset til
`knowledge_cutoff`, ellers måler vi i arkivet noe vi ikke kan gjenta live.

(Forkastet: 2611.17072 «Reasoning Supervision and Capability Retention in LoRA
Domain Adaptation» — LoRA-SFT på finansdata; vi finjusterer ikke, og
«behold generalisering under SFT» har ingen prompt-tids motstykke vi kan
handtere. 2611.14421 «Earlybird» — streaming-ASR med 29M parametere; call facts
kommer levert som tekst, vi har ingen ASR-pipeline. 2611.09232 «RAG-Enhanced LLMs
for Interactive Explainability in Clinical Decision Support» — klinisk
XAI/grensesnitt, ingen vei til avkastningsrangering.)

### Uke 2026-W45 (6. nov 2026)

Collect OK: 7 nye arXiv-papers, 0 feilede søk. 3 beholdt, 4 forkastet.
(Merk: ingen W44-oppføring i denne fila — forrige oppdatering er 23. okt;
cron-kjøringen 30. okt har ikke skrevet til dokumentet. Ukens `state.json`
har derimot alle 7 persistert, så dedup-setet er intakt — kun
dokumentasjonen har et hull.)

Ukens treff er metodiske snarere enn signalmessige: to av tre papers er
*negative* resultater om hvor mye tekst- og identitetsinformasjon egentlig
tilfører utover offentlig selskapsinformasjon — som er nøyaktig vår
ΔR²-definisjon. Det viktigste nye arbeidspunktet er en identitets-ablation
(kø 10): vi har hele tiden antatt at rangeringsinfo kommer fra materials,
men vet ikke hvor mye som kommer fra modellens minne om tickeren.

**Thinking Fast, Trading Late: System One Decision Models vs the Market** (OLIVIA-protokollen)
Dehkordi, Kargarzadeh, Khaledian, Parvini, Ghatak & Khaledian, 2026-11-02 ·
https://arxiv.org/abs/2611.03985 · cs.AI, cs.CL, cs.LG, q-fin.ST
Foreslår OLIVIA, en protokoll som skal drepe tre gratis-lunsjer i
avkastningsprediksjon med LLM: point-in-time-input med **maskerte
selskapsnavn**, seleksjon kun på valideringsdata, analyseplan fryst med
kryptografisk hash, og én avblinding av testperioden via logget lås. Anvendt
på nyhetslesing for S&P 500: en finstilt modell holdt IC 0,055/0,065 i to
valideringskvartaler, men falt til 0,020 (t = 1,7) i den blindede
jan–jul-2026-testen; kommersielle modeller treffer nattbevegelsen fram til
åpning (IC 0,074–0,077), men ikke bevegelsen etter åpning. To funn treffer
oss direkte: (i) **maskering skjuler navn, ikke selskaper** — kommersielle
modeller identifiserer det maskerte selskapet i 62–74 % av tilfellene mot en
28 %-baseline. Det er samme mekanisme som Khetan & Balasubramanian
(«Thin Evidence, Thick Priors», kø 6) og restatering-papiret under: modellen
leser seg til hvem det er og henter et narrativ fra treningen. (ii) Ingen
modell klarte å skille over- fra underreaksjon, og ingen pre-registrert
strategi overlevde kostnader + deflated Sharpe — et nyttig tak på
forventningene til rene nyhetssignaler. **Bruk:** kø 10 (identitets-ablation
i 3b/3c) og 3b-valideringshygiene (frys analyseplan før arkivkjøring, ikke
etter). Forbehold: nyhetsstrøm før åpning ≠ våre post-call-materials, så
«priced at the open»-funnet rammer ikke car1 direkte — det rammer
eventuelle eksterne nyhetssignaler vi måtte vurdere i kø 2/4.

**Do Earnings Calls Help Predict Financial Restatements? Evaluating Text Beyond Public Firm Information**
Efe, Sapra & Ahmed, 2026-10-31 · https://arxiv.org/abs/2611.01123 · cs.CL, cs.LG
109 call-transkript før restateringer mot 218 matchede kontroller: call-teksten
predikerer restateringer bedre enn sjanse, men gir **ingen påvisbar
rangeringsgevinst utover offentlig selskapsinformasjon** (en modell med kun
offentlig info scorer marginalt høyere; 95 %-intervallet for tekstens bidrag
er −0,05 til 0,11 AUROC). Klassifikatoren vinner hovedsakelig på
SPAC-relaterte restateringer — altså en artefakt av utvalget, ikke et språklig
varselsignal. LLM-en scorer høyere, men navngir eksakt ticker i **66 % av
maskerte transkript**, og modellen er lansert etter at restateringene skjedde.
**Bruk:** dette er den reneste demonstrasjonen av testen vi bør kjøre før vi
adopterer en ny tekstfeature (kø 5): (1) bygg en offentlig-info-baseline
først, (2) mål inkrementell rangeringsevne mot den, (3) sjekk om modellen
egentlig bare kjenner selskapet. Forventningen vår om at «unik call-tekst»
(OT-papiret, kø 4) bærer inkrementell kraft står, men listen for hva som
teller som bevis heves. Forbehold: restatering ≠ avkastningsreaksjon, og
n = 109 er lite.

**LENS: Reliability-Aware Stock Prediction via LLM-Extracted Priors and News-Driven Semantic Graphs**
Zhou, Ma & Costa Sperb, 2026-11-03 · https://arxiv.org/abs/2611.04217 · cs.LG (CIKM 2026)
GNN-rammeverk som gjør **pålitelighet til et førsteklasses signal**: statiske
LLM-utledede selskapsrelasjoner aggregeres over flere kjøringer med
konfidensvekting, slik at lav-konsistente kanter nedvektes; den dynamiske
nyhetsgrafen temporal-aggregeres med eksponentiell decay for å håndtere
**ujevn dekning**; en kontekstavhengig gated fusion rebalanserer de to
grafene per aksje per dag. +16,4 % AR@5 / +22,6 % SR@5 mot sterkeste baseline
på S&P 500, med ablationsstudie og menneskevalidering av utvalgte relasjoner.
**Bruk (3c):** selve arkitekturen er ikke transplanterbar til vårt
5-minutters LLM-kall, men to prinsipper er det: (a) *agreement-vekting* —
kjør den kritiske felt-ekstraksjonen to ganger og la uenighet mellom kjøringene
senke vekten/flagge feltet i stedet for å bruke det rått (Khaybullina viste
51–96 % numerisk nøyaktighet; dette er den billigste måten å fange de feilene);
(b) *ujevn dekning som eksplisitt gating* — events uten preview/option-stats
(<50 %) skal ha en egen, navngitt gren, ikke bare mangle tekst i prompten
(forsterker kø 6). Latens-forbehold: to ekstraksjonskall à 120 s passer i
5-min-vinduet, men bare så vidt — kjør dem parallelt, eller bruk den billige
modellen til den andre lesingen.

(Forkastet: 2611.06989 «The Two-Ledger Model» — kostnadsregnskap for
multi-agent-systemer, ingen kobling til avkastningsrangering; 2611.05611
«Hybrid Spark» — spekulativ dekoding/serving-latens, påvirker ikke
rangeringsinformasjon (og vi styrer ikke serveringen hos OpenAI); 2611.05515
«TSFM Meets LLM» — tekst som kovariater i tidsserieprognoser, men vårt utfall
er én dags tverrsnittsreaksjon, ikke en numerisk serie å predikere; 2611.03993
crowdfunding-algoritmeaudit — demografi/reputasjon, feil litteratur.)

### Uke 2026-W43 (23. okt 2026)

Collect OK: 8 nye arXiv-papers, 0 feilede søk (state.json verifisert: alle 8
persistert med last_seen 2026-10-23; sete vokst 28 → 36 seen-papers). 2
beholdt, 6 forkastet. Web-sjekk: bloggen uendret (siste fortsatt
«earnings-previews», 29. sep) og ingen nye modell-benchmarks — men
GitHub-orgen har 6 repos: model-card-skill nyoppdaget for oss (se
«Plattform-endringer» 2026-10-23 og ny kø 9).

**From SEC Filings to Financial Signals: Evaluating LLMs on Stock Market Reactions and Analyst Forecasts**
Wang, Ji, Wang, Mansi, Lu & Chen, 2026-10-16 · https://arxiv.org/abs/2610.24268 · cs.AI
Evaluerer prompted zero-shot-output fra 13 generelle og finans-spesialiserte
LLM-er på 45 964 Form 10-Q-filingeventer (2001–2024), med MD&A-tekst koblet
mot tverrsnitts-rangeringer av fundamentaltall, pre-filing-analystestimater
og realiserte abnormale avkastninger — samme målvariabel-familie som vår
car1. Funn: direkte LLM-forecast ligger i snitt på 43,4-persentilen i
analystfordelingen og slår ikke enkeltanalytikere konsistent; konsensus-
ankring hever gjennomsnittlig inside-range-andel fra 41,1 % til 59,5 %, men
øker EPS-feilen. For oss: (i) direkte «prognotiser avkastningen»-prompting
er underlegen strukturert ekstraksjon; (ii) konsensus-ankrede outputs
rekoderer nettopp det surprise-benchmarken allerede har — ΔR²-verdiløs.
Bruk (3c, forsterker kø 4+5): ekstrahér avviks-felt (hva i facts/preview
avviker fra forventet), aldri nivåer; aldri be om direkte prognose.
Forbehold: 10-Q MD&A er ikke earnings-call facts — designevidens, ikke
metode.

**Same Probabilities, Different Advice: Gain-Loss Framing Effects in High-Stakes LLM Decision Support**
Zhang, Cui, Zhu, Lu, Guo & Han, 2026-10-21 · https://arxiv.org/abs/2610.29294 · cs.AI, cs.CL
FrameBench-HPS: 2 880 prompts fra 240 høyinnsats-scenarioer (helse, finans,
utdanning/karriere, juridisk) over sju LLM-er. Gain-loss-ramming av samme
sannsynlighet skifter anbefalingskategori i 32,4 % av komplette grupper
(mest usikkerhetsskifter, ikke reversaler), holder under parafraser og
overstiger vanlig generasjonsvariasjon; sannsynlyskanonialisering reduserer
effekten betydelig. Previewen mizer allerede gain-/loss-rammer (bull
+6–11 % vs bear −8–13 %). Bruk (3c, mate kø 5): kanoniser retningen i
ekstraksjonsspørsmålene — elisiter alltid P(opp) i samme ramme, eller begge
retninger og forlikt deterministisk, før percentile-mapping; billig
prompt-hygiene mot rangeringsstøy. Forbehold: ikke earnings-spesifikt —
robusthetshygiene, ikke signalkilde.

(Forkastet: 2610.31012 «Artificial Wisdom»-rammeverk — beslutningsregulering,
ikke avkastning; 2610.28787 kartell-RL — prisagent-kollusjon; 2610.24520
HABIT-Bench — agent-minne; 2610.22980 KiranaBench — butikksimulering;
2610.26887 Navalia — post-trening av cowork-agenter på syntetiske
finansoppgaver, ingen vei til vår tekst+stats-prediksjon; 2610.28653
SciTaste — forskningsdomme-benchmark.)

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

> **Status 2026-11-13 — anbefalt rekkefølge for live-vinduet (til 15. des):**
> 1 (blokkerende, parser) → 9 (model card, hard frist) → **13 (surprise-konveksitet,
> ukens nye — høyest forventet ΔR² per innsats)** → 2/3 (opsjon + scenario) →
> 10/12 (3b-ablasjoner, ingen live-risiko) → 14 (referanseklasse i prompten).
> Kø 4–8, 11 er prompt-hygiene som allerede er delvis implementert; ikke rør
> SYSTEM_PROMPT mer enn én endring av gangen nå som vi er midt i scoring.

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
   *Tillegg 2026-10-23 (Wang et al. 2610.24268): direkte zero-shot-
   prognoser lander i snitt på 43,4-persentilen av analystfordelingen og
   slår ikke enkeltanalytikere konsistent; konsensus-ankring øker
   inside-rate (41,1 → 59,5 %) men øker EPS-feil — rekoderer altså
   konsensusinformasjon benchmarken allerede har. Ekstrahér avviks-felt,
   ikke nivåer.*
   *Tillegg 2026-10-23 (Zhang et al. 2610.29294): kanoniser
   sannsynlighetretningen i promptene — gain/loss-ramming skifter
   anbefalingskategori i 32,4 % av grupper; spør alltid i samme retning
   (eller begge + deterministisk forlikning) før percentile-mapping.*
   *Tillegg 2026-11-06 (Efe et al. 2611.01123): før en ny tekstfeature
   adopteres, kjør tre trinn — offentlig-info-baseline, inkrementell
   rangeringsevne mot den, og masked-identity-sjekk. Call-tekst ga
   −0,05 til 0,11 AUROC utover offentlig info i restateringsutvalget,
   og LLM-en navnga ticker i 66 % av maskerte transkript.*
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
9. **Model card — prize-eligibility (F1/F4; ikke ΔR², men hard krav-frist)**:
   arrangørens `model-card-skill` (github.com/explaining-markets/
   model-card-skill) skriver konkurransens standardkort (`em-model-card
   v1`) fra submissionskoden. Kjør skillen i mappen med agent-koden
   (default: IP-beskyttet nivå), valider med `validate_card.py`, lim inn
   i portalen (Public Profile → Model card → Preview → Publish).
   Kortet er public ved publisering og må holdes oppdatert ved
   materielle metodeendringer (Official Rules §3). Frist: Q4-slutt
   15. des. (Plattform-funn 2026-10-23.)
10. **Identitets-ablation (3b/3c)**: vi vet ikke hvor mye av ΔR² som kommer fra
   materials og hvor mye som kommer fra modellens minne om tickeren. Kjør
   arkiv-events på nytt med ticker/selskapsnavn erstattet av en anonym kode
   (preview og facts inneholder navnet — erstatt det også, eller sammenlign
   en variant hvor modellen instrueres til å ikke bruke selskapskunnskap og
   begrunne kun fra de leverte feltene). Faller ΔR² kraftig, er mye av poenget
   vårt «identity prior» — som er lovlig (kun knowledge_cutoff gjelder) men
   sårbart for reflektivitet, og som bør nedvektes der materials er rike.
   (OLIVIA 2611.03985 + Efe 2611.01123, 6. nov.) Ingen kodelås — dette er
   en 3b-analyse som kan kjøres mot arkivet uten å røre live-agenten.
11. **Agreement-vektet felt-ekstraksjon (3c)**: kjør den kritiske
   ekstraksjonen to ganger (parallelt, eller modell 2 = billig modell) og
   nedvekt/flagg felt der kjøringene er uenige, i stedet for å bruke rå
   enkeltlesing. Billigste motmiddel mot 51–96 % numerisk nøyaktighet i
   felt-uttrekk (Khaybullina) og samme prinsipp som LENS' konfidensvekting.
   Latensvakt: to kall à 120 s ligger nær 5-min-grensen — mål faktisk
   veggklokke i live-events før dette slås på for alle events; vurder
   kun for events med rik preview. (LENS 2611.04217, 6. nov.)
12. **Valideringshygiene for 3b**: frys analyseplan (hvilke events, hvilke
   features, hvilken metrikk) før en arkivkjøring, ikke etter — OLIVIA viser
   hvor mye av «funnet» som fordamper når seleksjonen bare har lov å skje på
   valideringsdata. Praktisk: skriv ablasjonsplanen i kanban-kommentar først,
   kjør, rapporter uansett utfall.
   *Tillegg 2026-11-13 (Brini 2611.14325): vintage-encodere på 412 248 calls gir
   den første tallfestede kalibreringen av hvor mye tekst-look-ahead betyr —
   stor gevinst for retrieval og surprise-prognoser, «no better» for
   avkastningsprognoser. To konsekvenser: (a) ΔR² fra arkivkjøringer er ikke
   systematisk oppblåst, men enhver tekstforbedring målt i arkivet er en
   retrieval-gevinst til vi har vist noe annet; (b) bruker vi embeddings/
   retrieval i 3c, må indeksen være vintage-begrenset til `knowledge_cutoff`.*
13. **Surprise-konveksitet betinget på verdsettelsesusikkerhet (3c — høyest
   forventet ΔR² per innsats)**: benchmarken bruker surprise som én lineær β₂.
   Graeber et al. viser at reaksjonen går via en heterogen multiplikator λ
   (earnings → verdi) som er fallende i verdsettelsesusikkerhet: høy-usikkerhet
   reagerer mindre i snitt men brattere nær null. Implementer som en monoton,
   ikke-lineær transform *oppå* surprise-percentilen: komprimer halene og
   ekspander midten for høy-u-selskaper, nærmest lineært for lav-u. u hentes fra
   opsjonsstats (implied vol vs. implied abs move) og preview-felt (multipler,
   «priset inn», analytikerspredning) via kø 5-ekstraksjonen. Dette er lovlig
   ΔR² fordi residualen ligger i *formen* på surprise-relasjonen, ikke i
   surprise-nivået. Rekkefølge: (1) frosset arkiv-ablasjon etter kø 12-formatet,
   (2) bare hvis positiv: prompt-instruks i 3c. (Graeber/Roth/Sammon/Schesch
   2611.15747, 13. nov.)
14. **Referanseklasse i prompten (3c, ICL-prinsippet)**: gi prediksjonskallet
   5–15 historiske referanseeventer (surprise-pct, opsjonsstats, nøkkel-facts,
   realisert car1-pct) og instruer modellen til å *interpolere i referanseklassen*
   framfor å resonnere fritt om selskapet — samme operasjon en tabellmodell gjør
   med kontekst-rader. Flytter rangeringsarbeidet fra selskapsminne til leverte
   data (jf. kø 10) og gir samtidig en naturlig plassering i kvartalets fordeling.
   Krav: radene må være pre-cutoff (vintage-hygiene, kø 12), lite tegnbudsjett,
   og valg av referanse må være deterministisk (samme regel hver gang) — ellers
   blir det støy. (deHaan & Huang 2611.13550, 13. nov.)

## Plattform-endringer

- 2026-11-13 — ukentlig web-sjekk (web_search mot blogg/leaderboard; web_extract
  OK mot github.com, fortsatt kun søkesnutter mot explainingmarkets.ai):
  - **Blogg: ingen nye poster.** Fortsatt «New data for Q4 2026» (29. sep) —
    nå 6,5 uker gammel, midt i live-vinduet (12. okt–15. des). Søkesnuttene
    gjengir R²-tabellen uendret (surprise ~10 %; facts 21–23 %; «every model
    does clearly better» med preview; Astra xhigh >30 %; Luna 24 % medium →
    29 % max for under \$3/1000). **Ingen nye modell-benchmarks →
    OPENAI_MODEL=gpt-6-astra står.**
  - **GitHub-org: uendret, 6 repos** (starter-modal, examples,
    starter-railway, baseline-earnings-summary, .github, model-card-skill).
    examples sist pushet 10. okt (PR #7 `options-market-data`: notebook for
    opsjonsmarkedsdata + implied-move-rescaling-helper); starter-modal og
    starter-railway 30. sep; model-card-skill 21. sep. Ingen SDK-/materials-
    endringer som berører 2c/3c.
  - **Nye scoring-detaljer fra `examples`-commit-historikken (bradfordlynch,
    aug 2026 — ikke tidligere logget):** 4. aug «Gate scoring credit on the sign
    of the prediction coefficient», 5. aug «Drop the sign gate and floor a
    no-spread prediction regressor». Gjeldende offentlige scorer har altså
    **ingen fortegns-gate** — kreditten er ren ΔR² — og en prediksjon uten
    spredning er eksplisitt *flooret*, ikke bare implisitt null. Bekrefter
    NOTES §3.1–§3.2: kun monotone rangeringsforskjeller teller, fortegn/skala
    er likegyldig. Praktisk konsekvens for kø 13: en monoton transform av
    surprise-percentilen kan implementeres uten orienteringshensyn.
  - Leaderboard/hjemmeside: uendret struktur (2026Q4, own/common sample);
    «Q4 scoring runs October 12 through December 15» bekreftet på nytt.

- 2026-11-06 — ukentlig web-sjekk (web_search + web_extract mot GitHub OK;
  explainingmarkets.ai kun søkesnutter, substack-feed avvises av backend
  med CRAWL_UNEXPECTED_CONTENT_TYPE = XML):
  - **Blogg: ingen nye poster.** Fortsatt kun «New data for Q4 2026»
    (29. sep) — den er nå 5 uker gammel, og vi er midt i live-vinduet
    (12. okt–15. des). Ingen nye modell-benchmarks → **OPENAI_MODEL=
    gpt-6-astra står**. Søkesnuttene gjengir R²-tabellen uendret
    (Luna 0,218–0,222 uten preview / 0,245–0,288 med; Sol 0,208–0,223 /
    0,281–0,305; Astra 0,230–0,231 / 0,309–0,312; surprise alene 0,099),
    og formuleringen «Astra xhigh explains more than 30%» er bekreftet.
  - **GitHub-org: uendret, 6 repos.** examples sist pushet 10. okt;
    starter-modal, starter-railway og baseline-earnings-summary 29.–30. sep;
    model-card-skill 21. sep; .github 6. jul. Ingen SDK-/materials-endringer
    som berører 2c/3c denne uken.
  - **Nye kilder oppdaget i org-README (legges til overvåkingen):**
    nyhetsbrev på explainingmarkets.substack.com og X-konto
    @explainingmrkts — arrangøren sier at kvartalsresultater,
    SDK-releaser og kunngjøringer går der. Cron kan ikke lese
    Substack-feeden (XML avvises), så ved mistanke om ny post må Kevin
    hente fulltekst interaktivt; X er heller ikke lesbart herfra.
  - **Verifisert detalj:** org-README lenker arbeidsartikkelen til
    SSRN abstract_id **6474601** — samme papir som NOTES.md §1 omtaler,
    nå med direkte ID (nyttig for fulltekstlesing av
    metodeavsnittet/scoring-validering).
  - Presse-/tredjepartssøk ga ingen nye tekniske detaljer utover NOTES.md.

- 2026-10-23 — ukentlig web-sjekk (web_search; explainingmarkets.ai
  fortsatt kun søkesnutter i cron — GitHub fungerte via web_extract):
  - Blogg: ingen nye poster (siste fortsatt «earnings-previews»,
    29. sep). Hjemmesiden bekrefter Q4-scoring 12. okt–15. des — vi er
    inne i live-vinduet. Ingen nye modell-benchmarks → OPENAI_MODEL=
    gpt-6-astra står (R²-tabellen fra 13. okt gjelder fortsatt;
    søksnuttene viser Astra 0,312 xhigh med preview).
  - GitHub-org: 6 repos. Nyoppdaget for oss (opprettet 21. sep, oversett
    i tidligere søkesnutt-sjekker): **model-card-skill** — Agent Skill
    (Claude Code/Codex/Cursor/Gemini CLI/Copilot) som leser
    submissionskoden og fyller konkurransens standard model card-format
    (`em-model-card v1`: sammendrag + seksraders klassifiseringstabell
    + fem korte seksjoner) til `MODEL_CARD.md`; to IP-nivåer («Protect
    my IP» default — ingen prompts/modellversjoner/settings — vs
    «Showcase my work»); validator `validate_card.py` (Python 3.8+,
    ingen deps, `--json`), taxonomy.json versjonert med CHANGELOG.
    Submission krever publisert model card i portalen for
    prize-eligibility. Kø 9.
  - Ellers uendret: examples sist pushet 10. okt, starter-modal/
    starter-railway/baseline-earnings-summary 30. sep — ingen
    SDK-endringer som berører 2c/3c denne uken.
  - Leaderboard-sidene bruker kjente parametre (2026Q4, -CONTEST,
    own/common sample) — ingen strukturendringer utover NOTES.md.
    Presse (UChicago News + Booth Review) dekker arbeidsartikkelen
    uten nye tekniske detaljer.

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
- explainingmarkets.substack.com (arrangørens nyhetsbrev — kunngjøringer og
  kvartalsresultater; XML-feed, ikke lesbar fra cron) og X @explainingmrkts
- github.com/explaining-markets/* (SDK/starter-endringer)
