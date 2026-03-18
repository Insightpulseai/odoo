#!/usr/bin/env bash
set -euo pipefail

export SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

echo "[superset] db upgrade"
superset db upgrade

echo "[superset] init"
superset init

# Create admin if missing (idempotent)
python - <<'PY'
import os
from superset import app
from superset.security import SupersetSecurityManager

u = os.getenv("SUPERSET_ADMIN_USERNAME", "admin")
p = os.getenv("SUPERSET_ADMIN_PASSWORD")
if not p:
    raise RuntimeError("Missing SUPERSET_ADMIN_PASSWORD")

with app.app_context():
    sm = app.appbuilder.sm
    user = sm.find_user(username=u)
    if user:
        print("[superset] admin exists:", u)
    else:
        sm.add_user(
            username=u,
            first_name=os.getenv("SUPERSET_ADMIN_FIRSTNAME", "Admin"),
            last_name=os.getenv("SUPERSET_ADMIN_LASTNAME", "User"),
            email=os.getenv("SUPERSET_ADMIN_EMAIL", "admin@example.com"),
            role=sm.find_role("Admin"),
            password=p,
        )
        print("[superset] admin created:", u)
PY

exec "$@"
