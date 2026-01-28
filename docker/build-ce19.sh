#!/usr/bin/env bash
# =============================================================================
# Build Script: Odoo CE 19 + OCA + ipai_enterprise_bridge (EE Parity Image)
# =============================================================================
# Usage:
#   ./docker/build-ce19.sh
#   ODOO_BASE_IMAGE=odoo:19.0-20260115 ./docker/build-ce19.sh
#   IMAGE_TAG=19.0.1 ./docker/build-ce19.sh
#
# Environment Variables:
#   ODOO_BASE_IMAGE - Base Odoo image (default: odoo:19.0)
#   REGISTRY_HOST   - Container registry host (default: ghcr.io)
#   REGISTRY_ORG    - Registry organization (default: jgtolentino)
#   IMAGE_NAME      - Full image name (default: ${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce)
#   IMAGE_TAG       - Image tag (default: 19.0-ee-parity)
#   NO_CACHE        - Set to 'true' to build without cache
# =============================================================================

set -euo pipefail

# Configuration with defaults
: "${ODOO_BASE_IMAGE:=odoo:19.0}"
: "${REGISTRY_HOST:=ghcr.io}"
: "${REGISTRY_ORG:=jgtolentino}"
: "${IMAGE_NAME:=${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce}"
: "${IMAGE_TAG:=19.0-ee-parity}"
: "${NO_CACHE:=false}"

# Derived values
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building Odoo CE 19 EE Parity Image${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Base Image:    ${ODOO_BASE_IMAGE}"
echo "  Target Image:  ${FULL_IMAGE}"
echo "  Repo Root:     ${REPO_ROOT}"
echo "  No Cache:      ${NO_CACHE}"
echo ""

# Change to repo root
cd "${REPO_ROOT}"

# Verify required files exist
echo -e "${YELLOW}[1/4] Verifying required files...${NC}"

if [ ! -f "docker/Dockerfile.ce19" ]; then
    echo -e "${RED}ERROR: docker/Dockerfile.ce19 not found${NC}"
    exit 1
fi

if [ ! -d "addons/ipai/ipai_enterprise_bridge" ]; then
    echo -e "${RED}ERROR: addons/ipai/ipai_enterprise_bridge not found${NC}"
    exit 1
fi

if [ ! -f "deploy/odoo.conf" ]; then
    echo -e "${RED}ERROR: deploy/odoo.conf not found${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ All required files present${NC}"

# Pull base image
echo -e "${YELLOW}[2/4] Pulling base image: ${ODOO_BASE_IMAGE}...${NC}"
docker pull "${ODOO_BASE_IMAGE}" || {
    echo -e "${YELLOW}  Warning: Could not pull base image (may be cached)${NC}"
}

# Build image
echo -e "${YELLOW}[3/4] Building image...${NC}"

BUILD_ARGS=(
    --build-arg "ODOO_BASE_IMAGE=${ODOO_BASE_IMAGE}"
    -t "${FULL_IMAGE}"
    -f docker/Dockerfile.ce19
)

# Add timestamp tags
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BUILD_ARGS+=(-t "${IMAGE_NAME}:${IMAGE_TAG}-${TIMESTAMP}")

# Add no-cache if requested
if [ "${NO_CACHE}" = "true" ]; then
    BUILD_ARGS+=(--no-cache)
fi

# Add labels
BUILD_ARGS+=(
    --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    --label "org.opencontainers.image.source=https://github.com/jgtolentino/odoo-ce"
    --label "org.opencontainers.image.revision=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
)

# Run build
docker build "${BUILD_ARGS[@]}" .

# Verify image
echo -e "${YELLOW}[4/4] Verifying built image...${NC}"

IMAGE_SIZE=$(docker images "${FULL_IMAGE}" --format "{{.Size}}")
IMAGE_ID=$(docker images "${FULL_IMAGE}" --format "{{.ID}}")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Build Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Image Details:"
echo "  Name:     ${FULL_IMAGE}"
echo "  ID:       ${IMAGE_ID}"
echo "  Size:     ${IMAGE_SIZE}"
echo ""
echo "Tags created:"
echo "  - ${FULL_IMAGE}"
echo "  - ${IMAGE_NAME}:${IMAGE_TAG}-${TIMESTAMP}"
echo ""
echo "Next steps:"
echo "  1. Run tests:  ./docker/test-ce19.sh"
echo "  2. Run local:  ./docker/run-local-ce19.sh"
echo "  3. Push:       ./docker/push-ce19.sh"
echo ""
