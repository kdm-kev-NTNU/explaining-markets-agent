# Research-cron-kontrakt (fredag 09:15)

`explaining-markets-research-cron` eier **to** filer i dette repoet, ikke bare én.

| Fil | Rolle |
|-----|--------|
| [`FORSKNING.md`](FORSKNING.md) | Prosa: ukentlige funn, paper-sammendrag, «Bruk (kø N …)», plattform-endringer |
| [`queue.yaml`](queue.yaml) | Maskinlesbar status: hva som er i kø / delvis / ferdig, risk, auto_pr, arXiv-lenker |

## Hva «skriv queue.yaml» betyr

Når cronen tidligere bare skrev:

```text
**Bruk (kø 13):** … implementer som monoton transform …
```

i `FORSKNING.md`, ble statusen usynlig for siden og for auto-PR-automasjonen.
Nå skal samme beslutning også lande som YAML:

```yaml
- id: 16          # neste ledige id
  title: "…"
  area: 3c        # 2c | 3b | 3c | F4 | ops
  status: queued  # queued | in_progress | partial | done | parked | rejected
  rank: 16        # unik blant ikke-ferdige
  risk: live_prompt   # live_* ⇒ automation MÅ være manual
  automation: manual  # eller auto_pr (kun docs | offline_analysis | observability)
  added: 2026-W48
  sources:
    - {kind: arxiv, ref: "2611.xxxxx"}
  history:
    - {date: 2026-11-27, status: queued, note: "kort begrunnelse"}
```

## Ukentlig sjekkliste for cron-agenten

1. Kjør `python3 research/collect.py` (som før).
2. Filtrer papers mot ΔR² / rangeringsinfo (som før).
3. Skriv ny `### Uke …`-seksjon i `FORSKNING.md` (som før).
4. **For hvert nytt eller endret kø-punkt:**
   - Nytt arbeidspunkt → `python -m app.queue_mutate add …` (fra `web/`), **eller** rediger `queue.yaml` manuelt etter skjemaet.
   - Statusendring (f.eks. «implementert som prompt») → `python -m app.queue_mutate set-status --id N --status partial --note "…"`.
5. Valider før commit:
   ```bash
   cd web && python -m app.research_registry --check ../research/queue.yaml --forskning ../research/FORSKNING.md
   ```
6. Commit begge filene i samme research-commit.

## Regler cronen må følge

- `risk` i `{live_prompt, live_infra}` ⇒ `automation: manual` (validator avviser alt annet).
  Det hindrer ikke auto-PR-agenten i å implementere punktet. `manual` betyr bare
  at feltet ikke kan stå som `auto_pr`.
- `auto_pr` bare for `docs`, `offline_analysis`, `observability`.
- Hver `sources[kind=arxiv].ref` må finnes som **beholdt** paper i `FORSKNING.md` samme uke (eller allerede i arkivet).
- `history` er append-only; siste entry sin `status` = feltet `status`.
- Ikke slett gamle items; sett `parked` / `rejected` ved behov.

## Lim-inn-fragment til cron-prompten

```
Etter at FORSKNING.md er oppdatert for uken: synk research/queue.yaml.
- Nye «Bruk (kø N)» / nye arbeidspunkter → add via web/app.queue_mutate (eller YAML).
- Statusnotater («Status …: implementert/delvis») → set-status.
- Kjør: cd web && python -m app.research_registry --check ../research/queue.yaml --forskning ../research/FORSKNING.md
- Commit FORSKNING.md og queue.yaml sammen. Ikke la kø-prosa stå uten YAML-motstykke.
```
