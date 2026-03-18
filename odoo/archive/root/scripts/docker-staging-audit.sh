#!/usr/bin/env bash
# scripts/docker-staging-audit.sh
#
# Audit Docker on staging droplet (178.128.112.214) against SSOT allow-lists.
# Non-destructive: this script only prints findings and logs them.
# NEVER performs docker rm/rmi operations.

set -euo pipefail

# --- Config: must mirror infra/docker/DOCKER_STAGING_SSOT.yaml ---

SSOT_FILE="${SSOT_FILE:-infra/docker/DOCKER_STAGING_SSOT.yaml}"
ENV="staging"
HOST="178.128.112.214"

ALLOWED_CONTAINERS=(
  "odoo-staging"
  "odoo-staging-db"
  # Future: superset-staging, n8n-staging, mailpit-staging
)

ALLOWED_VOLUMES=(
  "odoo-staging-db-data"
  "odoo-staging-filestore"
  # Future: superset-staging-data, n8n-staging-data
)

# For images we match by repository prefix (not full tag)
ALLOWED_IMAGE_PREFIXES=(
  "odoo:18.0"
  "postgres:16-alpine"
  # Future: apache/superset, n8nio/n8n
)

# CRITICAL: Never touch these (production protection)
PROTECTED_PREFIXES=(
  "prod-"
  "stable-"
  "ipai-"
  "odoo-erp-prod"
  "odoo-db-sgp1"
)

# Safe to delete patterns
SAFE_TO_DELETE_PATTERNS=(
  "test-"
  "tmp-"
  "experiment-"
  "docker-extension"
  "mcp/"
)

LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/docker_staging_audit_log.jsonl"

mkdir -p "${LOG_DIR}"

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

contains() {
  local needle="$1"; shift
  local x
  for x in "$@"; do
    if [[ "$x" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

prefix_allowed() {
  local repo="$1"
  local p
  for p in "${ALLOWED_IMAGE_PREFIXES[@]}"; do
    if [[ "$repo" == "$p" ]] || [[ "$repo" == "$p:"* ]] || [[ "$repo" == "$p/"* ]]; then
      return 0
    fi
  done
  return 1
}

is_protected() {
  local name="$1"
  local p
  for p in "${PROTECTED_PREFIXES[@]}"; do
    if [[ "$name" == "$p"* ]]; then
      return 0
    fi
  done
  return 1
}

is_safe_to_delete() {
  local name="$1"
  local p
  for p in "${SAFE_TO_DELETE_PATTERNS[@]}"; do
    if [[ "$name" == *"$p"* ]]; then
      return 0
    fi
  done
  return 1
}

echo "=== Docker Staging Audit ==="
echo "Host: $(hostname)"
echo "IP: ${HOST}"
echo "Environment: ${ENV}"
echo "Time: $(timestamp)"
echo "SSOT: ${SSOT_FILE}"
echo

# --- Containers ---

echo "[1/4] Containers"
mapfile -t containers < <(docker ps -a --format '{{.Names}}')

expected_containers=()
extra_containers=()
protected_containers=()
safe_to_delete_containers=()

for c in "${containers[@]}"; do
  if contains "$c" "${ALLOWED_CONTAINERS[@]}"; then
    printf "  ✔ expected container: %s\n" "$c"
    expected_containers+=("$c")
  elif is_protected "$c"; then
    printf "  🛡 protected container (NEVER touch): %s\n" "$c"
    protected_containers+=("$c")
  elif is_safe_to_delete "$c"; then
    printf "  🗑 safe to delete: %s\n" "$c"
    safe_to_delete_containers+=("$c")
  else
    printf "  ⚠ extra container (unknown): %s\n" "$c"
    extra_containers+=("$c")
  fi
done

echo

# --- Images ---

echo "[2/4] Images"
mapfile -t images_raw < <(docker images --format '{{.Repository}}:{{.Tag}}')

expected_images=()
extra_images=()
protected_images=()
safe_to_delete_images=()

for img in "${images_raw[@]}"; do
  repo="${img%%:*}"

  if prefix_allowed "$img"; then
    printf "  ✔ expected image: %s\n" "$img"
    expected_images+=("$img")
  elif is_protected "$img"; then
    printf "  🛡 protected image (NEVER touch): %s\n" "$img"
    protected_images+=("$img")
  elif is_safe_to_delete "$img"; then
    printf "  🗑 safe to delete: %s\n" "$img"
    safe_to_delete_images+=("$img")
  else
    printf "  ⚠ extra image (unknown): %s\n" "$img"
    extra_images+=("$img")
  fi
done

echo

# --- Volumes ---

echo "[3/4] Volumes"
mapfile -t volumes < <(docker volume ls --format '{{.Name}}')

expected_volumes=()
extra_volumes=()
protected_volumes=()
safe_to_delete_volumes=()

for v in "${volumes[@]}"; do
  if contains "$v" "${ALLOWED_VOLUMES[@]}"; then
    printf "  ✔ expected volume: %s\n" "$v"
    expected_volumes+=("$v")
  elif is_protected "$v"; then
    printf "  🛡 protected volume (NEVER touch): %s\n" "$v"
    protected_volumes+=("$v")
  elif is_safe_to_delete "$v"; then
    printf "  🗑 safe to delete: %s\n" "$v"
    safe_to_delete_volumes+=("$v")
  else
    printf "  ⚠ extra volume (unknown): %s\n" "$v"
    extra_volumes+=("$v")
  fi
done

echo

# --- Networks ---

echo "[4/4] Networks"
mapfile -t networks < <(docker network ls --format '{{.Name}}' | grep -v -E '^(bridge|host|none)$')

for n in "${networks[@]}"; do
  if [[ "$n" == *"staging"* ]]; then
    printf "  ✔ staging network: %s\n" "$n"
  elif is_protected "$n"; then
    printf "  🛡 protected network: %s\n" "$n"
  else
    printf "  ℹ other network: %s\n" "$n"
  fi
done

echo
echo "=== Summary ==="
echo "Expected containers:      ${#expected_containers[@]}"
echo "Extra containers:         ${#extra_containers[@]}"
echo "Protected containers:     ${#protected_containers[@]}"
echo "Safe to delete:           ${#safe_to_delete_containers[@]}"
echo
echo "Expected images:          ${#expected_images[@]}"
echo "Extra images:             ${#extra_images[@]}"
echo "Protected images:         ${#protected_images[@]}"
echo "Safe to delete:           ${#safe_to_delete_images[@]}"
echo
echo "Expected volumes:         ${#expected_volumes[@]}"
echo "Extra volumes:            ${#extra_volumes[@]}"
echo "Protected volumes:        ${#protected_volumes[@]}"
echo "Safe to delete:           ${#safe_to_delete_volumes[@]}"
echo

# --- JSONL log ---

jq_payload=$(
  jq -n \
    --arg time "$(timestamp)" \
    --arg host "$(hostname)" \
    --arg ip "${HOST}" \
    --arg env "${ENV}" \
    --argjson containers_expected     "$(printf '%s\n' "${expected_containers[@]:-}" | jq -R . | jq -s .)" \
    --argjson containers_extra        "$(printf '%s\n' "${extra_containers[@]:-}" | jq -R . | jq -s .)" \
    --argjson containers_protected    "$(printf '%s\n' "${protected_containers[@]:-}" | jq -R . | jq -s .)" \
    --argjson containers_safe_delete  "$(printf '%s\n' "${safe_to_delete_containers[@]:-}" | jq -R . | jq -s .)" \
    --argjson images_expected         "$(printf '%s\n' "${expected_images[@]:-}" | jq -R . | jq -s .)" \
    --argjson images_extra            "$(printf '%s\n' "${extra_images[@]:-}" | jq -R . | jq -s .)" \
    --argjson images_protected        "$(printf '%s\n' "${protected_images[@]:-}" | jq -R . | jq -s .)" \
    --argjson images_safe_delete      "$(printf '%s\n' "${safe_to_delete_images[@]:-}" | jq -R . | jq -s .)" \
    --argjson volumes_expected        "$(printf '%s\n' "${expected_volumes[@]:-}" | jq -R . | jq -s .)" \
    --argjson volumes_extra           "$(printf '%s\n' "${extra_volumes[@]:-}" | jq -R . | jq -s .)" \
    '{
      timestamp: $time,
      host: $host,
      ip: $ip,
      env: $env,
      containers_expected: $containers_expected,
      containers_extra: $containers_extra,
      containers_protected: $containers_protected,
      containers_safe_delete: $containers_safe_delete,
      images_expected: $images_expected,
      images_extra: $images_extra,
      images_protected: $images_protected,
      images_safe_delete: $images_safe_delete,
      volumes_expected: $volumes_expected,
      volumes_extra: $volumes_extra
    }'
)

echo "${jq_payload}" >> "${LOG_FILE}"

echo "Audit log appended to ${LOG_FILE}"
echo "Non-destructive audit complete."
echo
echo "⚠️  REMINDER: This script is READ-ONLY. To clean up safe-to-delete resources,"
echo "    review docs/runbooks/DOCKER_STAGING_CLEANUP.md and run cleanup commands manually."
