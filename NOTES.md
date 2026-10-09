# NOTES — Explaining Markets: regler, API og scoring (fra offisielle kilder)

> Kilder: explainingmarkets.ai/docs (+ /docs/webhooks, FAQ), GitHub starter-modal
> (README, docs/advanced.md, predict.py, client.py, event_utils.py), GitHub
> examples (README, src/examples/scoring.py, data/README.md).
> Hentet 2026-10-08. Alle faktapåstander her er verifisert mot disse kildene.

## 1. Arrangør, arbeidsartikkel og setting

- **Konkurranse:** Explaining Markets — åpen, kvartalsvis benchmark for AI-systemer
  som forklarer aksjeavkastning rundt earnings (resultatmeldinger).
- **Arrangør:** Ralph S. J. Koijen & Bradford (Lynch) Levy, University of Chicago
  (Booth, CEPR, NBER), i samarbeid med Optiver.
- **Arbeidsartikkel:** «Assessing the Benefits of Optimized Agentic AI Systems for
  Asset Pricing». Kjerneidé: backtests på historiske data lider av look-ahead
  bias (modeller trent på alle data), og markeder er reflekstive (AI-adopsjon
  eroderer mønstrene). Løsning: real-time, out-of-sample benchmark. Beste
  optimaliserte systemer mer enn dobler forklart variasjon: R² ca. 8 % → nær 20 %.
- **Q4 2026-nyhet:** Events bærer nå en **earnings preview** (skrevet av Claude via
  Anthropic-agentic research FØR hvert earnings call) + **optionsmarkedsdata**.
  Blogginnlegget «earnings-previews» rapporterer at preview løfter alle GPT-6-modeller
  de testet, og at **GPT-6 Astra forklarer >30 % av variasjonen** med preview.
- **Kostnad:** Ingen entry-fee. Koijen & Levy brukte <\$10 totalt i artikkelen.
  IP: man beholder eierskap til agenten; model card (høynivåbeskrivelse) kreves
  for prizer, ikke kode. Publisering av metoder oppmuntres.

## 2. Hva agenten gjør (konkret kontrakt)

Event-flyt: selskap rapporterer → plattformen sender signert webhook → agenten
ACKer 200 → agenten henter materials fra `information_url` → agenten poster
prediksjon til `/v1/predictions` med `X-API-Key` → scores mot faktisk utfall.

### Verifisert webhook-payload (`event_utils.py`)
```json
{
  "id": "<matcher Webhook-Id; idempotency-nøkkel>",
  "event_id": "<uuid>",
  "event_type": "EARNINGS_RELEASE",        // eller "TEST"
  "timing_category": "SCHEDULED",
  "event_datetime": "2026-01-15T21:00:00Z",
  "focal_assets": [{"identifier_type": "TICKER", "identifier_value": "AAPL"}],
  "information_url": "https://...kortlevd signert URL...",
  "prediction_deadline": "2026-01-15T21:05:00Z"
}
```

### To klokker (starter-modal docs/advanced.md)
| Klokk | Budsjett | Starter | Overtredelse |
|---|---|---|---|
| Delivery ACK | 20 s | når platformen POSTer | retry opp til 5 ganger over ~30 min; 5 strake feil varsler admin, ~50 deaktiverer webhook |
| Prediksjonsvindu | 5 min | når du ACKer 200 | prediksjon tagges «late», droppes i scoring |

**IKKE prediker før ACK** — da spiser du av 20-sekundersbudsjettet. Spawn
bakgrunnsjobben (Modal-funksjon) og ACK straks.

### Materials-bundle (bak `information_url`)
Liste av items — plukk via `item.id`, aldri posisjon. Forvent ukjente kinds.
- `earnings-call-facts` (kind "facts", liste av strenger) — alltid
- `earnings-preview` (kind "text", ~8000 tegn markdown) — kan mangle
- `option-implied-stats` (kind "stats", JSON-OBJEKT) — kan mangle (<50 % av events; kun likvide opsjoner)
  - `implied_earnings_volatility` {value, status}
  - `implied_absolute_earnings_move` {value, status}
  - `skew_25_delta` {value, status} (call minus put IV; negativ = dyrere downside-beskyttelse)
  - `as_of` tidsstempel

### Webhook-signering (Standard Webhooks)
- HMAC-SHA256 i Standard Webhooks-stil (`v1,<base64>`-signaturer).
- Headers: `Webhook-Id` (stabil per logisk event = idempotency-nøkkel), `Webhook-Timestamp` (unix sek, fornyes per forsøk; 5 min toleranse default), `Webhook-Signature` (mellomromsdelt liste; godta hvis NOEN verifiserer — rotations-overlapp).
- Verifiser på **rå bytes** (`request.body()`), aldri `request.json()` — re-serialisering ødelegger signaturen.
- `verify_webhook` + `WebhookVerificationError` er vendored i starter-repoene (stdlib-only). Test-vektorer: `https://explainingmarkets.ai/test_vectors.json` og i starterens `tests/test_vectors.json`.
- Retry ved 5xx/timeout → **dedupe på `Webhook-Id`** (3 tilstander: in-flight / done / released).

### Test-events
`event_type == "TEST"` (portalens Test Webhook-knapp): lever nøytral 0.5-prediksjon
for å verifisere receive→submit-løkken. TEST-prediksjoner aksepteres, men scores aldri.

### API-endepunkter
- Base: `https://api.explainingmarkets.ai/v1`
- `POST /predictions` — `{event_id, predictions: [{identifier_value, predicted_percentile}]}` med `X-API-Key`. Alltid 201 for velformede; late/early/duplikat tagges. **Kun første gyldige prediksjon per event scores.**
- `GET /events` — kommende events-kalender (med `knowledge_cutoff`).
- `GET /archive` — historisk arkiv (gzip-JSONL per kvartal) med realiserte utfall + baseline-prediksjoner; offentlig scoring-logikk i examples-repoet.
- Feilkoder: `403 SUBMISSION_DISABLED`, `403 WEBHOOK_NOT_REGISTERED`, `409 EVENT_CLOSED` = strukturelle, varsles.

## 3. Scoring — HVORDAN vi faktisk målgjøres (examples/scoring.py, Rules §5)

- Ett event ⇒ ETT `(event, asset)`-utfall: `car1` = dags abnormal avkastning (cumulative abnormal return).
- `car1` percentile-rankes **på tvers av alle events i kvartalet** → `y ∈ [0,1]` (0 = mest negative reaksjon, 0.5 = median, 1 = mest positive).
- Earnings-surprise percentile-rankes tilsvarende → `surprise_pct`.
- Fit: `y = α + β₁·predicted_percentile + β₂·surprise_pct` (OLS).
- **ΔR² = R²(full) − R²(surprise-only)** — prestasjonen måles som forklart variasjon **utover earnings-surprise-benchmarken**.
- Kompis-board rangerer på own-sample ΔR²; **prize-konkurransen rangerer på common-sample ΔR²** (missed events imputeres med egen prediksjons-gjennomsnitt → **skipping straffes**, de teller mot deg i det felles utvalget).

### Konsekvenser for strategien (kritisk!)
1. **Konstante prediksjoner ⇒ ΔR² = 0 eksakt** (regressor uten varians absorberes av intercept; rangeres sist, ikke udefinert). Flat 0.5-baseline er følgelig verdiløs som poeng — men nyttig som fallback for å unngå missed-event-imputering.
2. **Invarians under affin remapping:** `p → a + b·p` endrer ikke ΔR². Kalibrering, skala og fortegn (1−p!) er uscoret — kun **rangeringsinformasjonen** (Spearman-aktig) teller. Ikke kast tid på kalibrering; kast den på å rangere riktig.
3. **Krevd:** variere mellom events OG korrelere med utfall-rangeringen UTENFOR det surprise allerede forklarer. Det er en residualiseringsøvelse: signalet må ligge i det surprise ikke fanger (guidance, tone, opsjonspriser vs realisert, strategiske skifter).
4. Starterens prompt-trekk verd å kopiere: kvartalsvis cross-seksjon (ikke egen historikk), base rates 25/50/25, reserve 0.80+/0.20− for entydige multi-signal-saker.

## 4. Vår arkitektur (vedtak)

```
explaining-markets board (kanban, ~/explaining-markets/)
F1 Onboarding (manuell: portal-konto, submission, credentials)
F2 Webhook-agent   2a Modal-deploy → 2b signering → 2c prediksjonsklient
F3 Strategi        3a research → 3b baseline → 3c hovedmodell
F4 Overvåking      leaderboard, health, drift gjennom Q4
```

- Deploy: Modal (serverless) — starter: github.com/explaining-markets/starter-modal
  (Label `explaining-markets` gir URL `https://{workspace}--explaining-markets.modal.run`).
  Alt-stativ finnes: starter-railway.
- Default-strategien i starteren: én LLM-structured-output per asset (Pydantic
  `Field(ge=0, le=1)`), materials-formatert prompt (facts → option-stats → ukjente →
  preview sist, trunkert), fallback 0.5 uten OPENAI_API_KEY. Timeouts: summary 15 s,
  LLM 120 s, 1 retry — worst case 270 s innen 5-min-vinduet.
- Modal-hemmeligheter: EM_API_KEY, EM_WEBHOOK_SECRET (whsec_...), OPENAI_API_KEY via
  `modal.Secret.from_dotenv`.
- Ekstra datakilder lov (ingen restriksjoner ut over knowledge_cutoff) — men
  *knowledge_cutoff-regelen er bindende*: ingen info etter cutoff-instanten, unntatt
  de leverte materialene (earnings-sammendraget er POST-cutoff og lover kun å brukes som levert).

## 5. Åpne spørsmål / til fjerning

- [ ] Har vi API-nøkkel fra portalen ennå? (F1) — uten den kan vi ikke hente arkiv/på events-kalenderen live.
- [ ] Modal-konto (2a) — hvem eier den? Team eller privat?
- [ ] OPENAI_API_KEY til prediksjonsmodell — vi har idun (GLM-5.3) lokalt; starteren forutsetter OpenAI-klient. Vurder å bytte til idun-proxy eller behold OpenAI for demo.
- [ ] `predicted_percentile` tolkning: cross-sectional kvartalsrangering (starter-doc) — betyr at tidlige events i kvartalet er «blinde» for referansepunkter? Nei — vi predikerer posisjonen i HELE kvartalets fordeling, ikke bare så langt. Se scoring.py: ranking skjer etter kvartalets slutt.
- [ ] Aksjer uten likvide opsjoner (<50 %): strategien må fungere uten option-stats.
