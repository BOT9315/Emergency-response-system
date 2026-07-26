import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from . import models
from .security import hash_password
from .ai.classifier import engine as ai_engine

# Demo city center (adjust to any real city — defaults roughly to a generic
# metro area so the map has a sensible default view out of the box).
CITY_LAT, CITY_LON = 28.6139, 77.2090  # New Delhi, as a populous reference point

UNIT_SEED = [
    ("ENGINE-1", "fire_engine", "Central Fire Station"),
    ("ENGINE-2", "fire_engine", "North Fire Station"),
    ("ENGINE-3", "fire_engine", "South Fire Station"),
    ("AMB-1", "ambulance", "City Hospital"),
    ("AMB-2", "ambulance", "East Medical Center"),
    ("AMB-3", "ambulance", "West Medical Center"),
    ("AMB-4", "ambulance", "Central Hospital"),
    ("POLICE-1", "police", "Central Precinct"),
    ("POLICE-2", "police", "North Precinct"),
    ("POLICE-3", "police", "South Precinct"),
    ("POLICE-4", "police", "East Precinct"),
    ("HAZMAT-1", "hazmat_unit", "Regional Hazmat Base"),
    ("RESCUE-1", "rescue_team", "Urban Search & Rescue HQ"),
]

SAMPLE_DESCRIPTIONS = [
    ("Small kitchen fire, contained", "fire", "low"),
    ("Two car collision with minor injuries", "accident", "moderate"),
    ("Chest pain reported, patient conscious", "medical", "high"),
    ("Break in reported overnight", "crime", "moderate"),
    ("Gas smell near residential block", "hazmat", "high"),
    ("Street flooding after heavy rain", "natural_disaster", "moderate"),
    ("Minor fender bender, no injuries", "accident", "low"),
    ("Suspicious activity near the market", "crime", "low"),
]


def _jitter(base, spread=0.05):
    return base + random.uniform(-spread, spread)


def seed_if_empty(db: Session):
    if db.query(models.User).count() == 0:
        db.add(models.User(
            username="admin", hashed_password=hash_password("admin123"),
            full_name="System Administrator", role=models.UserRole.admin,
        ))
        db.add(models.User(
            username="dispatcher1", hashed_password=hash_password("dispatch123"),
            full_name="Priya Sharma", role=models.UserRole.dispatcher,
        ))

    if db.query(models.ResponderUnit).count() == 0:
        for call_sign, unit_type, base in UNIT_SEED:
            db.add(models.ResponderUnit(
                call_sign=call_sign, unit_type=unit_type,
                latitude=_jitter(CITY_LAT), longitude=_jitter(CITY_LON),
                status=models.UnitStatus.available, base_station=base,
                capacity=4 if unit_type == "ambulance" else 6, crew_size=3,
            ))

    if db.query(models.Incident).count() == 0:
        for days_ago in range(30, 0, -1):
            if random.random() > 0.55:
                continue
            desc, itype, sev = random.choice(SAMPLE_DESCRIPTIONS)
            result = ai_engine.classify(desc)
            priority = ai_engine.compute_priority(
                incident_type=itype, severity=sev, casualties=random.choice([0, 0, 0, 1, 2]),
                location_risk=0.5, age_minutes=0, model_confidence=result.type_confidence,
            )
            created = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            incident = models.Incident(
                reporter_name=random.choice(["Anonymous", "R. Kumar", "S. Patel", "A. Singh"]),
                description=desc, incident_type=itype, severity=sev, priority_score=priority,
                casualties_reported=random.choice([0, 0, 0, 1]),
                latitude=_jitter(CITY_LAT), longitude=_jitter(CITY_LON),
                status=models.IncidentStatus.resolved,
                ai_confidence=result.type_confidence, ai_notes=result.notes,
                created_at=created, updated_at=created,
                resolved_at=created + timedelta(minutes=random.randint(8, 45)),
            )
            db.add(incident)

    db.commit()
