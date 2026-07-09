"""Backend package for ComplyScan."""

# Import essential components
from .core import settings
from .models import ComplianceStatus, EvidenceItem, RequirementResult
from .matcher.engine import RequirementLoader, RequirementMatcher
from .semantic.analyzer import SemanticAnalyzer
from .scorer.cross_validation import CrossValidator
from .services.document_service import document_service
from .report.generator import save_report

__all__ = [
    "settings",
    "ComplianceStatus", 
    "EvidenceItem",
    "RequirementResult",
    "RequirementLoader",
    "RequirementMatcher",
    "SemanticAnalyzer",
    "CrossValidator",
    "document_service",
    "save_report"
]
