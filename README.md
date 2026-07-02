# ComplyScan

AI-powered Healthcare Compliance & Audit Automation Engine

ComplyScan is an AI-assisted compliance screening platform that helps hospitals perform pre-audit assessments against healthcare accreditation requirements. The MVP focuses on two major compliance chapters:

- Hospital Infection Control (HIC)
- Patient Rights & Education (PRE)

Instead of manually reviewing hundreds of pages of hospital documents, ComplyScan extracts evidence, evaluates compliance requirements, and generates an explainable gap report.

---

## Project Status

Current Stage: Knowledge Base Development

Completed

- Business Requirements Document (BRD)
- Functional Requirements Document (FRD)
- Standard Operating Procedure (SOP)
- Project Structure
- HIC Knowledge Base (12 Requirements)
- PRE Knowledge Base (12 Requirements)

In Progress

- Rule Engine
- Backend Development
- OCR Pipeline
- Compliance Matching Engine

Planned

- FastAPI Backend
- React Dashboard
- PDF Report Generation
- LLM-assisted Semantic Validation

---

## Project Structure

```
ComplyScan/

backend/
frontend/

data/
    knowledge_base/
        HIC/
        PRE/

    rules/
    schemas/
    prompts/
    synthetic_documents/
    evaluation/

database/
docs/
tests/
```

---

## Technology Stack

Backend
- Python
- FastAPI

AI
- OCR (Tesseract / PyMuPDF)
- LLM-assisted Semantic Matching
- Rule-based Compliance Engine

Database
- PostgreSQL

Frontend
- React
- Tailwind CSS

---

## MVP Scope

The MVP is intentionally limited to:

- 2 Accreditation Chapters
- 24 Compliance Requirements
- Synthetic Hospital Documents
- Explainable Compliance Reports

This project is intended for educational and portfolio purposes.

---

## Disclaimer

ComplyScan is **not** an official NABH assessment tool.

The compliance knowledge base is built using publicly available secondary references (WHO, CDC, ICMR, Ministry of Health guidance, and publicly available NABH-related training material). Results produced by the application are advisory only and should not be treated as an accreditation decision.

---

## Roadmap

- Complete Rule Engine
- Build Knowledge Loader
- Implement OCR Pipeline
- Develop Matching Engine
- Generate Compliance Reports
- Build Dashboard
- Deploy MVP

---

## Authors

Aakash Karna

Healthcare Analytics • AI • Hospital Operations
