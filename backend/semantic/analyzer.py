"""Semantic analyzer — orchestrates the dual-pass LLM enhancement.

Key improvements over the original:
1. **Intelligent text section selection**: Instead of sending the first 6000 chars
   of the full document, extracts relevant sections for each evidence item using
   expected_locations and keyword hits from the evidence schema.
2. **Tiered confidence thresholds**: Different thresholds depending on Pass 1 status
   (e.g., higher bar for NOT_FOUND → COMPLIANT than PARTIAL → COMPLIANT).
3. **Uncertainty handling**: LLM can express uncertainty (null), which is respected.
4. **Strict audit prompt**: Prompt explicitly requires verbatim quotes and forbids inference.
5. **Disagreement monitoring**: Flags when LLM overrides a strong Pass 1 verdict.
"""

import asyncio
import re
import logging
from typing import Optional

from ..core.config import settings
from ..models.schemas import ComplianceStatus, EvidenceItem, RequirementResult
from .llm_client import LLMClient
from .prompts import build_evidence_prompt

logger = logging.getLogger(__name__)

# Score mapping for recalculation
_SCORE_MAP = {
    ComplianceStatus.COMPLIANT: 1.0,
    ComplianceStatus.PARTIAL: 0.5,
    ComplianceStatus.NON_COMPLIANT: 0.2,
    ComplianceStatus.NOT_FOUND: 0.0,
}

# Maximum context to extract per section/location
_MAX_SECTION_CHARS = 600
_MAX_KEYWORD_CONTEXT_CHARS = 300
_MAX_TOTAL_EXCERPT_CHARS = 3000


def _recalculate_score(evidence_items: list[EvidenceItem]) -> tuple[ComplianceStatus, float]:
    """Recalculate weighted compliance score (mirrors RequirementMatcher._calculate_score).

    Critical evidence items are weighted 2x more than non-critical ones.
    Score maps: Compliant=1.0, Partial=0.5, Non-Compliant=0.2, Not Found=0.0
    """
    if not evidence_items:
        return ComplianceStatus.NOT_FOUND, 0.0

    total_weighted = 0.0
    total_weights = 0.0

    for item in evidence_items:
        weight = 2.0 if item.critical else 1.0
        score = _SCORE_MAP.get(item.status, 0.0)
        total_weighted += score * weight
        total_weights += weight

    avg_score = total_weighted / total_weights if total_weights > 0 else 0.0

    if avg_score >= 0.85:
        overall_status = ComplianceStatus.COMPLIANT
    elif avg_score >= 0.4:
        overall_status = ComplianceStatus.PARTIAL
    elif avg_score > 0:
        overall_status = ComplianceStatus.NON_COMPLIANT
    else:
        overall_status = ComplianceStatus.NOT_FOUND

    return overall_status, avg_score


def _get_tiered_threshold(pass1_status: ComplianceStatus) -> float:
    """Return the confidence threshold for overriding a given Pass 1 status.

    Higher thresholds for more dramatic upgrades:
      - NOT_FOUND → COMPLIANT: 0.85 (high bar — LLM must be very confident)
      - PARTIAL → COMPLIANT: 0.75 (moderate — some evidence already found)
      - NON_COMPLIANT → COMPLIANT: 0.80 (high — Pass 1 found weak evidence)
      - Non-compliant refinements (e.g., NOT_FOUND→PARTIAL): 0.70 (lower bar)
    """
    mapping = {
        ComplianceStatus.NOT_FOUND: settings.llm_threshold_notfound_to_compliant,
        ComplianceStatus.PARTIAL: settings.llm_threshold_partial_to_compliant,
        ComplianceStatus.NON_COMPLIANT: settings.llm_threshold_noncomp_to_compliant,
    }
    return mapping.get(pass1_status, settings.llm_confidence_threshold)


def _select_relevant_excerpt(
    full_text: str,
    evidence_item: EvidenceItem,
    evidence_schema_item: dict,
) -> str:
    """Build a focused text excerpt for an evidence item using schema knowledge.

    Instead of sending the first N chars of the full document, this function:
    1. Searches for `expected_locations` (section headers) from the evidence schema
    2. Extracts paragraphs/sections near those locations
    3. Also extracts context near keyword/concept hits
    4. Combines into a focused excerpt of ~3000 chars

    Fallback: if no locations or keywords are found, returns the first 4000 chars
    of the document (not 6000 — shorter because the prompt is now more focused).

    Args:
        full_text: The complete document text.
        evidence_item: The EvidenceItem being evaluated.
        evidence_schema_item: The raw evidence schema dict from the knowledge base
                              (contains search_strategy, extraction_hints, etc.).

    Returns:
        A string of relevant excerpts for the LLM prompt.
    """
    text_lower = full_text.lower()
    excerpts: list[str] = []

    search_strategy = evidence_schema_item.get("search_strategy", {})
    expected_locations = search_strategy.get("expected_locations", [])
    keywords = search_strategy.get("keywords", [])
    concepts = search_strategy.get("semantic_concepts", [])
    extraction_hints = evidence_schema_item.get("extraction_hints", {})

    # --- Extract from expected locations ---
    for location in expected_locations:
        if not isinstance(location, str) or len(location) < 3:
            continue
        # Try to find the location header in the text
        # Match "Section X.Y" or plain section names
        loc_lower = location.lower()
        idx = text_lower.find(loc_lower)
        if idx == -1:
            continue

        # Extract from the location heading onwards (up to _MAX_SECTION_CHARS chars)
        start = idx
        end = min(start + _MAX_SECTION_CHARS, len(full_text))

        # Try to find the next section heading to end the excerpt cleanly
        section_pattern = re.compile(r'\n(?=\d+\.\d+\s|\d+\)\s|[A-Z][A-Za-z\s]{2,30}\n)', re.MULTILINE)
        next_section = section_pattern.search(full_text, end)
        if next_section:
            end = min(next_section.start(), start + _MAX_SECTION_CHARS)

        snippet = full_text[start:end].strip()
        if len(snippet) > 40:  # Meaningful snippet
            excerpts.append(f"[Section: {location}]\n{snippet}")

        extra = end - start
        if extra >= _MAX_SECTION_CHARS:
            break  # Already have enough from this section

    # --- Extract from keyword matches ---
    all_terms = list(keywords) + list(concepts)
    found_terms = set()
    for term in all_terms:
        if not isinstance(term, str) or len(term) < 3:
            continue
        term_lower = term.lower()
        idx = 0
        while len(excerpts) * _MAX_KEYWORD_CONTEXT_CHARS < _MAX_TOTAL_EXCERPT_CHARS:
            idx = text_lower.find(term_lower, idx)
            if idx == -1:
                break
            found_terms.add(term)

            # Skip if already covered by a location excerpt
            already_covered = False
            current_line_start = full_text.rfind('\n', 0, idx)
            if current_line_start == -1:
                current_line_start = max(0, idx - 60)
            current_line = full_text[current_line_start:idx + len(term) + 100]
            for existing in excerpts:
                if current_line[:50] in existing:
                    already_covered = True
                    break
            if already_covered:
                idx += len(term)
                continue

            # Extract surrounding context (a few lines)
            para_start = max(0, idx - 150)
            para_end = min(len(full_text), idx + len(term) + 200)
            snippet = full_text[para_start:para_end].strip()
            if len(snippet) > 30:
                excerpts.append(f"[Near keyword: {term}]\n...{snippet}...")

            idx += len(term)

    # --- Extract from extraction hint patterns ---
    for hint_type, hint_values in extraction_hints.items():
        if not isinstance(hint_values, list):
            continue
        for hint in hint_values[:3]:  # Top 3 hints per type
            if not isinstance(hint, str) or len(hint) < 3:
                continue
            hint_lower = hint.lower()
            idx = text_lower.find(hint_lower)
            if idx == -1:
                continue

            # Check not already covered
            para_start = max(0, idx - 100)
            current = full_text[para_start:idx + len(hint) + 100]
            already_covered = any(current[:50] in e for e in excerpts)
            if already_covered:
                continue

            para_end = min(len(full_text), idx + len(hint) + 150)
            snippet = full_text[max(0, idx - 80):para_end].strip()
            if len(snippet) > 20:
                excerpts.append(f"[Hint: {hint_type}]\n...{snippet}...")

    # --- Combine excerpts ---
    combined = "\n\n---\n\n".join(excerpts)

    # Fallback: if nothing relevant found, use document start
    if not combined.strip():
        logger.info(
            "No relevant sections found for %s, using document start",
            evidence_item.evidence_id,
        )
        return full_text[:4000]

    # Truncate to max excerpt length
    if len(combined) > _MAX_TOTAL_EXCERPT_CHARS:
        combined = combined[:_MAX_TOTAL_EXCERPT_CHARS]
        # Try to break at a clean boundary
        last_break = combined.rfind("\n\n---\n\n")
        if last_break > _MAX_TOTAL_EXCERPT_CHARS * 0.7:
            combined = combined[:last_break]
        combined += "\n\n[... excerpt truncated ...]"

    logger.debug(
        "Built focused excerpt for %s: %d chars from %d locations/keywords (full doc: %d chars)",
        evidence_item.evidence_id,
        len(combined),
        len(excerpts),
        len(full_text),
    )

    return combined


class SemanticAnalyzer:
    """Orchestrate the dual-pass LLM enhancement of evidence analysis.

    Takes a RequirementResult from Pass 1 (keyword/concept/hint matching),
    runs LLM analysis on evidence items that scored below COMPLIANT,
    and merges high-confidence LLM results back into the result.

    Improvements over the original implementation:
    - Intelligent section selection per evidence item
    - Tiered confidence thresholds
    - Disagreement monitoring and logging
    - Respects LLM uncertainty (null is_compliant)
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the semantic analyzer.

        Args:
            llm_client: An LLMClient instance. If None, one is created
                        from the application settings.
        """
        if llm_client is not None:
            self._llm = llm_client
        else:
            self._llm = LLMClient(
                api_token=settings.cf_api_token,
                account_id=settings.cf_account_id,
                model=settings.cf_llm_model,
                timeout=settings.llm_timeout,
            )

    async def enhance(
        self,
        result: RequirementResult,
        text: str,
        *,
        evidence_schema: Optional[list[dict]] = None,
    ) -> RequirementResult:
        """Run Pass 2 LLM analysis on non-compliant items and merge results.

        Args:
            result: RequirementResult from Pass 1 (keyword matching).
            text: Original document text (for constructing focused excerpts).
            evidence_schema: Optional list of raw evidence schema dicts from the
                             knowledge base JSON. Provides expected_locations and
                             extraction_hints for intelligent section selection.
                             If omitted, falls back to using document start.

        Returns:
            An updated RequirementResult with LLM-enhanced evidence items.
            Items where LLM confidence >= tiered threshold have their status
            overridden. The overall status and score are recalculated.
            Disagreement flags are set on items where LLM overrides Pass 1.
        """
        # Build a lookup from evidence_id to raw schema dict
        schema_lookup: dict[str, dict] = {}
        if evidence_schema:
            for item_schema in evidence_schema:
                eid = item_schema.get("evidence_id", "")
                if eid:
                    schema_lookup[eid] = item_schema

        # Identify items that need LLM evaluation (below COMPLIANT)
        needs_llm = [
            item for item in result.evidence_items
            if item.status != ComplianceStatus.COMPLIANT
        ]

        if not needs_llm:
            logger.info(
                "All %d evidence items already COMPLIANT — skipping LLM pass",
                len(result.evidence_items),
            )
            return result

        logger.info(
            "Running LLM pass on %d/%d evidence items (tiered thresholds)",
            len(needs_llm),
            len(result.evidence_items),
        )

        # Build prompts for each item with intelligent section selection
        tasks = []
        for item in needs_llm:
            schema_item = schema_lookup.get(item.evidence_id, {})
            search_strategy = schema_item.get("search_strategy", {})

            # Intelligent section selection: focus on relevant parts of the document
            focused_text = _select_relevant_excerpt(text, item, schema_item)

            # Extract expected_locations and extraction_hints from schema
            expected_locations = search_strategy.get("expected_locations", [])
            extraction_hints = schema_item.get("extraction_hints", {})
            keywords = search_strategy.get("keywords", [])
            concepts = search_strategy.get("semantic_concepts", [])

            prompt = build_evidence_prompt(
                evidence_id=item.evidence_id,
                name=item.name,
                type=item.type,
                required=item.required,
                critical=item.critical,
                keywords=keywords,
                concepts=concepts,
                text=focused_text,
                expected_locations=expected_locations,
                extraction_hints=extraction_hints,
                pass1_status=item.status.value,
                pass1_justification=item.justification,
            )
            tasks.append(self._llm.analyze(prompt))

        llm_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge LLM results back into evidence items
        llm_count = 0
        override_count = 0
        disagreement_count = 0

        for item, llm_res in zip(needs_llm, llm_results):
            if isinstance(llm_res, Exception):
                logger.error(
                    "LLM analysis failed for %s: %s",
                    item.evidence_id, llm_res,
                )
                continue

            llm_count += 1
            confidence = llm_res.get("confidence", 0.0)
            is_compliant = llm_res.get("is_compliant")  # None = uncertain
            justification = llm_res.get("justification", "")

            # Populate the LLM metadata fields
            item.llm_evaluated = True
            item.llm_confidence = confidence
            item.llm_justification = justification if justification else None

            # Get the tiered threshold based on Pass 1 status
            threshold = _get_tiered_threshold(item.status)

            # Handle LLM uncertainty (null is_compliant)
            if is_compliant is None:
                logger.info(
                    "LLM uncertain for %s (confidence=%.2f, threshold=%.2f) — keeping Pass 1 status %s",
                    item.evidence_id, confidence, threshold, item.status.value,
                )
                item.justification = (
                    f"LLM uncertain: {justification}"
                    if justification
                    else item.justification
                )
                continue

            # Check if confidence meets the tiered threshold
            if confidence >= threshold:
                if is_compliant:
                    # OVERRIDE: LLM found evidence where Pass 1 didn't find enough
                    pass1_status = item.status

                    # Check for strong disagreement
                    # NOT_FOUND → COMPLIANT at ≥0.85: LLM found evidence Pass 1 missed entirely
                    # PARTIAL → COMPLIANT at ≥0.75: LLM upgraded incomplete Pass 1 evidence
                    if (pass1_status == ComplianceStatus.NOT_FOUND and confidence >= 0.85) or \
                       (pass1_status == ComplianceStatus.PARTIAL and confidence >= 0.75):
                        item.llm_disagreement = True
                        disagreement_count += 1
                        logger.warning(
                            "HIGH DISAGREEMENT: LLM overrode %s from %s→COMPLIANT "
                            "(confidence=%.2f, threshold=%.2f). Review recommended. %s",
                            item.evidence_id, pass1_status.value, confidence,
                            threshold, justification[:120],
                        )

                    item.status = ComplianceStatus.COMPLIANT
                    item.justification = (
                        f"LLM override: {justification}"
                        if justification
                        else "LLM override: Evidence considered sufficient"
                    )
                    override_count += 1
                    logger.info(
                        "LLM overrode %s %s→COMPLIANT (confidence=%.2f, threshold=%.2f): %.100s",
                        item.evidence_id, pass1_status.value, confidence,
                        threshold, justification,
                    )
                else:
                    # LLM says not compliant — keep Pass 1 status but note LLM agreed
                    if item.status in (ComplianceStatus.NOT_FOUND, ComplianceStatus.NON_COMPLIANT):
                        item.justification = (
                            f"LLM confirmed non-compliant: {justification}"
                            if justification
                            else item.justification
                        )
                        logger.info(
                            "LLM confirmed %s %s (confidence=%.2f, threshold=%.2f): %.100s",
                            item.evidence_id, item.status.value, confidence,
                            threshold, justification,
                        )
                    else:
                        # PARTIAL item where LLM says not compliant — lower confidence
                        item.justification = (
                            f"LLM suggests non-compliant: {justification}"
                            if justification
                            else item.justification
                        )
                        logger.info(
                            "LLM downgrade suggestion for %s (confidence=%.2f, threshold=%.2f): %.100s",
                            item.evidence_id, confidence, threshold, justification,
                        )
            else:
                # Confidence below threshold — log but keep Pass 1 status
                logger.info(
                    "LLM below threshold for %s (confidence=%.2f < threshold=%.2f, is_compliant=%s) — "
                    "keeping Pass 1 status %s",
                    item.evidence_id, confidence, threshold, is_compliant,
                    item.status.value,
                )

        # Recalculate overall status and score
        new_status, new_score = _recalculate_score(result.evidence_items)

        logger.info(
            "LLM pass complete: %d items evaluated, %d overrides, "
            "%d high-disagreement flags. Score: %.2f → %.2f",
            llm_count, override_count, disagreement_count,
            result.compliance_score, new_score,
        )

        result.overall_status = new_status
        result.compliance_score = new_score

        return result
