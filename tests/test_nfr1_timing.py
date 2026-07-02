"""NFR-1 Performance Test: Measure processing time for ≤20-page document.

Procedure:
1. Extract text from the 20-page HIC PDF using PyMuPDF (local)
2. POST text to /api/analyze-text/{requirement_id} for HIC-R01 (most evidence-rich)
3. Verify response < 30 seconds
4. Report individual and cumulative timings

NFR-1: A document of ≤20 pages processes and returns results in under 30 seconds.
"""
import httpx
import time
import json
import sys
import os
import pymupdf

PDF_PATH = "D:/ComplyScan/tests/nfr1_20page_hic.pdf"
BASE_URL = "http://localhost:8000"
TIMEOUT = 60  # generous timeout for each call

# All HIC requirements (12 items)
HIC_REQUIREMENTS = [f"HIC-R{i:02d}" for i in range(1, 13)]


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = pymupdf.open(pdf_path)
    pages = doc.page_count
    chunks = []
    for page_num in range(pages):
        page = doc.load_page(page_num)
        text = page.get_text()
        chunks.append(text)
    doc.close()
    full_text = "\n".join(chunks)
    return full_text, pages


def test_single_requirement(
    client: httpx.Client, text: str, requirement_id: str
) -> dict:
    """Test a single requirement and return timing data."""
    url = f"{BASE_URL}/api/analyze-text/{requirement_id}"

    start = time.time()
    try:
        resp = client.post(url, content=text, timeout=TIMEOUT)
        elapsed = time.time() - start
    except httpx.TimeoutException:
        elapsed = time.time() - start
        return {
            "requirement_id": requirement_id,
            "elapsed": elapsed,
            "status": "TIMEOUT",
            "http_status": None,
            "overall_status": None,
            "compliance_score": None,
            "evidence_count": None,
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "requirement_id": requirement_id,
            "elapsed": elapsed,
            "status": f"ERROR: {e}",
            "http_status": None,
            "overall_status": None,
            "compliance_score": None,
            "evidence_count": None,
        }

    # Parse response
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return {
            "requirement_id": requirement_id,
            "elapsed": elapsed,
            "status": "INVALID_JSON",
            "http_status": resp.status_code,
            "overall_status": None,
            "compliance_score": None,
            "evidence_count": None,
        }

    result = {
        "requirement_id": requirement_id,
        "elapsed": elapsed,
        "status": "OK" if resp.status_code == 200 else f"HTTP_{resp.status_code}",
        "http_status": resp.status_code,
        "overall_status": data.get("overall_status"),
        "compliance_score": data.get("compliance_score"),
        "evidence_count": len(data.get("evidence_items", [])),
    }
    return result


def print_report(req_timings: list[dict], total_elapsed: float, pages: int):
    """Print formatted timing report."""
    print(f"\n{'='*70}")
    print(f"  NFR-1 TIMING REPORT")
    print(f"  Document: {os.path.basename(PDF_PATH)} ({pages} pages)")
    print(f"  Server:   {BASE_URL}")
    print(f"  Threshold: < 30 seconds per requirement")
    print(f"{'='*70}")

    # Per-requirement results table
    print(f"\n  {'Req':<12} {'Status':<12} {'Time':<10} {'Overall':<14} {'Score':<8} {'Evid':<6}")
    print(f"  {'-'*12} {'-'*12} {'-'*10} {'-'*14} {'-'*8} {'-'*6}")
    for r in req_timings:
        elapsed_str = f"{r['elapsed']:.3f}s"
        print(f"  {r['requirement_id']:<12} {r['status']:<12} {elapsed_str:<10} "
              f"{str(r['overall_status'] or '-'):<14} {str(r['compliance_score'] or '-'):<8} "
              f"{str(r['evidence_count'] or '-'):<6}")

    # Summary
    print(f"\n  {'SUMMARY':^60}")
    print(f"  {'='*60}")
    ok_times = [r["elapsed"] for r in req_timings if r["status"] == "OK"]
    failed = [r for r in req_timings if r["status"] != "OK"]

    if ok_times:
        print(f"  Successful: {len(ok_times)}/{len(req_timings)}")
        print(f"  Avg time:   {sum(ok_times)/len(ok_times):.3f}s")
        print(f"  Max time:   {max(ok_times):.3f}s")
        print(f"  Min time:   {min(ok_times):.3f}s")

    if failed:
        print(f"  Failed:     {len(failed)}/{len(req_timings)}")
        for f in failed:
            print(f"    {f['requirement_id']}: {f['status']}")

    print(f"\n  Total wall time (all reqs): {total_elapsed:.3f}s")
    print(f"{'='*70}\n")


def test_nfr1(pass_name: str = "Pass 1", requirements: list[str] | None = None) -> bool:
    """Run NFR-1 timing test.

    Args:
        pass_name: Label for this test pass
        requirements: List of requirement IDs to test (default: all HIC)

    Returns:
        True if all requirements pass < 30s threshold
    """
    reqs = requirements or HIC_REQUIREMENTS
    print(f"\n{'='*70}")
    print(f"  NFR-1 Timing Test ({pass_name})")
    print(f"  Requirements: {len(reqs)} ({', '.join(reqs[:3])}{'...' if len(reqs) > 3 else ''})")
    print(f"{'='*70}")

    # Verify PDF exists
    if not os.path.exists(PDF_PATH):
        print(f"  FAIL: PDF not found at {PDF_PATH}")
        return False

    # Extract text
    print(f"\n  Extracting text from PDF...", end=" ", flush=True)
    text, pages = extract_text(PDF_PATH)
    print(f"done. ({pages} pages, {len(text):,} chars)")

    if pages > 20:
        print(f"  WARNING: Document is {pages} pages, exceeds 20-page limit")

    # Test each requirement
    req_timings = []
    overall_start = time.time()

    with httpx.Client(timeout=TIMEOUT) as client:
        for i, req_id in enumerate(reqs):
            print(f"\n  [{i+1}/{len(reqs)}] Testing {req_id}...", end=" ", flush=True)
            result = test_single_requirement(client, text, req_id)
            result_str = (f"{result['elapsed']:.3f}s"
                          if result["status"] == "OK"
                          else result["status"])
            print(f"{result_str}", flush=True)
            req_timings.append(result)

    total_elapsed = time.time() - overall_start

    # Print report
    print_report(req_timings, total_elapsed, pages)

    # Check pass/fail
    all_ok = all(r["status"] == "OK" and r["elapsed"] < 30 for r in req_timings)
    if all_ok:
        print(f"  >>> NFR-1: PASS <<<")
    else:
        failed = [r for r in req_timings
                  if r["status"] != "OK" or r["elapsed"] >= 30]
        for f in failed:
            if f["status"] == "OK":
                print(f"  >>> FAIL: {f['requirement_id']} took {f['elapsed']:.3f}s (>= 30s) <<<")
            else:
                print(f"  >>> FAIL: {f['requirement_id']}: {f['status']} <<<")

    return all_ok


if __name__ == "__main__":
    # Run multiple passes over HIC-R01 (most complex requirement)
    print("=" * 70)
    print("  NFR-1 PERFORMANCE VERIFICATION")
    print("  Running 3 iterations...")
    print("=" * 70)

    results = []
    for i in range(3):
        result = test_nfr1(pass_name=f"Pass {i+1}", requirements=["HIC-R01"])
        results.append(result)

    print(f"\n{'='*70}")
    print(f"  NFR-1 SUMMARY: {sum(results)}/3 passed (< 30s each)")
    print(f"{'='*70}")

    sys.exit(0 if all(results) else 1)
