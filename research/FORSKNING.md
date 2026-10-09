# FORSKNING — Explaining Markets: kuratert research for systemforbedring

> Vedlikeholdes ukentlig av explaining-markets-research-cron (fredag 09:15).
> Hvert paper er filtrert mot scoring-mekanikken i ../NOTES.md: ΔR² over
> surprise-benchmarken; kalibrering scorees ikke, kun rangeringsinformasjon.

## Ukentlige funn

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
4. **Surprise-residualisering + novelty-/taler-vekting i 3c**: prompt-føring:
   fakta som gjenforteller overraskelsen er allerede i benchmarken (nedveies);
   unikt fremoverrettet call-innhold og analyst-/CFO-uttalelser oppveies.
   (OT-paperet + Sidhu et al., 9. okt.)
5. **Formålsnøytral to-trinns-ekstraksjon i 3c**: steg 1 ekstraherer strukturerte
   felt uten å nevne prediksjonsformålet; steg 2 mappere til percentile.
   Foretrekk direkte spørsmål fremfor konstrukt-ratings, særlig på den
   8000-tegns previewen. (NBER w35142 + SSRN 7177500, 9. okt.)
6. **Missing-data-grener**: eksplisitte fallback-regler når preview/opsjonsstats
   mangler (LLM-prior-advarsel fra Khetan & Balasubramanian, 8. okt).
7. **Preview-håndtering etter arrangørens eget mønster** (plattform-funn
   2026-10-08): baseline-repoet sender preview FØR call facts (Luna max effort)
   — gjør det samme i 3c-prompten, slik at trunkering treffer facts, ikke
   preview. Arkiv-caveat for 3b: arkiverte previews er attached etter faktum
   (ikke strengt point-in-time) — ikke overvurder preview-signalet i
   arkiv-backtests; valider heller mot live events.
8. *(følger fra ny research hver uke)*

## Plattform-endringer

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
