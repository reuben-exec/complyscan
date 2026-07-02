import asyncio
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.matcher.engine import EvidenceMatcher, RequirementMatcher
from backend.models.schemas import ComplianceStatus, EvidenceItem, OverrideRequest, RequirementResult


client = TestClient(app)

SAMPLE_TEXT = """
Hand Hygiene Policy Document

1. Purpose and Scope
This hand hygiene policy applies to all healthcare workers, support staff, contractors,
and visitors within the hospital premises. The objective is to reduce healthcare-associated
infections through standardized hand hygiene practices in alignment with WHO Guidelines
on Hand Hygiene in Health Care.

2. Policy Statement
The hospital is committed to achieving and sustaining high hand hygiene compliance.
All staff must perform hand hygiene at the point of care using the WHO Five Moments
for Hand Hygiene framework. Alcohol-based hand rub is the preferred method for
routine hand antisepsis.

3. Roles and Responsibilities
- Infection Control Committee: Oversee hand hygiene strategy, review audit results.
- Nurse Manager: Monitor unit-level compliance, ensure supplies.
- Individual Staff: Comply with indications and technique, report deficits.

4. Hand Hygiene Indications (WHO 5 Moments)
1) Before touching a patient
2) Before clean/aseptic procedures
3) After body fluid exposure risk
4) After touching a patient
5) After touching patient surroundings

5. Technique
Alcohol-based hand rub: Apply 3-5 mL, rub all surfaces for 20-30 seconds.
Hand wash with soap and water: Minimum 40-60 seconds, especially when hands
are visibly soiled or after using the restroom.

6. Monitoring and Audit
Direct observation audits are conducted monthly across all wards by trained
infection control nurses using the WHO Hand Hygiene Observation Tool.
Compliance rates are calculated, reviewed in quality meetings, and displayed.

7. Training
All new employees receive hand hygiene training during orientation. Annual
competency assessments are mandatory. Refresher training is provided when
compliance drops below the 80% threshold.

8. Infrastructure
Alcohol-based hand rub dispensers are installed at every point of care,
entrance to patient rooms, and at each bed space. Hand washing sinks are
available in all patient care areas with soap and disposable paper towels.

9. Audit Results for Q1 2024
Hand Hygiene Compliance Rate: 87% (target >= 80%)
Observations: 340
Correct Actions: 296

10. Feedback and Improvement
A clear feedback mechanism and corrective action process are defined for non-compliance and performance improvement.
"""

PARTIAL_TEXT = """
Hand hygiene policy summary.
This document mentions hand hygiene and infection prevention but omits audit results,
training details, and monitoring targets.
"""

UNRELATED_TEXT = """
Cooking recipe for tomato soup:
Chop onions, garlic, and tomatoes. Simmer with broth and basil.
"""

WASTE_TEXT = """
Biomedical Waste Management Policy
The hospital generates biomedical waste from patient care, laboratory, and
surgical procedures. Waste segregation is performed at the point of generation
following CPCB color-coded bag system.
"""

PRE_TEXT = """
Patient Rights Policy
The hospital must ensure patient rights, privacy, informed consent, grievance redressal,
and respectful care. Patients and families are informed of their rights and responsibilities.
"""


@pytest.fixture
def matcher() -> RequirementMatcher:
    return RequirementMatcher()


def test_perfect_match_scores_as_compliant(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(SAMPLE_TEXT, "HIC-R01")
    assert result.overall_status == ComplianceStatus.COMPLIANT
    assert result.compliance_score >= 0.85


def test_empty_text_returns_not_found(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document("   \n\t", "HIC-R01")
    assert result.overall_status == ComplianceStatus.NOT_FOUND
    assert result.compliance_score == 0.0


def test_unrelated_text_scores_low(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(UNRELATED_TEXT, "HIC-R01")
    assert result.overall_status in {ComplianceStatus.NOT_FOUND, ComplianceStatus.NON_COMPLIANT}
    assert result.compliance_score < 0.25


def test_partial_evidence_downgrades_expected_item(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(PARTIAL_TEXT, "HIC-R01")
    audit_item = next(item for item in result.evidence_items if item.name.startswith("Monthly Audit Schedule"))
    assert audit_item.status in {ComplianceStatus.NOT_FOUND, ComplianceStatus.PARTIAL}


def test_critical_items_are_weighted_more_heavily(matcher: RequirementMatcher) -> None:
    items = [
        EvidenceItem(evidence_id="a", name="critical", type="policy", required=True, critical=True, status=ComplianceStatus.COMPLIANT),
        EvidenceItem(evidence_id="b", name="non-critical", type="policy", required=False, critical=False, status=ComplianceStatus.PARTIAL),
    ]
    status, score = matcher._calculate_score(items)
    assert score == pytest.approx((2.0 + 0.5) / 3.0)
    assert status == ComplianceStatus.COMPLIANT


def test_wrong_chapter_does_not_match_as_compliant(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(WASTE_TEXT, "HIC-R01")
    assert result.overall_status in {ComplianceStatus.NOT_FOUND, ComplianceStatus.NON_COMPLIANT}
    assert result.compliance_score < 0.4


def test_keyword_boundary_regex_does_not_match_partial_words() -> None:
    matcher = EvidenceMatcher()
    assert matcher._match_keywords("scrub technique", ["rub"]) == []
    assert matcher._match_keywords("rub all surfaces", ["rub"]) == ["rub"]


def test_multi_word_phrase_matches_without_overcounting() -> None:
    matcher = EvidenceMatcher()
    assert matcher._match_keywords("hand hygiene policy", ["hand hygiene", "hand"]) == ["hand hygiene"]


def test_log_scaled_scoring_increases_less_than_linearly() -> None:
    matcher = EvidenceMatcher()
    evidence = {
        "evidence_id": "EV-TEST-001",
        "name": "Test evidence",
        "type": "policy",
        "required": True,
        "critical": True,
        "search_strategy": {"keywords": ["hand hygiene", "compliance"], "semantic_concepts": [], "extraction_hints": {}},
    }
    two_hits = matcher._check_evidence("hand hygiene compliance", evidence)
    evidence["search_strategy"]["keywords"] = ["hand", "hygiene", "policy", "audit", "compliance", "training", "monitoring", "procedure"]
    eight_hits = matcher._check_evidence("hand hygiene policy audit compliance training monitoring procedure", evidence)
    assert two_hits.status in {ComplianceStatus.PARTIAL, ComplianceStatus.NON_COMPLIANT}
    assert eight_hits.status == ComplianceStatus.COMPLIANT


def test_score_boundaries_map_to_expected_statuses(matcher: RequirementMatcher) -> None:
    boundary_08 = [
        EvidenceItem(evidence_id="a", name="critical", type="policy", required=True, critical=True, status=ComplianceStatus.COMPLIANT),
        EvidenceItem(evidence_id="b", name="critical", type="policy", required=True, critical=True, status=ComplianceStatus.COMPLIANT),
        EvidenceItem(evidence_id="c", name="non-critical", type="policy", required=False, critical=False, status=ComplianceStatus.NOT_FOUND),
    ]
    status_08, score_08 = matcher._calculate_score(boundary_08)
    assert score_08 == pytest.approx(0.8)
    assert status_08 == ComplianceStatus.COMPLIANT

    boundary_05 = [
        EvidenceItem(evidence_id="a", name="critical", type="policy", required=True, critical=True, status=ComplianceStatus.PARTIAL),
        EvidenceItem(evidence_id="b", name="non-critical", type="policy", required=False, critical=False, status=ComplianceStatus.PARTIAL),
    ]
    status_05, score_05 = matcher._calculate_score(boundary_05)
    assert score_05 == pytest.approx(0.5)
    assert status_05 == ComplianceStatus.PARTIAL

    boundary_01 = [
        EvidenceItem(evidence_id="a", name="critical", type="policy", required=True, critical=True, status=ComplianceStatus.NON_COMPLIANT),
        EvidenceItem(evidence_id="b", name="non-critical", type="policy", required=False, critical=False, status=ComplianceStatus.NOT_FOUND),
        EvidenceItem(evidence_id="c", name="non-critical-2", type="policy", required=False, critical=False, status=ComplianceStatus.NOT_FOUND),
    ]
    status_01, score_01 = matcher._calculate_score(boundary_01)
    assert score_01 == pytest.approx(0.1)
    assert status_01 == ComplianceStatus.NON_COMPLIANT


def test_empty_pdf_upload_is_rejected() -> None:
    response = client.post("/api/upload", files={"file": ("empty.pdf", b"", "application/pdf")})
    assert response.status_code == 400


def test_image_only_pdf_uses_ocr_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _run() -> None:
        from backend.ocr.client import PDFTextExtractor

        monkeypatch.setattr(PDFTextExtractor, "_extract_pymupdf", staticmethod(lambda pdf_bytes: ""))
        monkeypatch.setattr(PDFTextExtractor, "_extract_ocr", staticmethod(lambda pdf_bytes: "OCR fallback text"))
        extractor = PDFTextExtractor()
        text = await extractor.extract_text(b"%PDF-1.4")
        assert text == "OCR fallback text"

    asyncio.run(_run())


def test_unsupported_file_type_is_rejected() -> None:
    response = client.post("/api/upload", files={"file": ("bad.xlsx", b"abc", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 400


def test_override_changes_score_and_marks_item() -> None:
    result = RequirementResult(
        requirement_id="HIC-R01",
        chapter="HIC",
        title="Hand Hygiene Policy",
        description="",
        criticality="Critical",
        evidence_items=[
            EvidenceItem(evidence_id="EV-HIC-R01-001", name="Policy", type="policy", required=True, critical=True, status=ComplianceStatus.NOT_FOUND),
        ],
    )
    response = client.put(
        "/api/override",
        json=OverrideRequest(
            result=result,
            evidence_id="EV-HIC-R01-001",
            new_status=ComplianceStatus.COMPLIANT,
            override_note="Verified by reviewer",
        ).model_dump(),
    )
    assert response.status_code == 200
    payload = response.json()["result"]
    assert payload["evidence_items"][0]["manually_overridden"] is True
    assert payload["evidence_items"][0]["override_note"] == "Verified by reviewer"
    assert payload["compliance_score"] > 0.0


def test_override_note_propagates_to_justification() -> None:
    result = RequirementResult(
        requirement_id="HIC-R01",
        chapter="HIC",
        title="Hand Hygiene Policy",
        description="",
        criticality="Critical",
        evidence_items=[
            EvidenceItem(evidence_id="EV-HIC-R01-001", name="Policy", type="policy", required=True, critical=True, status=ComplianceStatus.NOT_FOUND),
        ],
    )
    response = client.put(
        "/api/override",
        json=OverrideRequest(
            result=result,
            evidence_id="EV-HIC-R01-001",
            new_status=ComplianceStatus.COMPLIANT,
            override_note="Needs review",
        ).model_dump(),
    )
    assert response.status_code == 200
    justification = response.json()["result"]["evidence_items"][0]["justification"]
    assert "Needs review" in justification


def test_override_nonexistent_item_returns_404() -> None:
    result = RequirementResult(
        requirement_id="HIC-R01",
        chapter="HIC",
        title="Hand Hygiene Policy",
        description="",
        criticality="Critical",
        evidence_items=[EvidenceItem(evidence_id="EV-HIC-R01-001", name="Policy", type="policy", required=True, critical=True)],
    )
    response = client.put(
        "/api/override",
        json=OverrideRequest(result=result, evidence_id="missing", new_status=ComplianceStatus.COMPLIANT).model_dump(),
    )
    assert response.status_code == 404


def test_pre_requirement_with_hic_text_scores_low(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(SAMPLE_TEXT, "PRE-R01")
    assert result.overall_status in {ComplianceStatus.NOT_FOUND, ComplianceStatus.NON_COMPLIANT}
    assert result.compliance_score < 0.4


def test_hic_requirement_with_pre_text_scores_low(matcher: RequirementMatcher) -> None:
    result = matcher.analyze_document(PRE_TEXT, "HIC-R01")
    assert result.overall_status in {ComplianceStatus.NOT_FOUND, ComplianceStatus.NON_COMPLIANT}
    assert result.compliance_score < 0.4
