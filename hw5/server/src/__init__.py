"""Server package initialisation: load environment variables early."""

from pathlib import Path

from dotenv import load_dotenv

# Load .env files (if present) before any modules request configuration.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)
load_dotenv(_PROJECT_ROOT.parent / ".env", override=False)

__all__ = []
