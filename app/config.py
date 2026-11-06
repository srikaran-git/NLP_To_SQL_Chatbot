import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_database_url() -> str:
    """Return the configured database URL or this project's SQLite database."""
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if configured_url:
        return configured_url

    database_path = (PROJECT_ROOT / "store.db").as_posix()
    return f"sqlite:///{database_path}"
