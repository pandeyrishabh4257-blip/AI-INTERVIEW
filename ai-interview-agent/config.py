"""Application configuration values."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ai_interview_agent")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Feature flags for local fallback behavior when dependencies/services are unavailable.
USE_FAKE_DB = os.getenv("USE_FAKE_DB", "true").lower() == "true"
USE_FAKE_TTS = os.getenv("USE_FAKE_TTS", "true").lower() == "true"
