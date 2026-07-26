import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    dispatcher = "dispatcher"
    responder = "responder"
    citizen = "citizen"


class IncidentStatus(str, enum.Enum):
    reported = "reported"
    triaged = "triaged"
    dispatched = "dispatched"
    en_route = "en_route"
    on_scene = "on_scene"
    resolved = "resolved"
    closed = "closed"


class UnitStatus(str, enum.Enum):
    available = "available"
    dispatched = "dispatched"
    en_route = "en_route"
    on_scene = "on_scene"
    out_of_service = "out_of_service"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), default="")
    role = Column(Enum(UserRole), default=UserRole.citizen)
    created_at = Column(DateTime, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    reporter_name = Column(String(128), default="Anonymous")
    reporter_contact = Column(String(128), default="")
    description = Column(Text, nullable=False)
    incident_type = Column(String(32), default="other")       # fire/medical/crime/...
    severity = Column(String(16), default="moderate")          # low/moderate/high/critical
    priority_score = Column(Float, default=0.0)                # 0-100, AI computed
    casualties_reported = Column(Integer, default=0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(256), default="")
    status = Column(Enum(IncidentStatus), default=IncidentStatus.reported)
    ai_confidence = Column(Float, default=0.0)
    ai_notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    dispatches = relationship("Dispatch", back_populates="incident", cascade="all, delete-orphan")
    logs = relationship("IncidentLog", back_populates="incident", cascade="all, delete-orphan")


class ResponderUnit(Base):
    __tablename__ = "responder_units"
    id = Column(Integer, primary_key=True, index=True)
    call_sign = Column(String(32), unique=True, nullable=False)
    unit_type = Column(String(32), nullable=False)  # ambulance/fire_engine/police/hazmat_unit/rescue_team
    status = Column(Enum(UnitStatus), default=UnitStatus.available)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=1)
    crew_size = Column(Integer, default=2)
    base_station = Column(String(128), default="")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dispatches = relationship("Dispatch", back_populates="unit")


class Dispatch(Base):
    __tablename__ = "dispatches"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("responder_units.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    eta_minutes = Column(Float, default=0.0)
    distance_km = Column(Float, default=0.0)
    arrived_at = Column(DateTime, nullable=True)
    cleared_at = Column(DateTime, nullable=True)
    auto_assigned = Column(Boolean, default=True)

    incident = relationship("Incident", back_populates="dispatches")
    unit = relationship("ResponderUnit", back_populates="dispatches")


class IncidentLog(Base):
    """Append-only audit trail for every status transition / AI decision on an incident."""
    __tablename__ = "incident_logs"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    actor = Column(String(64), default="system-ai")
    action = Column(String(64), nullable=False)
    detail = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="logs")
