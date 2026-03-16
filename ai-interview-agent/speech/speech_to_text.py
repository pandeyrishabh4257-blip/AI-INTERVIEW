"""Speech-to-text wrapper using Whisper model with safe fallback."""
from __future__ import annotations

from pathlib import Path


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio with Whisper if available, otherwise provide fallback text."""
    path = Path(audio_path)
    if not path.exists():
        return "Audio file not found."

    try:
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(path))
        return result.get("text", "").strip()
    except Exception:
        return "Transcription unavailable in this environment. Please type your answer manually."
