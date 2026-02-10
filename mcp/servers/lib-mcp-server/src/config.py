"""
LIB MCP Server Configuration

Loads settings from environment variables and config files
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


class LibSettings(BaseSettings):
    """LIB configuration settings"""

    # Database
    lib_db_path: Path = Path(".lib/lib.db")

    # Scanner
    scan_roots: List[str] = []
    auto_scan_on_startup: bool = True
    content_extraction_enabled: bool = True
    content_max_size_kb: int = 50

    # FTS5
    fts5_enabled: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    class Config:
        env_prefix = "LIB_"
        env_file = ".env"
        case_sensitive = False


def load_config(config_path: Optional[Path] = None) -> LibSettings:
    """
    Load configuration from environment and optional JSON file

    Args:
        config_path: Optional path to lib.config.json

    Returns:
        LibSettings instance
    """
    settings = LibSettings()

    # Load from JSON if provided
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        # Override with JSON values
        if "database" in config_data:
            if "path" in config_data["database"]:
                settings.lib_db_path = Path(config_data["database"]["path"])

        if "scanner" in config_data:
            scanner = config_data["scanner"]
            if "scan_roots" in scanner:
                settings.scan_roots = scanner["scan_roots"]
            if "auto_scan_on_startup" in scanner:
                settings.auto_scan_on_startup = scanner["auto_scan_on_startup"]

            if "content_extraction" in scanner:
                ce = scanner["content_extraction"]
                if "enabled" in ce:
                    settings.content_extraction_enabled = ce["enabled"]
                if "max_size_kb" in ce:
                    settings.content_max_size_kb = ce["max_size_kb"]

        if "fts5" in config_data:
            if "enabled" in config_data["fts5"]:
                settings.fts5_enabled = config_data["fts5"]["enabled"]

    # Override from environment variables (highest priority)
    if os.getenv("LIB_SQLITE_PATH"):
        settings.lib_db_path = Path(os.getenv("LIB_SQLITE_PATH"))

    if os.getenv("LIB_SCAN_ROOTS"):
        settings.scan_roots = os.getenv("LIB_SCAN_ROOTS").split(",")

    if os.getenv("LIB_AUTO_SCAN_ON_STARTUP"):
        settings.auto_scan_on_startup = os.getenv("LIB_AUTO_SCAN_ON_STARTUP").lower() == "true"

    return settings


# Global settings instance
settings = load_config(Path(".lib/lib.config.json"))
