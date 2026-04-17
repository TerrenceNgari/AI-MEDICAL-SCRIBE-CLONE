from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import medical_scribe.transcriber as transcriber


def test_transcribe_uses_direct_text():
    result = transcriber.transcribe(direct_text="  hello world  ")
    assert result == "hello world"


def test_transcribe_uses_txt_file(tmp_path: Path):
    p = tmp_path / "note.txt"
    p.write_text("line one", encoding="utf-8")

    result = transcriber.transcribe(audio_file=str(p))
    assert result == "line one"


def test_convert_to_pcm_wav_fails_on_invalid_audio(tmp_path: Path):
    p = tmp_path / "bad.wav"
    p.write_bytes(b"not real audio")

    try:
        transcriber._convert_to_pcm_wav(p)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "could not be decoded" in str(exc).lower()
