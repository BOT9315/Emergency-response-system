from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..websocket_manager import manager

router = APIRouter(prefix="/api/units", tags=["units"])


@router.post("", response_model=schemas.UnitOut)
def create_unit(payload: schemas.UnitCreate, db: Session = Depends(get_db)):
    existing = db.query(models.ResponderUnit).filter(models.ResponderUnit.call_sign == payload.call_sign).first()
    if existing:
        raise HTTPException(status_code=400, detail="Call sign already exists")
    unit = models.ResponderUnit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.get("", response_model=List[schemas.UnitOut])
def list_units(status: Optional[str] = None, unit_type: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.ResponderUnit)
    if status:
        q = q.filter(models.ResponderUnit.status == status)
    if unit_type:
        q = q.filter(models.ResponderUnit.unit_type == unit_type)
    return q.all()


@router.patch("/{unit_id}/location", response_model=schemas.UnitOut)
async def update_unit_location(unit_id: int, payload: schemas.UnitLocationUpdate, db: Session = Depends(get_db)):
    unit = db.query(models.ResponderUnit).get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    unit.latitude = payload.latitude
    unit.longitude = payload.longitude
    db.commit()
    db.refresh(unit)
    await manager.broadcast("unit_updated", schemas.UnitOut.model_validate(unit).model_dump())
    return unit


@router.patch("/{unit_id}/status", response_model=schemas.UnitOut)
async def update_unit_status(unit_id: int, status: str, db: Session = Depends(get_db)):
    unit = db.query(models.ResponderUnit).get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    valid_statuses = [s.value for s in models.UnitStatus]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status, must be one of {valid_statuses}")
    unit.status = status
    db.commit()
    db.refresh(unit)
    await manager.broadcast("unit_updated", schemas.UnitOut.model_validate(unit).model_dump())
    return unit
