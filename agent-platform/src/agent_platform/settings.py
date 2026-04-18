"""Runtime settings loaded from environment variables."""

from __future__ import annotations

import os

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")

        env: str = Field("development", alias="AGENT_PLATFORM_ENV")
        log_level: str = Field("INFO", alias="AGENT_PLATFORM_LOG_LEVEL")
        port: int = Field(8000, alias="AGENT_PLATFORM_PORT")

        foundry_endpoint: str = Field(
            "https://ipai-copilot-resource.services.ai.azure.com"
            "/api/projects/proj-ipai-copilot",
            alias="AZURE_AI_FOUNDRY_ENDPOINT",
        )
        azure_client_id: str | None = Field(None, alias="AZURE_CLIENT_ID")

        odoo_url: str = Field("https://odoo.insightpulseai.com", alias="ODOO_URL")
        odoo_db: str = Field("odoo", alias="ODOO_DB")
        odoo_api_key: str | None = Field(None, alias="ODOO_API_KEY")

        otel_endpoint: str | None = Field(None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")

except ImportError:  # pragma: no cover — pydantic present in production

    class Settings:  # type: ignore[no-redef]
        """Stdlib fallback used only when pydantic-settings is not installed."""

        def __init__(self) -> None:
            self.env = os.getenv("AGENT_PLATFORM_ENV", "development")
            self.log_level = os.getenv("AGENT_PLATFORM_LOG_LEVEL", "INFO")
            self.port = int(os.getenv("AGENT_PLATFORM_PORT", "8000"))
            self.foundry_endpoint = os.getenv(
                "AZURE_AI_FOUNDRY_ENDPOINT",
                "https://ipai-copilot-resource.services.ai.azure.com"
                "/api/projects/proj-ipai-copilot",
            )
            self.azure_client_id = os.getenv("AZURE_CLIENT_ID")
            self.odoo_url = os.getenv("ODOO_URL", "https://odoo.insightpulseai.com")
            self.odoo_db = os.getenv("ODOO_DB", "odoo")
            self.odoo_api_key = os.getenv("ODOO_API_KEY")
            self.otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
