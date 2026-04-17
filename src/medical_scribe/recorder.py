from __future__ import annotations

from pathlib import Path


def record_audio(output_path: str, seconds: int = 10, samplerate: int = 16000) -> str:
    """Record mono audio from default microphone into a WAV file."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "Recording dependencies missing. Install requirements.txt first."
        ) from exc

    if seconds <= 0:
        raise ValueError("seconds must be greater than 0")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    frames = int(seconds * samplerate)
    recording = sd.rec(frames, samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    sf.write(str(out), recording, samplerate)
    return str(out)
