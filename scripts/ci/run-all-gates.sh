#!/usr/bin/env bash
set -euo pipefail

# Ensure we run from repo root
cd "$(git rev-parse --show-toplevel)"

echo "=== 1. compose-topology-guard ==="
bash -c '
  allowed=(
    "deploy/docker-compose.prod.yml"
    "deploy/docker-compose.ce19.yml"
    "infra/docker-compose.prod.yaml"
    "sandbox/dev/docker-compose.yml"
    "sandbox/dev/docker-compose.production.yml"
    "sandbox/workbench/docker-compose.workbench.yml"
    "docker-compose.dev.yml"
    "infra/do-oca-stack/docker-compose.yml"
    "infra/do-oca-stack/docker-compose.caddy.yml"
    "docker/docker-compose.ci.yml"
    "ci/odoo/docker-compose.ci.yml"
    "docker/analytics/docker-compose.yml"
    "odoo/compose/docker-compose.platform.yml"
  )

  mapfile -t found < <(git ls-files | grep -E "(^|/)(docker-compose[^/]*\.ya?ml)$" | grep -v "^archive/" | grep -v "^\.devcontainer/" || true)

  bad=0
  for f in "${found[@]}"; do
    ok=0
    for a in "${allowed[@]}"; do
      if [ "$f" = "$a" ]; then
        ok=1
        break
      fi
    done
    if [ "$ok" -eq 0 ]; then
      echo "❌ Unexpected compose file: $f"
      bad=1
    fi
  done

  if [ "$bad" -eq 0 ]; then
    echo "✅ All compose files allowed"
  else
    exit 1
  fi
'

echo
echo "=== 2. modules-audit-drift ==="
python3 - << 'PYEOF'
import json, re

with open("docs/deployment/MODULES_AUDIT.md") as f:
    content = f.read()

blocks = re.findall(r"```json\n(.*?)\n```", content, re.DOTALL)

if len(blocks) < 3:
    print("❌ Missing JSON blocks in docs/deployment/MODULES_AUDIT.md")
    raise SystemExit(1)

for i, b in enumerate(blocks[:3]):
    json.loads(b)
    print(f"✅ JSON block {i+1} valid")
PYEOF

echo
echo "=== 3. docs-current-state ==="
if grep -q "Canonical modules present:" README.md; then
  echo "✅ README has current state block"
else
  echo "❌ README missing current state block"
  exit 1
fi

echo
echo "=== 4. AI naming (deprecated modules) ==="
for m in addons/ipai/ipai_ai_*; do
  if [ -f "$m/__manifest__.py" ]; then
    name="$(basename "$m")"
    if grep -q '"installable": False' "$m/__manifest__.py"; then
      echo "✅ $name: deprecated (installable=False)"
    else
      echo "⚠️ $name: installable=True (canonical)"
    fi
  fi
done

echo
echo "=== ALL LOCAL GATES COMPLETED ==="
