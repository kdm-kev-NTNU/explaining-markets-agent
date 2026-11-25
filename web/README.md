# Presentasjonsside (FastAPI)

Kjør lokalt fra denne mappen:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Tester:

```bash
pytest tests -q
```

Deploy: Railway leser `railway.json` (root directory = `web/`).
Healthcheck: `GET /healthz`.
