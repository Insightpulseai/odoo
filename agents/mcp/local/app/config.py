"""
Configuration for local MCP server
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Local MCP Server Settings"""

    # Storage
    sqlite_data_dir: Path = Path("/data")
    skills_db_path: Path = sqlite_data_dir / "mcp_skills.db"
    rag_db_path: Path = sqlite_data_dir / "mcp_rag.db"
    memory_db_path: Path = sqlite_data_dir / "mcp_memory.db"

    # Odoo connection (lab instance)
    odoo_lab_url: str = os.getenv("ODOO_LAB_URL", "http://odoo:8069")
    odoo_lab_db: str = os.getenv("ODOO_LAB_DB", "odoo")
    odoo_lab_username: str = os.getenv("ODOO_LAB_USERNAME", "admin")
    odoo_lab_password: str = os.getenv("ODOO_LAB_PASSWORD", "")

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Git repository for commit indexing
    repo_path: Path = Path("/mnt/addons")

    # API
    api_key: str = os.getenv("MCP_LOCAL_API_KEY", "dev-only-insecure-key")

    # Performance
    max_conversation_history: int = 100
    max_commit_index: int = 1000

    class Config:
        env_prefix = "MCP_LOCAL_"
        case_sensitive = False


settings = Settings()

# Ensure data directory exists
settings.sqlite_data_dir.mkdir(parents=True, exist_ok=True)
