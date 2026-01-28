#!/usr/bin/env bash
# =============================================================================
# Push Script: Odoo CE 19 + OCA + ipai_enterprise_bridge (EE Parity Image)
# =============================================================================
# Pushes the built image to the container registry.
#
# Usage:
#   ./docker/push-ce19.sh
#   IMAGE_TAG=19.0.1 ./docker/push-ce19.sh
#
# Environment Variables:
#   REGISTRY_HOST   - Container registry host (default: ghcr.io)
#   REGISTRY_ORG    - Registry organization (default: jgtolentino)
#   IMAGE_NAME      - Full image name (default: ${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce)
#   IMAGE_TAG       - Image tag (default: 19.0-ee-parity)
#   PUSH_LATEST     - Also push as :latest-ee-parity (default: false)
#   DRY_RUN         - Show what would be pushed without pushing (default: false)
#
# Authentication:
#   For ghcr.io, authenticate with:
#     echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
# =============================================================================

set -euo pipefail

# Configuration with defaults
: "${REGISTRY_HOST:=ghcr.io}"
: "${REGISTRY_ORG:=jgtolentino}"
: "${IMAGE_NAME:=${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce}"
: "${IMAGE_TAG:=19.0-ee-parity}"
: "${PUSH_LATEST:=false}"
: "${DRY_RUN:=false}"

# Derived values
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE="${IMAGE_NAME}:latest-ee-parity"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Pushing Odoo CE 19 EE Parity Image${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Image:       ${FULL_IMAGE}"
echo "  Registry:    ${REGISTRY_HOST}"
echo "  Push Latest: ${PUSH_LATEST}"
echo "  Dry Run:     ${DRY_RUN}"
echo ""

# Verify image exists locally
echo -e "${YELLOW}[1/3] Verifying local image...${NC}"
if ! docker image inspect "${FULL_IMAGE}" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Image ${FULL_IMAGE} not found locally.${NC}"
    echo "Run ./docker/build-ce19.sh first."
    exit 1
fi
echo -e "${GREEN}  ✓ Image exists locally${NC}"

# Check registry authentication
echo -e "${YELLOW}[2/3] Checking registry authentication...${NC}"
if [ "${DRY_RUN}" = "false" ]; then
    # Try a simple API call to check auth
    if ! docker login "${REGISTRY_HOST}" --get-login > /dev/null 2>&1; then
        echo -e "${YELLOW}  Warning: Not logged in to ${REGISTRY_HOST}${NC}"
        echo ""
        echo "  To authenticate with ghcr.io:"
        echo "    echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin"
        echo ""
        read -p "  Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}  ✓ Authenticated with ${REGISTRY_HOST}${NC}"
    fi
else
    echo -e "${YELLOW}  (Skipped - dry run)${NC}"
fi

# Push image(s)
echo -e "${YELLOW}[3/3] Pushing image(s)...${NC}"

push_with_retry() {
    local image="$1"
    local max_retries=4
    local retry=0
    local wait_time=2

    while [ $retry -lt $max_retries ]; do
        if [ "${DRY_RUN}" = "true" ]; then
            echo "  [DRY RUN] Would push: ${image}"
            return 0
        fi

        echo "  Pushing ${image}..."
        if docker push "${image}"; then
            echo -e "${GREEN}  ✓ Pushed ${image}${NC}"
            return 0
        else
            retry=$((retry + 1))
            if [ $retry -lt $max_retries ]; then
                echo -e "${YELLOW}  Push failed, retrying in ${wait_time}s (attempt ${retry}/${max_retries})...${NC}"
                sleep $wait_time
                wait_time=$((wait_time * 2))
            fi
        fi
    done

    echo -e "${RED}  ✗ Failed to push ${image} after ${max_retries} attempts${NC}"
    return 1
}

# Push main tag
if ! push_with_retry "${FULL_IMAGE}"; then
    echo -e "${RED}ERROR: Failed to push main image${NC}"
    exit 1
fi

# Push latest tag if requested
if [ "${PUSH_LATEST}" = "true" ]; then
    echo ""
    echo "  Tagging as latest-ee-parity..."
    docker tag "${FULL_IMAGE}" "${LATEST_IMAGE}"

    if ! push_with_retry "${LATEST_IMAGE}"; then
        echo -e "${RED}ERROR: Failed to push latest tag${NC}"
        exit 1
    fi
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Push Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Pushed images:"
echo "  - ${FULL_IMAGE}"
if [ "${PUSH_LATEST}" = "true" ]; then
    echo "  - ${LATEST_IMAGE}"
fi
echo ""
echo "To pull this image:"
echo "  docker pull ${FULL_IMAGE}"
echo ""
echo "To deploy:"
echo "  docker run -d --name odoo-ce19 -p 8069:8069 ${FULL_IMAGE}"
echo ""
