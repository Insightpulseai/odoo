#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# DigitalOcean Production Odoo 18 CE Bootstrap
# ============================================================================
#
# This script automates the complete production deployment of Odoo 18 CE
# on a fresh DigitalOcean droplet following CloudPepper best practices.
#
# Prerequisites:
# - Fresh Ubuntu 24.04 LTS droplet (s-4vcpu-8gb recommended)
# - Root SSH access
# - DO Managed PostgreSQL database (or local PostgreSQL)
# - DO Spaces bucket for backups
#
# Usage:
#   # On fresh droplet as root:
#   curl -fsSL https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/scripts/deploy/do-bootstrap-odoo-prod.sh | bash
#
#   # Or with custom parameters:
#   export DOMAIN="erp.insightpulseai.com"
#   export EMAIL="admin@insightpulseai.com"
#   export DB_HOST="odoo-db-do-user-12345-0.db.ondigitalocean.com"
#   export DB_PORT="25060"
#   bash do-bootstrap-odoo-prod.sh
#
# ============================================================================

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ============================================================================
# Configuration (Override via environment variables)
# ============================================================================

DOMAIN="${DOMAIN:-erp.insightpulseai.com}"
EMAIL="${EMAIL:-admin@insightpulseai.com}"

# Database (DO Managed PostgreSQL or local)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-odoo_prod}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"

# Odoo configuration
ODOO_VERSION="${ODOO_VERSION:-18.0}"
ODOO_USER="${ODOO_USER:-odoo}"
ODOO_HOME="${ODOO_HOME:-/opt/odoo}"
ODOO_CONFIG="${ODOO_CONFIG:-/etc/odoo/odoo.conf}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(openssl rand -base64 32)}"

# System configuration
WORKERS="${WORKERS:-7}"  # (4 CPU × 2) + 1 - 2 cron = 7
MAX_CRON_THREADS="${MAX_CRON_THREADS:-2}"

# Repository
GIT_REPO="${GIT_REPO:-https://github.com/jgtolentino/odoo-ce.git}"
GIT_REF="${GIT_REF:-main}"

# Backup configuration
S3_BUCKET="${S3_BUCKET:-insightpulse-backups}"
S3_ENDPOINT="${S3_ENDPOINT:-sgp1.digitaloceanspaces.com}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

log_info "============================================================================"
log_info "DigitalOcean Production Odoo 18 CE Bootstrap"
log_info "============================================================================"
log_info "Domain: $DOMAIN"
log_info "Database Host: $DB_HOST"
log_info "Database Port: $DB_PORT"
log_info "Workers: $WORKERS"
log_info "Git Ref: $GIT_REF"
log_info "============================================================================"

# ============================================================================
# Step 1: System Dependencies
# ============================================================================

log_info "Step 1/12: Installing system dependencies..."

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  git \
  postgresql-client \
  python3 \
  python3-pip \
  python3-dev \
  python3-venv \
  build-essential \
  libxml2-dev \
  libxslt1-dev \
  libldap2-dev \
  libsasl2-dev \
  libjpeg-dev \
  libpq-dev \
  libffi-dev \
  libssl-dev \
  node-less \
  npm \
  xfonts-75dpi \
  xfonts-base \
  fontconfig \
  wkhtmltopdf \
  nginx \
  certbot \
  python3-certbot-nginx \
  ufw \
  s3cmd \
  > /dev/null 2>&1

log_info "✓ System dependencies installed"

# ============================================================================
# Step 2: Firewall Configuration
# ============================================================================

log_info "Step 2/12: Configuring firewall..."

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Allow PostgreSQL from DO Managed DB (if external)
if [ "$DB_HOST" != "localhost" ]; then
  log_info "External PostgreSQL detected - allowing inbound connection"
  # DO Managed DBs use VPC - no firewall rule needed
fi

ufw --force enable

log_info "✓ Firewall configured (ports: 22, 80, 443)"

# ============================================================================
# Step 3: PostgreSQL Setup (Local or Managed)
# ============================================================================

log_info "Step 3/12: Setting up PostgreSQL..."

if [ "$DB_HOST" = "localhost" ]; then
  log_info "Installing local PostgreSQL 16..."

  # Add PostgreSQL APT repository
  curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

  apt-get update -qq
  apt-get install -y -qq postgresql-16 postgresql-contrib-16

  # Configure PostgreSQL
  systemctl start postgresql
  systemctl enable postgresql

  # Create database and user
  sudo -u postgres psql << EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

  log_info "✓ Local PostgreSQL 16 installed and configured"
else
  log_info "Using DO Managed PostgreSQL at $DB_HOST:$DB_PORT"

  # Test connection
  PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1" > /dev/null 2>&1 || \
    log_error "Cannot connect to managed PostgreSQL. Check credentials and VPC configuration."

  log_info "✓ PostgreSQL connection verified"
fi

# ============================================================================
# Step 4: Create Odoo System User
# ============================================================================

log_info "Step 4/12: Creating Odoo system user..."

if ! id -u "$ODOO_USER" > /dev/null 2>&1; then
  useradd -m -d "$ODOO_HOME" -U -r -s /bin/bash "$ODOO_USER"
  log_info "✓ User '$ODOO_USER' created"
else
  log_warn "User '$ODOO_USER' already exists"
fi

# ============================================================================
# Step 5: Clone Repository
# ============================================================================

log_info "Step 5/12: Cloning Odoo CE repository..."

if [ ! -d "$ODOO_HOME/.git" ]; then
  sudo -u "$ODOO_USER" git clone "$GIT_REPO" "$ODOO_HOME"
  cd "$ODOO_HOME"
  sudo -u "$ODOO_USER" git checkout "$GIT_REF"
  sudo -u "$ODOO_USER" git submodule update --init --recursive
  log_info "✓ Repository cloned at $GIT_REF"
else
  log_warn "Repository already exists at $ODOO_HOME"
  cd "$ODOO_HOME"
  sudo -u "$ODOO_USER" git fetch origin
  sudo -u "$ODOO_USER" git checkout "$GIT_REF"
  sudo -u "$ODOO_USER" git pull origin "$GIT_REF"
  sudo -u "$ODOO_USER" git submodule update --init --recursive
  log_info "✓ Repository updated to $GIT_REF"
fi

# ============================================================================
# Step 6: Python Dependencies
# ============================================================================

log_info "Step 6/12: Installing Python dependencies..."

# Create virtual environment
if [ ! -d "$ODOO_HOME/venv" ]; then
  sudo -u "$ODOO_USER" python3 -m venv "$ODOO_HOME/venv"
fi

# Install dependencies
sudo -u "$ODOO_USER" bash << 'EOF'
source $ODOO_HOME/venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r $ODOO_HOME/requirements.txt
EOF

log_info "✓ Python dependencies installed"

# ============================================================================
# Step 7: Create Odoo Configuration
# ============================================================================

log_info "Step 7/12: Creating Odoo configuration..."

mkdir -p /etc/odoo
mkdir -p /var/lib/odoo/{filestore,sessions}
mkdir -p /var/log/odoo
chown -R "$ODOO_USER":"$ODOO_USER" /var/lib/odoo
chown -R "$ODOO_USER":"$ODOO_USER" /var/log/odoo

cat > "$ODOO_CONFIG" << EOF
[options]
# Database
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_name = $DB_NAME
db_filter = ^$DB_NAME$
list_db = False

# Paths
addons_path = $ODOO_HOME/odoo/addons,$ODOO_HOME/addons/oca,$ODOO_HOME/addons/ipai
data_dir = /var/lib/odoo/filestore

# Workers (for 4 vCPU / 8GB)
workers = $WORKERS
max_cron_threads = $MAX_CRON_THREADS
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
limit_request = 8192

# Security
admin_passwd = $ADMIN_PASSWORD
proxy_mode = True

# Logging
logfile = /var/log/odoo/odoo.log
log_level = info
log_handler = :INFO

# Longpolling (websocket)
gevent_port = 8072

# Performance
unaccent = True
EOF

chown "$ODOO_USER":"$ODOO_USER" "$ODOO_CONFIG"
chmod 640 "$ODOO_CONFIG"

log_info "✓ Odoo configuration created at $ODOO_CONFIG"

# ============================================================================
# Step 8: Create Systemd Service
# ============================================================================

log_info "Step 8/12: Creating systemd service..."

cat > /etc/systemd/system/odoo.service << EOF
[Unit]
Description=Odoo 18 CE
Documentation=https://www.odoo.com/documentation/18.0
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=$ODOO_USER
Group=$ODOO_USER
ExecStart=$ODOO_HOME/scripts/odoo.sh -c $ODOO_CONFIG
WorkingDirectory=$ODOO_HOME
StandardOutput=journal+console
StandardError=journal+console
Restart=on-failure
RestartSec=10s

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/odoo /var/log/odoo

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable odoo
systemctl start odoo

# Wait for Odoo to start
log_info "Waiting 30 seconds for Odoo to initialize..."
sleep 30

if systemctl is-active --quiet odoo; then
  log_info "✓ Odoo service started successfully"
else
  log_error "Odoo service failed to start. Check logs: journalctl -u odoo -n 50"
fi

# ============================================================================
# Step 9: Configure Nginx
# ============================================================================

log_info "Step 9/12: Configuring Nginx..."

cat > /etc/nginx/sites-available/odoo << 'NGINX_EOF'
upstream odoo {
    server 127.0.0.1:8069 weight=1 fail_timeout=0;
}

upstream odoo-chat {
    server 127.0.0.1:8072 weight=1 fail_timeout=0;
}

server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    # Let's Encrypt webroot
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    # SSL certificates (will be created by certbot)
    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
    ssl_session_timeout 30m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logs
    access_log /var/log/nginx/odoo-access.log;
    error_log /var/log/nginx/odoo-error.log;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Gzip
    gzip on;
    gzip_types text/css text/plain text/xml application/xml application/javascript application/json;

    # Longpolling (websocket)
    location /websocket {
        proxy_pass http://odoo-chat;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main Odoo
    location / {
        proxy_pass http://odoo;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload limit (100MB)
        client_max_body_size 100M;
    }

    # Static files caching
    location ~* /web/static/ {
        proxy_pass http://odoo;
        proxy_cache_valid 200 90m;
        expires 90d;
    }

    # Block database manager
    location ~* ^/web/database/ {
        deny all;
        return 404;
    }
}
NGINX_EOF

# Replace domain placeholder
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/odoo

# Enable site
ln -sf /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t || log_error "Nginx configuration test failed"

systemctl reload nginx

log_info "✓ Nginx configured for $DOMAIN"

# ============================================================================
# Step 10: Configure SSL with Let's Encrypt
# ============================================================================

log_info "Step 10/12: Configuring SSL with Let's Encrypt..."

# Create webroot directory
mkdir -p /var/www/html

# Obtain certificate
certbot --nginx \
  -d "$DOMAIN" \
  --non-interactive \
  --agree-tos \
  -m "$EMAIL" \
  --redirect \
  || log_warn "Certbot failed - continuing without SSL. Run manually: certbot --nginx -d $DOMAIN"

# Auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

log_info "✓ SSL configured (or skipped if DNS not ready)"

# ============================================================================
# Step 11: Configure Backups
# ============================================================================

log_info "Step 11/12: Configuring backups..."

# Create backup directory
mkdir -p /var/lib/odoo/backups
chown "$ODOO_USER":"$ODOO_USER" /var/lib/odoo/backups

# Create backup script
cat > /opt/odoo/scripts/backup.sh << 'BACKUP_EOF'
#!/bin/bash
set -e

DB_NAME="DB_NAME_PLACEHOLDER"
BACKUP_DIR="/var/lib/odoo/backups"
FILESTORE_DIR="/var/lib/odoo/filestore/$DB_NAME"
S3_BUCKET="S3_BUCKET_PLACEHOLDER"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Database backup
echo "[$(date)] Starting database backup..."
PGPASSWORD="DB_PASSWORD_PLACEHOLDER" pg_dump \
  -h DB_HOST_PLACEHOLDER \
  -p DB_PORT_PLACEHOLDER \
  -U DB_USER_PLACEHOLDER \
  -Fc "$DB_NAME" > "$BACKUP_DIR/${DB_NAME}_${DATE}.dump"
gzip "$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# 2. Filestore backup
echo "[$(date)] Starting filestore backup..."
if [ -d "$FILESTORE_DIR" ]; then
  tar -czf "$BACKUP_DIR/filestore_${DATE}.tar.gz" -C "$FILESTORE_DIR" .
fi

# 3. Upload to S3/Spaces
if command -v s3cmd &> /dev/null && [ -n "$S3_BUCKET" ]; then
  echo "[$(date)] Uploading to S3..."
  s3cmd put "$BACKUP_DIR/${DB_NAME}_${DATE}.dump.gz" "s3://$S3_BUCKET/db/"
  s3cmd put "$BACKUP_DIR/filestore_${DATE}.tar.gz" "s3://$S3_BUCKET/filestore/" || true
fi

# 4. Cleanup old local backups (keep 7 days)
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "[$(date)] Backup completed successfully."
BACKUP_EOF

# Replace placeholders
sed -i "s/DB_NAME_PLACEHOLDER/$DB_NAME/g" /opt/odoo/scripts/backup.sh
sed -i "s/DB_HOST_PLACEHOLDER/$DB_HOST/g" /opt/odoo/scripts/backup.sh
sed -i "s/DB_PORT_PLACEHOLDER/$DB_PORT/g" /opt/odoo/scripts/backup.sh
sed -i "s/DB_USER_PLACEHOLDER/$DB_USER/g" /opt/odoo/scripts/backup.sh
sed -i "s/DB_PASSWORD_PLACEHOLDER/$DB_PASSWORD/g" /opt/odoo/scripts/backup.sh
sed -i "s/S3_BUCKET_PLACEHOLDER/$S3_BUCKET/g" /opt/odoo/scripts/backup.sh

chmod +x /opt/odoo/scripts/backup.sh
chown "$ODOO_USER":"$ODOO_USER" /opt/odoo/scripts/backup.sh

# Create cron job (daily at 2 AM)
cat > /etc/cron.d/odoo-backup << EOF
0 2 * * * $ODOO_USER /opt/odoo/scripts/backup.sh >> /var/log/odoo/backup.log 2>&1
EOF

log_info "✓ Backup script configured (runs daily at 2 AM)"

# ============================================================================
# Step 12: Final Health Check
# ============================================================================

log_info "Step 12/12: Running health checks..."

# Check Odoo service
if systemctl is-active --quiet odoo; then
  log_info "✓ Odoo service: running"
else
  log_error "✗ Odoo service: not running"
fi

# Check Nginx
if systemctl is-active --quiet nginx; then
  log_info "✓ Nginx service: running"
else
  log_error "✗ Nginx service: not running"
fi

# Check HTTP endpoint
sleep 5
if curl -f http://localhost:8069/web/health > /dev/null 2>&1; then
  log_info "✓ Odoo health endpoint: OK"
else
  log_warn "✗ Odoo health endpoint: failed (may need more time to initialize)"
fi

# ============================================================================
# Summary
# ============================================================================

log_info "============================================================================"
log_info "Odoo 18 CE Production Deployment Complete!"
log_info "============================================================================"
log_info ""
log_info "Configuration:"
log_info "  Domain: https://$DOMAIN"
log_info "  Database: $DB_NAME ($DB_HOST:$DB_PORT)"
log_info "  Odoo Home: $ODOO_HOME"
log_info "  Config: $ODOO_CONFIG"
log_info ""
log_info "Credentials (SAVE THESE SECURELY):"
log_info "  Database User: $DB_USER"
log_info "  Database Password: $DB_PASSWORD"
log_info "  Admin Password: $ADMIN_PASSWORD"
log_info ""
log_info "Next Steps:"
log_info "  1. Access Odoo: https://$DOMAIN"
log_info "  2. Create database via UI (if not using managed DB)"
log_info "  3. Install IPAI modules: ipai_health, ipai_workspace_core"
log_info "  4. Configure S3/Spaces credentials for backups:"
log_info "     s3cmd --configure"
log_info "  5. Test backup: /opt/odoo/scripts/backup.sh"
log_info ""
log_info "Useful Commands:"
log_info "  systemctl status odoo"
log_info "  systemctl restart odoo"
log_info "  journalctl -u odoo -f"
log_info "  tail -f /var/log/odoo/odoo.log"
log_info ""
log_info "Documentation:"
log_info "  https://github.com/jgtolentino/odoo-ce/blob/main/docs/ODOO_DEPLOYMENT_BEST_PRACTICES.md"
log_info "============================================================================"

# Save credentials to file (secure)
cat > /root/odoo-credentials.txt << EOF
Odoo Production Credentials
Generated: $(date)

Domain: https://$DOMAIN
Database: $DB_NAME
Database Host: $DB_HOST
Database Port: $DB_PORT
Database User: $DB_USER
Database Password: $DB_PASSWORD
Admin Password: $ADMIN_PASSWORD

Keep this file secure and delete after saving to password manager.
EOF

chmod 600 /root/odoo-credentials.txt

log_info "Credentials saved to: /root/odoo-credentials.txt"
log_info "Bootstrap complete!"
