from dataclasses import dataclass
from pathlib import Path
import os
from typing import List


def _split_csv(value: str | None, default: List[str]) -> List[str]:
    if not value:
        return default
    items = [v.strip() for v in value.split(",")]
    return [v for v in items if v]


@dataclass(frozen=True)
class Settings:
    cors_origins: List[str]
    cors_allow_credentials: bool
    workspace_dir: Path
    agent_db_path: Path
    execution_ttl_seconds: int
    execution_cleanup_interval: int
    sqlite_busy_timeout_ms: int
    sqlite_journal_mode: str


def load_settings() -> Settings:
    workspace_dir = Path(os.getenv("WORKSPACE_DIR", "workspace"))
    cors_default = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    cors_origins = _split_csv(os.getenv("CORS_ALLOW_ORIGINS"), cors_default)
    allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
    return Settings(
        cors_origins=cors_origins,
        cors_allow_credentials=allow_credentials,
        workspace_dir=workspace_dir,
        agent_db_path=Path(os.getenv("AGENT_DB_PATH", "agent.db")),
        execution_ttl_seconds=int(os.getenv("EXECUTION_TTL_SECONDS", "3600")),
        execution_cleanup_interval=int(os.getenv("EXECUTION_CLEANUP_INTERVAL", "300")),
        sqlite_busy_timeout_ms=int(os.getenv("SQLITE_BUSY_TIMEOUT_MS", "5000")),
        sqlite_journal_mode=os.getenv("SQLITE_JOURNAL_MODE", "WAL"),
    )


settings = load_settings()
