"""FastAPI application entry point."""
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

from backend.services.document_service import document_service
from backend.matcher.engine import RequirementLoader, RequirementMatcher
from backend.report.generator import save_report
from backend.models.schemas import RequirementResult, EvidenceItem, OverrideRequest, OverrideResponse
from backend.core.config import settings, DISCLAIMER
from backend.semantic.analyzer import SemanticAnalyzer


app = FastAPI(
    title="ComplyScan API",
    description="NABH Compliance & Audit Automation Engine",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "ComplyScan API - NABH Compliance Automation Engine", "disclaimer": DISCLAIMER}


@app.get("/api/chapters")
async def get_chapters():
    """Get available NABH chapters."""
    return {
        "chapters": [
            {"code": "HIC", "name": "Hospital Infection Control"},
            {"code": "PRE", "name": "Patient Rights & Education"}
        ],
        "disclaimer": DISCLAIMER
    }


@app.get("/api/requirements/{chapter}")
async def get_requirements(chapter: str):
    """Get requirements for a specific chapter."""
    loader = RequirementLoader()
    all_reqs = loader.load_all()
    
    requirements = [
        {
            "requirement_id": r["requirement_id"],
            "title": r["title"],
            "criticality": r["criticality"]
        }
        for r in all_reqs.values()
        if r.get("chapter") == chapter.upper()
    ]
    
    if not requirements:
        raise HTTPException(status_code=404, detail=f"No requirements found for chapter {chapter}")
    
    return {"chapter": chapter.upper(), "requirements": requirements, "disclaimer": DISCLAIMER}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = Path(file.filename).suffix.lower()
    allowed = {".pdf", ".txt", ".docx"}
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(allowed))}"
        )
    
    file_bytes = await file.read()
    
    try:
        response = await document_service.upload_document(file_bytes, file.filename)
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Upload a file and extract its text content.
    
    Supports .txt, .pdf, and .docx files. Returns the extracted text
    which can then be pasted into the analysis text area.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = Path(file.filename).suffix.lower()
    content = await file.read()
    text = ""
    
    try:
        if ext == ".txt":
            text = content.decode("utf-8", errors="replace")
        
        elif ext == ".pdf":
            from backend.ocr import PDFTextExtractor
            extractor = PDFTextExtractor()
            text = await extractor.extract_text(content)
        
        elif ext == ".docx":
            try:
                import io
                from docx import Document
                doc = Document(io.BytesIO(content))
                paragraphs = []
                for p in doc.paragraphs:
                    if p.text.strip():
                        paragraphs.append(p.text.strip())
                text = "\n\n".join(paragraphs)
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="DOCX support requires python-docx package. Install with: pip install python-docx"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported formats: .txt, .pdf, .docx"
            )
        
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file. The file may be empty or contain only images."
            )
        
        return {
            "text": text.strip(),
            "filename": file.filename,
            "format": ext,
            "char_count": len(text.strip())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")


@app.post("/api/analyze/{requirement_id}")
async def analyze_document(requirement_id: str, document_id: str):
    """Analyze uploaded document against a requirement (requires Workers AI OCR).
    
    Args:
        requirement_id: Requirement to check (HIC-R01, PRE-R01)
        document_id: Document ID from upload
    """
    try:
        result = await document_service.process_document(document_id, requirement_id)
        return result.model_dump()
    except ValueError as e:
        msg = str(e)
        if "CF_API_TOKEN" in msg or "CF_ACCOUNT_ID" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-text/{requirement_id}")
async def analyze_text(
    requirement_id: str,
    text: str = Body(..., media_type="text/plain"),
    use_llm: bool = Query(False, description="Enable LLM semantic pass for items below COMPLIANT"),
):
    """Analyze raw text against a requirement (no OCR needed - useful for testing).
    
    Args:
        requirement_id: Requirement to check (HIC-R01, PRE-R01)
        text: Raw document text to analyze
        use_llm: If true, run LLM semantic pass on non-compliant evidence items
    """
    try:
        matcher = RequirementMatcher()
        result = matcher.analyze_document(text, requirement_id)  # Pass 1
        
        if use_llm and settings.llm_enabled:
            loader = RequirementLoader()
            requirement = loader.load(requirement_id)
            evidence_schema = requirement.get("evidence_schema", {}).get("evidence", [])
            analyzer = SemanticAnalyzer()
            result = await analyzer.enhance(result, text, evidence_schema=evidence_schema)  # Pass 2
        
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-semantic/{requirement_id}")
async def analyze_semantic(
    requirement_id: str,
    text: str = Body(..., media_type="text/plain"),
):
    """Analyze text with both keyword (Pass 1) and LLM semantic (Pass 2) passes.
    
    This endpoint runs the full dual-pass pipeline:
      Pass 1 — Fast keyword/concept/hint matching
      Pass 2 — LLM semantic analysis for items scoring below COMPLIANT
    
    Args:
        requirement_id: Requirement to check (HIC-R01, PRE-R01)
        text: Raw document text to analyze
    """
    try:
        matcher = RequirementMatcher()
        result = matcher.analyze_document(text, requirement_id)  # Pass 1
        
        if settings.llm_enabled:
            loader = RequirementLoader()
            requirement = loader.load(requirement_id)
            evidence_schema = requirement.get("evidence_schema", {}).get("evidence", [])
            analyzer = SemanticAnalyzer()
            result = await analyzer.enhance(result, text, evidence_schema=evidence_schema)  # Pass 2
        
        return result.model_dump()
    except ValueError as e:
        msg = str(e)
        if "CF_API_TOKEN" in msg or "CF_ACCOUNT_ID" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/override")
async def manual_override(request: OverrideRequest):
    """Manually override an evidence item's compliance status (human-in-the-loop).

    Per SOP Step 4, allows the reviewer to correct auto-assigned statuses
    when the tool misclassifies an item (false positive/negative).

    Args:
        request: The full RequirementResult + override parameters.

    Returns:
        Updated RequirementResult with the override applied and score recalculated.
    """
    try:
        from backend.matcher.engine import RequirementMatcher
        matcher = RequirementMatcher()

        # Apply override to the evidence item
        found = False
        for item in request.result.evidence_items:
            if item.evidence_id == request.evidence_id:
                item.status = request.new_status
                item.manually_overridden = True
                item.override_note = request.override_note
                item.justification = (
                    f"Manual override to {request.new_status.value}"
                    + (f" \u2014 {request.override_note}" if request.override_note else "")
                )
                found = True
                break

        if not found:
            raise HTTPException(
                status_code=404,
                detail=f"Evidence item '{request.evidence_id}' not found in result"
            )

        # Recalculate overall status and score
        new_status, new_score = matcher._calculate_score(request.result.evidence_items)

        request.result.overall_status = new_status
        request.result.compliance_score = new_score

        return OverrideResponse(result=request.result).model_dump()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report")
async def generate_report(result: dict = Body(...)):
    """Generate PDF report from analysis result.
    
    Args:
        result: Analysis result JSON (from /api/analyze or /api/analyze-text)
    
    Returns:
        PDF file download
    """
    try:
        evidence_items = [EvidenceItem(**e) for e in result.get("evidence_items", [])]
        req_result = RequirementResult(**result)
        
        pdf_path = save_report(req_result)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"{req_result.requirement_id}_compliance_report.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend SPA at /app
app.mount("/static", StaticFiles(directory="backend/static"), name="static_files")
app.mount("/app", StaticFiles(directory="backend/static", html=True), name="static_app")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)