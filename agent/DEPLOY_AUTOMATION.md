# Cursor Automation — Modal deploy

Erstatt Hermes `explaining-markets-deploy` (hvert 10. min) med denne.

## Draft (lim inn i Create Automation)

| Felt | Verdi |
|------|--------|
| Name | Explaining Markets — Modal deploy |
| Description | Ved push til main: pytest, deretter `modal deploy`. Ingen Hermes. |
| Trigger | Git push til `main` på `kdm-kev-NTNU/explaining-markets-agent` |
| Tools | Terminal, GitHub |
| Repo | `kdm-kev-NTNU/explaining-markets-agent` · branch `main` |
| Secrets (Cloud Agent) | `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`, og evt. `EM_API_KEY` + `EM_WEBHOOK_SECRET` + `OPENAI_API_KEY` hvis deploy fortsatt leser `.env` |

> Modal-appen bruker `Secret.from_dotenv` ved deploy. Cloud Agent har ikke din lokale `.env`.  
> **Før første kjøring:** legg token + EM-nøkler som Cloud Agent-secrets, og la automasjonen skrive `agent/.env` midlertidig før deploy (se prompt under). Eller flytt credentials til Modal Secret Store og oppdater `modal_app.py` senere.

## Instructions (lim inn som prompt)

```
Du deployer Explaining Markets Modal-webhooken.

Repo: explaining-markets-agent. Jobb kun under agent/.

1. cd agent
2. Installer deps: uv sync
3. Kjør tester: uv run pytest
   Stopp ved feil. Ikke deploy.
4. Sørg for at Modal er autentisert via miljøvariablene MODAL_TOKEN_ID og MODAL_TOKEN_SECRET
   (allerede satt som Cloud Agent-secrets — ikke logg dem, ikke commit dem).
5. Skriv agent/.env fra secrets (aldri commit):
   EM_API_KEY=…
   EM_WEBHOOK_SECRET=…
   OPENAI_API_KEY=…   # hvis satt
6. Deploy:
   uv run modal deploy modal_app.py
7. Health-sjekk: GET på Modal-URLen som printes (path /). Forvent 200/JSON health.
8. Slett agent/.env etter deploy hvis du opprettet den.
9. Avslutt med én linje: DEPLOY ok:true · <modal-url>  eller DEPLOY ok:false · <årsak>

HARD STOP:
- Ikke endre predict.py, SYSTEM_PROMPT, eller webhook-logikk «underveis».
- Ikke merge PRs. Ikke rør research/ eller web/ i denne jobben.
- Ikke print secrets.
```

## Etter at den er lagret

1. Deaktiver Hermes `explaining-markets-deploy`.
2. Push en tom/no-op commit til `main` (eller **Run now**) for å verifisere.
3. Behold Hermes deploy **ikke** parallelt — dobbel deploy er rot.
