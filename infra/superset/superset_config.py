# =============================================================================
# SUPERSET - Production Configuration
# =============================================================================
# Configuration for Apache Superset with embedded dashboard support.
#
# Required environment variables:
# - SUPERSET_SECRET_KEY: Flask secret key
# - DO_PG_HOST, DO_PG_PORT, DO_PG_USER, DO_PG_PASSWORD, DB_SUPERSET: Database
# - SUPERSET_GUEST_TOKEN_SECRET: JWT signing secret for guest tokens
# - SUPERSET_GUEST_TOKEN_AUDIENCE: JWT audience claim (default: superset)
#
# Optional:
# - REDIS_HOST, REDIS_PORT: Cache/Celery backend
# - SUPERSET_GUEST_ROLE_NAME: Role for guest users (default: Public)
# =============================================================================
import os


def _env(k, d=None):
    """Get required environment variable or raise error."""
    v = os.getenv(k, d)
    if v is None or v == "":
        raise RuntimeError(f"Missing required env: {k}")
    return v


def _env_opt(k, d=None):
    """Get optional environment variable."""
    return os.getenv(k, d)


# =============================================================================
# Core Security
# =============================================================================
SUPERSET_SECRET_KEY = _env("SUPERSET_SECRET_KEY")

# =============================================================================
# Database (DigitalOcean Managed PostgreSQL)
# =============================================================================
DO_PG_HOST = _env("DO_PG_HOST")
DO_PG_PORT = _env("DO_PG_PORT")
DO_PG_USER = _env("DO_PG_USER")
DO_PG_PASSWORD = _env("DO_PG_PASSWORD")
DB_SUPERSET = _env("DB_SUPERSET")
DO_PG_SSLMODE = _env_opt("DO_PG_SSLMODE", "require")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DO_PG_USER}:{DO_PG_PASSWORD}"
    f"@{DO_PG_HOST}:{DO_PG_PORT}/{DB_SUPERSET}?sslmode={DO_PG_SSLMODE}"
)

# =============================================================================
# Embedded Dashboard Configuration
# =============================================================================
# Enable embedded dashboard feature
EMBEDDED_SUPERSET = True

# Guest token JWT configuration
# These must match the token API service configuration
GUEST_TOKEN_JWT_SECRET = _env_opt("SUPERSET_GUEST_TOKEN_SECRET")
GUEST_TOKEN_JWT_AUDIENCE = _env_opt("SUPERSET_GUEST_TOKEN_AUDIENCE", "superset")

# Guest role for embedded users (must exist in Superset)
GUEST_ROLE_NAME = _env_opt("SUPERSET_GUEST_ROLE_NAME", "Public")

# Allowed domains for embedding (comma-separated in env)
_allowed_domains_str = _env_opt(
    "SUPERSET_ALLOWED_EMBEDDED_DOMAINS",
    "https://erp.insightpulseai.com,https://scout-mvp.vercel.app,http://localhost:8069,http://localhost:3000"
)
ALLOWED_EMBEDDED_DOMAINS = [d.strip() for d in _allowed_domains_str.split(",") if d.strip()]

# =============================================================================
# CORS Configuration
# =============================================================================
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": ALLOWED_EMBEDDED_DOMAINS,
    "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    "allow_headers": "*",
    "expose_headers": "*",
    "resources": "*",
}

# =============================================================================
# Content Security Policy (CSP)
# =============================================================================
# Allow embedding in iframes from specified domains
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    "content_security_policy": {
        "frame-ancestors": ALLOWED_EMBEDDED_DOMAINS,
    },
}

# =============================================================================
# Redis Cache / Celery
# =============================================================================
REDIS_HOST = _env_opt("REDIS_HOST", "redis")
REDIS_PORT = _env_opt("REDIS_PORT", "6379")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": int(REDIS_PORT),
}


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    task_annotations = {"sql_lab.get_sql_results": {"rate_limit": "100/s"}}
    imports = ("superset.sql_lab", "superset.tasks")


CELERY_CONFIG = CeleryConfig

# =============================================================================
# Feature Flags
# =============================================================================
FEATURE_FLAGS = {
    # Enable scheduled reports and alerts
    "ALERT_REPORTS": True,
    # Enable embedded dashboards
    "EMBEDDED_SUPERSET": True,
    # Enable row-level security
    "ROW_LEVEL_SECURITY": True,
}

# =============================================================================
# Security Settings
# =============================================================================
WTF_CSRF_ENABLED = True

# Row-level security configuration
RLS_BASE_RELATED_FIELD_FILTERS = ["employee_id", "company_id", "user_id"]

# =============================================================================
# Logging
# =============================================================================
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = _env_opt("SUPERSET_LOG_LEVEL", "INFO")
