#!/usr/bin/env bash
set -euo pipefail

# Script to build and push versioned Docker images
# Usage: ./scripts/build_and_push_version.sh [version]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Default version if not provided
VERSION="${1:-v0.9.0}"
IMAGE_BASE="ghcr.io/jgtolentino/odoo-ce"

echo "▶ Building and pushing versioned Docker images..."
echo "Version: $VERSION"
echo "Image: $IMAGE_BASE"

# Validate version format
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
  echo "❌ Invalid version format. Expected: vX.Y.Z or vX.Y.Z-suffix"
  exit 1
fi

# Check if we're logged in to GHCR
if ! docker info 2>/dev/null | grep -q "ghcr.io"; then
  echo "⚠️  Not logged in to GHCR. Please login first:"
  echo "   echo \"\$GHCR_PAT\" | docker login ghcr.io -u jgtolentino --password-stdin"
  exit 1
fi

echo "▶ Building Docker image..."
docker build -t "$IMAGE_BASE:$VERSION" -t "$IMAGE_BASE:latest" .

echo "▶ Pushing versioned image..."
docker push "$IMAGE_BASE:$VERSION"

echo "▶ Pushing latest tag..."
docker push "$IMAGE_BASE:latest"

echo "✅ Successfully built and pushed:"
echo "   - $IMAGE_BASE:$VERSION"
echo "   - $IMAGE_BASE:latest"

echo ""
echo "📋 Next steps:"
echo "1. Update deployment manifests to use $VERSION"
echo "2. Deploy to VPS: docker compose -f docker-compose.prod.yml pull odoo && docker compose -f docker-compose.prod.yml up -d"
echo "3. Deploy to DOKS: kubectl apply -f deploy/k8s/"
echo "4. Validate deployment with: scripts/full_deploy_sanity.sh"
