#!/usr/bin/env bash
# Sync GitHub Actions secrets from env vars (idempotent)
set -euo pipefail

REG="infra/secrets/registry.yaml"

python3 - <<'PY'
import os, sys
from pathlib import Path
import yaml

reg = Path("infra/secrets/registry.yaml")
data = yaml.safe_load(reg.read_text())
secrets = data.get("secrets", [])

for s in secrets:
    if s.get("store") != "github_actions":
        continue
    name = s["name"]
    repo = s.get("repo")
    env_var = s["env_var"]
    required = bool(s.get("required", False))
    auto_injected = bool(s.get("auto_injected", False))

    if not repo:
        print(f"ERROR: {name}: missing repo", file=sys.stderr); sys.exit(2)

    # Skip auto-injected secrets (like GITHUB_TOKEN)
    if auto_injected:
        continue

    val = os.environ.get(env_var)
    if (val is None or val == "") and required:
        print(f"ERROR: {name}: env var {env_var} is required but not set", file=sys.stderr)
        sys.exit(2)

    if val:
        # Emit a shell line per secret for execution by parent script
        print(f'gh secret set {name} -b "${{{env_var}}}" -R {repo}')
PY
