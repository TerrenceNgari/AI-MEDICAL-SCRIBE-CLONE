from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SupportResult:
    area1_real_world_evidence: list[str]
    area2_medical_issues: list[str]
    area3_guidelines: list[str]
    references: list[str]


class SupportEngine:
    def __init__(self, knowledge_map: dict[str, dict]):
        self.knowledge_map = knowledge_map

    @classmethod
    def from_file(cls, path: str) -> "SupportEngine":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(payload)

    def _lookup_entry(self, complaint: str, transcript: str) -> dict:
        normalized_complaint = complaint.lower().strip()
        transcript_lower = transcript.lower()

        if normalized_complaint in self.knowledge_map:
            return self.knowledge_map[normalized_complaint]

        for key, value in self.knowledge_map.items():
            if key in transcript_lower:
                return value

        return self.knowledge_map.get("default", {
            "real_world_evidence": ["No specific evidence match found"],
            "medical_issues": ["Use clinician judgement and broaden differential"],
            "guidelines": ["Consult local protocol"],
            "references": [],
        })

    def generate(self, complaint: str, transcript: str) -> SupportResult:
        entry = self._lookup_entry(complaint, transcript)

        med_issues = list(entry.get("medical_issues", []))
        text = transcript.lower()
        if "penicillin" in text and "allergy" in text:
            med_issues.append("Possible medication allergy concern: verify allergy list")
        if "pregnan" in text:
            med_issues.append("Pregnancy context detected: verify safe treatment options")

        return SupportResult(
            area1_real_world_evidence=list(entry.get("real_world_evidence", [])),
            area2_medical_issues=med_issues,
            area3_guidelines=list(entry.get("guidelines", [])),
            references=list(entry.get("references", [])),
        )
