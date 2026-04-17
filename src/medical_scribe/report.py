from __future__ import annotations

from datetime import datetime
from pathlib import Path

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
