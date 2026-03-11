#!/usr/bin/env bash
# Sync Supabase Edge Function secrets from env vars (idempotent)
set -euo pipefail

python3 - <<'PY'
import os, sys
from pathlib import Path
import yaml

data = yaml.safe_load(Path("infra/secrets/registry.yaml").read_text())
secrets = data.get("secrets", [])

# Determine project ref from the first supabase secret entry
project_ref_env = None
for s in secrets:
    if s.get("store") == "supabase_edge_secrets":
        project_ref_env = s.get("supabase_project_ref_env")
        break

if not project_ref_env:
    print("No supabase_edge_secrets entries; nothing to do.")
    raise SystemExit(0)

project_ref = os.environ.get(project_ref_env)
if not project_ref:
    print(f"ERROR: Supabase project ref env var {project_ref_env} is not set", file=sys.stderr)
    raise SystemExit(2)

print(f'supabase link --project-ref "${{{project_ref_env}}}"')

for s in secrets:
    if s.get("store") != "supabase_edge_secrets":
        continue
    name = s["name"]
    env_var = s["env_var"]
    required = bool(s.get("required", False))
    val = os.environ.get(env_var)

    if (val is None or val == "") and required:
        print(f"ERROR: {name}: env var {env_var} is required but not set", file=sys.stderr)
        raise SystemExit(2)

    if val:
        print(f'supabase secrets set {name}="${{{env_var}}}"')
PY
