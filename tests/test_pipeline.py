from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_scribe.analyzer import analyze_visit
from medical_scribe.report import build_report_pdf
from medical_scribe.support import SupportEngine


def test_analyze_visit_extracts_complaint_and_soap():
    transcript = "Patient has headache with fever for 2 days, BP 140/90."
    analysis = analyze_visit(transcript)

    assert analysis.chief_complaint in {"headache", "fever"}
    assert "S:" in analysis.soap_note
    assert "O:" in analysis.soap_note
    assert "A:" in analysis.soap_note
    assert "P:" in analysis.soap_note


def test_support_engine_matches_knowledge_base(tmp_path: Path):
    kb = {
        "headache": {
            "real_world_evidence": ["rwe1"],
            "medical_issues": ["issue1"],
            "guidelines": ["guide1"],
            "references": ["ref1"],
        },
        "default": {
            "real_world_evidence": ["default rwe"],
            "medical_issues": ["default issue"],
            "guidelines": ["default guide"],
            "references": ["default ref"],
        },
    }
    kb_path = tmp_path / "kb.json"
    kb_path.write_text(json.dumps(kb), encoding="utf-8")

    engine = SupportEngine.from_file(str(kb_path))
    result = engine.generate("headache", "Patient reports headache")

    assert result.area1_real_world_evidence == ["rwe1"]
    assert result.area2_medical_issues[0] == "issue1"
    assert result.area3_guidelines == ["guide1"]
    assert result.references == ["ref1"]


def test_negated_symptom_not_selected_as_chief_complaint():
    transcript = "Patient has headache and fever, no chest pain, BP 145/95."
    analysis = analyze_visit(transcript)

    assert analysis.chief_complaint != "chest pain"
    assert analysis.chief_complaint in {"headache", "fever"}


def test_build_report_pdf_returns_pdf_bytes():
    sample_markdown = "# Medical Scribe Report\n\n## Transcript\nPatient reports cough.\n"
    pdf_bytes = build_report_pdf(sample_markdown)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
