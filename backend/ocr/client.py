"""PDF text extraction with PyMuPDF (digital PDFs) + Tesseract (scanned fallback)."""
import os
from typing import Optional

import pytesseract
from PIL import Image


# ── Tesseract path configuration ──────────────────────────────────────────
_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
]
for _p in _TESSERACT_PATHS:
    if os.path.isfile(_p):
        pytesseract.pytesseract.tesseract_cmd = _p
        break


class PDFTextExtractor:
    """Extract text from PDFs.

    Two-pass approach:
      1. PyMuPDF (fast, local) — works for all digital/text-based PDFs.
      2. Tesseract OCR fallback — renders each page to an image and OCRs
         it, used when PyMuPDF yields little or no text (scanned docs).
    """

    MIN_TEXT_LENGTH = 20     # minimum chars to consider PyMuPDF successful

    # ── Public API ────────────────────────────────────────────────────────

    async def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text from a PDF, falling back to OCR when needed."""
        text = self._extract_pymupdf(pdf_bytes)

        if len(text.strip()) < self.MIN_TEXT_LENGTH:
            ocr_text = self._extract_ocr(pdf_bytes)
            if ocr_text.strip():
                text = ocr_text

        return text.strip()

    async def close(self):
        """No-op.  Kept for compatibility with dependency injection."""
        pass

    # ── PyMuPDF extraction ────────────────────────────────────────────────

    @staticmethod
    def _extract_pymupdf(pdf_bytes: bytes) -> str:
        """Extract embedded text via PyMuPDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("PyMuPDF not available. Install with: pip install pymupdf")
            return ""

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            texts = []
            for page in doc:
                page_text = page.get_text().strip()
                if page_text:
                    texts.append(page_text)
            doc.close()
            return "\n\n".join(texts).strip()
        except Exception as e:
            print(f"PyMuPDF extraction error: {e}")
            return ""

    # ── Tesseract OCR fallback ────────────────────────────────────────────

    @staticmethod
    def _extract_ocr(pdf_bytes: bytes) -> str:
        """Render PDF pages to images and run Tesseract OCR."""
        try:
            import fitz  # PyMuPDF used here just for rendering
        except ImportError:
            print("PyMuPDF required for OCR rendering. pip install pymupdf")
            return ""

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_texts = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Render page at 300 DPI to a pixmap
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                ocr_result = pytesseract.image_to_string(img, lang="eng")
                if ocr_result.strip():
                    page_texts.append(ocr_result.strip())

            doc.close()
            return "\n\n".join(page_texts).strip()
        except pytesseract.TesseractNotFoundError:
            print("Tesseract executable not found. Install Tesseract OCR.")
            return ""
        except Exception as e:
            print(f"Tesseract OCR error: {e}")
            return ""


async def get_ocr_client() -> PDFTextExtractor:
    """Get OCR client for dependency injection."""
    return PDFTextExtractor()
