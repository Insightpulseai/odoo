"""
Configuration settings for MCP Coordinator
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """MCP Coordinator configuration"""

    # Server settings
    coordinator_api_key: str = "coordinator-dev-key"
    environment: str = "development"

    # MCP Server endpoints
    odoo_prod_mcp_url: str = "http://odoo-prod-mcp:8767"
    odoo_lab_mcp_url: str = "http://localhost:8765"
    agent_coordination_url: str = "http://localhost:8768"

    # Supabase connection
    supabase_url: str
    supabase_service_role_key: str

    # Redis cache (optional for dev)
    redis_url: Optional[str] = None

    # Routing configuration
    default_target: str = "odoo_prod"
    enable_aggregation: bool = True
    cache_ttl: int = 300  # 5 minutes

    # GitHub App settings (pulser-hub)
    github_app_id: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    github_app_private_key_b64: Optional[str] = None  # Base64 encoded PEM
    public_base_url: Optional[str] = None  # For OAuth callbacks

    class Config:
        env_file = ".env"


settings = Settings()
