"""Score calculation logic shared between engine and tests.

This module provides standalone scoring utilities that mirror the
logic in backend/matcher/engine.py but can be used independently.
Thresholds are imported from the centralized config.
"""
from backend.core import settings
from backend.models.schemas import ComplianceStatus


def calculate_weighted_score(evidence_items, weights=None):
    """Calculate a weighted compliance score from evidence items.

    Args:
        evidence_items: list of evidence items with .status attribute
        weights: optional dict mapping evidence_id -> weight multiplier.
                 If None, critical items get 2x weight, others 1x.
    """
    if not evidence_items:
        return ComplianceStatus.NOT_FOUND, 0.0

    total_weighted = 0.0
    total_weights = 0.0

    for item in evidence_items:
        if weights and item.evidence_id in weights:
            weight = weights[item.evidence_id]
        else:
            weight = 2.0 if item.critical else 1.0

        score = {
            ComplianceStatus.COMPLIANT: 1.0,
            ComplianceStatus.PARTIAL: 0.5,
            ComplianceStatus.NON_COMPLIANT: 0.0,
            ComplianceStatus.NOT_FOUND: 0.0,
        }.get(item.status, 0.0)

        total_weighted += score * weight
        total_weights += weight

    avg_score = total_weighted / total_weights if total_weights > 0 else 0.0
    return get_status_from_score(avg_score), avg_score


def get_status_from_score(score):
    """Map a numeric score (0-1) to a compliance status.

    Uses >= for all thresholds (consistent with engine.py and analyzer.py).
    Thresholds are imported from the centralized config.
    """
    if score >= settings.score_compliant:
        return ComplianceStatus.COMPLIANT
    elif score >= settings.score_partial:
        return ComplianceStatus.PARTIAL
    elif score >= settings.score_noncompliant_floor:
        return ComplianceStatus.NON_COMPLIANT
    else:
        return ComplianceStatus.NOT_FOUND


def format_score_percentage(score):
    """Format score as percentage string (e.g., 0.75 -> '75%')."""
    return f"{round(score * 100)}%"
