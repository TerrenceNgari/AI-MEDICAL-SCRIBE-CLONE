from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from medical_scribe.analyzer import VisitAnalysis
from medical_scribe.support import SupportResult


def init_records_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                source_mode TEXT NOT NULL,
                transcript TEXT NOT NULL,
                chief_complaint TEXT NOT NULL,
                soap_note TEXT NOT NULL,
                area1_real_world_evidence TEXT NOT NULL,
                area2_medical_issues TEXT NOT NULL,
                area3_guidelines TEXT NOT NULL,
                support_references TEXT NOT NULL,
                report_markdown TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_visit_record(
    *,
    db_path: str,
    patient_id: str,
    source_mode: str,
    analysis: VisitAnalysis,
    support: SupportResult,
    report_markdown: str,
    created_by: str,
) -> int:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO patient_reports (
                patient_id,
                source_mode,
                transcript,
                chief_complaint,
                soap_note,
                area1_real_world_evidence,
                area2_medical_issues,
                area3_guidelines,
                support_references,
                report_markdown,
                created_by,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id.strip() or "UNKNOWN",
                source_mode,
                analysis.transcript,
                analysis.chief_complaint,
                analysis.soap_note,
                json.dumps(support.area1_real_world_evidence),
                json.dumps(support.area2_medical_issues),
                json.dumps(support.area3_guidelines),
                json.dumps(support.references),
                report_markdown,
                created_by,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_visit_records(db_path: str, created_by: str) -> list[dict[str, str]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, patient_id, chief_complaint, source_mode, created_at
            FROM patient_reports
            WHERE created_by = ?
            ORDER BY id DESC
            """,
            (created_by,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_visit_record(db_path: str, record_id: int, created_by: str) -> dict | None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT *
            FROM patient_reports
            WHERE id = ? AND created_by = ?
            """,
            (record_id, created_by),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    result = dict(row)
    result["area1_real_world_evidence"] = json.loads(result["area1_real_world_evidence"])
    result["area2_medical_issues"] = json.loads(result["area2_medical_issues"])
    result["area3_guidelines"] = json.loads(result["area3_guidelines"])
    result["references"] = json.loads(result["support_references"])
    return result
