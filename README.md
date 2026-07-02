# ComplyScan

## AI-Powered Healthcare Compliance & Audit Automation Engine

> ComplyScan turns hospital policy documents into structured NABH compliance insights with explainable evidence scoring, human review hooks, downloadable reports, and a premium audit-console experience for healthcare reviewers.

## What It Does
- Upload hospital documents and check them against NABH-aligned requirements.
- Run a deterministic keyword-first pass followed by optional LLM semantic validation.
- Produce per-evidence findings, compliance scores, override workflows, executive summaries, and PDF-ready reports.

## Business Requirements (BRD Trace)

| BR ID | Requirement | Status | How It Is Implemented |
|---|---|---|---|
| BR-1 | Upload hospital documents tied to a NABH chapter | ✅ Implemented | FastAPI upload endpoint and document service |
| BR-2 | Compare documents against pre-defined compliance checklists | ✅ Implemented | JSON-based knowledge base under data/knowledge_base/ |
| BR-3 | Flag each evidence item as Compliant/Partial/Non-Compliant/Not Found with rationale | ✅ Implemented | Evidence matcher and requirement result schema |
| BR-4 | Generate downloadable summary reports for reviewers | ✅ Implemented | PDF report generation through backend/report/generator.py |
| BR-5 | Clearly disclose advisory-only usage | ✅ Implemented | Disclaimer banner in API responses and UI |

## Functional Requirements (FRD Trace)

| FR ID | Requirement | Priority | Status | Code Location |
|---|---|---|---|---|
| FR-1.1 | Accept PDF/text uploads | Must | ✅ | backend/api/main.py |
| FR-1.2 | Extract text from digital and scanned PDFs | Must | ✅ | backend/ocr/client.py |
| FR-2.1 | Store structured chapter-based requirement data | Must | ✅ | data/knowledge_base/ |
| FR-2.2 | Run dual-pass matching (keyword + semantic) | Must | ✅ | backend/matcher/engine.py and backend/semantic/analyzer.py |
| FR-3.1 | Return evidence-level status and justification | Must | ✅ | backend/models/schemas.py |
| FR-3.2 | Support manual override and recalculate score | Should | ✅ | backend/api/main.py |
| FR-4.1 | Surface grouped chapter/requirement review in the UI | Must | ✅ | backend/static/ |
| FR-4.2 | Export reports to PDF | Must | ✅ | backend/report/generator.py |
| FR-5.1 | Keep a persistent advisory disclaimer | Must | ✅ | backend/core/config.py |

## Architecture

ComplyScan uses a two-pass pipeline:

1. Pass 1: deterministic keyword/concept matching for rapid evidence detection.
2. Pass 2: optional LLM semantic validation for items that need deeper interpretation.

### Tech Stack

| Layer | Stack |
|---|---|
| API | FastAPI |
| Frontend | Vanilla JavaScript, HTML, CSS |
| OCR | PyMuPDF + Tesseract |
| AI | Cloudflare Workers AI |
| Data | JSON knowledge base |

### Knowledge Base Stats
- 24 JSON requirement files
- 2 chapters: HIC and PRE
- 136 evidence items across the current knowledge base

## Edge Cases & Testing

The project now includes deterministic regression tests for:
- perfect-match and empty-input scoring
- keyword-boundary and multi-word phrase behavior
- partial-evidence downgrades and critical-item weighting
- override recalculation and note propagation
- cross-requirement isolation between HIC and PRE content

## NABH Coverage
- HIC chapter: 12 requirements
- PRE chapter: 12 requirements
- Evidence items are mapped per requirement and scored at evidence level

## Quick Start

### Local Development
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

### Live Demo
- https://complyscan-llm-calling.onrender.com/app/

## Build Timeline

The MVP was built in a focused five-day sprint based on the project plan:

- Day 1: Data source consolidation and knowledge base setup
- Day 2: Rule engine and dual-pass matcher implementation
- Day 3: Frontend experience and report generation
- Day 4: FRD/SOP alignment and review workflow
- Day 5: Testing, polish, and deployment preparation

## Why ComplyScan Stands Out
- Applies LLM reasoning to healthcare compliance rather than generic document QA.
- Combines fast deterministic scoring with explainable semantic review.
- Supports human-in-the-loop override decisions for reviewer confidence.
- Designed as an advisory tool, not a replacement for formal NABH assessment.
- Built to run on low-cost or free-tier deployment environments.

## Non-Functional Requirements

| NFR ID | Requirement | Status |
|---|---|---|
| NFR-1 | Process 20-page PDFs in under 30 seconds | ⚠️ Verified through local smoke tests, pending formal benchmark |
| NFR-2 | Avoid PHI and use synthetic examples | ✅ Implemented |
| NFR-3 | Keep the upload-to-report workflow simple | ✅ Implemented |
| NFR-4 | Deploy on a free-tier environment | ✅ Live demo available |

## Limitations & Known Issues
- MVP scope covers 2 NABH chapters rather than the full 10-chapter library.
- The tool is advisory-only and not an official NABH determination.
- Authentication and multi-user persistence are not included in the MVP.
- Storage is currently in-memory for the prototype workflow.

## Project Structure

```text
backend/
  api/
  core/
  matcher/
  models/
  ocr/
  parser/
  report/
  scorer/
  semantic/
  services/
  static/
data/
  knowledge_base/
logs/
output/
  exports/
  reports/
tests/
```

## Team
- Reuben RL — Project Lead / Healthcare Analytics & AI
- Aakash Karna — Project Co-Lead (Knowledge Base & Documentation)

## Disclaimer

This tool is intended for advisory and educational use only. It is not a substitute for an official NABH assessment, regulatory interpretation, or professional quality review.
