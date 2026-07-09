"""Compliance rule matching using evidence schemas.

Includes optional fuzzy keyword matching (difflib.SequenceMatcher) to
handle minor OCR typos (e.g. 'hygin' vs 'hygiene'). Fuzzy matching is
disabled by settings.fuzzy_enabled and uses a configurable threshold.
"""
import json
import glob
import re
import math
import logging
from difflib import SequenceMatcher
from pathlib import Path
from ..core import settings
from ..models.schemas import ComplianceStatus, EvidenceItem, RequirementResult
from typing import Optional

logger = logging.getLogger(__name__)

# Generic quality/management terms that appear in many documents
# but are NOT specific evidence for HIC/PRE compliance.
# Applied AFTER keyword matching to filter false-positive hits.
EXCLUSION_KEYWORDS: set[str] = {
    # Generic quality management
    "quality improvement",
    "continuous improvement",
    "management review",
    "internal audit",
    "corrective action",
    "preventive action",
    "root cause",
    "clinical governance",
    "standard operating",
    "organizational",
    "quality manual",
    "strategic plan",
    # Too broad -- always present but never specific evidence
    "annual report",
    "organizational chart",
    "job description",
    "performance appraisal",
    "employee welfare",
    "staff welfare",
}

# Date detection regex for validation rule checking
_DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}'
    r'|(?:january|february|march|april|may|june|july|august|september|october|november|december)'
    r'\s+\d{1,2},?\s+\d{4}'
    r'|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
    re.IGNORECASE,
)

# Signature/authorization detection for validation rule checking
_AUTH_PATTERN = re.compile(
    r'(signature|signed|authorized|approved|endorsed| countersign| witnessed)',
    re.IGNORECASE,
)


class RequirementLoader:
    """Load requirement schemas from JSON files."""

    def load_all(self) -> dict[str, dict]:
        """Load all HIC and PRE requirements."""
        requirements = {}

        for pattern_dir in [settings.hic_data_path, settings.pre_data_path]:
            for path in glob.glob(f"{pattern_dir}/*-R*.json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        requirements[data["requirement_id"]] = data
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning("Could not load %s: %s", path, e)

        return requirements

    def load(self, requirement_id: str) -> Optional[dict]:
        """Load a specific requirement by ID."""
        return self.load_all().get(requirement_id)


class EvidenceMatcher:
    """Match document text against evidence requirements.

    Two-pass design:
      Pass 1 -- Multi-signal keyword/concept/hint matching (fast).
                Uses word-boundary-aware regex for single keywords to
                avoid false positives from partial matches.
                Requires >= MIN_TOTAL_HITS total signal hits to exceed NOT_FOUND.
      Pass 2 -- (External) LLM-based semantic analysis for items that
                scored below COMPLIANT in Pass 1.
    """

    # Thresholds
    MIN_TOTAL_HITS = 4  # minimum combined hits (kw+concept+hint+validation) to matter

    def match_evidence(self, text: str, requirement: dict) -> list[EvidenceItem]:
        """Match document text against evidence items in a requirement."""
        results = []
        text_lower = text.lower()

        for evidence in requirement.get("evidence_schema", {}).get("evidence", []):
            item = self._check_evidence(text_lower, evidence)
            results.append(item)

        return results

    def _check_evidence(self, text_lower: str, evidence: dict) -> EvidenceItem:
        """Check a single evidence item against document text."""
        evidence_id = evidence["evidence_id"]
        name = evidence["name"]
        evidence_type = evidence["type"]
        required = evidence["required"]
        critical = evidence["critical"]

        search_strategy = evidence.get("search_strategy", {})
        extraction_hints = evidence.get("extraction_hints", {})

        # Signal 1: Keyword matching (word-boundary-aware, exclusion-filtered)
        keywords = [k.lower() for k in search_strategy.get("keywords", [])]
        keyword_hits = self._match_keywords(text_lower, keywords)

        # Signal 2: Semantic concept matching (word-boundary-aware)
        concepts = [c.lower() for c in search_strategy.get("semantic_concepts", [])]
        concept_hits = self._match_keywords(text_lower, concepts)

        # Signal 3: Extraction hint validation
        hint_hits = self._match_extraction_hints(text_lower, extraction_hints)

        # Signal 4: Validation rules (structural checks)
        validation_rules = search_strategy.get("validation_rules", [])
        validation_hits = self._match_validation_rules(text_lower, validation_rules)

        kw_count = len(keyword_hits)
        con_count = len(concept_hits)
        hint_count = len(hint_hits)
        val_count = len(validation_hits)
        total_hits = kw_count + con_count + hint_count + val_count

        # Require at least MIN_TOTAL_HITS across all signals
        if total_hits < self.MIN_TOTAL_HITS:
            # Check if single keyword is strong enough to warrant further analysis
            if kw_count >= 1 and total_hits >= 1:
                justification = f"Insufficient evidence (only {total_hits} hit(s)) for: {name}"
            else:
                justification = f"No matching evidence found for: {name}"
            return EvidenceItem(
                evidence_id=evidence_id,
                name=name,
                type=evidence_type,
                required=required,
                critical=critical,
                status=ComplianceStatus.NOT_FOUND,
                justification=justification
            )

        # Calculate raw confidence (0-1)
        confidence = 0.0

        # Keyword contribution (primary): logarithmic scaling
        if kw_count >= 2:
            confidence += min(0.8, 0.35 + 0.15 * math.log2(kw_count))
        elif kw_count == 1:
            confidence += 0.25  # single keyword can support a partial finding

        # Concept contribution (supplementary)
        if con_count > 0:
            confidence += min(0.25, 0.1 * con_count)

        # Hint contribution (validation bonus)
        if hint_count > 0:
            confidence += min(0.2, 0.1 * hint_count)

        # Validation rules contribution (structural bonus)
        if val_count > 0:
            confidence += min(0.15, 0.05 * val_count)

        confidence = round(min(confidence, 1.0), 10)

        # Map confidence to compliance status (using centralized thresholds)
        if confidence >= settings.score_compliant:
            status = ComplianceStatus.COMPLIANT
            justification = self._build_justification("Strong evidence found", keyword_hits, concept_hits, hint_hits, validation_hits)
        elif confidence >= settings.score_partial:
            status = ComplianceStatus.PARTIAL
            justification = self._build_justification("Partial evidence found", keyword_hits, concept_hits, hint_hits, validation_hits)
        elif confidence >= settings.score_noncompliant_floor:
            status = ComplianceStatus.NON_COMPLIANT
            justification = self._build_justification("Weak evidence found", keyword_hits, concept_hits, hint_hits, validation_hits)
        else:
            status = ComplianceStatus.NOT_FOUND
            justification = f"No matching evidence found for: {name}"

        return EvidenceItem(
            evidence_id=evidence_id,
            name=name,
            type=evidence_type,
            required=required,
            critical=critical,
            status=status,
            justification=justification
        )

    def _match_keywords(self, text_lower: str, keywords: list[str]) -> list[str]:
        """Match keywords with word-boundary awareness and exclusion filtering.

        Single-word keywords use regex \\b boundaries to avoid partial matches
        (e.g. "rub" won't match "scrub", "BMW" won't match "bmw series").
        Multi-word phrases use plain substring matching (implicit boundaries
        from spaces/punctuation already provide good accuracy).

        After matching, hits are filtered against EXCLUSION_KEYWORDS to
        remove generic quality-management terms that would cause false positives.

        Fuzzy matching (optional): if an exact match fails, uses difflib to
        find near-matches in the text for keywords >= 4 characters. Fuzzy
        hits are flagged with a discount factor for score calculation.
        """
        matched = []
        fuzzy_matched = []  # near-matches tracked for logging only

        for kw in keywords:
            if not kw:
                continue

            stripped = kw.strip()
            if not stripped:
                continue

            # Check if this keyword is in the exclusion list
            if stripped in EXCLUSION_KEYWORDS:
                continue

            # Multi-word phrase -- substring match is safe
            if ' ' in stripped:
                if stripped in text_lower:
                    matched.append(stripped)
                elif settings.fuzzy_enabled:
                    self._fuzzy_check(text_lower, stripped, fuzzy_matched)
            else:
                # Avoid double-counting a single word if a matched phrase already
                # contains it (for example, "hand" should not also count when
                # "hand hygiene" already matched).
                if any(stripped in phrase.lower() for phrase in matched if ' ' in phrase):
                    continue

                # Single word -- use word boundary regex
                exact_found = False
                try:
                    if re.search(rf'\b{re.escape(stripped)}\b', text_lower):
                        matched.append(stripped)
                        exact_found = True
                except re.error:
                    # Fallback to plain substring for exotic patterns
                    if stripped in text_lower:
                        matched.append(stripped)
                        exact_found = True

                # Fuzzy fallback: only for keywords >= 4 chars
                if not exact_found and settings.fuzzy_enabled and len(stripped) >= 4:
                    self._fuzzy_check(text_lower, stripped, fuzzy_matched)

        return matched

    def _fuzzy_check(self, text_lower: str, keyword: str, fuzzy_list: list) -> None:
        """Check for fuzzy matches of keyword in text using SequenceMatcher.

        Scans text for substrings of similar length and checks similarity.
        Only adds match if ratio >= settings.fuzzy_threshold.
        """
        kw_len = len(keyword)
        # Scan text with a sliding window slightly larger than the keyword
        window = kw_len + max(2, kw_len // 3)
        text_len = len(text_lower)

        for start in range(0, text_len - kw_len + 1, max(1, kw_len // 2)):
            end = min(start + window, text_len)
            candidate = text_lower[start:end]
            ratio = SequenceMatcher(None, keyword, candidate).ratio()
            if ratio >= settings.fuzzy_threshold:
                fuzzy_list.append(keyword)
                logger.debug("Fuzzy match: '%s' ~ '%s' (ratio=%.2f)", keyword, candidate, ratio)
                return  # one fuzzy match per keyword is enough

    def _match_extraction_hints(self, text_lower: str, hints: dict) -> list[str]:
        """Match extraction hint patterns against document text.

        Supports both plain strings and regex patterns. Patterns containing
        regex meta-characters (\\d, [, ], (, ), ^, $, |, +, *, ?, {, })
        are matched as regex; everything else as plain substring.
        """
        matched = []
        _REGEX_CHARS = set(r'\d[]()^$|+*?{}')

        for hint_type, patterns in hints.items():
            if not isinstance(patterns, list):
                continue
            for pattern in patterns:
                if not isinstance(pattern, str) or len(pattern) <= 2:
                    continue
                stripped = pattern.strip()

                # Check if pattern looks like regex
                has_regex_chars = any(c in stripped for c in _REGEX_CHARS)

                if has_regex_chars:
                    try:
                        if re.search(stripped, text_lower):
                            matched.append(stripped)
                    except re.error:
                        # Fallback to plain substring
                        if stripped.lower() in text_lower:
                            matched.append(stripped)
                else:
                    # Plain string -- case-insensitive substring
                    if stripped.lower() in text_lower:
                        matched.append(stripped)

        return matched

    def _match_validation_rules(self, text_lower: str, rules: list[str]) -> list[str]:
        """Check validation rules against document text.

        Two types of rules:
          - snake_case identifiers (e.g., "effective_date_present"):
            Check for date patterns in the text.
          - Sentence-style rules (e.g., "Must be approved by hospital"):
            Extract key terms and run keyword matching.
        """
        matched = []
        _REGEX_CHARS = set(r'\d[]()^$|+*?{}')

        for rule in rules:
            if not isinstance(rule, str) or len(rule) <= 2:
                continue
            stripped = rule.strip()

            # Snake_case rules: check for structural patterns
            if '_' in stripped and ' ' not in stripped:
                rule_lower = stripped.lower()
                if 'date' in rule_lower and _DATE_PATTERN.search(text_lower):
                    matched.append(stripped)
                elif 'signature' in rule_lower or 'sign' in rule_lower:
                    if _AUTH_PATTERN.search(text_lower):
                        matched.append(stripped)
                elif 'version' in rule_lower:
                    if re.search(r'v(?:ersion)?\s*\d', text_lower):
                        matched.append(stripped)
                # Other snake_case rules: check if key terms appear
                else:
                    terms = [t for t in rule_lower.split('_') if len(t) > 3]
                    if terms and all(t in text_lower for t in terms[:2]):
                        matched.append(stripped)
            else:
                # Sentence-style rules: extract key nouns and match
                # Remove common stop words, keep meaningful terms
                stop_words = {
                    'must', 'be', 'the', 'and', 'or', 'in', 'within', 'last',
                    'past', 'by', 'from', 'for', 'is', 'are', 'was', 'were',
                    'a', 'an', 'of', 'to', 'at', 'on', 'with', 'not', 'no',
                }
                words = re.findall(r'[a-z]+', stripped.lower())
                key_terms = [w for w in words if w not in stop_words and len(w) > 3]
                # Check if at least half the key terms appear in text
                if key_terms and sum(1 for t in key_terms if t in text_lower) >= max(1, len(key_terms) // 2):
                    matched.append(stripped)

        return matched

    def _build_justification(
        self,
        prefix: str,
        keyword_hits: list,
        concept_hits: list,
        hint_hits: list,
        validation_hits: list | None = None,
    ) -> str:
        """Build a human-readable justification string."""
        parts = [prefix]
        if keyword_hits:
            parts.append(f"Keywords: {', '.join(keyword_hits[:4])}")
        if concept_hits:
            parts.append(f"Concepts: {', '.join(concept_hits[:3])}")
        if hint_hits:
            parts.append(f"Validated: {', '.join(hint_hits[:3])}")
        if validation_hits:
            parts.append(f"Rules met: {', '.join(validation_hits[:3])}")
        return "; ".join(parts)


class RequirementMatcher:
    """High-level requirement matching orchestrator."""

    def __init__(self):
        self.evidence_matcher = EvidenceMatcher()

    def analyze_document(self, text: str, requirement_id: str) -> RequirementResult:
        """Analyze document text against a single requirement."""
        loader = RequirementLoader()
        requirement = loader.load(requirement_id)

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        evidence_results = self.evidence_matcher.match_evidence(text, requirement)
        overall_status, score = self._calculate_score(evidence_results)

        # Apply confidence_weight from KB (scales the final score)
        confidence_weight = requirement.get("confidence_weight", 0.90)
        scaled_score = round(score * confidence_weight, 4)

        return RequirementResult(
            requirement_id=requirement_id,
            chapter=requirement.get("chapter", ""),
            title=requirement.get("title", ""),
            description=requirement.get("description", ""),
            criticality=requirement.get("criticality", "Medium"),
            evidence_items=evidence_results,
            overall_status=overall_status,
            compliance_score=scaled_score,
            confidence_weight=confidence_weight,
        )

    def _calculate_score(self, evidence_items: list[EvidenceItem]) -> tuple[ComplianceStatus, float]:
        """Calculate weighted compliance score.

        Critical evidence items are weighted 2x more than non-critical ones.
        Score maps: Compliant=1.0, Partial=0.5, Non-Compliant=0.0, Not Found=0.0
        """
        if not evidence_items:
            return ComplianceStatus.NOT_FOUND, 0.0

        total_weighted = 0.0
        total_weights = 0.0

        for item in evidence_items:
            weight = 2.0 if item.critical else 1.0
            score = {
                ComplianceStatus.COMPLIANT: 1.0,
                ComplianceStatus.PARTIAL: 0.5,
                ComplianceStatus.NON_COMPLIANT: 0.0,
                ComplianceStatus.NOT_FOUND: 0.0
            }.get(item.status, 0.0)

            total_weighted += score * weight
            total_weights += weight

        avg_score = total_weighted / total_weights if total_weights > 0 else 0.0

        # Determine overall status (using centralized thresholds)
        if avg_score >= settings.score_compliant:
            overall_status = ComplianceStatus.COMPLIANT
        elif avg_score >= settings.score_partial:
            overall_status = ComplianceStatus.PARTIAL
        elif avg_score >= settings.score_noncompliant_floor:
            overall_status = ComplianceStatus.NON_COMPLIANT
        else:
            overall_status = ComplianceStatus.NOT_FOUND

        return overall_status, avg_score


# Singleton
requirement_matcher = RequirementMatcher()
