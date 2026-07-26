# IERCS — Intelligent Emergency Response Coordination System

A full-stack reference application for coordinating emergency responders. Report an incident in plain language, and an AI layer classifies it, scores its priority, and helps dispatch the nearest suitable unit — all synced live across a command console dashboard.

![status](https://img.shields.io/badge/status-demo-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![node](https://img.shields.io/badge/node-18%2B-green) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What it does

- **Free-text triage** — type a description like *"car crash on the highway, two people injured"* and the AI classifier (TF-IDF + Naive Bayes) predicts incident **type** (fire, medical, crime, accident, natural disaster, hazmat, other) and **severity** (low / moderate / high / critical).
- **Priority scoring** — a 0–100 score computed from severity, casualties, incident-type risk, location risk, and wait time.
- **AI dispatch** — the optimizer matches each incident to the nearest suitable responder unit, either one at a time or as a one-click "clear the queue" batch action.
- **Live command console** — a dashboard with a map (incident + unit markers), a live incident feed, fleet status, and analytics — all pushed in real time over WebSocket.

## Tech stack

| Layer | Stack |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy + SQLite, scikit-learn, JWT auth, WebSockets |
| Frontend | React, Vite, Leaflet (maps), Recharts (analytics) |
| Deployment | Docker Compose |

## Architecture

```
┌──────────────┐     REST /api/...      ┌───────────────┐
│   Frontend   │ ─────────────────────► │    Backend    │
│ React + Vite │ ◄───────────────────── │    FastAPI    │
│   :5173      │     WebSocket /ws/live │     :8000     │
└──────────────┘ ◄────────────────────► └───────┬───────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  SQLite database │
                                         └─────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for details.

## Getting started

### Option A — Docker (recommended)

```bash
git clone https://github.com/<your-username>/emergency-response-system.git
cd emergency-response-system
docker compose up --build
```

- Dashboard: http://localhost:3000
- API docs (Swagger): http://localhost:8000/docs

### Option B — Run manually

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (in a separate terminal)

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. The Vite dev server proxies `/api` and `/ws` requests to the backend, so start the backend first.

### Demo login

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Dispatcher | `dispatcher1` | `dispatch123` |

## API overview

All endpoints are served under `/api`, with interactive docs at `/docs`.

| Prefix | Purpose |
|---|---|
| `/api/auth` | Login, JWT tokens |
| `/api/incidents` | Create, list, update incidents |
| `/api/units` | Manage responder units |
| `/api/dispatch` | Assign units, auto-dispatch |
| `/api/analytics` | Stats, hotspots, timelines |
| `/ws/live` | WebSocket — live push updates |

## Project structure

```
emergency-response-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, router registration, startup seeding
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── database.py        # DB connection
│   │   ├── websocket_manager.py
│   │   ├── routers/           # incidents, resources, dispatch, analytics, auth
│   │   └── ai/                # classifier, dispatch optimizer, hotspot predictor
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # top-level state, WebSocket connection
│   │   ├── api.js             # all backend calls live here
│   │   └── components/        # Dashboard, MapView, IncidentFeed, ResourcePanel, Analytics...
│   └── package.json
├── docs/architecture.md
├── docker-compose.yml
└── README.md
```

## Notes

This is a reference implementation meant to demonstrate the full pipeline (triage → prioritize → dispatch → live coordination → analytics) end to end. For production use you'd want a managed database, a real routing/ETA provider, SMS/voice intake, and hardened auth/secrets management.

## License

MIT — see [LICENSE](LICENSE) for details.
