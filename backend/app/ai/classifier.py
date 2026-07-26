"""
IERCS AI Engine — Incident Understanding
=========================================
Turns a free-text incident report into a structured, actionable record:

    raw text  ->  (incident_type, severity, confidence)  ->  priority_score (0-100)

Two lightweight but *real* trained models power this (TF-IDF + Multinomial
Naive Bayes), one for incident-type and one for severity. They train in
milliseconds on process start from the synthetic corpus in train_data.py, so
the whole system is self-contained (no external API key, no network call,
no GPU) while still doing genuine supervised text classification rather than
a hardcoded keyword table.

A keyword-based risk booster sits on top of the ML output to catch
high-stakes phrases the small training set may not fully cover (e.g. "not
breathing", "trapped", "explosion") — this mirrors how real triage systems
combine statistical models with safety-critical override rules.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from .train_data import get_texts_labels_severity
from ..config import PRIORITY_WEIGHTS, INCIDENT_TYPE_BASE_RISK, SEVERITY_LEVELS

SEVERITY_NUMERIC = {"low": 25, "moderate": 50, "high": 75, "critical": 100}

# Phrases that, if present, force a minimum severity floor regardless of the
# model's own confidence — a critical safety net for life-threatening cases.
CRITICAL_OVERRIDE_PHRASES = [
    "not breathing", "unresponsive", "trapped", "explosion", "collapsed",
    "shots fired", "hostage", "drowning", "cardiac", "unconscious and pale",
    "no pulse", "severe bleeding", "building collapse",
]


@dataclass
class ClassificationResult:
    incident_type: str
    type_confidence: float
    severity: str
    severity_confidence: float
    notes: str = ""


class IncidentAIEngine:
    """Singleton-style engine: instantiate once, reuse across requests."""

    def __init__(self):
        texts, types, severities = get_texts_labels_severity()
        self._type_pipeline: Pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("clf", MultinomialNB(alpha=0.3)),
        ])
        self._severity_pipeline: Pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("clf", MultinomialNB(alpha=0.3)),
        ])
        self._type_pipeline.fit(texts, types)
        self._severity_pipeline.fit(texts, severities)
        self._trained_on = len(texts)

    # ------------------------------------------------------------------
    def classify(self, description: str) -> ClassificationResult:
        text = description.strip()
        if not text:
            return ClassificationResult("other", 0.0, "low", 0.0, "Empty report")

        type_probs = self._type_pipeline.predict_proba([text])[0]
        type_classes = self._type_pipeline.named_steps["clf"].classes_
        best_type_idx = type_probs.argmax()
        incident_type = type_classes[best_type_idx]
        type_conf = float(type_probs[best_type_idx])

        sev_probs = self._severity_pipeline.predict_proba([text])[0]
        sev_classes = self._severity_pipeline.named_steps["clf"].classes_
        best_sev_idx = sev_probs.argmax()
        severity = sev_classes[best_sev_idx]
        sev_conf = float(sev_probs[best_sev_idx])

        notes = ""
        lowered = text.lower()
        hit = next((p for p in CRITICAL_OVERRIDE_PHRASES if p in lowered), None)
        if hit and SEVERITY_NUMERIC[severity] < SEVERITY_NUMERIC["critical"]:
            notes = f"Escalated to critical: safety-critical phrase detected ('{hit}')"
            severity = "critical"
            sev_conf = max(sev_conf, 0.95)

        return ClassificationResult(
            incident_type=incident_type,
            type_confidence=round(type_conf, 3),
            severity=severity,
            severity_confidence=round(sev_conf, 3),
            notes=notes,
        )

    # ------------------------------------------------------------------
    def compute_priority(
        self,
        incident_type: str,
        severity: str,
        casualties: int = 0,
        location_risk: float = 0.5,
        age_minutes: float = 0.0,
        model_confidence: float = 0.8,
    ) -> float:
        """
        Weighted multi-factor priority score, 0 (low) - 100 (drop everything).
        See config.PRIORITY_WEIGHTS for the tunable weighting.
        """
        severity_component = SEVERITY_NUMERIC.get(severity, 50) * (0.6 + 0.4 * model_confidence)
        casualty_component = min(casualties * 20, 100)
        type_risk_component = INCIDENT_TYPE_BASE_RISK.get(incident_type, 0.4) * 100
        location_component = max(0.0, min(location_risk, 1.0)) * 100
        # Waiting longer without dispatch increases urgency, saturating at 30 min.
        time_component = min(age_minutes / 30.0, 1.0) * 100

        score = (
            PRIORITY_WEIGHTS["severity_model"] * severity_component
            + PRIORITY_WEIGHTS["casualties"] * casualty_component
            + PRIORITY_WEIGHTS["incident_type_risk"] * type_risk_component
            + PRIORITY_WEIGHTS["location_risk"] * location_component
            + PRIORITY_WEIGHTS["time_decay"] * time_component
        )
        return round(max(0.0, min(score, 100.0)), 1)


# Module-level singleton reused by routers (training happens once at import).
engine = IncidentAIEngine()
