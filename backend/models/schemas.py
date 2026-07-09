"""Pydantic models for ComplyScan."""
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class ComplianceStatus(str, Enum):
    """Compliance status for evidence items."""
    COMPLIANT = "Compliant"
    PARTIAL = "Partial"
    NON_COMPLIANT = "Non-Compliant"
    NOT_FOUND = "Not Found"


class EvidenceItem(BaseModel):
    """Single evidence item from requirement schema."""
    evidence_id: str
    name: str
    type: str
    required: bool
    critical: bool
    status: ComplianceStatus = ComplianceStatus.NOT_FOUND
    justification: str = ""
    llm_evaluated: bool = False
    llm_confidence: Optional[float] = None
    llm_justification: Optional[str] = None
    manually_overridden: bool = False
    override_note: str = ""
    llm_disagreement: bool = False
    llm_reasoning: Optional[str] = None  # Chain-of-thought reasoning from LLM


class RequirementResult(BaseModel):
    """Result for a single requirement check."""
    requirement_id: str
    chapter: str
    title: str
    description: str
    criticality: str
    evidence_items: list[EvidenceItem]
    overall_status: ComplianceStatus = ComplianceStatus.NOT_FOUND
    compliance_score: float = 0.0
    confidence_weight: Optional[float] = None
    disclaimer: str = "Advisory tool only \u2014 not a substitute for an official NABH assessment."


class AnalysisResponse(BaseModel):
    """Response from document analysis."""
    requirement_id: str
    results: list[RequirementResult]
    overall_score: float
    summary: dict
    disclaimer: str = "Advisory tool only \u2014 not a substitute for an official NABH assessment."


class UploadResponse(BaseModel):
    """Response from document upload."""
    document_id: str
    filename: str
    pages: int
    text_preview: str
    disclaimer: str = "Advisory tool only \u2014 not a substitute for an official NABH assessment."


class OverrideRequest(BaseModel):
    """Request to manually override an evidence item's compliance status.

    The client sends the full RequirementResult from a previous analysis
    plus the evidence ID to override and the new status. The server applies
    the override and recalculates the overall score.
    """
    result: RequirementResult
    evidence_id: str
    new_status: ComplianceStatus
    override_note: str = ""


class OverrideResponse(BaseModel):
    """Response from manual override."""
    result: RequirementResult
    disclaimer: str = "Advisory tool only \u2014 not a substitute for an official NABH assessment."
