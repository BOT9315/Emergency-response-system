from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..ai.dispatch_optimizer import best_units_for_incident, optimize_assignments
from ..websocket_manager import manager

router = APIRouter(prefix="/api/dispatch", tags=["dispatch"])


async def _create_dispatch(db: Session, incident: models.Incident, unit: models.ResponderUnit,
                            distance_km: float, eta: float, auto: bool) -> models.Dispatch:
    dispatch = models.Dispatch(
        incident_id=incident.id, unit_id=unit.id,
        distance_km=distance_km, eta_minutes=eta, auto_assigned=auto,
    )
    unit.status = models.UnitStatus.dispatched
    incident.status = models.IncidentStatus.dispatched
    db.add(dispatch)
    db.add(models.IncidentLog(
        incident_id=incident.id, actor="system-ai" if auto else "dispatcher",
        action="unit_dispatched",
        detail=f"{unit.call_sign} ({unit.unit_type}) assigned, ETA {eta} min, {distance_km} km away",
    ))
    db.commit()
    db.refresh(dispatch)

    await manager.broadcast("dispatch_created", {
        "incident_id": incident.id, "unit_id": unit.id, "call_sign": unit.call_sign,
        "eta_minutes": eta, "distance_km": distance_km,
    })
    return dispatch


@router.post("/assign", response_model=schemas.DispatchOut)
async def assign_dispatch(payload: schemas.DispatchRequest, db: Session = Depends(get_db)):
    """
    Assign a unit to an incident. If `unit_id` is omitted, the AI dispatch
    optimizer picks the best available unit automatically (nearest suitable
    type, respecting the incident's category routing rules).
    """
    incident = db.query(models.Incident).get(payload.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if payload.unit_id:
        unit = db.query(models.ResponderUnit).get(payload.unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail="Unit not found")
        if unit.status != models.UnitStatus.available:
            raise HTTPException(status_code=400, detail="Unit is not available")
        from ..ai.dispatch_optimizer import haversine_km, eta_minutes
        dist = haversine_km(incident.latitude, incident.longitude, unit.latitude, unit.longitude)
        return await _create_dispatch(db, incident, unit, round(dist, 2), eta_minutes(dist), auto=False)

    available = db.query(models.ResponderUnit).filter(
        models.ResponderUnit.status == models.UnitStatus.available
    ).all()
    candidates = best_units_for_incident(incident.incident_type, incident.latitude, incident.longitude, available)
    if not candidates:
        raise HTTPException(status_code=409, detail="No suitable available unit found for this incident type")

    best = candidates[0]
    unit = db.query(models.ResponderUnit).get(best.unit_id)
    return await _create_dispatch(db, incident, unit, best.distance_km, best.eta_minutes, auto=True)


@router.post("/auto-optimize")
async def auto_optimize(db: Session = Depends(get_db)):
    """
    Batch-runs the AI optimizer across every pending (triaged, undispatched)
    incident against every available unit in one pass. Useful right after a
    surge of reports (e.g. a natural disaster) to dispatch the whole queue
    optimally in one click instead of one at a time.
    """
    pending = db.query(models.Incident).filter(
        models.Incident.status == models.IncidentStatus.triaged
    ).all()
    available = db.query(models.ResponderUnit).filter(
        models.ResponderUnit.status == models.UnitStatus.available
    ).all()
    if not pending:
        return {"assigned": 0, "results": []}

    plan = optimize_assignments(pending, available)
    assigned_count = 0
    results = []
    for item in plan:
        if item.unit_id is None:
            results.append({"incident_id": item.incident_id, "assigned": False, "reason": item.reason})
            continue
        incident = db.query(models.Incident).get(item.incident_id)
        unit = db.query(models.ResponderUnit).get(item.unit_id)
        if unit.status != models.UnitStatus.available:
            results.append({"incident_id": item.incident_id, "assigned": False, "reason": "Unit taken this tick"})
            continue
        await _create_dispatch(db, incident, unit, item.distance_km, item.eta_minutes, auto=True)
        assigned_count += 1
        results.append({"incident_id": item.incident_id, "assigned": True, "unit": item.call_sign,
                         "eta_minutes": item.eta_minutes})

    return {"assigned": assigned_count, "results": results}


@router.get("", response_model=List[schemas.DispatchOut])
def list_dispatches(db: Session = Depends(get_db)):
    return db.query(models.Dispatch).order_by(models.Dispatch.assigned_at.desc()).limit(200).all()


@router.post("/{dispatch_id}/clear")
async def clear_dispatch(dispatch_id: int, db: Session = Depends(get_db)):
    """Mark a unit as back in service once it has cleared the scene."""
    from datetime import datetime
    dispatch = db.query(models.Dispatch).get(dispatch_id)
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    dispatch.cleared_at = datetime.utcnow()
    unit = db.query(models.ResponderUnit).get(dispatch.unit_id)
    unit.status = models.UnitStatus.available
    db.commit()
    await manager.broadcast("unit_updated", schemas.UnitOut.model_validate(unit).model_dump())
    return {"ok": True}
