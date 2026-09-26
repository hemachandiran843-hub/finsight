"""FinSight X backend configuration.

AI / LLM configuration is read from `.env` (or process env):
    LLM_API_KEY   - API key for an OpenAI-compatible endpoint
    LLM_BASE_URL  - e.g. https://api.openai.com/v1
    LLM_MODEL     - e.g. gpt-4o-mini

If LLM_API_KEY is empty the platform runs in DEMO MODE with the curated
XYZ Manufacturing Ltd. dataset, so the prototype always works.
"""
import os
import secrets
from pathlib import Path

try:
    from dotenv import load_dotenv
    _BASE = Path(__file__).resolve().parent
    load_dotenv(_BASE / ".env")
except Exception:  # pragma: no cover
    pass

LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

AI_ENABLED = bool(LLM_API_KEY)

# CORS: comma-separated list of allowed browser origins for the deployed
# frontend, e.g. "https://finsight.vercel.app,https://finsight-git-main.vercel.app".
# Default "*" keeps local development and previews working with zero config.
_CORS = os.getenv("CORS_ORIGINS", "*").strip()
ALLOWED_ORIGINS = ["*"] if _CORS in ("", "*") else [o.strip() for o in _CORS.split(",") if o.strip()]

DB_PATH = os.getenv("FS_DB_PATH", str(Path(__file__).resolve().parent.parent / "db" / "finsight.db"))
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_reports"
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"

MAX_UPLOAD_MB = 20
MAX_PAGES = 200

# Token secret: persisted so tokens survive backend restarts.
_SECRET_FILE = Path(__file__).resolve().parent / "secret.key"


def token_secret() -> bytes:
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_bytes()
    s = secrets.token_hex(32).encode()
    _SECRET_FILE.write_bytes(s)
    return s


TOKEN_TTL_SECONDS = 12 * 3600
