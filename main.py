from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from medical_scribe.analyzer import analyze_visit
from medical_scribe.display import render_screen
from medical_scribe.emailer import send_email_report
from medical_scribe.recorder import record_audio
from medical_scribe.report import build_report_markdown, save_report
from medical_scribe.support import SupportEngine
from medical_scribe.transcriber import transcribe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Medical Scribe Clone")
    parser.add_argument("--text", type=str, help="Direct text input instead of speech")
    parser.add_argument("--audio-file", type=str, help="Path to audio file (wav/aiff/flac)")
    parser.add_argument(
        "--record-seconds",
        type=int,
        help="Record from microphone for N seconds",
    )
    parser.add_argument("--patient-id", default="UNKNOWN", help="Patient identifier")
    parser.add_argument("--send-email", type=str, help="Recipient email")
    parser.add_argument(
        "--knowledge-base",
        default=str(ROOT / "data" / "knowledge_base.json"),
        help="Path to JSON knowledge base",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    audio_file = args.audio_file
    if args.record_seconds:
        audio_file = str(ROOT / "outputs" / "recorded_input.wav")
        print(f"Recording for {args.record_seconds} seconds...")
        record_audio(audio_file, seconds=args.record_seconds)

    transcript = transcribe(audio_file=audio_file, direct_text=args.text)
    analysis = analyze_visit(transcript)
    support_engine = SupportEngine.from_file(args.knowledge_base)
    support = support_engine.generate(analysis.chief_complaint, transcript)

    screen_output = render_screen(analysis, support)
    print(screen_output)

    report_content = build_report_markdown(args.patient_id, analysis, support)
    report_path = save_report(report_content)
    print(f"Report saved: {report_path}")

    if args.send_email:
        send_email_report(
            recipient=args.send_email,
            subject=f"Medical Scribe Report - {args.patient_id}",
            body=report_content,
        )
        print(f"Email sent to: {args.send_email}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
