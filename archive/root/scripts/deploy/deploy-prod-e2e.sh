#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# End-to-End Production Deployment for odoo-prod-01
# ============================================================================
#
# This script executes the complete deployment on 178.128.112.214:
# 0. SSH connection
# 1. Baseline hardening + Docker + firewall
# 2. Install doctl + fetch Managed Postgres connection
# 3. Clone jgtolentino/odoo-ce + run bootstrap
# 4. Wire Managed Postgres into deploy env
# 5. Deploy stack + verification
#
# Prerequisites:
# - SSH access to root@178.128.112.214
# - DigitalOcean PAT token
# - Managed PostgreSQL database online (ID: 3bbd7e2a-d9ce-4253-a9ae-96ef55e24908)
#
# ============================================================================

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Configuration
DROPLET_IP="178.128.112.214"
DB_ID="3bbd7e2a-d9ce-4253-a9ae-96ef55e24908"
DO_TOKEN="${DIGITALOCEAN_ACCESS_TOKEN:-}"
DOMAIN="${DOMAIN:-erp.insightpulseai.com}"

log_info "============================================================================"
log_info "End-to-End Production Deployment"
log_info "============================================================================"
log_info "Droplet IP: $DROPLET_IP"
log_info "Database ID: $DB_ID"
log_info "Domain: $DOMAIN"
log_info "============================================================================"

# Verify SSH access
log_info "Step 0/5: Verifying SSH access..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new root@"$DROPLET_IP" "echo 'SSH OK'" > /dev/null 2>&1; then
  log_error "Cannot SSH to root@$DROPLET_IP. Verify SSH key is configured."
fi
log_info "✓ SSH access verified"

# ============================================================================
# Step 1: Baseline Hardening + Docker + Firewall
# ============================================================================

log_info "Step 1/5: Baseline hardening + Docker + firewall..."

ssh root@"$DROPLET_IP" bash << 'REMOTE_STEP1'
set -euo pipefail

apt-get update -qq
apt-get install -y -qq \
  git curl ca-certificates ufw fail2ban jq unzip \
  docker.io

systemctl enable --now docker

# Install Docker Compose V2 (standalone)
DOCKER_COMPOSE_VERSION=$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -fsSL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Sanity checks
docker --version
docker-compose --version
ufw status
systemctl is-active docker
REMOTE_STEP1

log_info "✓ Baseline hardening complete"

# ============================================================================
# Step 2: Install doctl + Fetch Managed Postgres Connection
# ============================================================================

log_info "Step 2/5: Installing doctl + fetching Managed Postgres connection..."

if [ -z "$DO_TOKEN" ]; then
  log_error "DIGITALOCEAN_ACCESS_TOKEN not set. Export it first:
  export DIGITALOCEAN_ACCESS_TOKEN='your-token-here'"
fi

ssh root@"$DROPLET_IP" bash << REMOTE_STEP2
set -euo pipefail

# Install doctl
DOCTL_VER="\$(curl -fsSL https://api.github.com/repos/digitalocean/doctl/releases/latest | jq -r .tag_name | sed 's/^v//')"
curl -fsSL "https://github.com/digitalocean/doctl/releases/download/v\${DOCTL_VER}/doctl-\${DOCTL_VER}-linux-amd64.tar.gz" -o /tmp/doctl.tgz
tar -xzf /tmp/doctl.tgz -C /tmp
install -m 0755 /tmp/doctl /usr/local/bin/doctl
doctl version

# Initialize doctl
export DIGITALOCEAN_ACCESS_TOKEN="$DO_TOKEN"
doctl auth init -t "\$DIGITALOCEAN_ACCESS_TOKEN"

# Fetch DB connection URI (no echo to terminal)
mkdir -p /opt/odoo-ce/secrets
chmod 700 /opt/odoo-ce/secrets
doctl databases connection $DB_ID --format URI --no-header > /opt/odoo-ce/secrets/pg_uri.txt
chmod 600 /opt/odoo-ce/secrets/pg_uri.txt

# Verify URI format (redacted display)
python3 - <<'PY'
import re, pathlib
u = pathlib.Path("/opt/odoo-ce/secrets/pg_uri.txt").read_text().strip()
print("OK" if re.match(r"^postgres(ql)?://", u) else "BAD_URI")
PY
REMOTE_STEP2

log_info "✓ doctl installed + Managed Postgres connection secured"

# ============================================================================
# Step 3: Clone jgtolentino/odoo-ce + Run Bootstrap
# ============================================================================

log_info "Step 3/5: Cloning jgtolentino/odoo-ce + running bootstrap..."

ssh root@"$DROPLET_IP" bash << 'REMOTE_STEP3'
set -euo pipefail

mkdir -p /opt/odoo-ce
cd /opt/odoo-ce

# Fresh clone
rm -rf repo
git clone https://github.com/jgtolentino/odoo-ce.git repo
cd repo

# Pin to latest tag (deterministic deploy)
git fetch --tags
LATEST_TAG="$(git tag --sort=-creatordate | head -n1 || true)"
if [ -n "${LATEST_TAG}" ]; then
  echo "Checking out tag: $LATEST_TAG"
  git checkout "$LATEST_TAG"
else
  echo "No tags found, using main branch"
fi

# Run repo bootstrap if present
if [ -f "scripts/deploy/bootstrap_from_tag.sh" ]; then
  echo "Running bootstrap_from_tag.sh..."
  bash scripts/deploy/bootstrap_from_tag.sh
else
  echo "No bootstrap_from_tag.sh found, skipping"
fi
REMOTE_STEP3

log_info "✓ Repository cloned and bootstrapped"

# ============================================================================
# Step 4: Wire Managed Postgres into Deploy Env
# ============================================================================

log_info "Step 4/5: Wiring Managed Postgres into deploy environment..."

ssh root@"$DROPLET_IP" bash << 'REMOTE_STEP4'
set -euo pipefail
cd /opt/odoo-ce/repo

# Ensure deploy env exists
mkdir -p deploy
[ -f deploy/.env ] || cp -n .env.example deploy/.env || true

# Write ODOO_DB_URI entry
export DB_URI="$(cat /opt/odoo-ce/secrets/pg_uri.txt | tr -d '\n')"
python3 - <<'PY'
import pathlib, re, os
p = pathlib.Path("deploy/.env")
txt = p.read_text() if p.exists() else ""
db_uri = os.environ["DB_URI"]
line = f"ODOO_DB_URI={db_uri}\n"
if re.search(r"^ODOO_DB_URI=.*$", txt, flags=re.M):
    txt = re.sub(r"^ODOO_DB_URI=.*$", line.strip(), txt, flags=re.M) + "\n"
else:
    if txt and not txt.endswith("\n"): txt += "\n"
    txt += line
p.write_text(txt)
print("OK: wrote ODOO_DB_URI into deploy/.env")
PY
REMOTE_STEP4

log_info "✓ Managed Postgres connection configured"

# ============================================================================
# Step 5: Deploy Stack + Verification
# ============================================================================

log_info "Step 5/5: Deploying stack + running verification..."

ssh root@"$DROPLET_IP" bash << 'REMOTE_STEP5'
set -euo pipefail
cd /opt/odoo-ce/repo/deploy

echo "Pulling Docker images..."
docker-compose pull

echo "Starting services..."
docker-compose up -d

echo "Waiting 10 seconds for services to initialize..."
sleep 10

echo "Checking service status..."
docker-compose ps

echo ""
echo "Recent Odoo logs:"
docker-compose logs --tail=50 odoo || true

echo ""
echo "Recent Nginx logs:"
docker-compose logs --tail=50 nginx || true

echo ""
echo "Health check (local):"
curl -sS -I http://127.0.0.1/web | head -n 10 || echo "Local health check failed"
REMOTE_STEP5

log_info "✓ Stack deployed"

# ============================================================================
# Final Verification
# ============================================================================

log_info "============================================================================"
log_info "Deployment Complete!"
log_info "============================================================================"
log_info ""
log_info "Next Steps:"
log_info "  1. Update DNS: $DOMAIN → $DROPLET_IP"
log_info "  2. Wait 5 minutes for DNS propagation"
log_info "  3. Verify HTTPS: curl -I https://$DOMAIN/web"
log_info "  4. Access UI: https://$DOMAIN"
log_info ""
log_info "Troubleshooting:"
log_info "  SSH: ssh root@$DROPLET_IP"
log_info "  Logs: cd /opt/odoo-ce/repo/deploy && docker-compose logs -f"
log_info "  Status: cd /opt/odoo-ce/repo/deploy && docker-compose ps"
log_info ""
log_info "Database Connection:"
log_info "  URI stored in: /opt/odoo-ce/secrets/pg_uri.txt (root-only)"
log_info "  Database ID: $DB_ID"
log_info ""
log_info "============================================================================"
