"""Compliance rule matching using evidence schemas."""
import json
import glob
import re
import math
import logging
from pathlib import Path
from ..core import settings
from ..models.schemas import ComplianceStatus, EvidenceItem, RequirementResult
from typing import Optional

logger = logging.getLogger(__name__)


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
      Pass 1 — Multi-signal keyword/concept/hint matching (fast).
                Uses word-boundary-aware regex for single keywords to
                avoid false positives from partial matches.
                Requires ≥2 total signal hits to exceed NOT_FOUND.
      Pass 2 — (External) LLM-based semantic analysis for items that
                scored below COMPLIANT in Pass 1.
    """
    
    # Thresholds
    MIN_TOTAL_HITS = 2        # minimum combined hits (kw+concept+hint) to matter
    
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
        
        # Signal 1: Keyword matching (word-boundary-aware)
        keywords = [k.lower() for k in search_strategy.get("keywords", [])]
        keyword_hits = self._match_keywords(text_lower, keywords)
        
        # Signal 2: Semantic concept matching (word-boundary-aware)
        concepts = [c.lower() for c in search_strategy.get("semantic_concepts", [])]
        concept_hits = self._match_keywords(text_lower, concepts)
        
        # Signal 3: Extraction hint validation
        hint_hits = self._match_extraction_hints(text_lower, extraction_hints)
        
        kw_count = len(keyword_hits)
        con_count = len(concept_hits)
        hint_count = len(hint_hits)
        total_hits = kw_count + con_count + hint_count
        
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
        
        confidence = min(confidence, 1.0)
        
        # Map confidence to compliance status
        if confidence >= 0.8:
            status = ComplianceStatus.COMPLIANT
            justification = self._build_justification("Strong evidence found", keyword_hits, concept_hits, hint_hits)
        elif confidence >= 0.5:
            status = ComplianceStatus.PARTIAL
            justification = self._build_justification("Partial evidence found", keyword_hits, concept_hits, hint_hits)
        elif confidence > 0.1:
            status = ComplianceStatus.NON_COMPLIANT
            justification = self._build_justification("Weak evidence found", keyword_hits, concept_hits, hint_hits)
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
        """Match keywords with word-boundary awareness.
        
        Single-word keywords use regex \b boundaries to avoid partial matches
        (e.g. "rub" won't match "scrub", "BMW" won't match "bmw series").
        Multi-word phrases use plain substring matching (implicit boundaries
        from spaces/punctuation already provide good accuracy).
        """
        matched = []
        for kw in keywords:
            if not kw:
                continue

            stripped = kw.strip()
            if not stripped:
                continue

            # Multi-word phrase — substring match is safe
            if ' ' in stripped:
                if stripped in text_lower:
                    matched.append(stripped)
            else:
                # Avoid double-counting a single word if a matched phrase already
                # contains it (for example, "hand" should not also count when
                # "hand hygiene" already matched).
                if any(stripped in phrase.lower() for phrase in matched if ' ' in phrase):
                    continue

                # Single word — use word boundary regex
                try:
                    if re.search(rf'\b{re.escape(stripped)}\b', text_lower):
                        matched.append(stripped)
                except re.error:
                    # Fallback to plain substring for exotic patterns
                    if stripped in text_lower:
                        matched.append(stripped)
        return matched
    
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
                    # Plain string — case-insensitive substring
                    if stripped.lower() in text_lower:
                        matched.append(stripped)
        
        return matched
    
    def _build_justification(
        self, 
        prefix: str, 
        keyword_hits: list, 
        concept_hits: list, 
        hint_hits: list
    ) -> str:
        """Build a human-readable justification string."""
        parts = [prefix]
        if keyword_hits:
            parts.append(f"Keywords: {', '.join(keyword_hits[:4])}")
        if concept_hits:
            parts.append(f"Concepts: {', '.join(concept_hits[:3])}")
        if hint_hits:
            parts.append(f"Validated: {', '.join(hint_hits[:3])}")
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
        
        return RequirementResult(
            requirement_id=requirement_id,
            chapter=requirement.get("chapter", ""),
            title=requirement.get("title", ""),
            description=requirement.get("description", ""),
            criticality=requirement.get("criticality", "Medium"),
            evidence_items=evidence_results,
            overall_status=overall_status,
            compliance_score=score
        )
    
    def _calculate_score(self, evidence_items: list[EvidenceItem]) -> tuple[ComplianceStatus, float]:
        """Calculate weighted compliance score.
        
        Critical evidence items are weighted 2x more than non-critical ones.
        Score maps: Compliant=1.0, Partial=0.5, Non-Compliant=0.2, Not Found=0.0
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
                ComplianceStatus.NON_COMPLIANT: 0.2,
                ComplianceStatus.NOT_FOUND: 0.0
            }.get(item.status, 0.0)
            
            total_weighted += score * weight
            total_weights += weight
        
        avg_score = total_weighted / total_weights if total_weights > 0 else 0.0
        
        # Determine overall status
        if avg_score >= 0.8:
            overall_status = ComplianceStatus.COMPLIANT
        elif avg_score >= 0.5:
            overall_status = ComplianceStatus.PARTIAL
        elif avg_score >= 0.1:
            overall_status = ComplianceStatus.NON_COMPLIANT
        else:
            overall_status = ComplianceStatus.NOT_FOUND
        
        return overall_status, avg_score


# Singleton
requirement_matcher = RequirementMatcher()
