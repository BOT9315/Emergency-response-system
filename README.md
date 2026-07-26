# IERCS — Intelligent Emergency Response Coordination System

An AI-powered platform that takes a free-text emergency report, automatically
classifies its type and severity, computes a dispatch priority, and
recommends (or auto-assigns) the nearest suitable responder unit — with a
real-time command console dashboard, live map, fleet management, and
analytics.

> Full architecture and AI algorithm details: [`docs/architecture.md`](docs/architecture.md)

## Features

- **AI incident triage** — TF-IDF + Naive Bayes text classifier decides
  incident type (fire, medical, crime, accident, natural disaster, hazmat,
  other) and severity (low/moderate/high/critical) from a free-text report,
  with a safety-critical keyword override.
- **Multi-factor priority scoring** — 0-100 dispatch priority combining
  severity, casualties, incident-type risk, location risk, and wait time.
- **AI dispatch optimizer** — nearest-suitable-unit matching by real
  distance/ETA, plus one-click batch auto-dispatch for a whole backlog.
- **Predictive hotspots** — recency- and severity-weighted density map of
  where incidents are clustering, for proactive pre-positioning.
- **Real-time dashboard** — live incident queue, map (Leaflet), fleet
  status, and analytics (Recharts), synced over WebSocket.
- **Full REST API** with JWT auth, OpenAPI docs at `/docs`.

## Project structure

```
emergency-response-system/
├── backend/                 FastAPI application
│   ├── app/
│   │   ├── ai/               classifier, dispatch optimizer, predictor
│   │   ├── routers/          incidents, units, dispatch, analytics, auth
│   │   ├── models.py         SQLAlchemy ORM models
│   │   ├── schemas.py        Pydantic request/response schemas
│   │   ├── security.py       JWT + password hashing
│   │   ├── websocket_manager.py
│   │   ├── seed_data.py      demo units + historical incidents
│   │   ├── config.py         all tunable weights/constants
│   │   └── main.py           app entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 React + Vite dashboard
│   ├── src/
│   │   ├── components/       Navbar, Dashboard, MapView, IncidentFeed,
│   │   │                     ReportIncident, ResourcePanel, Analytics
│   │   ├── api.js             REST + WebSocket client
│   │   ├── utils.js
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   └── architecture.md
└── docker-compose.yml
```

## Quick start — Docker (recommended)

```bash
docker compose up --build
```

- Dashboard: http://localhost:3000
- API + docs: http://localhost:8000/docs

## Quick start — manual

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The database (SQLite) and demo data (13 responder units + ~2 weeks of
sample incident history) are created automatically on first run. Two demo
accounts are seeded:

| Username     | Password     | Role       |
|--------------|--------------|------------|
| `admin`      | `admin123`   | admin      |
| `dispatcher1`| `dispatch123`| dispatcher |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` and `/ws`
to `localhost:8000`, so run the backend first.

## Using the system

1. Open the dashboard and click **+ Report Incident**. Describe a situation
   in your own words (e.g. "car crash on the highway, two people injured")
   — the AI engine classifies type/severity and shows you the computed
   priority instantly.
2. The incident appears in the live queue, color-coded by severity, and as
   a marker on the map.
3. Click **Dispatch** on any triaged incident to let the AI pick the
   nearest suitable unit, or use **AI Auto-Dispatch** to clear the entire
   pending queue in one pass (useful right after a surge of reports).
4. Check the **Fleet** tab for unit status, and **Analytics** for system-wide
   stats, a 14-day incident timeline, and the incident-type breakdown.

## Configuration

All AI weights, unit-routing rules, and tunables live in
`backend/app/config.py` — no code changes needed elsewhere to retune the
system (e.g. give casualties more weight in the priority formula, or add a
new incident category).

Environment variables (optional):

- `IERCS_SECRET_KEY` — JWT signing secret (set a real one in production)
- `IERCS_DATABASE_URL` — defaults to local SQLite; point at Postgres etc. by
  changing this

## API reference

Full interactive OpenAPI docs are served at `/docs` once the backend is
running. Key endpoints:

| Method | Path                             | Purpose                          |
|--------|-----------------------------------|-----------------------------------|
| POST   | `/api/incidents`                  | Report + AI-triage an incident    |
| GET    | `/api/incidents`                  | List incidents (priority sorted)  |
| GET    | `/api/incidents/{id}/suggested-units` | Ranked AI unit recommendations |
| PATCH  | `/api/incidents/{id}/status`      | Update incident lifecycle status  |
| POST   | `/api/dispatch/assign`            | Assign a unit (AI or manual)      |
| POST   | `/api/dispatch/auto-optimize`     | Batch-dispatch the whole queue    |
| GET    | `/api/analytics/stats`            | System-wide stats                 |
| GET    | `/api/analytics/hotspots`         | AI-predicted incident hotspots    |
| GET    | `/api/analytics/timeline`         | Incidents/day by severity         |
| WS     | `/ws/live`                        | Real-time event stream            |

## Notes on scope

This is a complete, runnable reference implementation intended to
demonstrate the full architecture end-to-end (AI triage → prioritization →
optimized dispatch → real-time coordination → analytics). For a production
deployment you would additionally want: a managed database with backups,
HTTPS/production JWT secret management, a real turn-by-turn routing
provider for ETA, SMS/phone intake integration, and role-based UI gating
per user (currently the dashboard itself is open; the API already enforces
JWT roles on write operations that need them).
