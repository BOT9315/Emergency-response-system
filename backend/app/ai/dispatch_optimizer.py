"""
IERCS AI Engine — Dispatch Optimization
=========================================
Given a set of pending incidents (each with a priority score) and a pool of
responder units, decide *who goes where*.

Algorithm (priority-weighted nearest-available assignment):
  1. Sort incidents by priority_score descending — the most critical incident
     always gets first pick of resources, mirroring real-world triage.
  2. For each incident, filter units to the types appropriate for that
     incident category (see config.UNIT_ROUTING), keep only 'available'
     units, and pick the one with the lowest travel time (great-circle
     distance / avg city speed as a network-free ETA proxy).
  3. Remove the assigned unit from the pool and continue down the list.

This greedy-by-priority approach is the same family of algorithm real CAD
(Computer-Aided Dispatch) systems use for real-time assignment, favoured
over a full Hungarian/optimal-assignment solve because incidents arrive
continuously and must be dispatched in milliseconds, not batched — but a
batch `optimize_assignments` entry point is included for the case where
several incidents are triaged in the same tick.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Optional

from ..config import UNIT_ROUTING, AVG_RESPONSE_SPEED_KMH


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def eta_minutes(distance_km: float, avg_speed_kmh: float = AVG_RESPONSE_SPEED_KMH) -> float:
    if avg_speed_kmh <= 0:
        return float("inf")
    # +1.5 min fixed "wheels rolling" dispatch/turnout delay, standard in EMS response models.
    return round((distance_km / avg_speed_kmh) * 60 + 1.5, 1)


@dataclass
class AssignmentCandidate:
    unit_id: int
    call_sign: str
    unit_type: str
    distance_km: float
    eta_minutes: float


def best_units_for_incident(
    incident_type: str,
    incident_lat: float,
    incident_lon: float,
    available_units: list,
    max_results: int = 3,
) -> List[AssignmentCandidate]:
    """
    Rank the best available units for a single incident. `available_units`
    is a list of ORM ResponderUnit objects already filtered to status == available.
    Returns candidates sorted by ETA ascending, respecting the preferred
    unit-type ordering for this incident category.
    """
    preferred_types = UNIT_ROUTING.get(incident_type, UNIT_ROUTING["other"])
    candidates: List[AssignmentCandidate] = []

    for unit in available_units:
        if unit.unit_type not in preferred_types:
            continue
        dist = haversine_km(incident_lat, incident_lon, unit.latitude, unit.longitude)
        candidates.append(AssignmentCandidate(
            unit_id=unit.id,
            call_sign=unit.call_sign,
            unit_type=unit.unit_type,
            distance_km=round(dist, 2),
            eta_minutes=eta_minutes(dist),
        ))

    def sort_key(c: AssignmentCandidate):
        # Primary: how "preferred" the unit type is for this incident (fire
        # engine before police for a fire, etc). Secondary: ETA.
        type_rank = preferred_types.index(c.unit_type) if c.unit_type in preferred_types else 99
        return (type_rank, c.eta_minutes)

    candidates.sort(key=sort_key)
    return candidates[:max_results]


@dataclass
class BatchAssignment:
    incident_id: int
    unit_id: Optional[int]
    call_sign: Optional[str]
    distance_km: Optional[float]
    eta_minutes: Optional[float]
    reason: str


def optimize_assignments(pending_incidents: list, available_units: list) -> List[BatchAssignment]:
    """
    Batch version: assign as many pending incidents as possible in one pass,
    processing highest priority_score first and removing each unit from the
    pool once assigned so two incidents never get double-booked with the
    same unit in the same tick.
    """
    results: List[BatchAssignment] = []
    pool = list(available_units)
    ordered = sorted(pending_incidents, key=lambda i: i.priority_score, reverse=True)

    for incident in ordered:
        candidates = best_units_for_incident(
            incident.incident_type, incident.latitude, incident.longitude, pool
        )
        if not candidates:
            results.append(BatchAssignment(
                incident_id=incident.id, unit_id=None, call_sign=None,
                distance_km=None, eta_minutes=None,
                reason="No available unit of a suitable type in range",
            ))
            continue

        chosen = candidates[0]
        results.append(BatchAssignment(
            incident_id=incident.id,
            unit_id=chosen.unit_id,
            call_sign=chosen.call_sign,
            distance_km=chosen.distance_km,
            eta_minutes=chosen.eta_minutes,
            reason=f"Nearest suitable {chosen.unit_type} unit ({chosen.distance_km} km)",
        ))
        pool = [u for u in pool if u.id != chosen.unit_id]

    return results
