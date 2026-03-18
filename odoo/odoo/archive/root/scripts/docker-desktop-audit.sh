#!/usr/bin/env bash
# scripts/docker-desktop-audit.sh
#
# Audit local Docker Desktop against the SSOT allow-lists.
# Non-destructive: this script only prints findings and logs them.

set -euo pipefail

# --- Config: must mirror infra/docker/DOCKER_DESKTOP_SSOT.yaml ---

ALLOWED_CONTAINERS=(
  "odoo-dev"
  "odoo-dev-db"
  "odoo-mailpit"
  "odoo-pgadmin"
)

ALLOWED_VOLUMES=(
  "odoo-dev-db-data"
  "odoo-dev-filestore"
)

# For images we match by repository prefix (not full tag)
ALLOWED_IMAGE_PREFIXES=(
  "odoo"
  "postgres"
  "axllent/mailpit"
  "dpage/pgadmin4"
)

LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/docker_audit_log.jsonl"

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

echo "=== Docker Desktop Audit ==="
echo "Host: $(hostname)"
echo "Time: $(timestamp)"
echo

# --- Containers ---

echo "[1/3] Containers"
mapfile -t containers < <(docker ps -a --format '{{.Names}}')

extra_containers=()

for c in "${containers[@]}"; do
  if contains "$c" "${ALLOWED_CONTAINERS[@]}"; then
    printf "  ✔ expected container: %s\n" "$c"
  else
    printf "  ⚠ extra container: %s\n" "$c"
    extra_containers+=("$c")
  fi
done

echo

# --- Images ---

echo "[2/3] Images"
mapfile -t images_raw < <(docker images --format '{{.Repository}}:{{.Tag}}')

extra_images=()

for img in "${images_raw[@]}"; do
  repo="${img%%:*}"
  if prefix_allowed "$repo"; then
    printf "  ✔ expected image: %s\n" "$img"
  else
    printf "  ⚠ extra image: %s\n" "$img"
    extra_images+=("$img")
  fi
done

echo

# --- Volumes ---

echo "[3/3] Volumes"
mapfile -t volumes < <(docker volume ls --format '{{.Name}}')

extra_volumes=()

for v in "${volumes[@]}"; do
  if contains "$v" "${ALLOWED_VOLUMES[@]}"; then
    printf "  ✔ expected volume: %s\n" "$v"
  else
    printf "  ⚠ extra volume: %s\n" "$v"
    extra_volumes+=("$v")
  fi
done

echo
echo "=== Summary ==="
echo "Extra containers: ${#extra_containers[@]}"
echo "Extra images:     ${#extra_images[@]}"
echo "Extra volumes:    ${#extra_volumes[@]}"
echo

# --- JSONL log ---

jq_payload=$(
  jq -n \
    --arg time "$(timestamp)" \
    --arg host "$(hostname)" \
    --argjson containers_expected "$(printf '%s\n' "${ALLOWED_CONTAINERS[@]}" | jq -R . | jq -s .)" \
    --argjson containers_extra     "$(printf '%s\n' "${extra_containers[@]:-}" | jq -R . | jq -s .)" \
    --argjson images_extra         "$(printf '%s\n' "${extra_images[@]:-}" | jq -R . | jq -s .)" \
    --argjson volumes_expected     "$(printf '%s\n' "${ALLOWED_VOLUMES[@]}" | jq -R . | jq -s .)" \
    --argjson volumes_extra        "$(printf '%s\n' "${extra_volumes[@]:-}" | jq -R . | jq -s .)" \
    '{
      timestamp: $time,
      host: $host,
      containers_expected: $containers_expected,
      containers_extra: $containers_extra,
      images_extra: $images_extra,
      volumes_expected: $volumes_expected,
      volumes_extra: $volumes_extra
    }'
)

echo "${jq_payload}" >> "${LOG_FILE}"

echo "Audit log appended to ${LOG_FILE}"
echo "Non-destructive audit complete."
