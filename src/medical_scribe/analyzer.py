from __future__ import annotations

import re
from dataclasses import dataclass


COMMON_SYMPTOMS = {
    "fever",
    "headache",
    "cough",
    "shortness of breath",
    "chest pain",
    "fatigue",
    "nausea",
    "vomiting",
    "diarrhea",
    "dizziness",
    "wheeze",
    "sore throat",
    "abdominal pain",
}


@dataclass
class VisitAnalysis:
    transcript: str
    chief_complaint: str
    soap_note: str


def extract_chief_complaint(transcript: str) -> str:
    text = " ".join(transcript.split()).strip().lower()
    if not text:
        return "unspecified concern"

    def is_negated(symptom: str) -> bool:
        escaped = re.escape(symptom)
        # Basic negation detector for phrases such as "no chest pain" or "denies cough".
        return bool(
            re.search(rf"\b(no|denies|without)\s+{escaped}\b", text)
        )

    for symptom in sorted(COMMON_SYMPTOMS, key=len, reverse=True):
        if symptom in text and not is_negated(symptom):
            return symptom

    # Fall back to the first sentence fragment when no known symptom is matched.
    sentence = re.split(r"[.!?]", text)[0].strip()
    return sentence[:90] if sentence else "unspecified concern"


def _extract_objective(transcript: str) -> str:
    bp_match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", transcript)
    temp_match = re.search(r"(\d{2,3}(?:\.\d)?)\s*(?:f|c|degrees)", transcript, re.I)

    findings: list[str] = []
    if bp_match:
        findings.append(f"Blood pressure noted at {bp_match.group(1)}/{bp_match.group(2)}")
    if temp_match:
        findings.append(f"Temperature reported: {temp_match.group(1)}")

    if not findings:
        findings.append("No structured vital signs detected in transcript")

    return "; ".join(findings)


def _assessment(transcript: str, complaint: str) -> str:
    text = transcript.lower()
    if "viral" in text or "flu" in text:
        return f"Likely infectious process related to {complaint}"
    if "chronic" in text:
        return f"Possible chronic condition flare presenting with {complaint}"
    return f"Undifferentiated presentation with primary complaint of {complaint}"


def _plan(transcript: str, complaint: str) -> str:
    text = transcript.lower()
    steps = [
        "Reassess after focused history and physical exam",
        "Document red flags and escalation thresholds",
    ]

    if complaint in {"chest pain", "shortness of breath"}:
        steps.insert(0, "Consider urgent evaluation and ECG/oxygen assessment")

    if "fever" in text:
        steps.append("Hydration and antipyretic counseling if appropriate")

    return "; ".join(steps)


def build_soap_note(transcript: str, complaint: str) -> str:
    subjective = transcript.strip()
    objective = _extract_objective(transcript)
    assessment = _assessment(transcript, complaint)
    plan = _plan(transcript, complaint)

    return (
        "S: " + subjective + "\n"
        + "O: " + objective + "\n"
        + "A: " + assessment + "\n"
        + "P: " + plan
    )


def analyze_visit(transcript: str) -> VisitAnalysis:
    complaint = extract_chief_complaint(transcript)
    soap = build_soap_note(transcript, complaint)
    return VisitAnalysis(transcript=transcript, chief_complaint=complaint, soap_note=soap)
