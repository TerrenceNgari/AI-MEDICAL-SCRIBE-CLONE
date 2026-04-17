from __future__ import annotations

from textwrap import indent

from medical_scribe.analyzer import VisitAnalysis
from medical_scribe.support import SupportResult


def _section(title: str, items: list[str]) -> str:
    lines = "\n".join(f"- {item}" for item in items) if items else "- None"
    return f"{title}\n{lines}"


def render_screen(analysis: VisitAnalysis, support: SupportResult) -> str:
    blocks = [
        "=" * 72,
        "AI MEDICAL SCRIBE OUTPUT (with references)",
        "=" * 72,
        f"Chief Complaint: {analysis.chief_complaint}",
        "",
        "SOAP Note",
        indent(analysis.soap_note, "  "),
        "",
        _section("Area 1: Real-World Evidence", support.area1_real_world_evidence),
        "",
        _section("Area 2: Med Issues", support.area2_medical_issues),
        "",
        _section("Area 3: Guidelines", support.area3_guidelines),
        "",
        _section("References", support.references),
        "=" * 72,
    ]
    return "\n".join(blocks)
