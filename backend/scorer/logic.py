"""Compliance scoring logic."""
from ..models.schemas import ComplianceStatus, EvidenceItem


class ComplianceScorer:
    """Calculate compliance scores for requirements."""
    
    @staticmethod
    def calculate_evidence_score(items: list[EvidenceItem]) -> float:
        """Calculate weighted average score for evidence items."""
        if not items:
            return 0.0
        
        total_weighted = 0.0
        total_weights = 0.0
        
        for item in items:
            weight = 1.0 if item.critical else 0.5
            score = {
                ComplianceStatus.COMPLIANT: 1.0,
                ComplianceStatus.PARTIAL: 0.5,
                ComplianceStatus.NON_COMPLIANT: 0.2,
                ComplianceStatus.NOT_FOUND: 0.0
            }.get(item.status, 0.0)
            
            total_weighted += score * weight
            total_weights += weight
        
        return total_weighted / total_weights if total_weights > 0 else 0.0
    
    @staticmethod
    def get_status_from_score(score: float) -> ComplianceStatus:
        """Convert numeric score to compliance status."""
        if score >= 0.9:
            return ComplianceStatus.COMPLIANT
        elif score >= 0.5:
            return ComplianceStatus.PARTIAL
        elif score > 0:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.NOT_FOUND
    
    @staticmethod
    def summarize_results(results: list[tuple]) -> dict:
        """Summarize analysis results.
        
        Args:
            results: List of (requirement_id, status, score) tuples
            
        Returns:
            Summary statistics
        """
        total = len(results)
        compliant = sum(1 for r in results if r[1] == ComplianceStatus.COMPLIANT)
        partial = sum(1 for r in results if r[1] == ComplianceStatus.PARTIAL)
        non_compliant = sum(1 for r in results if r[1] == ComplianceStatus.NON_COMPLIANT)
        not_found = sum(1 for r in results if r[1] == ComplianceStatus.NOT_FOUND)
        
        avg_score = sum(r[2] for r in results) / total if total > 0 else 0.0
        
        return {
            "total_requirements": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": non_compliant,
            "not_found": not_found,
            "average_score": round(avg_score, 2),
            "overall_status": ComplianceScorer.get_status_from_score(avg_score).value
        }