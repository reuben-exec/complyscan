"""Prompt templates for LLM-based evidence analysis.

This module provides the prompt template and builder function for the
LLM semantic analysis pass (Pass 2). The prompt is designed to be strict
and audit-focused, requiring verifiable evidence rather than inference.
"""

EVIDENCE_PROMPT = """You are a strict NABH compliance audit assistant evaluating a specific evidence item.

## Evidence Item
- ID: {evidence_id}
- Name: {name}
- Type: {type} | Required: {required} | Critical: {critical}

## Evidence Schema Context
- Expected Locations in Document: {expected_locations}
- Search Keywords: {keywords}
- Semantic Concepts: {concepts}
- Extraction Hints: {extraction_hints}

## Pass 1 (Keyword Matching) Result
- Status: {pass1_status}
- What Pass 1 Found: {pass1_justification}

## Document Text (Relevant Excerpts)
{text}

## Evaluation Rules (READ CAREFULLY)

1. **BE STRICT** — Evaluate only the text provided above. Do NOT infer, assume,
   or extrapolate missing information. A well-written document that lacks the
   specific evidence item is still non-compliant for that item.

2. **REQUIRE EXPLICIT EVIDENCE** — The document must explicitly address the
   specific evidence item by name or by clearly describing the required element.
   Generic professional language (dates, approvals, headers) does NOT count.

3. **CITE VERBATIM TEXT** — Your justification MUST quote the specific text that
   supports your decision. If you cannot quote relevant text, the evidence is
   insufficient.

4. **USE UNCERTAINTY** — If the text is ambiguous, partially relevant, or you
   cannot clearly determine compliance, set is_compliant to **null** (not false).

5. **CALIBRATE CONFIDENCE** — Confidence should reflect how explicitly the text
   addresses the evidence item:
   - 0.90-1.00: Direct, verbatim evidence with specific details
   - 0.70-0.89: Clear evidence present, some indirectness
   - 0.50-0.69: Partial or implied evidence, significant gaps
   - Below 0.50: Guessing or weak inference — should not override Pass 1

6. **INDEPENDENT EVALUATION** — Each evidence item is evaluated independently.
   A document may meet one item but fail another. Do not carry over compliance
   from one item to another.

## Response Format
Respond ONLY with valid JSON. No markdown, no extra text.

{{"is_compliant": true/false/null, "confidence": 0.0-1.0, "justification": "..."}}"""


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
    max_text_length: int = 3000,
) -> str:
    """Build a prompt for the LLM to evaluate a single evidence item.

    Uses the evidence schema's expected_locations and extraction_hints
    to provide focused context, and instructs the LLM to be strict.

    Args:
        evidence_id: Evidence item identifier (e.g. EV-HIC-R01-001)
        name: Human-readable name of the evidence item
        type: Evidence type (policy, procedure, etc.)
        required: Whether the item is required
        critical: Whether the item is critical
        keywords: List of search keywords from the evidence schema
        concepts: List of semantic concepts from the evidence schema
        text: Relevant document excerpts (already section-selected, not full doc)
        expected_locations: Section names/headers where evidence should appear
        extraction_hints: Dict of extraction hint patterns
        pass1_status: The compliance status determined by Pass 1 keyword matching
        pass1_justification: What Pass 1 found (for context)
        max_text_length: Maximum characters for document excerpts (default 3000)

    Returns:
        A formatted prompt string ready to send to the LLM
    """
    import logging
    logger = logging.getLogger(__name__)

    # Truncate text if it exceeds the maximum length
    if len(text) > max_text_length:
        logger.debug(
            "Truncating document excerpts from %d to %d chars for LLM prompt",
            len(text), max_text_length,
        )
        # Try to truncate at paragraph boundary
        truncated = text[:max_text_length]
        last_para = truncated.rfind("\n\n")
        if last_para > max_text_length * 0.8:
            truncated = truncated[:last_para]
        text = truncated + "\n\n[... excerpt truncated ...]"

    kw_str = ", ".join(keywords) if keywords else "(none from schema)"
    co_str = ", ".join(concepts) if concepts else "(none from schema)"

    # Format expected_locations as a readable string
    if expected_locations:
        loc_str = ", ".join(expected_locations)
    else:
        loc_str = "(not specified in schema)"

    # Format extraction_hints as a readable string (limit verbosity)
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

    return EVIDENCE_PROMPT.format(
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
        pass1_justification=pass1_justification[:200],
        text=text,
    )
