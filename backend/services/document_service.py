"""Business logic services."""
import uuid
from pathlib import Path
from backend.ocr import PDFTextExtractor, get_ocr_client
from backend.matcher import requirement_matcher
from backend.report import save_report
from backend.models.schemas import RequirementResult, UploadResponse
from typing import Optional


class DocumentService:
    """Handle document processing workflow."""
    
    def __init__(self):
        self._documents: dict[str, bytes] = {}  # In-memory storage for MVP
    
    async def upload_document(self, file_bytes: bytes, filename: str) -> UploadResponse:
        """Upload and store a document.
        
        Args:
            file_bytes: Raw PDF bytes
            filename: Original filename
            
        Returns:
            UploadResponse with document ID
        """
        document_id = uuid.uuid4().hex
        self._documents[document_id] = file_bytes
        
        # Quick page estimate (rough)
        pages = file_bytes.count(b"%PDF") if b"%PDF" in file_bytes else 1
        
        return UploadResponse(
            document_id=document_id,
            filename=filename,
            pages=pages,
            text_preview="(pending OCR)"
        )
    
    async def process_document(
        self, 
        document_id: str,
        requirement_id: str
    ) -> RequirementResult:
        """Process uploaded document against a requirement.
        
        Args:
            document_id: ID from upload
            requirement_id: Requirement to check (HIC-R01, PRE-R01)
            
        Returns:
            RequirementResult with analysis
        """
        if document_id not in self._documents:
            raise ValueError(f"Document {document_id} not found")
        
        # Get OCR client
        ocr_client = await get_ocr_client()
        
        try:
            # Extract text from PDF
            text = await ocr_client.extract_text(self._documents[document_id])
            
            # Match against requirement
            result = requirement_matcher.analyze_document(text, requirement_id)
            
            return result
            
        finally:
            await ocr_client.close()
    
    def get_report(self, result: RequirementResult) -> str:
        """Generate and save report.
        
        Args:
            result: Analysis result
            
        Returns:
            Path to saved PDF
        """
        return save_report(result)


# Singleton
document_service = DocumentService()
