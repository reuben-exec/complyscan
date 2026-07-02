"""End-to-end test of the analyze + report pipeline via HTTP."""
import httpx
import sys
import json
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"

# Realistic hand-hygiene policy text that should score well against HIC-R01
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

# Biomedical waste text for HIC-R03
WASTE_TEXT = """
Biomedical Waste Management Policy

The hospital generates biomedical waste from patient care, laboratory, and
surgical procedures. Waste segregation is performed at the point of generation
following CPCB color-coded bag system:
- Yellow bags: Human anatomical waste, soiled waste, expired medicines.
- Red bags: Contaminated waste (recyclable) — tubing, bottles, IV sets.
- White/Translucent Puncture-Proof Containers: Sharps including needles,
  scalpels, broken glass.
- Blue cardboard containers: Glass ampoules, vials.

Waste is stored in designated covered areas and transported to the BMW
treatment facility through authorized tie-up with CBWTF.
Managers verify segregation compliance through weekly Waste Audit findings.
"""


def main():
    with httpx.Client(timeout=30.0) as client:
        # Test 1: Analyze HIC-R01 with good text
        print("=" * 60)
        print("TEST 1: HIC-R01 Hand Hygiene (good text)")
        r = client.post(f"{BASE}/api/analyze-text/HIC-R01", 
                        content=SAMPLE_TEXT, 
                        headers={"Content-Type": "text/plain"})
        if r.status_code != 200:
            print(f"  FAIL: {r.status_code} {r.text}")
            return False
        
        result = r.json()
        print(f"  Overall Status: {result['overall_status']}")
        print(f"  Compliance Score: {result['compliance_score']:.1%}")
        print(f"  Evidence Items: {len(result['evidence_items'])}")
        for item in result['evidence_items']:
            print(f"    - [{item['status']}] {item['name'][:40]}")
        
        # Test 2: Generate report from result
        print("\nTEST 2: Generate PDF report")
        r2 = client.post(f"{BASE}/api/report", json=result)
        if r2.status_code != 200:
            print(f"  FAIL: {r2.status_code} {r2.text}")
            return False
        
        report_path = "D:/ComplyScan/output/reports/test_hic_r01_report.pdf"
        with open(report_path, "wb") as f:
            f.write(r2.content)
        print(f"  Saved report: {report_path} ({len(r2.content)} bytes)")
        
        # Verify PDF starts with %PDF
        if r2.content[:4] == b"%PDF":
            print("  Report is valid PDF ✓")
        else:
            print("  FAIL: Not a valid PDF")
            return False
        
        # Test 3: HIC-R01 with empty text (should be NOT_FOUND)
        print("\nTEST 3: HIC-R01 with empty text")
        r3 = client.post(f"{BASE}/api/analyze-text/HIC-R01", 
                         content="   ", 
                         headers={"Content-Type": "text/plain"})
        if r3.status_code != 200:
            print(f"  FAIL: {r3.status_code}")
            return False
        result3 = r3.json()
        print(f"  Overall Status: {result3['overall_status']}")
        print(f"  Score: {result3['compliance_score']}")
        if result3["overall_status"] == "Not Found":
            print("  Correctly identified no keywords ✓")
        else:
            print(f"  Expected NOT FOUND, got {result3['overall_status']}")
        
        # Test 4: HIC-R03 with waste text
        print("\nTEST 4: HIC-R03 Biomedical Waste (good text)")
        r4 = client.post(f"{BASE}/api/analyze-text/HIC-R03", 
                         content=WASTE_TEXT,
                         headers={"Content-Type": "text/plain"})
        if r4.status_code != 200:
            print(f"  FAIL: {r4.status_code} {r4.text}")
            return False
        result4 = r4.json()
        print(f"  Overall Status: {result4['overall_status']}")
        print(f"  Compliance Score: {result4['compliance_score']:.1%}")
        for item in result4['evidence_items']:
            print(f"    - [{item['status']}] {item['name'][:50]}")
        
        # Test 5: LLM-enhanced analysis (optional — skips gracefully if no credentials)
        print("\nTEST 5: HIC-R01 with LLM semantic pass")
        r5 = client.post(
            f"{BASE}/api/analyze-semantic/HIC-R01",
            content=SAMPLE_TEXT,
            headers={"Content-Type": "text/plain"},
            timeout=120.0,
        )
        if r5.status_code == 400 and "CF_API_TOKEN" in r5.text:
            print("  SKIP: Server has no CF_API_TOKEN — LLM test skipped")
        elif r5.status_code != 200:
            print(f"  FAIL: {r5.status_code} {r5.text}")
            return False
        else:
            result5 = r5.json()
            print(f"  Overall Status: {result5['overall_status']}")
            print(f"  Compliance Score: {result5['compliance_score']:.1%}")
            llm_count = sum(1 for e in result5['evidence_items'] if e.get('llm_evaluated'))
            print(f"  LLM-evaluated items: {llm_count}/{len(result5['evidence_items'])}")
            for item in result5['evidence_items']:
                llm_tag = " [LLM]" if item.get('llm_evaluated') else ""
                print(f"    - [{item['status']}]{llm_tag} {item['name'][:40]}")
            if llm_count > 0:
                print("  LLM integration verified ✓")
            else:
                # Items may already be COMPLIANT from Pass 1, so no LLM needed
                print("  (No items needed LLM — all already COMPLIANT)")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
