#!/usr/bin/env bash
# =============================================================================
# Odoo 18 CE + OCA Enterprise Parity - Docker Build Script
# =============================================================================
# Builds the delta image from v1.0.1-paddlepaddle-fix base
#
# Usage:
#   ./docker/build-enterprise-parity.sh [--push] [--no-cache]
#
# Environment:
#   REGISTRY    - Container registry (default: ghcr.io/jgtolentino)
#   IMAGE_NAME  - Image name (default: odoo-ce)
#   IMAGE_TAG   - Image tag (default: v1.1.0-enterprise-parity)
#
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

REGISTRY="${REGISTRY:-ghcr.io/jgtolentino}"
IMAGE_NAME="${IMAGE_NAME:-odoo-ce}"
IMAGE_TAG="${IMAGE_TAG:-v1.1.0-enterprise-parity}"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Parse arguments
PUSH_IMAGE=false
NO_CACHE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--push] [--no-cache]"
            echo ""
            echo "Options:"
            echo "  --push      Push image to registry after build"
            echo "  --no-cache  Build without Docker cache"
            echo ""
            echo "Environment Variables:"
            echo "  REGISTRY    Container registry (default: ghcr.io/jgtolentino)"
            echo "  IMAGE_NAME  Image name (default: odoo-ce)"
            echo "  IMAGE_TAG   Image tag (default: v1.1.0-enterprise-parity)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "Odoo 18 CE + OCA Enterprise Parity Build"
echo "========================================="
echo "Registry:    ${REGISTRY}"
echo "Image:       ${IMAGE_NAME}"
echo "Tag:         ${IMAGE_TAG}"
echo "Full Image:  ${FULL_IMAGE}"
echo "Push:        ${PUSH_IMAGE}"
echo "========================================="

# Verify we're in the right directory
if [ ! -f "${SCRIPT_DIR}/Dockerfile.v1.1.0-enterprise-parity" ]; then
    echo "❌ Error: Dockerfile.v1.1.0-enterprise-parity not found in ${SCRIPT_DIR}"
    exit 1
fi

# Build the image
echo ""
echo "📦 Building Docker image..."
echo ""

cd "$PROJECT_ROOT"

docker build \
    ${NO_CACHE} \
    -f docker/Dockerfile.v1.1.0-enterprise-parity \
    -t "${FULL_IMAGE}" \
    -t "${REGISTRY}/${IMAGE_NAME}:latest-enterprise-parity" \
    --label "org.opencontainers.image.source=https://github.com/jgtolentino/odoo-ce" \
    --label "org.opencontainers.image.version=${IMAGE_TAG}" \
    --label "org.opencontainers.image.title=Odoo 18 CE + OCA Enterprise Parity" \
    --label "org.opencontainers.image.description=Odoo 18 CE with OCA modules for enterprise feature parity" \
    --label "org.opencontainers.image.vendor=InsightPulseAI" \
    --label "com.insightpulse.base-image=v1.0.1-paddlepaddle-fix" \
    --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    .

echo ""
echo "✅ Build completed successfully!"
echo ""

# Show image info
echo "📊 Image Details:"
docker images "${FULL_IMAGE}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Push if requested
if [ "$PUSH_IMAGE" = true ]; then
    echo ""
    echo "📤 Pushing image to registry..."

    # Check if logged in
    if ! docker info 2>/dev/null | grep -q "Username"; then
        echo "⚠️  Warning: Not logged into Docker registry. Run 'docker login ${REGISTRY}' first."
    fi

    docker push "${FULL_IMAGE}"
    docker push "${REGISTRY}/${IMAGE_NAME}:latest-enterprise-parity"

    echo ""
    echo "✅ Push completed!"
    echo "   ${FULL_IMAGE}"
    echo "   ${REGISTRY}/${IMAGE_NAME}:latest-enterprise-parity"
fi

echo ""
echo "========================================="
echo "Build Summary"
echo "========================================="
echo "Image: ${FULL_IMAGE}"
echo ""
echo "To run locally:"
echo "  docker compose -f docker/docker-compose.enterprise-parity.yml up -d"
echo ""
echo "To test the image:"
echo "  docker run --rm ${FULL_IMAGE} odoo --version"
echo ""
echo "========================================="
