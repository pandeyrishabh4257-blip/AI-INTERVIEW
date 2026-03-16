"""Text-to-speech wrapper using Coqui/ElevenLabs with browser fallback."""
from __future__ import annotations

from pathlib import Path

from config import ELEVENLABS_API_KEY, USE_FAKE_TTS


def synthesize_text(text: str, output_file: str) -> str:
    """Generate interviewer voice audio; returns path to generated audio if available."""
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)

    if USE_FAKE_TTS:
        # Frontend can rely on Web Speech API when this is enabled.
        return ""

    if ELEVENLABS_API_KEY:
        try:
            import requests

            voice_id = "21m00Tcm4TlvDq8ikWAM"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "accept": "audio/mpeg",
                "Content-Type": "application/json",
            }
            payload = {"text": text, "model_id": "eleven_multilingual_v2"}
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            out.write_bytes(response.content)
            return str(out)
        except Exception:
            return ""

    return ""
