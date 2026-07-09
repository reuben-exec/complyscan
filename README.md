<div align="center">
  <img src="frontend-next/public/shield-icon.svg" alt="ComplyScan" width="80" height="92" />
  <h1 align="center">ComplyScan</h1>
  <p align="center"><strong>AI-Powered NABH Healthcare Compliance Analysis Engine</strong></p>

  [![Version](https://img.shields.io/badge/version-MVP--1.0-blue?style=flat-square)](https://github.com/reuben-exec/complyscan)
  [![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
  [![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
  [![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)
  [![Cloudflare AI](https://img.shields.io/badge/Cloudflare%20AI-Llama%203.3%2070B-F38020?style=flat-square&logo=cloudflare)](https://ai.cloudflare.com)
  [![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)]()

  <br />

  <blockquote>
    Transform hospital policy documents into structured NABH compliance insights with explainable evidence scoring, human-in-the-loop review workflows, and downloadable audit-ready reports.
  </blockquote>

  <br />
</div>

---

## Overview

**ComplyScan** is a dual‑pass compliance analysis tool that evaluates healthcare policy documents against NABH (National Accreditation Board for Hospitals & Healthcare Providers) standards. It combines a **fast deterministic keyword matcher** with an **optional LLM semantic validation pass** to produce per‑evidence compliance scores, justifications, and actionable reports.

The MVP covers **2 NABH chapters** (HIC — Hospital Infection Control, and PRE — Patient Rights & Education) with **24 requirements** and **136+ evidence items**. The architecture is designed to scale to all 10 NABH chapters.

---

## Features

| Feature | Description |
|---|---|
| **📄 Document Upload** | Drag‑and‑drop PDF upload with real‑time progress indicator |
| **🔍 Dual‑Pass Analysis** | Deterministic keyword matching → optional LLM semantic reasoning |
| **📊 Dashboard** | Compliance gauge, status breakdown donut, KPI cards, chapter progress bars with temperature color gradients |
| **📑 Requirement Explorer** | Browse assessments by chapter and individual requirement |
| **✏️ Override Workflow** | Human reviewers can override scores with justification notes |
| **📥 PDF Report Export** | Downloadable report with evidence cards, LLM assessment section, and summary scorecard |
| **🌓 Dark Mode** | Theme toggle with persistent preference |
| **🛡️ Advisory Disclaimer** | Persistent banner across all pages |

---

## Compliance Scores

Each evidence item is evaluated and assigned one of the following compliance states:

| Score | Status | Meaning |
|---|---|---|
| **≥ 0.80** | ✅ **Compliant** | Document adequately addresses this requirement |
| **0.50 – 0.79** | ⚠️ **Partial** | Requirement is partially addressed but has gaps |
| **0.10 – 0.49** | ❌ **Non-Compliant** | Requirement is not adequately addressed |
| **0.00** | ➖ **Not Found** | No relevant evidence detected in the document |

The **overall compliance score** is the average across all evidence items. Chapter scores are computed per chapter. The UI uses a **red‑to‑green temperature gradient** for visual reference:
- **Red (0%)** → **Amber (50%)** → **Green (100%)**

> 💡 *The frontend color thresholds (0.70 / 0.40) are deliberately lower than backend thresholds (0.80 / 0.50) for visual comfort — they only affect CSS rendering, not compliance logic.*

---

## Strengths

- **Explainable AI**: Every evidence finding includes a clear justification and optional chain‑of‑thought reasoning from the LLM.
- **Human‑in‑the‑Loop**: Reviewers can override any score and add notes, maintaining audit trail integrity.
- **OCR‑Resilient**: Built‑in fuzzy keyword matching (difflib `SequenceMatcher`, threshold 0.85) tolerates OCR typos.
- **Cross‑Validation**: Corroborating evidence across related requirements boosts confidence scores automatically.
- **Dual‑Pass Efficiency**: Fast deterministic pass for routine items, optional LLM pass only for items needing deeper analysis.
- **Zero External Dependencies for Fuzzy Matching**: Uses Python standard library — no extra pip packages.
- **Lightweight Deployment**: Designed to run on free‑tier hosting (Cloudflare Workers AI, small VPS, or Render).

---

## Limitations

> *These are acknowledged MVP constraints, not design flaws.*

| Limitation | Status |
|---|---|
| **NABH Coverage** | 2 of 10 chapters implemented (HIC, PRE) |
| **Authentication** | Not included in MVP |
| **Multi‑User Persistence** | In‑memory storage for prototype workflow |
| **LLM Dependency** | Semantic pass requires internet access to Cloudflare Workers AI |
| **Language Support** | English‑only at MVP stage |
| **Document Types** | PDF and plain text only |
| **Scalability** | Not load‑tested for concurrent enterprise usage |

---

## Use Cases

- **Hospital Quality Teams** — Pre‑assessment gap analysis before official NABH audits
- **Compliance Consultants** — Rapid policy document review for multiple healthcare facilities
- **Healthcare Administrators** — Internal documentation quality checks
- **Accreditation Prep** — Identify missing or weak areas in policy documentation before submission
- **Training & Education** — Demonstrate NABH requirements and evidence expectations to staff
- **Research** — Benchmark policy completeness across departments or facilities

---

## How to Use

### 1. Upload a Document

Navigate to the **Upload** page and drag‑and‑drop a PDF or text file. ComplyScan supports both digital and scanned PDFs (via OCR).

### 2. Review Chapter Results

After analysis, the **Dashboard** shows:
- Overall compliance score (semicircle gauge)
- Status breakdown (compliant / partial / non‑compliant / not found)
- Per‑chapter progress bars with temperature colors
- KPI summary cards

### 3. Explore Requirements

Click any chapter to see individual requirement assessments. Each requirement shows:
- Compliance score with color indicator
- Detected evidence items with justifications
- LLM analysis (when enabled) with confidence levels

### 4. Override Scores (if needed)

As a reviewer, you can:
- Change a score via the override modal
- Add notes explaining your decision
- The recalculated score updates instantly

### 5. Export Report

Generate a downloadable PDF report containing:
- Summary scorecard
- Per‑evidence findings with full justifications
- LLM assessment section (when available)
- Advisory disclaimer in footer

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Cloudflare Workers AI API key (for LLM pass; optional for keyword‑only mode)

### Backend

```bash
# Clone the repository
git clone https://github.com/reuben-exec/complyscan.git
cd complyscan

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn backend.api.main:app --reload
```

### Frontend

```bash
cd frontend-next
npm install
npm run dev
```

The application will be available at `http://localhost:3000` (dev) or served from `http://localhost:8000/app` (production build via FastAPI static mount).

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
```

> The LLM semantic pass is optional. Without API keys, ComplyScan runs in keyword‑only mode.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI (Python 3.12) |
| **Frontend** | Next.js 16 (App Router) |
| **UI Components** | Tailwind CSS v3, shadcn/ui |
| **Charts** | react-gauge-component, Recharts |
| **Icons** | Phosphor Icons |
| **Fonts** | Quicksand + JetBrains Mono |
| **OCR** | PyMuPDF + Tesseract |
| **LLM** | Cloudflare Workers AI (Llama 3.3 70B Instruct FP8) |
| **State Management** | Zustand (localStorage‑persisted) |
| **Knowledge Base** | JSON files in `data/knowledge_base/` |
| **PDF Report** | fpdf2 |

---

## Architecture Overview

```
User ──▶ Next.js Frontend ──▶ FastAPI Backend ──▶ Knowledge Base (JSON)
                               │
                          ┌────┴────┐
                          │         │
                    Keyword     Optional
                    Matcher     LLM Semantic
                          │    Pass
                          └────┬────┘
                               │
                          ┌────┴────┐
                          │         │
                     Scorer    Report
                    (Cross‑    Generator
                    Validation)  (PDF)
```

### Pipeline

1. **Upload & OCR** — Extract text from digital or scanned PDFs
2. **Keyword Matching** — Fast deterministic pass using 289+ keywords with exclusion filters
3. **Scoring** — Evidence‑level scores with confidence weighting, fuzzy matching, and cross‑validation
4. **LLM Analysis** *(optional)* — Chain‑of‑thought reasoning for items needing deeper interpretation
5. **Reporting** — Dashboard visualization + PDF report generation

---

## Project Status

**Phase**: MVP (Minimum Viable Product) — Version 1.0

| Milestone | Status |
|---|---|
| Core matching engine | ✅ Complete |
| Dual‑pass (keyword + LLM) | ✅ Complete |
| Dashboard & chapter pages | ✅ Complete |
| Override workflow | ✅ Complete |
| PDF report export | ✅ Complete |
| OCR support | ✅ Complete |
| Cross‑validation | ✅ Complete |
| All 10 NABH chapters | 🔄 In progress |
| Multi‑user support | 📋 Planned |
| Authentication | 📋 Planned |

---

## Contributors

<div>
  <table>
    <tr>
      <td align="center">
        <strong>Reuben RL</strong><br />
        <em>Project Lead — Healthcare Analytics & AI</em><br />
        <a href="https://github.com/reuben-exec">@reuben-exec</a>
      </td>
      <td align="center">
        <strong>Aakash Karna</strong><br />
        <em>Project Co-Lead — Healthcare Architecture, Knowledge Engineering, Testing, Reporting & Documentation</em>
      </td>
    </tr>
  </table>
</div>

---

## ⚠️ Disclaimer

> **ComplyScan is an advisory tool intended for educational and preparatory use only.** It is **not** a substitute for:
>
> - An official NABH accreditation assessment
> - Professional regulatory interpretation
> - A certified quality audit
>
> The scores, findings, and reports generated by this tool should be used as **reference material** to guide documentation improvement efforts. Always consult certified NABH assessors for official accreditation decisions.
>
> *This tool does not store or transmit protected health information (PHI). All analysis is performed on synthetic or anonymized document content.*

---

<div align="center">
  <small>Built with ❤️ for healthcare quality improvement</small>
  <br />
  <small>© 2026 Reuben RL & Aakash Karna. MIT License.</small>
</div>
