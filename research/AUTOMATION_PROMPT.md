# Cursor Automation — queue auto-PR

Opprett denne via **Agents Window** → Automations (chat-handoff er ikke tilgjengelig i alle sesjoner).

## Draft

| Felt | Verdi |
|------|--------|
| Name | Explaining Markets — queue auto-PR |
| Description | Hver fredag: ta neste kø-punkt, også `live_prompt` og `live_infra`, åpne en PR, og merge den når pytest er grønn. |
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

2. Velg neste punkt blant status == queued, lavest rank.
   Rekkefølge: først automation == auto_pr, deretter risk live_prompt eller live_infra
   (de står som automation: manual; validatoren krever det, og det blokkerer ikke arbeidet).
   Hvis ingen: merge likevel åpne, grønne kø-PR-er, og avslutt.

3. live_prompt og live_infra skal implementeres, ikke hoppes over.
   Da er endring i agent/predict.py, SYSTEM_PROMPT og Modal-webhook lov
   når punktet krever det. Behold scoring-kontrakten i APPROACH.md.
   Ikke kall OpenAI. Ikke kjør arkiv-prediksjoner. Ikke publiser model card i portalen.

4. Lag branch auto/queue-<id>.

5. Implementer kun det punktet tillater:
   - docs (kø 9): utkast til MODEL_CARD.md via model-card-skill-mønsteret; ikke publiser.
   - offline_analysis (kø 10/12): frosset plan + script under research/ablations/; ingen kjøreresultater.
   - observability (kø 15): passiv spredningslogging (sd / andel i midtbånd) — ingen multi-run LLM-kall.
   - live_prompt / live_infra: den konkrete endringen kø-punktet beskriver, med tester.

6. Kjør pytest i agent/ og web/. Stopp ved feil. Ikke merge en rød PR.

7. Oppdater queue.yaml: status → in_progress, append history med date, note, pr-URL (når kjent).
   Etter merge: status → partial hvis noe av punktet gjenstår, ellers done.

8. Åpne PR med tittel TYPE: kort beskrivelse (FEATURE/TEST/DOC).
   I body: kø-id, trials=1 (eller antall varianter forsøkt), cutoff-antagelse ukjent for Astra.
   Når pytest er grønn: merge PR-en inn i main. Ikke force-push.
```

## Første kandidater (allerede merket `auto_pr` i queue.yaml)

- #9 model card (docs)
- #15 spredningsvakt / logging (observability) — ikke multi-run
- #10 / #12 ablasjonsplan + script (offline_analysis)

## Research-cron (fredag 09:15) — separat automatisering

Se [`CRON_CONTRACT.md`](CRON_CONTRACT.md). Den ukentlige research-cronen må synke
`queue.yaml` når den skriver nye «Bruk (kø N)»-punkter i FORSKNING.md — ellers
driver ikke siden eller denne auto-PR-automasjonen.
