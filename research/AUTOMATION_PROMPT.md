# Cursor Automation — queue auto-PR

Opprett denne via **Agents Window** → Automations (chat-handoff er ikke tilgjengelig i alle sesjoner).

## Draft

| Felt | Verdi |
|------|--------|
| Name | Explaining Markets — queue auto-PR |
| Description | Hver fredag: ta neste lavrisiko-kø-punkt (`automation: auto_pr`) og åpne en PR til manuell review. Aldri merge. Aldri rør live-prompt. |
| Trigger | Cron fredag 11:00 (`0 11 * * 5`) |
| Tools | GitHub (branch + PR), terminal/pytest |
| Repo | `kdm-kev-NTNU/explaining-markets-agent` (default branch) |
| To finish in editor | Bekreft cron-tidssone, repo-scope, Cloud Agent compute |

## Instructions (lim inn som prompt)

```
Du kjører i explaining-markets-agent.

1. Valider research/queue.yaml:
   cd web && python -m app.research_registry --check ../research/queue.yaml --forskning ../research/FORSKNING.md
   Stopp ved feil.

2. Velg neste punkt: status == queued OG automation == auto_pr, lavest rank.
   Hvis ingen: avslutt uten endringer (skriv kort commit-melding i PR-kommentar: «ingen auto_pr-kandidat»).

3. HARD STOP: hvis risk er live_prompt eller live_infra, ikke rør punktet (validator skal allerede ha forhindret auto_pr).
   Ikke endre agent/predict.py, SYSTEM_PROMPT, eller Modal-webhook-kode.
   Ikke kall OpenAI. Ikke kjør arkiv-prediksjoner.

4. Lag branch auto/queue-<id>.

5. Implementer kun det punktet tillater:
   - docs (kø 9): utkast til MODEL_CARD.md via model-card-skill-mønsteret; ikke publiser.
   - offline_analysis (kø 10/12): frosset plan + script under research/ablations/; ingen kjøreresultater.
   - observability (kø 15): passiv spredningslogging (sd / andel i midtbånd) — ingen multi-run LLM-kall.

6. Kjør pytest i agent/ og web/.

7. Oppdater queue.yaml: status → in_progress, append history med date, note, pr-URL (når kjent).

8. Åpne PR med tittel TYPE: kort beskrivelse (FEATURE/TEST/DOC).
   I body: kø-id, trials=1 (eller antall varianter forsøkt), cutoff-antagelse ukjent for Astra,
   «ingen merge — manuell review». Ikke merge.
```

## Første kandidater (allerede merket `auto_pr` i queue.yaml)

- #9 model card (docs)
- #15 spredningsvakt / logging (observability) — ikke multi-run
- #10 / #12 ablasjonsplan + script (offline_analysis)

## Research-cron (fredag 09:15) — separat automatisering

Se [`CRON_CONTRACT.md`](CRON_CONTRACT.md). Den ukentlige research-cronen må synke
`queue.yaml` når den skriver nye «Bruk (kø N)»-punkter i FORSKNING.md — ellers
driver ikke siden eller denne auto-PR-automasjonen.
