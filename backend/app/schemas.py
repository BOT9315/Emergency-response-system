from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ---------- Incidents ----------
class IncidentCreate(BaseModel):
    reporter_name: Optional[str] = "Anonymous"
    reporter_contact: Optional[str] = ""
    description: str = Field(..., min_length=5, description="Free text describing what is happening")
    latitude: float
    longitude: float
    address: Optional[str] = ""
    casualties_reported: Optional[int] = 0
    # Optional manual override; if omitted the AI classifier decides.
    incident_type: Optional[str] = None
    severity: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    reporter_name: str
    description: str
    incident_type: str
    severity: str
    priority_score: float
    casualties_reported: int
    latitude: float
    longitude: float
    address: str
    status: str
    ai_confidence: float
    ai_notes: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str


# ---------- Responder Units ----------
class UnitCreate(BaseModel):
    call_sign: str
    unit_type: str
    latitude: float
    longitude: float
    capacity: Optional[int] = 1
    crew_size: Optional[int] = 2
    base_station: Optional[str] = ""


class UnitOut(BaseModel):
    id: int
    call_sign: str
    unit_type: str
    status: str
    latitude: float
    longitude: float
    capacity: int
    crew_size: int
    base_station: str

    class Config:
        from_attributes = True


class UnitLocationUpdate(BaseModel):
    latitude: float
    longitude: float


# ---------- Dispatch ----------
class DispatchOut(BaseModel):
    id: int
    incident_id: int
    unit_id: int
    eta_minutes: float
    distance_km: float
    assigned_at: datetime
    auto_assigned: bool

    class Config:
        from_attributes = True


class DispatchRequest(BaseModel):
    incident_id: int
    unit_id: Optional[int] = None  # if omitted, AI picks the best unit(s)


# ---------- Analytics ----------
class HotspotOut(BaseModel):
    latitude: float
    longitude: float
    weight: float
    incident_count: int
    dominant_type: str


class SystemStats(BaseModel):
    total_incidents: int
    active_incidents: int
    resolved_incidents: int
    avg_response_minutes: float
    units_available: int
    units_total: int
    incidents_by_type: dict
    incidents_by_severity: dict


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = ""
    role: Optional[str] = "citizen"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
