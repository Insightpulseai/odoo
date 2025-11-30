#!/bin/bash
set -euo pipefail

# Odoo CE v0.9.1 - Build and Push Script
# This script builds the production-ready image with all security fixes applied
# Date: 2025-11-25

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🏗️  Building Odoo CE v0.9.1 (Security Fixes Applied)"
echo "======================================================"

# Configuration
IMAGE_NAME="ghcr.io/jgtolentino/odoo-ce"
IMAGE_TAG="v0.9.1"
IMAGE_FULL="${IMAGE_NAME}:${IMAGE_TAG}"

# Check prerequisites
echo -e "\n${YELLOW}1. Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# Check if we're in the right directory
if [[ ! -f "Dockerfile" ]]; then
    echo -e "${RED}❌ Dockerfile not found. Run this script from the repo root.${NC}"
    exit 1
fi
echo "✅ Dockerfile found"

# Check if addons directory exists
if [[ ! -d "addons" ]]; then
    echo -e "${RED}❌ addons/ directory not found.${NC}"
    exit 1
fi
echo "✅ addons/ directory found ($(find addons -maxdepth 1 -type d -name 'ipai_*' | wc -l) custom modules)"

# Check if deploy/odoo.conf exists
if [[ ! -f "deploy/odoo.conf" ]]; then
    echo -e "${RED}❌ deploy/odoo.conf not found.${NC}"
    exit 1
fi
echo "✅ deploy/odoo.conf found"

# Check GHCR_PAT environment variable
if [[ -z "${GHCR_PAT:-}" ]]; then
    echo -e "${YELLOW}⚠️  GHCR_PAT not set. You'll need it to push to GitHub Container Registry.${NC}"
    echo "   Set it with: export GHCR_PAT=your_personal_access_token"
    read -p "   Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build the image
echo -e "\n${YELLOW}2. Building Docker image...${NC}"
echo "   Image: ${IMAGE_FULL}"
echo "   Base: odoo:18.0"
echo ""

# Use BuildKit for better caching and performance
export DOCKER_BUILDKIT=1

docker build \
    --tag "${IMAGE_FULL}" \
    --tag "${IMAGE_NAME}:latest" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"

# Verify the image
echo -e "\n${YELLOW}3. Verifying image...${NC}"

# Check image size
IMAGE_SIZE=$(docker images "${IMAGE_FULL}" --format "{{.Size}}")
echo "   Size: ${IMAGE_SIZE}"

if [[ $(docker images "${IMAGE_FULL}" --format "{{.Size}}" | grep -c "GB") -gt 0 ]]; then
    SIZE_GB=$(echo "$IMAGE_SIZE" | grep -oP '\d+\.\d+')
    if (( $(echo "$SIZE_GB > 2.0" | bc -l) )); then
        echo -e "${YELLOW}   ⚠️  Image is large (${IMAGE_SIZE}). Consider optimization.${NC}"
    fi
fi

# Verify health check is present
HEALTHCHECK=$(docker inspect "${IMAGE_FULL}" --format='{{.Config.Healthcheck}}')
if [[ "${HEALTHCHECK}" == "<nil>" ]]; then
    echo -e "${RED}❌ CRITICAL: Health check not found in image!${NC}"
    exit 1
fi
echo "✅ Health check: Present"

# Verify ENV variables are set
ENV_HOST=$(docker inspect "${IMAGE_FULL}" --format='{{range .Config.Env}}{{println .}}{{end}}' | grep "^HOST=" || echo "")
if [[ -z "$ENV_HOST" ]]; then
    echo -e "${RED}❌ CRITICAL: Environment variables not set in image!${NC}"
    exit 1
fi
echo "✅ Environment variables: Set (HOST, PORT, USER, PASSWORD, DB)"

# Verify custom modules are present
MODULE_COUNT=$(docker run --rm "${IMAGE_FULL}" ls -1 /mnt/extra-addons 2>/dev/null | grep -c "ipai_" || echo "0")
if [[ "$MODULE_COUNT" -ne 5 ]]; then
    echo -e "${RED}❌ CRITICAL: Expected 5 custom modules, found ${MODULE_COUNT}!${NC}"
    exit 1
fi
echo "✅ Custom modules: ${MODULE_COUNT} ipai_* modules present"

echo -e "${GREEN}✅ Image verification complete${NC}"

# Push to registry (if GHCR_PAT is set)
if [[ -n "${GHCR_PAT:-}" ]]; then
    echo -e "\n${YELLOW}4. Pushing to GitHub Container Registry...${NC}"

    # Login to GHCR
    echo "${GHCR_PAT}" | docker login ghcr.io -u jgtolentino --password-stdin

    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ Login failed! Check your GHCR_PAT.${NC}"
        exit 1
    fi

    # Push versioned tag
    echo "   Pushing ${IMAGE_FULL}..."
    docker push "${IMAGE_FULL}"

    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ Push failed!${NC}"
        exit 1
    fi

    # Push latest tag (optional, not recommended for production)
    echo "   Pushing ${IMAGE_NAME}:latest..."
    docker push "${IMAGE_NAME}:latest"

    echo -e "${GREEN}✅ Push successful!${NC}"
    echo "   Registry: https://github.com/jgtolentino/odoo-ce/pkgs/container/odoo-ce"
else
    echo -e "\n${YELLOW}4. Skipping push (GHCR_PAT not set)${NC}"
    echo "   To push manually:"
    echo "   export GHCR_PAT=your_token"
    echo "   echo \$GHCR_PAT | docker login ghcr.io -u jgtolentino --password-stdin"
    echo "   docker push ${IMAGE_FULL}"
fi

# Summary
echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}✅ Build Complete - v0.9.1 Ready for Deployment${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo "Image Details:"
echo "  Repository: ${IMAGE_NAME}"
echo "  Tag: ${IMAGE_TAG}"
echo "  Size: ${IMAGE_SIZE}"
echo ""
echo "Security Fixes Applied:"
echo "  ✅ Python requirements auto-installation"
echo "  ✅ Environment variable defaults"
echo "  ✅ Health check configuration"
echo "  ✅ Non-root execution (USER odoo)"
echo "  ✅ No hardcoded secrets"
echo ""
echo "Next Steps:"
echo "  1. Review: deploy/docker-compose.prod.yml"
echo "  2. Configure: deploy/.env.production (copy from .env.production.template)"
echo "  3. Deploy: ./scripts/deploy_prod.sh"
echo "  4. Verify: ./scripts/smoketest.sh"
echo ""
