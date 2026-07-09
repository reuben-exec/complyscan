"""
Report Generator
Generates clean, structured PDF compliance reports from analysis results.
"""

import os
import uuid
from typing import Optional

from fpdf import FPDF

from backend.matcher.engine import ComplianceStatus
from backend.core import settings
from backend.models.schemas import RequirementResult


# Colors
PRIMARY = (16, 46, 78)
GREEN = (22, 163, 74)
YELLOW = (217, 119, 6)
RED = (220, 38, 38)
GRAY = (107, 114, 128)
LIGHT_GRAY = (243, 244, 246)
DARK = (17, 24, 39)
MID_GRAY = (156, 163, 175)

STATUS_LABELS = {
    ComplianceStatus.COMPLIANT: "Compliant",
    ComplianceStatus.PARTIAL: "Partial Compliance",
    ComplianceStatus.NON_COMPLIANT: "Non-Compliant",
    ComplianceStatus.NOT_FOUND: "Not Found",
}

STATUS_COLORS = {
    ComplianceStatus.COMPLIANT: GREEN,
    ComplianceStatus.PARTIAL: YELLOW,
    ComplianceStatus.NON_COMPLIANT: RED,
    ComplianceStatus.NOT_FOUND: GRAY,
}

# Advisory disclaimer text (BR-5 / FR-5.1)
DISCLAIMER_TEXT = (
    "Advisory tool only -- not a substitute for an official NABH assessment."
)


def _get_attr(obj, attr, default=""):
    """Extract an attribute from either a dict-like object or a Pydantic model."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _get_font() -> str:
    """Return available font name."""
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "Helvetica"


def _get_bold_font() -> str:
    """Return available bold font name."""
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "Helvetica-Bold"


class ComplianceReport(FPDF):
    def __init__(self, requirement: RequirementResult):
        super().__init__()
        self.requirement = requirement

        # Register Unicode font
        font_regular = _get_font()
        font_bold = _get_bold_font()
        self.add_font("ComplyFont", "", font_regular, uni=True)
        self.add_font("ComplyFont", "B", font_bold, uni=True)

        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()
        self.set_font("ComplyFont", "B", 18)
        self.set_text_color(*PRIMARY)
        self.cell(0, 12, "Compliance Report", ln=True)
        self.set_font("ComplyFont", "", 9)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Healthcare Facility Compliance Analysis", ln=True)
        self.ln(4)
        self._draw_separator()

    def _draw_separator(self):
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(4)

    def _draw_summary_scorecard(self):
        """Draw summary scorecard (FR-4.2) with status distribution and compliance score."""
        r = self.requirement
        self.set_font("ComplyFont", "B", 11)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, "Summary Scorecard", ln=True)
        self.ln(2)

        # Compute status counts from evidence_items
        evidence_items = r.evidence_items or []
        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0
        not_found_count = 0

        for ev in evidence_items:
            status_str = ""
            if isinstance(ev, dict):
                status_str = str(ev.get("status", "")).upper().strip()
            elif hasattr(ev, "status"):
                status_str = str(ev.status).upper().strip()

            if "COMPLIANT" in status_str and "NON" not in status_str and "PARTIAL" not in status_str:
                compliant_count += 1
            elif "PARTIAL" in status_str:
                partial_count += 1
            elif "NON" in status_str:
                non_compliant_count += 1
            else:
                not_found_count += 1

        total = len(evidence_items)

        # Compliance score
        score = r.compliance_score
        score_pct = f"{score * 100:.0f}%" if score is not None else "N/A"

        # Score color (compliance_score is 0-1 float; use config thresholds)
        if score is not None:
            score_pct_val = score * 100
            if score_pct_val >= settings.score_compliant * 100:
                score_color = GREEN
            elif score_pct_val >= settings.score_partial * 100:
                score_color = YELLOW
            else:
                score_color = RED
        else:
            score_color = GRAY

        # Draw scorecard box
        y_start = self.get_y()
        self.set_fill_color(245, 247, 250)
        self.rect(10, y_start, self.w - 20, 28, "F")

        # Score (left)
        self.set_xy(14, y_start + 4)
        self.set_font("ComplyFont", "B", 8)
        self.set_text_color(*GRAY)
        self.cell(30, 5, "Compliance Score", ln=True)
        self.set_x(14)
        self.set_font("ComplyFont", "B", 20)
        self.set_text_color(*score_color)
        self.cell(30, 10, score_pct, ln=True)

        # Status (right)
        self.set_xy(90, y_start + 4)
        self.set_font("ComplyFont", "B", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "Overall Status", ln=True)
        self.set_x(90)
        self.set_font("ComplyFont", "B", 11)
        status_color = STATUS_COLORS.get(r.overall_status, GRAY)
        self.set_text_color(*status_color)
        self.cell(0, 8, STATUS_LABELS.get(r.overall_status, str(r.overall_status)), ln=True)

        # Status breakdown
        self.set_xy(14, y_start + 22)
        self.set_font("ComplyFont", "", 8)
        parts = []
        if compliant_count:
            parts.append(f"{compliant_count} compliant")
        if partial_count:
            parts.append(f"{partial_count} partial")
        if non_compliant_count:
            parts.append(f"{non_compliant_count} non-compliant")
        if not_found_count:
            parts.append(f"{not_found_count} not found")
        breakdown = ", ".join(parts) if parts else "No evidence items"
        self.set_text_color(*DARK)
        self.cell(0, 5, f"Evidence breakdown ({total} items): {breakdown}", ln=True)

        self.set_y(y_start + 30)
        self._draw_separator()

    def _draw_requirement_header(self):
        r = self.requirement
        self.set_font("ComplyFont", "B", 11)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, "Requirement", ln=True)

        self.set_font("ComplyFont", "", 9)
        self.set_text_color(*DARK)
        self.cell(35, 5, "ID:", ln=False)
        self.set_font("ComplyFont", "B", 9)
        self.cell(0, 5, str(r.requirement_id), ln=True)

        self.set_font("ComplyFont", "", 9)
        self.cell(35, 5, "Description:", ln=False)
        self.set_text_color(*DARK)
        self.multi_cell(self.w - 45, 5, str(r.description or "N/A"))

        self.set_font("ComplyFont", "", 9)
        self.set_text_color(*GRAY)
        self.cell(35, 5, "Chapter:", ln=False)
        self.set_text_color(*DARK)
        self.cell(0, 5, str(r.chapter or "N/A"), ln=True)

        self.set_font("ComplyFont", "", 9)
        self.set_text_color(*GRAY)
        self.cell(35, 5, "Sub Chapter:", ln=False)
        self.set_text_color(*DARK)
        sub_chapter = str(r.title or "N/A")
        self.multi_cell(self.w - 45, 5, sub_chapter)

        self._draw_separator()

    def _draw_evidence_cards(self):
        r = self.requirement
        self.set_font("ComplyFont", "B", 11)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, "Evidence Details", ln=True)

        evidence_items = r.evidence_items or []
        if not evidence_items:
            self.set_font("ComplyFont", "", 9)
            self.set_text_color(*GRAY)
            self.cell(0, 6, "No evidence found.", ln=True)
        else:
            for i, ev in enumerate(evidence_items):
                # Check if we need a page break (estimate ~30mm per card)
                if self.get_y() + 35 > self.h - 25:
                    self.add_page()

                y_start = self.get_y()

                # Card background
                self.set_fill_color(249, 250, 251)
                self.rect(10, y_start, self.w - 20, 1, "F")

                self.set_xy(10, y_start + 3)

                # Evidence name
                self.set_font("ComplyFont", "B", 9)
                self.set_text_color(*DARK)
                ev_name = str(_get_attr(ev, "name", "Unnamed"))
                self.cell(0, 5, f"Evidence #{i+1}: {ev_name}", ln=True)

                # Type
                self.set_x(10)
                self.set_font("ComplyFont", "", 8)
                self.set_text_color(*GRAY)
                ev_type = str(_get_attr(ev, "type", "N/A"))
                # criticality comes from EvidenceItem.critical (bool) -> Yes/No
                ev_critical = _get_attr(ev, "critical", False)
                critical_label = "Yes" if ev_critical else "No"
                self.cell(45, 5, f"Type: {ev_type}", ln=False)
                self.cell(0, 5, f"Critical: {critical_label}", ln=True)

                # Status
                self.set_x(10)
                ev_status = str(_get_attr(ev, "status", "N/A"))
                self.set_font("ComplyFont", "B", 8)
                status_color = GRAY
                if "not found" in ev_status.lower() or ev_status == "N/A":
                    status_color = GRAY
                elif "partial" in ev_status.lower():
                    status_color = YELLOW
                elif "non" in ev_status.lower() or "not compliant" in ev_status.lower():
                    status_color = RED
                elif "compliant" in ev_status.lower():
                    status_color = GREEN
                self.set_text_color(*status_color)
                self.cell(0, 5, f"Status: {ev_status}", ln=True)

                # Justification -- full text
                self.set_x(10)
                self.set_font("ComplyFont", "", 8)
                self.set_text_color(*DARK)
                justification = str(_get_attr(ev, "justification", ""))
                if justification:
                    self.set_font("ComplyFont", "B", 8)
                    self.set_text_color(*GRAY)
                    self.cell(0, 5, "Justification:", ln=True)
                    self.set_x(10)
                    self.set_font("ComplyFont", "", 8)
                    self.set_text_color(*DARK)
                    self.multi_cell(self.w - 22, 4.5, justification)
                else:
                    self.set_font("ComplyFont", "", 8)
                    self.set_text_color(*GRAY)
                    self.cell(0, 5, "Justification: N/A", ln=True)

                self.ln(3)

                # Separator between cards
                self.set_draw_color(220, 220, 220)
                self.line(10, self.get_y(), self.w - 10, self.get_y())
                self.ln(3)

    def _draw_overall_assessment(self):
        r = self.requirement
        self.set_font("ComplyFont", "B", 11)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, "Overall Assessment", ln=True)

        self.set_font("ComplyFont", "B", 9)
        self.set_text_color(*GRAY)
        self.cell(35, 5, "Status:", ln=False)
        color = STATUS_COLORS.get(r.overall_status, GRAY)
        self.set_text_color(*color)
        self.cell(0, 5, STATUS_LABELS.get(r.overall_status, str(r.overall_status)), ln=True)

        if r.compliance_score is not None:
            self.set_x(10)
            self.set_font("ComplyFont", "", 9)
            self.set_text_color(*GRAY)
            self.cell(35, 5, "Score:", ln=False)
            self.set_text_color(*DARK)
            self.cell(0, 5, f"{r.compliance_score * 100:.1f}%", ln=True)

        # Compute evidence counts from evidence_items
        evidence_items = r.evidence_items or []
        compliant_count = 0
        partial_count = 0
        non_compliant_count = 0
        for ev in evidence_items:
            status_str = ""
            if isinstance(ev, dict):
                status_str = str(ev.get("status", "")).upper().strip()
            elif hasattr(ev, "status"):
                status_str = str(ev.status).upper().strip()
            if "COMPLIANT" in status_str and "NON" not in status_str and "PARTIAL" not in status_str:
                compliant_count += 1
            elif "PARTIAL" in status_str:
                partial_count += 1
            elif "NON" in status_str:
                non_compliant_count += 1

        if evidence_items:
            self.set_x(10)
            self.set_font("ComplyFont", "", 9)
            self.set_text_color(*GRAY)
            parts = (
                f"{compliant_count} compliant, "
                f"{partial_count} partial, "
                f"{non_compliant_count} non-compliant"
            )
            self.cell(35, 5, "Evidence:", ln=False)
            self.set_text_color(*DARK)
            self.cell(0, 5, parts, ln=True)

        # Collect LLM justifications from evidence items (per-item, not a top-level field)
        llm_notes = []
        for ev in evidence_items:
            note = _get_attr(ev, "llm_justification", "")
            if note:
                llm_notes.append(str(note))
        if llm_notes:
            self.set_x(10)
            self.set_font("ComplyFont", "B", 9)
            self.set_text_color(*GRAY)
            self.cell(0, 5, "LLM Analysis Notes:", ln=True)
            for note in llm_notes:
                self.set_x(10)
                self.set_font("ComplyFont", "", 8)
                self.set_text_color(*DARK)
                self.multi_cell(self.w - 22, 4.5, f"- {note}")
                self.ln(1)

        self._draw_separator()

    def _draw_llm_assessment(self):
        """Draw a dedicated LLM assessment section showing per-evidence LLM analysis,
        excluding chain-of-thought reasoning."""
        r = self.requirement
        evidence_items = r.evidence_items or []

        # Check if any evidence has LLM data
        has_llm_data = False
        for ev in evidence_items:
            llm_evaluated = _get_attr(ev, "llm_evaluated", False)
            llm_conf = _get_attr(ev, "llm_confidence", None)
            llm_just = _get_attr(ev, "llm_justification", "")
            if llm_evaluated or llm_conf is not None or llm_just:
                has_llm_data = True
                break

        if not has_llm_data:
            return

        # Check if we need a page break
        if self.get_y() + 15 > self.h - 25:
            self.add_page()

        self._draw_separator()

        self.set_font("ComplyFont", "B", 11)
        self.set_text_color(*PRIMARY)
        self.cell(0, 7, "LLM Assessment", ln=True)

        for i, ev in enumerate(evidence_items):
            # Check page break
            if self.get_y() + 25 > self.h - 25:
                self.add_page()

            ev_name = str(_get_attr(ev, "name", f"Evidence #{i+1}"))
            llm_conf = _get_attr(ev, "llm_confidence", None)
            llm_just = str(_get_attr(ev, "llm_justification", ""))
            llm_disagreement = _get_attr(ev, "llm_disagreement", False)

            # Evidence name header
            self.set_font("ComplyFont", "B", 9)
            self.set_text_color(*DARK)
            self.cell(0, 5, f"LLM Analysis: {ev_name}", ln=True)

            # Confidence bar
            if llm_conf is not None:
                try:
                    conf_pct = float(llm_conf) * 100
                except (ValueError, TypeError):
                    conf_pct = 0.0
                self.set_x(10)
                self.set_font("ComplyFont", "", 8)
                self.set_text_color(*GRAY)
                self.cell(0, 5, f"Confidence: {conf_pct:.0f}%", ln=True)
                # Draw confidence bar
                self.set_x(10)
                bar_width = 60
                bar_height = 4
                self.set_fill_color(230, 230, 230)
                self.rect(10, self.get_y(), bar_width, bar_height, "F")
                fill_color = GREEN
                if conf_pct < 50:
                    fill_color = RED
                elif conf_pct < 75:
                    fill_color = YELLOW
                self.set_fill_color(*fill_color)
                bar_fill = max(2, int(bar_width * (conf_pct / 100)))
                self.rect(10, self.get_y(), bar_fill, bar_height, "F")
                self.ln(6)

            # LLM Justification
            if llm_just:
                self.set_x(10)
                self.set_font("ComplyFont", "B", 8)
                self.set_text_color(*GRAY)
                self.cell(0, 5, "LLM Justification:", ln=True)
                self.set_x(10)
                self.set_font("ComplyFont", "", 8)
                self.set_text_color(*DARK)
                self.multi_cell(self.w - 22, 4.5, llm_just)

            # Disagreement warning (if LLM disagrees with keyword result)
            if llm_disagreement:
                self.set_x(10)
                self.set_font("ComplyFont", "B", 8)
                self.set_text_color(*RED)
                self.cell(0, 5, "⚠ LLM Disagreement: LLM analysis differs from keyword-based result.", ln=True)

            self.ln(3)

        self._draw_separator()

    def _draw_footer(self):
        self.set_y(-25)
        self.set_font("ComplyFont", "", 7)
        self.set_text_color(*GRAY)
        self.cell(
            0, 4,
            f"Generated by ComplyScan | {self.requirement.requirement_id}",
            ln=True, align="C",
        )
        import datetime
        self.cell(0, 4, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ln=True, align="C")
        # Advisory disclaimer (BR-5 / FR-5.1)
        self.set_font("ComplyFont", "B", 7)
        self.set_text_color(*RED)
        self.cell(0, 4, DISCLAIMER_TEXT, ln=True, align="C")

    def build(self):
        # Draw summary scorecard first (FR-4.2)
        self._draw_summary_scorecard()
        self._draw_requirement_header()
        self._draw_evidence_cards()
        self._draw_llm_assessment()
        # Check if assessment needs new page
        if self.get_y() + 40 > self.h - 25:
            self.add_page()
        self._draw_overall_assessment()
        self._draw_footer()

    def save_report(self, output_dir: str = "output/reports") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.requirement.requirement_id}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(output_dir, filename)
        self.output(filepath)
        return filepath


def generate_report(
    requirement: RequirementResult, output_dir: Optional[str] = None
) -> str:
    if output_dir is None:
        output_dir = "output/reports"
    report = ComplianceReport(requirement)
    report.build()
    filepath = report.save_report(output_dir)
    return filepath


# Backward-compatible alias
save_report = generate_report
