from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..ai.classifier import engine as ai_engine
from ..ai.predictor import location_risk_score
from ..ai.dispatch_optimizer import best_units_for_incident
from ..websocket_manager import manager

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


def _log(db: Session, incident_id: int, actor: str, action: str, detail: str = ""):
    db.add(models.IncidentLog(incident_id=incident_id, actor=actor, action=action, detail=detail))


@router.post("", response_model=schemas.IncidentOut)
async def report_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db)):
    """
    Public intake endpoint. Runs the full AI triage pipeline:
      1. Classify incident type + severity from free text (or respect a
         manual override if the caller supplied one).
      2. Score location risk from recent history in the same area.
      3. Compute a 0-100 dispatch priority.
      4. Persist, log, and broadcast to all connected dashboards in real time.
    """
    result = ai_engine.classify(payload.description)
    incident_type = payload.incident_type or result.incident_type
    severity = payload.severity or result.severity

    recent_cutoff = datetime.utcnow() - timedelta(days=30)
    recent_incidents = db.query(models.Incident).filter(models.Incident.created_at >= recent_cutoff).all()
    loc_risk = location_risk_score(payload.latitude, payload.longitude, recent_incidents)

    priority = ai_engine.compute_priority(
        incident_type=incident_type,
        severity=severity,
        casualties=payload.casualties_reported or 0,
        location_risk=loc_risk,
        age_minutes=0,
        model_confidence=result.type_confidence,
    )

    incident = models.Incident(
        reporter_name=payload.reporter_name or "Anonymous",
        reporter_contact=payload.reporter_contact or "",
        description=payload.description,
        incident_type=incident_type,
        severity=severity,
        priority_score=priority,
        casualties_reported=payload.casualties_reported or 0,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address=payload.address or "",
        status=models.IncidentStatus.triaged,
        ai_confidence=result.type_confidence,
        ai_notes=result.notes,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    _log(db, incident.id, "system-ai",
         "triaged",
         f"type={incident_type} ({result.type_confidence:.0%} conf), "
         f"severity={severity}, priority={priority}")
    db.commit()

    await manager.broadcast("incident_created", schemas.IncidentOut.model_validate(incident).model_dump())

    return incident


@router.get("", response_model=List[schemas.IncidentOut])
def list_incidents(
    status: Optional[str] = None,
    incident_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(models.Incident)
    if status:
        q = q.filter(models.Incident.status == status)
    if incident_type:
        q = q.filter(models.Incident.incident_type == incident_type)
    return q.order_by(models.Incident.priority_score.desc(), models.Incident.created_at.desc()).limit(limit).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("/{incident_id}/logs")
def get_incident_logs(incident_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.IncidentLog).filter(
        models.IncidentLog.incident_id == incident_id
    ).order_by(models.IncidentLog.timestamp.asc()).all()
    return [
        {"actor": l.actor, "action": l.action, "detail": l.detail, "timestamp": l.timestamp}
        for l in logs
    ]


@router.get("/{incident_id}/suggested-units")
def suggested_units(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    available = db.query(models.ResponderUnit).filter(
        models.ResponderUnit.status == models.UnitStatus.available
    ).all()
    candidates = best_units_for_incident(
        incident.incident_type, incident.latitude, incident.longitude, available
    )
    return [c.__dict__ for c in candidates]


@router.patch("/{incident_id}/status", response_model=schemas.IncidentOut)
async def update_status(incident_id: int, payload: schemas.IncidentStatusUpdate, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    valid_statuses = [s.value for s in models.IncidentStatus]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status, must be one of {valid_statuses}")

    old_status = incident.status
    incident.status = payload.status
    if payload.status in ("resolved", "closed"):
        incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)

    _log(db, incident.id, "dispatcher", "status_change", f"{old_status} -> {payload.status}")
    db.commit()

    await manager.broadcast("incident_updated", schemas.IncidentOut.model_validate(incident).model_dump())
    return incident
