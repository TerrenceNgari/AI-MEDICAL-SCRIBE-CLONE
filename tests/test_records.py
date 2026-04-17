from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from medical_scribe.analyzer import VisitAnalysis
from medical_scribe.records import get_visit_record, init_records_db, list_visit_records, save_visit_record
from medical_scribe.support import SupportResult


def test_save_and_fetch_visit_record(tmp_path: Path):
    db_path = tmp_path / "clinical_records.db"
    init_records_db(str(db_path))

    analysis = VisitAnalysis(
        transcript="Patient reports cough for 3 days.",
        chief_complaint="cough",
        soap_note="S: cough\nO: none\nA: viral syndrome\nP: rest",
    )
    support = SupportResult(
        area1_real_world_evidence=["evidence-1"],
        area2_medical_issues=["issue-1"],
        area3_guidelines=["guideline-1"],
        references=["ref-1"],
    )

    record_id = save_visit_record(
        db_path=str(db_path),
        patient_id="P-001",
        source_mode="Typed Text",
        analysis=analysis,
        support=support,
        report_markdown="# Report",
        created_by="doctor@example.com",
    )

    assert record_id > 0

    records = list_visit_records(str(db_path), created_by="doctor@example.com")
    assert len(records) == 1
    assert records[0]["patient_id"] == "P-001"

    record = get_visit_record(str(db_path), record_id=record_id, created_by="doctor@example.com")
    assert record is not None
    assert record["chief_complaint"] == "cough"
    assert record["area1_real_world_evidence"] == ["evidence-1"]
    assert record["report_markdown"] == "# Report"


def test_records_are_scoped_by_user(tmp_path: Path):
    db_path = tmp_path / "clinical_records.db"
    init_records_db(str(db_path))

    analysis = VisitAnalysis(transcript="abc", chief_complaint="fever", soap_note="soap")
    support = SupportResult([], [], [], [])

    record_id = save_visit_record(
        db_path=str(db_path),
        patient_id="P-XYZ",
        source_mode="Typed Text",
        analysis=analysis,
        support=support,
        report_markdown="md",
        created_by="owner@example.com",
    )

    assert list_visit_records(str(db_path), created_by="other@example.com") == []
    assert get_visit_record(str(db_path), record_id=record_id, created_by="other@example.com") is None
