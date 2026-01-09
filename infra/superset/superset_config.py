import os

def _env(k, d=None):
    v = os.getenv(k, d)
    if v is None or v == "":
        raise RuntimeError(f"Missing env: {k}")
    return v

SUPERSET_SECRET_KEY = _env("SUPERSET_SECRET_KEY")

# Use DO Managed Postgres for Superset metadata
DO_PG_HOST = _env("DO_PG_HOST")
DO_PG_PORT = _env("DO_PG_PORT")
DO_PG_USER = _env("DO_PG_USER")
DO_PG_PASSWORD = _env("DO_PG_PASSWORD")
DB_SUPERSET = _env("DB_SUPERSET")
DO_PG_SSLMODE = os.getenv("DO_PG_SSLMODE", "require")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DO_PG_USER}:{DO_PG_PASSWORD}"
    f"@{DO_PG_HOST}:{DO_PG_PORT}/{DB_SUPERSET}?sslmode={DO_PG_SSLMODE}"
)

# Redis cache / celery
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

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

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
}

WTF_CSRF_ENABLED = True
