"""Cross-requirement evidence validator.

Analyzes related requirements and boosts scores when multiple related
requirements are COMPLIANT (corroborating evidence). This addresses the
"corroborating evidence" concept in the plan without changing Pass 1 logic.

Usage:
    from backend.scorer.cross_validation import CrossValidator
    cv = CrossValidator()
    boosted = cv.apply_boosts(requirement_results)

Design:
    - Loads the knowledge base to build a relationship graph from
      `related_requirements` fields.
    - For each COMPLIANT result, checks if >=50% of its related requirements
      are also COMPLIANT. If so, applies a small score boost (max +0.03).
    - This is a post-processing step called after the per-requirement
      analysis loop in main.py.
"""
import logging
from ..core import settings
from ..models.schemas import ComplianceStatus, RequirementResult
from ..matcher.engine import RequirementLoader

logger = logging.getLogger(__name__)


class CrossValidator:
    """Boost compliance scores based on corroborating evidence across related requirements."""

    # Maximum boost applied when corroborating evidence is found
    MAX_BOOST = 0.03

    # Minimum fraction of related requirements that must be COMPLIANT
    MIN_CORROBORATION_RATIO = 0.50

    def __init__(self):
        self._loader = RequirementLoader()
        self._relationship_graph: dict[str, list[str]] | None = None

    def _build_graph(self) -> dict[str, list[str]]:
        """Build a relationship graph from the knowledge base.

        Returns a dict mapping requirement_id -> list of related requirement_ids.
        """
        if self._relationship_graph is not None:
            return self._relationship_graph

        all_reqs = self._loader.load_all()
        graph: dict[str, list[str]] = {}

        for req_id, req_data in all_reqs.items():
            related = req_data.get("related_requirements", [])
            graph[req_id] = [r for r in related if isinstance(r, str)]

        self._relationship_graph = graph
        logger.debug("Built cross-requirement graph: %d nodes", len(graph))
        return graph

    def apply_boosts(self, results: dict[str, RequirementResult]) -> dict[str, RequirementResult]:
        """Apply cross-requirement evidence boosts to analysis results.

        Args:
            results: dict mapping requirement_id -> RequirementResult

        Returns:
            Updated results dict with boosted scores (same objects, modified in place).
        """
        graph = self._build_graph()
        boost_count = 0

        for req_id, result in results.items():
            related_ids = graph.get(req_id, [])
            if not related_ids:
                continue

            # Only boost COMPLIANT results that have corroborating evidence
            if result.overall_status != ComplianceStatus.COMPLIANT:
                continue

            # Count how many related requirements are COMPLIANT
            corroborating = sum(
                1 for rid in related_ids
                if rid in results and results[rid].overall_status == ComplianceStatus.COMPLIANT
            )
            total_related = len(related_ids)
            ratio = corroborating / total_related if total_related > 0 else 0

            if ratio >= self.MIN_CORROBORATION_RATIO:
                # Apply boost
                old_score = result.compliance_score
                result.compliance_score = round(
                    min(result.compliance_score + self.MAX_BOOST, 1.0), 4
                )
                boost_count += 1
                logger.info(
                    "Cross-requirement boost for %s: %.2f -> %.2f "
                    "(%d/%d related COMPLIANT, ratio=%.1f%%)",
                    req_id, old_score, result.compliance_score,
                    corroborating, total_related, ratio * 100,
                )

        if boost_count > 0:
            logger.info(
                "Cross-validation complete: %d requirements boosted by +%.2f",
                boost_count, self.MAX_BOOST,
            )

        return results
