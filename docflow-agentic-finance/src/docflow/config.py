from __future__ import annotations
from dataclasses import dataclass
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = [
    "LLM_MODEL",
    # Add other absolutely critical vars here if needed,
    # but strictly speaking runner might run without Odoo if just testing extraction.
]


@dataclass(frozen=True)
class DocflowConfig:
    inbox_dir: Path
    archive_dir: Path
    artifacts_dir: Path
    log_level: str
    llm_provider: str
    llm_model: str
    openai_api_key: str | None
    anthropic_api_key: str | None
    odoo_url: str | None
    odoo_db: str | None
    odoo_username: str | None
    odoo_password: str | None
    ingest_token: str | None
    push_needs_review: bool
    dupe_threshold: float


def load_config() -> DocflowConfig:
    missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            "Missing required env vars: "
            + ", ".join(missing)
            + " (copy .env.example to .env and fill values)"
        )

    return DocflowConfig(
        inbox_dir=Path(os.getenv("DOCFLOW_INBOX_DIR", "./inbox")),
        archive_dir=Path(os.getenv("DOCFLOW_ARCHIVE_DIR", "./archive")),
        artifacts_dir=Path(os.getenv("DOCFLOW_ARTIFACTS_DIR", "./artifacts")),
        log_level=os.getenv("DOCFLOW_LOG_LEVEL", "INFO"),
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_model=os.environ["LLM_MODEL"],
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        odoo_url=os.getenv("ODOO_URL"),
        odoo_db=os.getenv("ODOO_DB"),
        odoo_username=os.getenv("ODOO_USERNAME"),
        odoo_password=os.getenv("ODOO_PASSWORD"),
        ingest_token=os.getenv("ODOO_DOCFLOW_INGEST_TOKEN"),
        push_needs_review=os.getenv("ODOO_DOCFLOW_PUSH_NEEDS_REVIEW", "false").lower() == "true",
        dupe_threshold=float(os.getenv("DUPE_BLOCK_THRESHOLD", "0.8")),
    )
