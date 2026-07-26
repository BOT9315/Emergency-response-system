"""
Central configuration for the Intelligent Emergency Response Coordination System (IERCS).
All tunables for the AI engine, security, and database live here so the rest of the
codebase never hardcodes a magic number.
"""
import os
from datetime import timedelta

# --- Security -----------------------------------------------------------
SECRET_KEY = os.environ.get("IERCS_SECRET_KEY", "dev-secret-change-in-production-3f9a7c")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=12)

# --- Database -------------------------------------------------------------
DATABASE_URL = os.environ.get("IERCS_DATABASE_URL", "sqlite:///./iercs.db")

# --- AI Engine tunables ----------------------------------------------------
# Priority score weights (must sum to 1.0). Used by ai/classifier.py to turn a
# raw incident report into a 0-100 dispatch priority.
PRIORITY_WEIGHTS = {
    "severity_model": 0.40,   # ML text-severity classifier confidence
    "casualties": 0.25,       # reported injured/trapped persons
    "incident_type_risk": 0.15,  # baseline risk of the incident category
    "location_risk": 0.10,    # historical incident density at location
    "time_decay": 0.10,       # how long the incident has been waiting
}

# Baseline risk per incident category (0-1), used both for priority scoring
# and for default unit-type routing.
INCIDENT_TYPE_BASE_RISK = {
    "fire": 0.90,
    "medical": 0.85,
    "crime": 0.65,
    "accident": 0.70,
    "natural_disaster": 0.95,
    "hazmat": 0.88,
    "other": 0.40,
}

# Which responder unit types are appropriate for each incident type, in
# priority order. Used by the dispatch optimizer.
UNIT_ROUTING = {
    "fire": ["fire_engine", "ambulance", "police"],
    "medical": ["ambulance", "police"],
    "crime": ["police", "ambulance"],
    "accident": ["ambulance", "police", "fire_engine"],
    "natural_disaster": ["fire_engine", "ambulance", "police", "rescue_team"],
    "hazmat": ["hazmat_unit", "fire_engine", "ambulance"],
    "other": ["police"],
}

# Severity levels output by the classifier
SEVERITY_LEVELS = ["low", "moderate", "high", "critical"]

# Average city driving speed (km/h) used to estimate ETA when routing data
# isn't available (kept as a pure-python fallback, no external maps API key
# required so the project runs fully offline).
AVG_RESPONSE_SPEED_KMH = 38.0

# How many past days count toward the hotspot/prediction engine.
PREDICTION_WINDOW_DAYS = 30
