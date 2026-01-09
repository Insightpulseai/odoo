#!/bin/bash
# scripts/odoo_runtime_snapshot.sh
# Basher - Odoo Runtime Snapshot Collector
# Generates a deterministic snapshot of the running environment (Host + Docker + Odoo).

set -u

# --- Configuration ---
SNAPSHOT_ROOT="docs/architecture/runtime_snapshot"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUT_DIR="${SNAPSHOT_ROOT}/${TIMESTAMP}"
PROOFS_DIR="${OUT_DIR}/PROOFS"
INSPECT_DIR="${OUT_DIR}/container_inspects"
SUMMARY_MD="${OUT_DIR}/PROD_RUNTIME_SNAPSHOT.md"
IDENTIFIERS_JSON="${OUT_DIR}/runtime_identifiers.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Setup ---
mkdir -p "$PROOFS_DIR" "$INSPECT_DIR"

log "Starting Snapshot Collection -> $OUT_DIR"

# --- A. Host Layer ---
log "Collecting Host Layer..."
{
    echo "=== Host Info ==="
    uname -a
    echo -e "\n=== OS Release ==="
    cat /etc/os-release
    echo -e "\n=== Uptime ==="
    uptime
    echo -e "\n=== Disk ==="
    df -h
    echo -e "\n=== Memory ==="
    free -h
    echo -e "\n=== Docker Service ==="
    systemctl status docker --no-pager || echo "Systemd not found/docker not strict service"
} > "${PROOFS_DIR}/host_info.txt" 2>&1

{
    echo "=== Ports ==="
    ss -lntup
} > "${PROOFS_DIR}/host_ports.txt" 2>&1

{
    echo "=== Docker Journal (Tail) ==="
    journalctl -u docker --since "24 hours ago" --no-pager | tail -n 200
} > "${PROOFS_DIR}/docker_journal.txt" 2>&1 || echo "No journal access" > "${PROOFS_DIR}/docker_journal.txt"

# --- B. Docker Inventory ---
log "Collecting Docker Inventory..."
docker info > "${PROOFS_DIR}/docker_info.txt" 2>&1
docker ps -a --no-trunc > "${PROOFS_DIR}/docker_ps.txt" 2>&1
docker images --digests > "${PROOFS_DIR}/docker_images.txt" 2>&1
docker network ls > "${PROOFS_DIR}/docker_networks.txt" 2>&1
docker volume ls > "${PROOFS_DIR}/docker_volumes.txt" 2>&1

# Inspect all containers
docker ps -aq | xargs -r docker inspect > "${INSPECT_DIR}/all_containers.json"

# --- C. Compose/Stack Discovery ---
log "Collecting Compose Configs..."
# Try to find standard compose file locations or assume current dir if running from repo
if [ -f "docker-compose.prod.yml" ]; then
    docker compose -f docker-compose.prod.yml config > "${PROOFS_DIR}/docker_compose_config.txt" 2>&1
    # Env file keys only (redact values)
    if [ -f ".env" ]; then
        grep -v '^#' .env | cut -d= -f1 > "${PROOFS_DIR}/env_keys.txt"
    fi
else
    echo "No docker-compose.prod.yml found in current dir" > "${PROOFS_DIR}/docker_compose_config.txt"
fi

# --- D. Reverse Proxy (Nginx) ---
log "Collecting Proxy (Nginx)..."
if systemctl is-active --quiet nginx; then
    {
        echo "=== Nginx Status ==="
        systemctl status nginx --no-pager
        echo -e "\n=== Nginx Config Check ==="
        nginx -t
        echo -e "\n=== Upstreams ==="
        grep -R "upstream" /etc/nginx/ || echo "No direct upstream grep access"
    } > "${PROOFS_DIR}/nginx_info.txt" 2>&1
else
    echo "Nginx systemd service not active" > "${PROOFS_DIR}/nginx_info.txt"
fi

# Curl checks
curl -I -k https://localhost/web/login > "${PROOFS_DIR}/curl_localhost.txt" 2>&1 || true

# --- E. Postgres Layer ---
log "Collecting Postgres Layer..."
# Detect DB container
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E "db|postgres" | head -n 1)

if [ -n "$DB_CONTAINER" ]; then
    log "Found DB Container: $DB_CONTAINER"
    
    # Version
    docker exec "$DB_CONTAINER" psql -U odoo -d odoo -c "SELECT version();" > "${PROOFS_DIR}/pg_version.txt" 2>&1 || true
    
    # DB List & Size
    docker exec "$DB_CONTAINER" psql -U odoo -d odoo -c "\l+" > "${PROOFS_DIR}/pg_databases.txt" 2>&1 || true
    
    # Extensions
    docker exec "$DB_CONTAINER" psql -U odoo -d odoo -c "SELECT * FROM pg_extension;" > "${PROOFS_DIR}/pg_extensions.txt" 2>&1 || true
    
    # Activity Stats
    docker exec "$DB_CONTAINER" psql -U odoo -d odoo -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY 1;" > "${PROOFS_DIR}/pg_activity.txt" 2>&1 || true
else
    echo "No DB Container found" > "${PROOFS_DIR}/pg_error.txt"
fi

# --- F. Odoo Runtime ---
log "Collecting Odoo Runtime..."
ODOO_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E "odoo|ce" | grep -v "db" | head -n 1)

if [ -n "$ODOO_CONTAINER" ]; then
    log "Found Odoo Container: $ODOO_CONTAINER"
    
    # Version (cli)
    docker exec "$ODOO_CONTAINER" odoo --version > "${PROOFS_DIR}/odoo_version.txt" 2>&1 || true
    
    # Conf (Attempt to cat, might need root)
    docker exec "$ODOO_CONTAINER" cat /etc/odoo/odoo.conf | sed 's/password.*/password = [REDACTED]/g' > "${PROOFS_DIR}/odoo_conf.txt" 2>&1 || true
    
    # Installed Modules
    docker exec "$DB_CONTAINER" psql -U odoo -d odoo -c "SELECT name, state, latest_version FROM ir_module_module WHERE state = 'installed' ORDER BY name;" > "${PROOFS_DIR}/odoo_modules_installed.txt" 2>&1 || true
    
    # Logs
    docker logs --tail 200 "$ODOO_CONTAINER" > "${PROOFS_DIR}/odoo_logs_tail.txt" 2>&1
else
    echo "No Odoo Container found" > "${PROOFS_DIR}/odoo_error.txt"
fi


# --- Output Generation (JSON Identifiers) ---
log "Generating Identifiers JSON..."
cat <<EOF > "$IDENTIFIERS_JSON"
{
  "timestamp": "$TIMESTAMP",
  "host": {
    "hostname": "$(hostname)",
    "kernel": "$(uname -r)"
  },
  "docker": {
    "version": "$(docker --version | awk '{print $3}' | tr -d ,)",
    "containers": {
        "odoo": "$ODOO_CONTAINER",
        "db": "$DB_CONTAINER"
    }
  }
}
EOF

# --- Output Generation (Markdown Summary) ---
log "Generating Markdown Summary..."
cat <<EOF > "$SUMMARY_MD"
# Prod Runtime Snapshot ($TIMESTAMP)

## Executive Summary
- **Host**: $(hostname) (\`$(uname -r)\`)
- **Time**: $(date)
- **Odoo Container**: \`$ODOO_CONTAINER\`
- **DB Container**: \`$DB_CONTAINER\`

## Evidence Index
- [Host Info](PROOFS/host_info.txt)
- [Docker PS](PROOFS/docker_ps.txt)
- [Odoo Logs](PROOFS/odoo_logs_tail.txt)
- [Postgres DBs](PROOFS/pg_databases.txt)
- [Installed Modules](PROOFS/odoo_modules_installed.txt)

## Key Findings (Auto-Generated)
- **Active Ports**: Check \`PROOFS/host_ports.txt\`
- **Database Size**: Check \`PROOFS/pg_databases.txt\`
- **Extensions**: Check \`PROOFS/pg_extensions.txt\`

EOF

log "Snapshot Complete: $OUT_DIR"
echo "Run: git add $OUT_DIR && git commit -m 'chore: runtime snapshot' && git push"
