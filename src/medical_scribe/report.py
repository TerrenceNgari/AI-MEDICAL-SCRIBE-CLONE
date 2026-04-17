from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from medical_scribe.analyzer import VisitAnalysis
from medical_scribe.support import SupportResult


def build_report_markdown(patient_id: str, analysis: VisitAnalysis, support: SupportResult) -> str:
    def bullet(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- None"

    return f"""# Medical Scribe Report

Generated: {datetime.utcnow().isoformat()}Z
Patient ID: {patient_id}

## Transcript

{analysis.transcript}

## Chief Complaint

{analysis.chief_complaint}

## SOAP Note

{analysis.soap_note}

## Area 1: Real-World Evidence

{bullet(support.area1_real_world_evidence)}

## Area 2: Med Issues

{bullet(support.area2_medical_issues)}

## Area 3: Guidelines

{bullet(support.area3_guidelines)}

## References

{bullet(support.references)}
"""


def save_report(content: str, output_dir: str = "outputs", filename_prefix: str = "visit") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"{filename_prefix}_{stamp}.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


def build_report_pdf(markdown_content: str) -> bytes:
    """Render report markdown into a simple, readable PDF document."""

    def _safe_text(value: str) -> str:
        # Core PDF fonts support latin-1; replace unsupported code points.
        return value.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    for raw_line in markdown_content.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            pdf.ln(4)
            continue

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(content_width, 10, _safe_text(line[2:].strip()))
            pdf.ln(1)
            continue

        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(content_width, 8, _safe_text(line[3:].strip()))
            pdf.ln(1)
            continue

        if line.startswith("- "):
            pdf.set_font("Helvetica", "", 11)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(content_width, 6, _safe_text(f"- {line[2:].strip()}"))
            continue

        pdf.set_font("Helvetica", "", 11)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(content_width, 6, _safe_text(line))

    return bytes(pdf.output())


def save_pdf_report(pdf_content: bytes, output_dir: str = "outputs", filename_prefix: str = "visit") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"{filename_prefix}_{stamp}.pdf"
    path.write_bytes(pdf_content)
    return str(path)
