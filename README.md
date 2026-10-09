# Explaining Markets — Cogito NTNU

Kvartalsvis konkurranse: AI-agent forutsier aksjeavkastning rundt earnings.
Arrangør: U. Chicago (Koijen & Levy) + Optiver. Q4-scoring: 12. okt – 15. des 2026.

- Docs: https://explainingmarkets.ai/docs
- API base: https://api.explainingmarkets.ai/v1
- Premiepott $7 500 (kun US-borgere 18+ — vi deltar for live-evalueringen, ikke premien)
- Kontakt: contact@explainingmarkets.ai

## Arkitektur (fra docs)
Event (selskap rapporterer) → signert webhook til agenten → ACK 200 →
les prediction_deadline (default +5 min fra ACK) → POST prediksjon til
/v1/predictions med X-API-Key → scores mot faktisk markedsutfall →
offentlig leaderboard.

## Materials per event (plukk via item.id, aldri posisjon)
1. Sammendrag av earnings call (POST-knowledge_cutoff)
2. Earnings preview (PRE-cutoff, agentic research + opsjonsimplisitte tall — nytt fra Q4)
3. Option-implied stats (JSON-objekt, kun likvide opsjoner): implied earnings vol, implied absolute move, 25-delta skew

## Regler
- Kun informasjon tilgjengelig ved knowledge_cutoff (ISO 8601 UTC)
- Kun FØRSTE gyldige prediksjon per event teller (late/early/duplikat = 201, ignoreres)
- 403 SUBMISSION_DISABLED / 403 WEBHOOK_NOT_REGISTERED / 409 EVENT_CLOSED = strukturelle feil

## Kanban-board
Slug: `explaining-markets` — vis i dashboard: Kanban-tab → board-velger.
CLI: `hermes kanban --board explaining-markets <cmd>`

## Faser
1. Onboarding (portal-konto + submission) — manuell, Kevin/Cogito
2. Webhook-agent (Modal-deploy, signering, prediksjonsklient)
3. Prediksjonsstrategi (artikkel, baseline, hovedmodell)
4. Overvåking (leaderboard, health, drift gjennom Q4)
