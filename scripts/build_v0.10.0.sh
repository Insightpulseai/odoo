#!/usr/bin/env bash
# Build script for Odoo CE v0.10.0 with OCA modules
# Date: 2025-11-25

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ghcr.io/jgtolentino/odoo-ce"
VERSION="v0.10.0"
DOCKERFILE="Dockerfile.v0.10.0"

echo -e "${GREEN}=== Building Odoo CE ${VERSION} with OCA modules ===${NC}"

# Check if GHCR_PAT is set
if [ -z "${GHCR_PAT:-}" ]; then
    echo -e "${RED}Error: GHCR_PAT environment variable not set${NC}"
    echo "Please set it with: export GHCR_PAT=\"\$GITHUB_TOKEN\""
    exit 1
fi

# Verify OCA directories exist
echo -e "${YELLOW}Checking OCA module directories...${NC}"
for repo in project mis-builder purchase-workflow reporting-engine server-ux; do
    if [ ! -d "oca-addons/$repo" ]; then
        echo -e "${RED}Error: oca-addons/$repo directory not found${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All OCA modules present${NC}"

# Login to GitHub Container Registry
echo -e "${YELLOW}Logging in to GHCR...${NC}"
echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin

# Build the image
echo -e "${YELLOW}Building Docker image ${IMAGE_NAME}:${VERSION}...${NC}"
docker build \
    --platform linux/amd64 \
    -f "$DOCKERFILE" \
    -t "${IMAGE_NAME}:${VERSION}" \
    -t "${IMAGE_NAME}:latest" \
    .

# Push to registry
echo -e "${YELLOW}Pushing to GitHub Container Registry...${NC}"
docker push "${IMAGE_NAME}:${VERSION}"
docker push "${IMAGE_NAME}:latest"

echo -e "${GREEN}=== Build complete ===${NC}"
echo -e "Image: ${IMAGE_NAME}:${VERSION}"
echo -e "Tagged: ${IMAGE_NAME}:latest"
echo -e ""
echo -e "Next steps:"
echo -e "1. Update docker-compose.prod.v0.10.0.yml to use ${VERSION}"
echo -e "2. Deploy to VPS: doctl apps update <APP_ID> --spec infra/do/odoo-ce-v0.10.0.yaml"
echo -e "3. Install OCA modules: docker exec odoo-ce odoo -d odoo -i project_timeline,mis_builder,purchase_request --stop-after-init"
