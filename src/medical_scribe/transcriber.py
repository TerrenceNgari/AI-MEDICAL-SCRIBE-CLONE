from __future__ import annotations

from pathlib import Path


def transcribe(audio_file: str | None = None, direct_text: str | None = None) -> str:
    """Return transcript from direct text or audio input.

    Priority:
    1) direct_text argument
    2) .txt file provided as audio_file (useful for demos/tests)
    3) speech recognition from a WAV/AIFF/FLAC audio file
    """
    if direct_text and direct_text.strip():
        return direct_text.strip()

    if not audio_file:
        raise ValueError("Either direct_text or audio_file must be provided")

    source_path = Path(audio_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Input file not found: {audio_file}")

    if source_path.suffix.lower() == ".txt":
        content = source_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError("Text file is empty")
        return content

    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError(
            "SpeechRecognition not installed. Install requirements.txt first."
        ) from exc

    recognizer = sr.Recognizer()
    with sr.AudioFile(str(source_path)) as src:
        audio_data = recognizer.record(src)

    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError as exc:
        raise RuntimeError("Could not understand audio") from exc
    except sr.RequestError as exc:
        raise RuntimeError(f"Speech recognition service error: {exc}") from exc
