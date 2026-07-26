# IERCS Architecture

## Overview

IERCS (Intelligent Emergency Response Coordination System) is a full-stack
application that takes a free-text emergency report from a citizen or call
taker and, in under a second, produces a structured, prioritized, dispatch-
ready incident — then recommends and can auto-assign the nearest suitable
responder unit.

```
┌─────────────┐      REST + WebSocket      ┌──────────────────┐
│   React      │ ─────────────────────────▶ │   FastAPI         │
│   Dashboard  │ ◀───────────────────────── │   Backend          │
└─────────────┘                             └──────────────────┘
                                                     │
                          ┌──────────────────────────┼──────────────────────────┐
                          ▼                          ▼                          ▼
                 ┌────────────────┐        ┌──────────────────┐       ┌─────────────────┐
                 │ AI Classifier   │        │ Dispatch          │       │ Predictive        │
                 │ (TF-IDF + NB)   │        │ Optimizer          │       │ Hotspot Engine     │
                 │ type + severity │        │ haversine + ETA    │       │ grid density model │
                 └────────────────┘        └──────────────────┘       └─────────────────┘
                          │                          │                          │
                          └──────────────────────────┼──────────────────────────┘
                                                     ▼
                                            ┌──────────────────┐
                                            │ SQLite / SQLAlchemy│
                                            │ Incidents, Units,   │
                                            │ Dispatches, Logs     │
                                            └──────────────────┘
```

## AI Pipeline

1. **Intake** — `POST /api/incidents` receives free text + GPS coordinates.
2. **Classification** — `app/ai/classifier.py` runs two TF-IDF + Multinomial
   Naive Bayes pipelines (trained at process startup on `train_data.py`):
   one predicts incident *type*, the other predicts *severity*. A
   keyword safety net escalates severity to `critical` when phrases like
   "not breathing" or "trapped" appear, regardless of model confidence.
3. **Location risk** — `app/ai/predictor.py` checks how many incidents have
   recently occurred in the same ~1km grid cell, feeding a 0-1 risk score
   into the priority formula.
4. **Priority scoring** — a weighted sum (severity, casualties, incident-type
   base risk, location risk, time waiting) produces a 0-100 dispatch
   priority. Weights live in `app/config.py` and are tunable without code
   changes.
5. **Dispatch** — `app/ai/dispatch_optimizer.py` filters available units to
   the types appropriate for the incident category (e.g. fire → fire engine,
   then ambulance, then police), ranks by estimated travel time
   (great-circle distance / average city speed), and assigns the best
   match. A batch mode (`POST /api/dispatch/auto-optimize`) processes an
   entire backlog at once, highest priority first, without double-booking
   a unit within the same pass.
6. **Prediction** — `app/ai/predictor.py` also aggregates recent incidents
   into hotspots (recency- and severity-weighted density per grid cell) so
   dispatchers can see where to pre-position units before the next call.

## Why these algorithm choices

- **TF-IDF + Naive Bayes** over a larger transformer model: trains in
  milliseconds on CPU with no external dependency or API key, keeping the
  whole system self-contained and reproducible — appropriate for a
  reference implementation, and swappable for a larger model in
  `classifier.py` without touching any other file.
- **Greedy priority-ordered assignment** over a full Hungarian/optimal
  solve: real dispatch systems assign continuously as calls arrive, not in
  large batches, so an algorithm that produces a correct, explainable
  answer in O(incidents × units) and can run per-incident in real time was
  prioritized over a globally optimal but batch-oriented solve.
- **Grid-based density** over full ML clustering (e.g. DBSCAN) for
  hotspots: no external geo library dependency, easy to explain to a
  non-technical dispatcher ("this area has had 6 incidents in 3 days"),
  and cheap enough to recompute on every request.

## Data model

- `Incident` — the report itself, plus AI outputs (type, severity, priority,
  confidence) and lifecycle status.
- `ResponderUnit` — a fire engine / ambulance / police / hazmat / rescue
  asset with live location and status.
- `Dispatch` — the join between an incident and a unit, with computed
  distance/ETA.
- `IncidentLog` — append-only audit trail of every AI decision and status
  change, for after-action review.

## Real-time layer

`app/websocket_manager.py` maintains a set of connected dashboard clients
and broadcasts `incident_created`, `incident_updated`, `unit_updated`, and
`dispatch_created` events as they happen, so every open dashboard reflects
new reports and assignments within milliseconds — no polling required
(the frontend also polls every 20s as a safety net in case a socket drops
silently).

## Extending this project

- Swap the classifier for a hosted LLM by replacing the body of
  `IncidentAIEngine.classify` in `classifier.py` — the rest of the system
  only depends on the `ClassificationResult` shape.
- Add real turn-by-turn ETA by replacing `eta_minutes()` in
  `dispatch_optimizer.py` with a call to a routing API.
- Swap SQLite for Postgres by changing `IERCS_DATABASE_URL`.
