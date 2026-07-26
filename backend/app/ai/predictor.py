"""
IERCS AI Engine — Predictive Hotspot Analysis
================================================
Lightweight spatial density model that looks at recent incident history and
surfaces geographic hotspots so dispatchers can pre-position units *before*
the next call comes in, rather than purely reacting.

Approach: grid-based kernel density estimate. Incidents are bucketed into
~1km lat/lon cells; each cell's "weight" is a recency- and severity-weighted
sum of incidents that fell in it. This is intentionally simple (no external
GIS dependency) but captures the same signal real hotspot-policing /
resource-allocation tools use: recent + severe + clustered = high priority
for pre-positioning.
"""
from __future__ import annotations
import math
from collections import defaultdict
from datetime import datetime
from typing import List

from .classifier import SEVERITY_NUMERIC

# Roughly 1km at mid latitudes.
GRID_SIZE_DEG = 0.01


def _cell_key(lat: float, lon: float):
    return (round(lat / GRID_SIZE_DEG), round(lon / GRID_SIZE_DEG))


def _cell_center(key) -> tuple[float, float]:
    return key[0] * GRID_SIZE_DEG, key[1] * GRID_SIZE_DEG


def compute_hotspots(incidents: list, top_n: int = 8, window_days: int = 30) -> List[dict]:
    """
    incidents: ORM Incident rows (any status) from the last `window_days`.
    Returns top_n hotspot cells sorted by weight descending.
    """
    now = datetime.utcnow()
    cells = defaultdict(lambda: {"weight": 0.0, "count": 0, "types": defaultdict(int)})

    for inc in incidents:
        age_days = max((now - inc.created_at).total_seconds() / 86400.0, 0.0)
        if age_days > window_days:
            continue
        recency_factor = math.exp(-age_days / (window_days / 2))  # exponential decay
        severity_factor = SEVERITY_NUMERIC.get(inc.severity, 50) / 100.0
        key = _cell_key(inc.latitude, inc.longitude)
        cell = cells[key]
        cell["weight"] += recency_factor * severity_factor
        cell["count"] += 1
        cell["types"][inc.incident_type] += 1

    ranked = sorted(cells.items(), key=lambda kv: kv[1]["weight"], reverse=True)[:top_n]

    hotspots = []
    for key, data in ranked:
        lat, lon = _cell_center(key)
        dominant_type = max(data["types"].items(), key=lambda kv: kv[1])[0] if data["types"] else "other"
        hotspots.append({
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "weight": round(data["weight"], 3),
            "incident_count": data["count"],
            "dominant_type": dominant_type,
        })
    return hotspots


def location_risk_score(lat: float, lon: float, recent_incidents: list) -> float:
    """
    Used by the priority engine: how "hot" is this location historically?
    Returns 0-1. A brand new area with no history defaults to a moderate 0.3
    rather than 0 so first-ever incidents in a zone aren't under-prioritized.
    """
    key = _cell_key(lat, lon)
    matches = [i for i in recent_incidents if _cell_key(i.latitude, i.longitude) == key]
    if not matches:
        return 0.3
    score = min(len(matches) / 10.0, 1.0)
    return round(score, 2)
