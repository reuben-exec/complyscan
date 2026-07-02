"""Test the FR-3.2 manual override endpoint."""
import httpx
import sys
import io
import json

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"

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
"""


def main():
    with httpx.Client(timeout=30.0) as client:
        # Step 1: Get baseline analysis result
        print("=" * 60)
        print("TEST 1: Get baseline analysis")
        r = client.post(
            f"{BASE}/api/analyze-text/HIC-R01",
            content=SAMPLE_TEXT,
            headers={"Content-Type": "text/plain"},
        )
        assert r.status_code == 200, f"Analysis failed: {r.status_code} {r.text}"
        baseline = r.json()
        print(f"  Overall: {baseline['overall_status']} ({baseline['compliance_score']:.1%})")

        # Show pre-override state of target items
        target_ids = ["EV-HIC-R01-007", "EV-HIC-R01-003", "EV-HIC-R01-001"]
        for item in baseline["evidence_items"]:
            if item["evidence_id"] in target_ids:
                print(f"  Pre-override [{item['status']}] {item['evidence_id']} — {item['name'][:40]}")
                print(f"    Justification: {item['justification'][:80]}")

        # Step 2: Override NOT_FOUND item to COMPLIANT
        print("\n" + "-" * 60)
        print("TEST 2: Override EV-HIC-R01-007 (Not Found → Compliant)")
        override_payload = {
            "result": baseline,
            "evidence_id": "EV-HIC-R01-007",
            "new_status": "Compliant",
            "override_note": "Hospital has a feedback mechanism in the quality committee minutes",
        }
        r2 = client.put(f"{BASE}/api/override", json=override_payload)
        assert r2.status_code == 200, f"Override failed: {r2.status_code} {r2.text}"
        result2 = r2.json()
        overridden = result2["result"]

        # Verify override
        found_007 = None
        for item in overridden["evidence_items"]:
            if item["evidence_id"] == "EV-HIC-R01-007":
                found_007 = item
                break
        assert found_007 is not None, "EV-HIC-R01-007 not found in result"
        assert found_007["status"] == "Compliant", (
            f"Expected Compliant, got {found_007['status']}"
        )
        assert found_007["manually_overridden"] is True, "manually_overridden should be True"
        assert "Manual override" in found_007["justification"], (
            f"Justification should mention override: {found_007['justification']}"
        )
        assert "quality committee" in found_007["justification"], (
            f"Justification should contain override note: {found_007['justification']}"
        )
        print(f"  ✓ Status now: {found_007['status']}")
        print(f"  ✓ manually_overridden: {found_007['manually_overridden']}")
        print(f"  ✓ Justification: {found_007['justification'][:100]}")
        print(f"  ✓ Score recalculated: {overridden['compliance_score']:.1%}")

        # Step 3: Override PARTIAL item to COMPLIANT
        print("\n" + "-" * 60)
        print("TEST 3: Override EV-HIC-R01-001 (Partial → Compliant)")
        override_payload2 = {
            "result": overridden,  # chain from previous override
            "evidence_id": "EV-HIC-R01-001",
            "new_status": "Compliant",
            "override_note": "Policy document clearly states effective date and review cycle",
        }
        r3 = client.put(f"{BASE}/api/override", json=override_payload2)
        assert r3.status_code == 200, f"Override failed: {r3.status_code} {r3.text}"
        result3 = r3.json()
        overridden2 = result3["result"]

        # Verify multiple overrides preserved
        overridden_count = sum(
            1 for e in overridden2["evidence_items"] if e.get("manually_overridden")
        )
        print(f"  Items manually overridden: {overridden_count}")
        assert overridden_count == 2, f"Expected 2 overrides, found {overridden_count}"
        print(f"  ✓ Overall: {overridden2['overall_status']} ({overridden2['compliance_score']:.1%})")

        # Step 4: Override NON_COMPLIANT to PARTIAL
        print("\n" + "-" * 60)
        print("TEST 4: Override EV-HIC-R01-003 (Non-Compliant → Partial)")
        override_payload3 = {
            "result": overridden2,
            "evidence_id": "EV-HIC-R01-003",
            "new_status": "Partial",
            "override_note": "Technique partly described, hand washing duration included",
        }
        r4 = client.put(f"{BASE}/api/override", json=override_payload3)
        assert r4.status_code == 200, f"Override failed: {r4.status_code} {r4.text}"
        result4 = r4.json()
        overridden3 = result4["result"]
        print(f"  ✓ Overall: {overridden3['overall_status']} ({overridden3['compliance_score']:.1%})")
        for item in overridden3["evidence_items"]:
            if item.get("manually_overridden"):
                print(f"    [{item['status']}] {item['evidence_id']} (overridden)")

        # Step 5: Verify 404 for non-existent evidence_id
        print("\n" + "-" * 60)
        print("TEST 5: Override non-existent evidence_id (should 404)")
        override_payload4 = {
            "result": baseline,
            "evidence_id": "EV-NONEXISTENT",
            "new_status": "Compliant",
        }
        r5 = client.put(f"{BASE}/api/override", json=override_payload4)
        assert r5.status_code == 404, f"Expected 404, got {r5.status_code}: {r5.text}"
        print(f"  ✓ Got 404: {r5.json()['detail'][:60]}")

        # Step 6: Verify disclaimer in override response
        print("\n" + "-" * 60)
        print("TEST 6: Verify disclaimer presence")
        assert "disclaimer" in result2, "Override response missing disclaimer"
        assert "Advisory tool only" in result2["disclaimer"], (
            f"Unexpected disclaimer: {result2['disclaimer']}"
        )
        print(f"  ✓ {result2['disclaimer'][:60]}...")

        print("\n" + "=" * 60)
        print("ALL OVERRIDE TESTS PASSED ✓")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
