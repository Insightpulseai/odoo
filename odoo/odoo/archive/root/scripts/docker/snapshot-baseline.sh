#!/bin/bash
# snapshot-baseline.sh
# Capture Docker infrastructure baseline for audit and compliance
#
# Portfolio Initiative: PORT-2026-010
# Process: PROC-INFRA-001, PROC-AUDIT-001
# Control: CTRL-SOP-003
# Evidence: EVID-20260212-005

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${TIMESTAMP}/docker-baseline"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +%Y-%m-%d\ %H:%M:%S)]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# ============================================================================
# Create Evidence Directory
# ============================================================================

log "Creating evidence directory: ${EVIDENCE_DIR}"
mkdir -p "$EVIDENCE_DIR"

# ============================================================================
# Capture Container List
# ============================================================================

log "Capturing running containers..."
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "${EVIDENCE_DIR}/container-list.txt"
log "✅ Saved: container-list.txt"

log "Capturing all containers (including stopped)..."
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.CreatedAt}}" > "${EVIDENCE_DIR}/container-list-all.txt"
log "✅ Saved: container-list-all.txt"

# ============================================================================
# Capture Network Configuration
# ============================================================================

log "Capturing Docker networks..."
docker network ls > "${EVIDENCE_DIR}/network-list.txt"
log "✅ Saved: network-list.txt"

log "Capturing network details..."
{
    echo "========================================="
    echo "Docker Network Details"
    echo "Timestamp: $(date)"
    echo "========================================="
    echo ""

    for network in $(docker network ls --format '{{.Name}}' | grep -v "bridge\|host\|none"); do
        echo "========================================="
        echo "Network: $network"
        echo "========================================="
        docker network inspect "$network"
        echo ""
    done
} > "${EVIDENCE_DIR}/network-details.txt"
log "✅ Saved: network-details.txt"

# ============================================================================
# Capture Volume Information
# ============================================================================

log "Capturing Docker volumes..."
docker volume ls > "${EVIDENCE_DIR}/volume-list.txt"
log "✅ Saved: volume-list.txt"

log "Capturing volume details..."
{
    echo "========================================="
    echo "Docker Volume Details"
    echo "Timestamp: $(date)"
    echo "========================================="
    echo ""

    for volume in $(docker volume ls --format '{{.Name}}'); do
        echo "========================================="
        echo "Volume: $volume"
        echo "========================================="
        docker volume inspect "$volume"
        echo ""
    done
} > "${EVIDENCE_DIR}/volume-details.txt"
log "✅ Saved: volume-details.txt"

# ============================================================================
# Capture Image List
# ============================================================================

log "Capturing Docker images..."
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedAt}}" > "${EVIDENCE_DIR}/image-list.txt"
log "✅ Saved: image-list.txt"

# ============================================================================
# Capture Container Configurations
# ============================================================================

log "Capturing container configurations..."
mkdir -p "${EVIDENCE_DIR}/container-configs"

for container in $(docker ps --format '{{.Names}}'); do
    log "Inspecting: ${container}"
    docker inspect "$container" > "${EVIDENCE_DIR}/container-configs/${container}.json"
done
log "✅ Saved: container-configs/"

# ============================================================================
# Resource Usage Snapshot
# ============================================================================

log "Capturing resource usage..."
docker stats --no-stream > "${EVIDENCE_DIR}/resource-usage.txt"
log "✅ Saved: resource-usage.txt"

# ============================================================================
# Compliance Check
# ============================================================================

log "Running compliance checks..."

{
    echo "========================================="
    echo "Docker Container Compliance Check"
    echo "Timestamp: $(date)"
    echo "SOP: CTRL-SOP-003"
    echo "========================================="
    echo ""

    echo "Checking resource limits..."
    for container in $(docker ps --format '{{.Names}}'); do
        echo "----------------------------------------"
        echo "Container: $container"
        echo "----------------------------------------"

        # Memory limit
        MEMORY_LIMIT=$(docker inspect "$container" --format '{{.HostConfig.Memory}}')
        if [ "$MEMORY_LIMIT" -eq 0 ]; then
            echo "❌ FAIL: No memory limit set"
        else
            MEMORY_MB=$((MEMORY_LIMIT / 1024 / 1024))
            echo "✅ PASS: Memory limit: ${MEMORY_MB}MB"
        fi

        # CPU limit
        CPU_LIMIT=$(docker inspect "$container" --format '{{.HostConfig.NanoCpus}}')
        if [ "$CPU_LIMIT" -eq 0 ]; then
            echo "❌ FAIL: No CPU limit set"
        else
            CPU_CORES=$(awk "BEGIN {print $CPU_LIMIT / 1000000000}")
            echo "✅ PASS: CPU limit: ${CPU_CORES} cores"
        fi

        # Restart policy
        RESTART_POLICY=$(docker inspect "$container" --format '{{.HostConfig.RestartPolicy.Name}}')
        echo "Restart policy: $RESTART_POLICY"

        echo ""
    done

    echo "========================================="
    echo "Compliance Check Complete"
    echo "========================================="
} > "${EVIDENCE_DIR}/compliance-check.txt"
log "✅ Saved: compliance-check.txt"

# ============================================================================
# Generate Summary Report
# ============================================================================

log "Generating summary report..."

{
    echo "========================================="
    echo "Docker Infrastructure Baseline Snapshot"
    echo "========================================="
    echo ""
    echo "Timestamp: $(date)"
    echo "Evidence ID: EVID-${TIMESTAMP}-005"
    echo "Portfolio Initiative: PORT-2026-010"
    echo "Process: PROC-INFRA-001"
    echo "Control: CTRL-SOP-003"
    echo ""
    echo "========================================="
    echo "Summary Statistics"
    echo "========================================="
    echo ""
    echo "Running Containers: $(docker ps --format '{{.Names}}' | wc -l | tr -d ' ')"
    echo "Total Containers: $(docker ps -a --format '{{.Names}}' | wc -l | tr -d ' ')"
    echo "Networks: $(docker network ls --format '{{.Name}}' | wc -l | tr -d ' ')"
    echo "Volumes: $(docker volume ls --format '{{.Name}}' | wc -l | tr -d ' ')"
    echo "Images: $(docker images --format '{{.Repository}}' | wc -l | tr -d ' ')"
    echo ""
    echo "========================================="
    echo "Running Containers"
    echo "========================================="
    echo ""
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    echo ""
    echo "========================================="
    echo "Evidence Artifacts"
    echo "========================================="
    echo ""
    ls -lh "$EVIDENCE_DIR"
    echo ""
    echo "========================================="
    echo "Snapshot Complete"
    echo "========================================="
} > "${EVIDENCE_DIR}/README.md"
log "✅ Saved: README.md"

# ============================================================================
# Summary
# ============================================================================

log "========================================="
log "Baseline Snapshot Complete"
log "========================================="
log "Evidence Directory: ${EVIDENCE_DIR}"
log "Total Files: $(find "$EVIDENCE_DIR" -type f | wc -l | tr -d ' ')"
log "Total Size: $(du -sh "$EVIDENCE_DIR" | cut -f1)"
log "========================================="

# Display compliance summary
if grep -q "FAIL" "${EVIDENCE_DIR}/compliance-check.txt"; then
    warn "⚠️  Compliance issues detected. Review: ${EVIDENCE_DIR}/compliance-check.txt"
else
    log "✅ All containers pass compliance checks"
fi

exit 0
