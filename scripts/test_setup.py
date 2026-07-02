#!/usr/bin/env python3
"""Test script for ComplyScan MVP."""
import asyncio
import json
from pathlib import Path

# Test the requirement loader
from backend.matcher.engine import RequirementLoader, RequirementMatcher

def test_requirement_loader():
    """Test loading requirements."""
    loader = RequirementLoader()
    
    # Test loading all
    all_reqs = loader.load_all()
    print(f"Total requirements loaded: {len(all_reqs)}")
    
    # Test loading specific
    hic_r01 = loader.load("HIC-R01")
    pre_r01 = loader.load("PRE-R01")
    
    print(f"\nHIC-R01: {hic_r01['title']}")
    print(f"Evidence items: {hic_r01['evidence_schema']['total_evidence_items']}")
    
    print(f"\nPRE-R01: {pre_r01['title']}")
    print(f"Evidence items: {pre_r01['evidence_schema']['total_evidence_items']}")


def test_matcher():
    """Test matching logic with sample text."""
    matcher = RequirementMatcher()
    
    # Sample text that should match HIC-R01
    sample_text = """
    HAND HYGIENE POLICY
    
    Effective Date: 2024-01-15
    Review Date: 2025-01-15
    
    This policy follows the WHO Five Moments for Hand Hygiene framework.
    
    Indications:
    1. Before touching a patient
    2. After body fluid exposure
    3. Before clean procedure
    4. After touching patient
    5. After touching surroundings
    
    Technique: Alcohol-based hand rub (ABHR) with 60-70% alcohol content.
    Apply product and rub hands for at least 20-30 seconds.
    
    Training: All staff must complete hand hygiene training within 48 hours
    of joining, with annual refresher training and competency assessment.
    
    Audit: Monthly hand hygiene audits will be conducted with a target of >=90% compliance.
    
    Approved by: Medical Director
    """
    
    result = matcher.analyze_document(sample_text, "HIC-R01")
    
    print(f"\n=== HIC-R01 Analysis Results ===")
    print(f"Overall Status: {result.overall_status.value}")
    print(f"Compliance Score: {result.compliance_score:.0%}")
    
    for item in result.evidence_items:
        print(f"\n  {item.name}: {item.status.value}")
        print(f"    Justification: {item.justification}")


if __name__ == "__main__":
    test_requirement_loader()
    test_matcher()
