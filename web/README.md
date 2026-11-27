# Presentasjonsside (FastAPI)

Kjør lokalt fra denne mappen:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Miljøvariabler (admin / Forskning)

Forskning-siden krever innlogging. Sett disse før start:

| Variabel | Eksempel | Beskrivelse |
|----------|----------|-------------|
| `ADMIN_USERNAME` | `ADMIN` | Admin-brukernavn |
| `ADMIN_PASSWORD` | `FUTURE` | Admin-passord |
| `SESSION_SECRET` | tilfeldig streng | Signerer sesjonscookien |

Uten alle tre er innlogging deaktivert (fail closed).

Lokal PowerShell:

```powershell
$env:ADMIN_USERNAME = "ADMIN"
$env:ADMIN_PASSWORD = "FUTURE"
$env:SESSION_SECRET = "dev-secret-change-me"
uvicorn app.main:app --reload --port 8000
```

På Railway: sett de samme variablene under tjenestens Variables.

Tester:

```bash
pytest tests -q
```

Deploy: Railway leser `railway.json` (root directory = `web/`).
Healthcheck: `GET /healthz`.
