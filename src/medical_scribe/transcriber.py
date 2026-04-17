from __future__ import annotations

import tempfile
from pathlib import Path


def _convert_to_pcm_wav(source_path: Path) -> Path:
    """Convert audio to PCM WAV for SpeechRecognition compatibility."""
    try:
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "soundfile is required for audio normalization. Install requirements.txt first."
        ) from exc

    try:
        audio_data, sample_rate = sf.read(str(source_path), always_2d=False)
    except Exception as exc:  # pragma: no cover - depends on local audio backend/codecs
        raise RuntimeError(
            "Audio file could not be decoded. Please upload PCM WAV, AIFF, FLAC, or a readable text transcript."
        ) from exc

    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()
    temp_path = Path(temp_file.name)

    sf.write(str(temp_path), audio_data, sample_rate, format="WAV", subtype="PCM_16")
    return temp_path


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

    converted_path: Path | None = None
    normalized_source = source_path
    try:
        converted_path = _convert_to_pcm_wav(source_path)
        normalized_source = converted_path
    except RuntimeError:
        # If conversion fails, allow SpeechRecognition to attempt direct read.
        normalized_source = source_path

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(str(normalized_source)) as src:
            audio_data = recognizer.record(src)
    finally:
        if converted_path and converted_path.exists():
            converted_path.unlink(missing_ok=True)

    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError as exc:
        raise RuntimeError("Could not understand audio") from exc
    except sr.RequestError as exc:
        raise RuntimeError(f"Speech recognition service error: {exc}") from exc
