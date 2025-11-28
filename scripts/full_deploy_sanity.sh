#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "▶ Verifying canonical image references..."
grep -q "image: ghcr.io/jgtolentino/odoo-ce:latest" docker-compose.prod.yml
grep -R "ghcr.io/jgtolentino/odoo-ce:latest" deploy/k8s/odoo-deployment.yaml >/dev/null

echo "✔ Canonical image OK"

echo "▶ Verifying core docs and PRD exist..."
test -f docs/SECRETS_NAMING_AND_STORAGE.md
test -f docs/DEPLOYMENT_NAMING_MATRIX.md
test -f specs/003-odoo-custom-image.prd.md

echo "✔ Docs + PRD present"

echo "▶ Checking Dockerfile alignment..."
if ! grep -q "FROM odoo:18.0" Dockerfile; then
  echo "✖ Dockerfile base image is not odoo:18.0"
  exit 1
fi
grep -q "/mnt/extra-addons" Dockerfile
grep -q "/etc/odoo/odoo.conf" Dockerfile
grep -q "USER odoo" Dockerfile

echo "✔ Dockerfile matches spec"

echo "▶ (Optional) Local build smoketest..."
if command -v docker >/dev/null 2>&1; then
  docker build -t odoo-ce-sanity:latest . >/dev/null
  echo "✔ Local docker build succeeded"
else
  echo "ℹ docker not available, skipping local build"
fi

echo "✅ Full deploy sanity check PASSED"
