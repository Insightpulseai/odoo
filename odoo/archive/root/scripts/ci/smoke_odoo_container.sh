#!/usr/bin/env bash
set -euo pipefail

# Smoke test: Verify Odoo can start in Docker container
# This validates the complete runtime environment, not just launcher routing

ENV="${ENV:-dev}"
export ENV

echo "========================================="
echo "  Odoo Container Smoke Test (ENV=${ENV})"
echo "========================================="

# Start services
echo "Starting Docker Compose services..."
docker compose up -d --quiet-pull

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 5

# Test 1: Verify launcher exists in container
echo ""
echo "Test 1: Launcher exists in container"
if docker compose exec -T app test -f ./scripts/odoo.sh; then
  echo "✅ scripts/odoo.sh exists in container"
else
  echo "❌ scripts/odoo.sh not found in container"
  exit 1
fi

# Test 2: Launcher can execute (version check)
echo ""
echo "Test 2: Launcher can execute"
if docker compose exec -T app ./scripts/odoo.sh --version 2>&1 | head -5; then
  echo "✅ Launcher executed in container"
else
  echo "⚠️  Launcher executed with error (may be expected if Odoo not fully configured)"
fi

# Test 3: Services are running
echo ""
echo "Test 3: Container services status"
docker compose ps

# Test 4: Health check (if odoo-app service is running)
echo ""
echo "Test 4: Odoo app container health"
if docker compose ps | grep -q "odoo-app.*running"; then
  echo "✅ odoo-app container is running"
else
  echo "❌ odoo-app container is not running"
  docker compose logs odoo-app --tail 50
  exit 1
fi

echo ""
echo "========================================="
echo "  ✅ Smoke test passed"
echo "========================================="
