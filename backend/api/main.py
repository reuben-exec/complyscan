"""FastAPI application entry point."""
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse
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
from backend.scorer.cross_validation import CrossValidator


# ── Constants ────────────────────────────────────────────────────
FRONTEND_DIR = Path("frontend-next/out")
INDEX_HTML = FRONTEND_DIR / "index.html"


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


# ── API Routes ───────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


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
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
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


# ── Frontend SPA ────────────────────────────────────────────────
# Mount immutable assets (JS/CSS) at /_app with cache headers
if FRONTEND_DIR.exists():
    # Mount Next.js _next assets
    next_dir = FRONTEND_DIR / "_next"
    if next_dir.exists():
        app.mount(
            "/app/_next",
            StaticFiles(directory=str(next_dir)),
            name="next_assets",
        )


# SPA catch-all: for any path under /app/* that isn't an API route
# or a real static file, return index.html (SPA client-side routing)
@app.get("/app/{path:path}")
async def spa_serve(path: str):
    """SPA catch-all - serve static files or index.html for client-side routing."""
    # Try to serve the actual file first
    file_path = FRONTEND_DIR / path
    if file_path.is_file():
        return FileResponse(str(file_path))

    # Try with .html extension (e.g. /app/upload -> upload.html)
    html_path = FRONTEND_DIR / (path + ".html")
    if html_path.is_file():
        return FileResponse(str(html_path))

    # Try index.html in subdirectory
    index_path = FRONTEND_DIR / path / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))

    # Fallback to root index.html for SPA routing
    if INDEX_HTML.exists():
        return HTMLResponse(content=INDEX_HTML.read_text(encoding="utf-8"))

    return HTMLResponse(content="<h1>Frontend not built. Run: cd frontend-next && npm run build</h1>", status_code=501)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    """Serve favicon.ico."""
    favicon_path = FRONTEND_DIR / "favicon.ico"
    if favicon_path.is_file():
        return FileResponse(str(favicon_path), media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="Favicon not found")


@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    """Serve apple-touch-icon.png."""
    icon_path = FRONTEND_DIR / "apple-touch-icon.png"
    if icon_path.is_file():
        return FileResponse(str(icon_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Icon not found")


@app.get("/site.webmanifest", include_in_schema=False)
async def webmanifest():
    """Serve site.webmanifest."""
    manifest_path = FRONTEND_DIR / "site.webmanifest"
    if manifest_path.is_file():
        return FileResponse(str(manifest_path), media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="Manifest not found")


@app.get("/favicon-96x96.png", include_in_schema=False)
async def favicon_96():
    """Serve favicon-96x96.png (referenced in webmanifest)."""
    favicon_path = FRONTEND_DIR / "favicon-96x96.png"
    if favicon_path.is_file():
        return FileResponse(str(favicon_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Favicon 96 not found")


@app.get("/web-app-manifest-192x192.png", include_in_schema=False)
async def manifest_icon_192():
    """Serve web-app-manifest-192x192.png."""
    icon_path = FRONTEND_DIR / "web-app-manifest-192x192.png"
    if icon_path.is_file():
        return FileResponse(str(icon_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Manifest icon 192 not found")


@app.get("/web-app-manifest-512x512.png", include_in_schema=False)
async def manifest_icon_512():
    """Serve web-app-manifest-512x512.png."""
    icon_path = FRONTEND_DIR / "web-app-manifest-512x512.png"
    if icon_path.is_file():
        return FileResponse(str(icon_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Manifest icon 512 not found")


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect bare root to the SPA."""
    return RedirectResponse(url="/app/", status_code=307)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
