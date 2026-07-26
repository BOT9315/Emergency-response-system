from datetime import datetime, timedelta
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..ai.predictor import compute_hotspots
from ..config import PREDICTION_WINDOW_DAYS

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/stats", response_model=schemas.SystemStats)
def system_stats(db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).all()
    units = db.query(models.ResponderUnit).all()

    active_statuses = {"reported", "triaged", "dispatched", "en_route", "on_scene"}
    active = [i for i in incidents if i.status in active_statuses]
    resolved = [i for i in incidents if i.status in ("resolved", "closed")]

    response_times = []
    for i in resolved:
        if i.resolved_at:
            response_times.append((i.resolved_at - i.created_at).total_seconds() / 60.0)
    avg_response = round(sum(response_times) / len(response_times), 1) if response_times else 0.0

    by_type = Counter(i.incident_type for i in incidents)
    by_severity = Counter(i.severity for i in incidents)

    return schemas.SystemStats(
        total_incidents=len(incidents),
        active_incidents=len(active),
        resolved_incidents=len(resolved),
        avg_response_minutes=avg_response,
        units_available=len([u for u in units if u.status == models.UnitStatus.available]),
        units_total=len(units),
        incidents_by_type=dict(by_type),
        incidents_by_severity=dict(by_severity),
    )


@router.get("/hotspots")
def hotspots(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=PREDICTION_WINDOW_DAYS)
    incidents = db.query(models.Incident).filter(models.Incident.created_at >= cutoff).all()
    return compute_hotspots(incidents, top_n=10, window_days=PREDICTION_WINDOW_DAYS)


@router.get("/timeline")
def incident_timeline(days: int = 14, db: Session = Depends(get_db)):
    """Incidents-per-day for the last N days, split by severity — powers the analytics chart."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    incidents = db.query(models.Incident).filter(models.Incident.created_at >= cutoff).all()
    buckets: dict = {}
    for i in incidents:
        day = i.created_at.strftime("%Y-%m-%d")
        buckets.setdefault(day, {"date": day, "low": 0, "moderate": 0, "high": 0, "critical": 0})
        buckets[day][i.severity] = buckets[day].get(i.severity, 0) + 1
    return sorted(buckets.values(), key=lambda b: b["date"])
