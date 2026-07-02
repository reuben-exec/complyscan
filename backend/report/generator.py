"""PDF report generation."""
import os
import shutil
import uuid
from pathlib import Path

from fpdf import FPDF

from ..core import settings
from ..models.schemas import ComplianceStatus, RequirementResult


class ComplianceReport:
    """Generate compliance report PDFs."""
    
    STATUS_COLORS = {
        ComplianceStatus.COMPLIANT: (76, 175, 80),    # Green
        ComplianceStatus.PARTIAL: (255, 193, 7),       # Amber
        ComplianceStatus.NON_COMPLIANT: (244, 67, 54), # Red
        ComplianceStatus.NOT_FOUND: (158, 158, 158)    # Gray
    }
    
    def __init__(self, requirement_result: RequirementResult):
        self.result = requirement_result
        self.pdf = FPDF()
        # Add Unicode-supporting font (cross-platform)
        try:
            font_map = {
                "regular": self._resolve_font_path(["Arial.ttf", "arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]),
                "bold": self._resolve_font_path(["Arial Bold.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]),
                "italic": self._resolve_font_path(["Arial Italic.ttf", "ariali.ttf", "DejaVuSans-Oblique.ttf", "LiberationSans-Italic.ttf"]),
            }
            if font_map["regular"]:
                self.pdf.add_font("Arial", "", font_map["regular"], uni=True)
            if font_map["bold"]:
                self.pdf.add_font("Arial", "B", font_map["bold"], uni=True)
            if font_map["italic"]:
                self.pdf.add_font("Arial", "I", font_map["italic"], uni=True)
        except Exception:
            # Fallback to built-in font
            pass  # Use default Helvetica
    
    def generate(self) -> bytes:
        """Generate PDF report."""
        self.pdf.add_page()
        self._add_header()
        self._add_requirement_info()
        self._add_evidence_table()
        self._add_footer()
        
        return self.pdf.output()
    
    def _add_header(self):
        """Add report header."""
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(0, 10, "ComplyScan - NABH Compliance Report", ln=True)
        self.pdf.ln(3)
        self.pdf.set_font("Arial", "I", 9)
        self.pdf.set_text_color(100, 100, 100)
        self.pdf.cell(0, 8, "* Advisory Output - Not Official NABH Determination *", ln=True)
        self.pdf.ln(8)
    
    def _add_requirement_info(self):
        """Add requirement information."""
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font("Arial", "B", 11)
        self.pdf.cell(0, 8, f"Requirement: {self.result.requirement_id}", ln=True)
        
        self.pdf.set_font("Arial", "", 10)
        self.pdf.cell(0, 6, f"Chapter: {self.result.chapter}", ln=True)
        self.pdf.cell(0, 6, f"Title: {self.result.title}", ln=True)
        self.pdf.ln(4)
        
        # Description
        self.pdf.set_font("Arial", "I", 9)
        self.pdf.multi_cell(0, 5, f"Description: {self.result.description}")
        self.pdf.ln(4)
        
        # Overall status box
        status_text = f"Overall Status: {self.result.overall_status.value}"
        self.pdf.set_font("Arial", "B", 11)
        self.pdf.set_fill_color(*self.STATUS_COLORS[self.result.overall_status])
        self.pdf.cell(0, 10, status_text, ln=True, fill=True)
        self.pdf.ln(6)
    
    def _add_evidence_table(self):
        """Add evidence items table."""
        self.pdf.set_font("Arial", "B", 10)
        self.pdf.cell(0, 8, "Evidence Items Analysis", ln=True)
        self.pdf.ln(2)
        
        # Table header
        self.pdf.set_font("Arial", "B", 8)
        self.pdf.set_fill_color(240, 240, 240)
        col_widths = [50, 30, 25, 20, 70]
        
        self.pdf.cell(col_widths[0], 7, "Evidence Name", border=1, fill=True)
        self.pdf.cell(col_widths[1], 7, "Type", border=1, fill=True)
        self.pdf.cell(col_widths[2], 7, "Critical", border=1, fill=True)
        self.pdf.cell(col_widths[3], 7, "Status", border=1, fill=True)
        self.pdf.cell(col_widths[4], 7, "Justification", border=1, fill=True)
        self.pdf.ln(7)
        
        # Table rows
        self.pdf.set_font("Arial", "", 7)
        for item in self.result.evidence_items:
            self.pdf.set_fill_color(*self.STATUS_COLORS[item.status])
            self.pdf.cell(col_widths[0], 7, self._truncate(item.name, 20), border=1, fill=True)
            self.pdf.cell(col_widths[1], 7, item.type[:15], border=1, fill=True)
            self.pdf.cell(col_widths[2], 7, "Yes" if item.critical else "No", border=1, fill=True)
            self.pdf.cell(col_widths[3], 7, item.status.value[:15], border=1, fill=True)
            self.pdf.cell(col_widths[4], 7, self._truncate(item.justification, 30), border=1, fill=True)
            self.pdf.ln(7)
        
        self.pdf.ln(4)
        
        # Score
        self.pdf.set_font("Arial", "B", 10)
        self.pdf.cell(0, 8, f"Compliance Score: {self.result.compliance_score:.0%}", ln=True)
    
    def _add_footer(self):
        """Add report footer."""
        self.pdf.set_y(-30)
        self.pdf.set_font("Arial", "I", 7)
        self.pdf.set_text_color(100, 100, 100)
        self.pdf.cell(0, 10, f"Generated by ComplyScan MVP - {self.result.requirement_id}", align="C")
    
    def _resolve_font_path(self, candidates: list[str]) -> str | None:
        """Resolve a font file from common system locations and PATH."""
        paths = []
        if os.name == "nt":
            paths.extend([
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\Arial.ttf",
                r"C:\Windows\Fonts\ARIAL.TTF",
                r"C:\Windows\Fonts\DejaVuSans.ttf",
                r"C:\Windows\Fonts\dejavusans.ttf",
            ])
        else:
            paths.extend([
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
            ])

        for path in paths + candidates:
            if not path:
                continue
            if Path(path).exists():
                return str(path)
            resolved = shutil.which(path)
            if resolved:
                return resolved
        return None

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text for table display."""
        return text[:max_len] + "..." if len(text) > max_len else text


def save_report(result: RequirementResult, output_dir: str = None) -> str:
    """Generate and save report to file.
    
    Args:
        result: Requirement result
        output_dir: Output directory (defaults to settings)
        
    Returns:
        Path to saved PDF file
    """
    output_dir = Path(output_dir or settings.reports_output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = ComplianceReport(result)
    pdf_bytes = report.generate()
    
    filename = f"{result.requirement_id}_report_{uuid.uuid4().hex[:8]}.pdf"
    filepath = output_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    
    return str(filepath)