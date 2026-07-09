"""Structured prompt architecture for LLM-based evidence analysis.

This module provides a modular prompt system designed for the 70B model's
capabilities: chain-of-thought reasoning, structured JSON output, and
evidence-grounded compliance evaluation.

Architecture:
- SYSTEM_PROMPT: Role definition, output schema, reasoning instructions
- EVIDENCE_PROMPT_TEMPLATE: Structured sections with clear delimiters
- build_evidence_prompt(): Builder that assembles the full prompt
- validate_llm_response(): Post-parse validation of LLM output
"""

import re
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System Prompt — defines role, constraints, and output format
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior NABH (National Accreditation Board for Hospitals & Healthcare Providers) compliance auditor.

Your task is to evaluate whether a hospital document contains EVIDENCE of a specific compliance requirement.

## Core Principles
1. EVIDENCE-BASED: Only judge what is explicitly stated in the document text provided. Do not infer, assume, or extrapolate.
2. AUDIT-GRADE STRICTNESS: You are performing a regulatory audit. Ambiguity favors non-compliance.
3. VERBATIM QUOTING: Your justification MUST cite the exact text from the document that supports your conclusion.
4. STEP-BY-STEP REASONING: Before your final answer, think through what evidence exists, what is missing, and how they compare.

## Output Schema
You MUST respond with a single JSON object matching this exact schema:

{
  "reasoning": "Step-by-step analysis of the evidence",
  "is_compliant": true | false | null,
  "confidence": 0.0 to 1.0,
  "justification": "Concise summary with verbatim quotes from the document"
}

Field definitions:
- "reasoning": Your chain-of-thought analysis. Explain what you looked for, what you found, and why you reached your conclusion. This is for transparency and audit trail.
- "is_compliant": true = evidence explicitly present, false = evidence absent or insufficient, null = ambiguous/uncertain
- "confidence": How certain you are about your is_compliant judgment:
  - 0.90-1.00: Direct verbatim evidence with specific details matching the requirement
  - 0.70-0.89: Clear evidence present, minor indirectness or interpretation needed
  - 0.50-0.69: Partial or implied evidence, notable gaps or ambiguity
  - 0.00-0.49: Weak inference, no direct evidence, or significant uncertainty
- "justification": One-paragraph summary (max 500 chars) with key verbatim quotes from the document

## Critical Rules
- Respond with JSON ONLY. No markdown, no code fences, no extra text outside the JSON.
- If the document text is empty or unreadable, set is_compliant to null with confidence 0.0.
- Never fabricate quotes. If you cannot quote relevant text, the evidence is insufficient.
- Each evidence item is evaluated INDEPENDENTLY. Do not carry over compliance from other items."""


# ---------------------------------------------------------------------------
# Evidence Prompt Template — structured sections for each evaluation
# ---------------------------------------------------------------------------

EVIDENCE_PROMPT_TEMPLATE = """## Evidence Requirement

**ID**: {evidence_id}
**Name**: {name}
**Type**: {type} | **Required**: {required} | **Critical**: {critical}

### What to Look For
- **Expected Document Sections**: {expected_locations}
- **Search Keywords**: {keywords}
- **Semantic Concepts**: {concepts}
- **Extraction Patterns**: {extraction_hints}

---

## Pass 1 (Keyword Matcher) Initial Assessment
- **Status**: {pass1_status}
- **Summary**: {pass1_justification}

Note: You are performing an INDEPENDENT evaluation. The Pass 1 result is provided for context only — do not defer to it. If you disagree with Pass 1, explain why in your reasoning.

---

## Document Excerpts (Relevant to This Evidence Item)

{text}

---

## Your Task

Evaluate whether the document excerpts above contain EXPLICIT EVIDENCE that the hospital meets this specific requirement: **{name}**

### Step-by-Step Process:
1. **Identify**: What specific evidence does this requirement demand?
2. **Search**: Scan the document excerpts for text that directly addresses this requirement.
3. **Verify**: Is the found text explicit evidence, or just related language? Does it meet the full requirement or only part of it?
4. **Conclude**: Based ONLY on what is explicitly stated, determine compliance.

### Remember:
- Generic professional language (policies, headers, dates) does NOT count unless it explicitly addresses THIS specific requirement.
- Partial evidence = is_compliant: false (not null). Null is ONLY for genuinely ambiguous cases.
- Your confidence must reflect how DIRECTLY the text addresses the requirement, not how well-written the document is."""


# ---------------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------------

def build_evidence_prompt(
    evidence_id: str,
    name: str,
    type: str,
    required: bool,
    critical: bool,
    keywords: list[str],
    concepts: list[str],
    text: str,
    *,
    expected_locations: list[str] | None = None,
    extraction_hints: dict | None = None,
    pass1_status: str = "",
    pass1_justification: str = "",
    max_text_length: int = 8000,
) -> str:
    """Build a structured prompt for the LLM to evaluate a single evidence item.

    The prompt is divided into clear sections:
    1. Evidence requirement details
    2. Pass 1 initial assessment (context only)
    3. Document excerpts (intelligently selected)
    4. Step-by-step evaluation instructions

    Args:
        evidence_id: Evidence item identifier (e.g. EV-HIC-R01-001)
        name: Human-readable name of the evidence item
        type: Evidence type (policy, procedure, etc.)
        required: Whether the item is required
        critical: Whether the item is critical
        keywords: List of search keywords from the evidence schema
        concepts: List of semantic concepts from the evidence schema
        text: Relevant document excerpts (already section-selected)
        expected_locations: Section names/headers where evidence should appear
        extraction_hints: Dict of extraction hint patterns
        pass1_status: The compliance status determined by Pass 1 keyword matching
        pass1_justification: What Pass 1 found (for context)
        max_text_length: Maximum characters for document excerpts (default 8000)

    Returns:
        A formatted prompt string ready to send to the LLM
    """
    # Truncate text at paragraph boundary if needed
    if len(text) > max_text_length:
        logger.debug(
            "Truncating document excerpts from %d to %d chars for LLM prompt",
            len(text), max_text_length,
        )
        truncated = text[:max_text_length]
        last_para = truncated.rfind("\n\n")
        if last_para > max_text_length * 0.8:
            truncated = truncated[:last_para]
        text = truncated + "\n\n[... excerpt truncated ...]"

    # Format structured fields
    kw_str = ", ".join(keywords) if keywords else "(none specified)"
    co_str = ", ".join(concepts) if concepts else "(none specified)"

    if expected_locations:
        loc_str = "; ".join(expected_locations)
    else:
        loc_str = "(not specified in schema)"

    if extraction_hints:
        hint_parts = []
        for hint_key, hint_values in extraction_hints.items():
            if isinstance(hint_values, list) and hint_values:
                hint_parts.append(f"{hint_key}: {', '.join(hint_values[:5])}")
        hints_str = "; ".join(hint_parts) if hint_parts else "(none)"
    else:
        hints_str = "(none)"

    if not pass1_status:
        pass1_status = "Not yet evaluated"
    if not pass1_justification:
        pass1_justification = "(no prior analysis)"

    return EVIDENCE_PROMPT_TEMPLATE.format(
        evidence_id=evidence_id,
        name=name,
        type=type,
        required=required,
        critical=critical,
        expected_locations=loc_str,
        keywords=kw_str,
        concepts=co_str,
        extraction_hints=hints_str,
        pass1_status=pass1_status,
        pass1_justification=pass1_justification[:300],
        text=text,
    )


# ---------------------------------------------------------------------------
# Response Validation
# ---------------------------------------------------------------------------

# Expected schema for LLM response
_EXPECTED_FIELDS = {"reasoning", "is_compliant", "confidence", "justification"}


def validate_llm_response(parsed: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize an LLM response dict.

    Ensures all required fields exist with correct types, clamps values
    to valid ranges, and provides safe defaults for missing fields.

    Args:
        parsed: Parsed JSON dict from LLM response (may be partial or malformed).

    Returns:
        Normalized dict with guaranteed keys: reasoning, is_compliant,
        confidence, justification. Falls back to safe defaults on any error.
    """
    if not parsed or not isinstance(parsed, dict):
        return _fallback_response()

    result: dict[str, Any] = {}

    # --- reasoning (new field, optional for backward compat) ---
    reasoning = parsed.get("reasoning")
    if reasoning and isinstance(reasoning, str):
        result["reasoning"] = reasoning[:2000]  # Cap reasoning length
    else:
        result["reasoning"] = None

    # --- is_compliant ---
    is_compliant = parsed.get("is_compliant")
    if is_compliant is None:
        result["is_compliant"] = None  # null = uncertain (valid)
    elif isinstance(is_compliant, bool):
        result["is_compliant"] = is_compliant
    elif isinstance(is_compliant, str):
        # Handle string responses like "true", "false", "null"
        lower = is_compliant.lower().strip()
        if lower == "true":
            result["is_compliant"] = True
        elif lower == "false":
            result["is_compliant"] = False
        elif lower in ("null", "none", "uncertain", "ambiguous"):
            result["is_compliant"] = None
        else:
            result["is_compliant"] = None
            logger.warning("Unrecognized is_compliant value: %s", is_compliant)
    else:
        result["is_compliant"] = bool(is_compliant)

    # --- confidence ---
    try:
        confidence = float(parsed.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))
    except (TypeError, ValueError):
        confidence = 0.0
    result["confidence"] = confidence

    # --- justification ---
    justification = parsed.get("justification", "")
    if justification and isinstance(justification, str):
        result["justification"] = justification[:500]
    else:
        result["justification"] = ""

    return result


def _fallback_response() -> dict[str, Any]:
    """Return safe fallback when LLM response is completely invalid."""
    return {
        "reasoning": None,
        "is_compliant": None,
        "confidence": 0.0,
        "justification": "",
    }
