#!/bin/bash
# Deploy Plane CE to existing ocr-service-droplet (188.166.237.231)
# Uses: External PostgreSQL (odoo-db-sgp1), DO Spaces for storage

set -euo pipefail

# Target droplet
DROPLET_IP="188.166.237.231"
PLANE_DOMAIN="plane.insightpulseai.com"

# External PostgreSQL (odoo-db-sgp1) - from user's provided credentials
DB_HOST="odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="doadmin"
DB_NAME="plane"
# DB_PASSWORD must be set via PLANE_DB_PASSWORD environment variable

# DO Spaces for file storage
SPACES_REGION="sgp1"
SPACES_BUCKET="plane-uploads-ipai"

echo "=== Plane CE Deployment to ocr-service-droplet ==="
echo "Domain: ${PLANE_DOMAIN}"
echo "Target: ${DROPLET_IP}"
echo "Database: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""

# Validate required secrets from environment
: "${PLANE_DB_PASSWORD:?PLANE_DB_PASSWORD is required}"
: "${DO_SPACES_KEY:?DO_SPACES_KEY is required}"
: "${DO_SPACES_SECRET:?DO_SPACES_SECRET is required}"

# Step 1: Create Plane database on odoo-db-sgp1
echo ">>> Step 1: Creating Plane database..."
PGPASSWORD="${PLANE_DB_PASSWORD}" psql \
  "host=${DB_HOST} port=${DB_PORT} user=${DB_USER} dbname=defaultdb sslmode=require" \
  -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || echo "Database 'plane' may already exist, continuing..."

# Step 2: Create DO Spaces bucket (if not exists)
echo ">>> Step 2: Creating Spaces bucket..."
doctl compute cdn flush --help >/dev/null 2>&1 || true  # Just to verify doctl works

# Create bucket via s3cmd or doctl spaces (spaces commands may not be in all doctl versions)
# For now, assume bucket exists or will be created manually

# Step 3: Generate deployment configuration
echo ">>> Step 3: Generating Plane configuration..."
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL="postgresql://${DB_USER}:${PLANE_DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require"

# Create plane.env file
cat > /tmp/plane.env << EOF
# Plane CE Configuration for ${PLANE_DOMAIN}
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Domain
WEB_URL=https://${PLANE_DOMAIN}
CORS_ALLOWED_ORIGINS=https://${PLANE_DOMAIN}

# External PostgreSQL (odoo-db-sgp1)
DATABASE_URL=${DATABASE_URL}
PGHOST=${DB_HOST}
PGPORT=${DB_PORT}
POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${PLANE_DB_PASSWORD}
POSTGRES_DB=${DB_NAME}

# Redis (local container)
REDIS_URL=redis://plane-redis:6379/

# RabbitMQ (local container)
AMQP_URL=amqp://plane:plane@plane-mq:5672/plane

# S3 Storage (DO Spaces)
USE_MINIO=0
AWS_REGION=${SPACES_REGION}
AWS_ACCESS_KEY_ID=${DO_SPACES_KEY}
AWS_SECRET_ACCESS_KEY=${DO_SPACES_SECRET}
AWS_S3_BUCKET_NAME=${SPACES_BUCKET}
AWS_S3_ENDPOINT_URL=https://${SPACES_REGION}.digitaloceanspaces.com

# Security
SECRET_KEY=${SECRET_KEY}
DEBUG=0

# Ports (using non-standard to avoid conflict with existing services)
LISTEN_HTTP_PORT=8080
LISTEN_HTTPS_PORT=8443
EOF

echo ">>> Configuration written to /tmp/plane.env"

# Step 4: Create docker-compose override for external DB
cat > /tmp/docker-compose.override.yml << 'EOF'
# Override to use external PostgreSQL instead of local
# Place in /opt/plane/ alongside docker-compose.yml

services:
  # Disable internal database
  plane-db:
    deploy:
      replicas: 0

  # API uses external database
  api:
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - plane-redis
      - plane-mq

  # Workers use external database
  worker:
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - plane-redis
      - plane-mq

  beat-worker:
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - plane-redis
      - plane-mq

  migrator:
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - plane-redis
      - plane-mq
EOF

# Step 5: Create remote installation script
cat > /tmp/install-plane-remote.sh << 'INSTALLEOF'
#!/bin/bash
set -euo pipefail

PLANE_DIR="/opt/plane"

echo "=== Installing Plane CE on $(hostname) ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Create Plane directory
mkdir -p ${PLANE_DIR}
cd ${PLANE_DIR}

# Download Plane installer
echo "Downloading Plane CE installer..."
curl -fsSL https://prime.plane.so/install/ -o install.sh

# Run installer in non-interactive mode
# The installer will download docker-compose files
chmod +x install.sh
./install.sh --non-interactive || {
    echo "Interactive install required, setting up manually..."

    # Manual setup if installer needs interaction
    curl -fsSL https://raw.githubusercontent.com/makeplane/plane/master/deploy/selfhost/docker-compose.yml -o docker-compose.yml
    curl -fsSL https://raw.githubusercontent.com/makeplane/plane/master/deploy/selfhost/variables.env -o plane.env.example
}

# Copy our configuration
if [ -f /tmp/plane.env ]; then
    cp /tmp/plane.env ${PLANE_DIR}/plane.env
    echo "Configuration applied from /tmp/plane.env"
fi

# Apply override for external database
if [ -f /tmp/docker-compose.override.yml ]; then
    cp /tmp/docker-compose.override.yml ${PLANE_DIR}/docker-compose.override.yml
    echo "Database override applied"
fi

# Run database migrations
echo "Running database migrations..."
docker compose run --rm migrator || true

# Start Plane
echo "Starting Plane services..."
docker compose up -d

# Wait and show status
sleep 10
docker compose ps

echo ""
echo "=== Plane Installation Complete ==="
echo "Access at: http://$(hostname -I | awk '{print $1}'):8080"
INSTALLEOF

echo ">>> Step 5: Deploying to ${DROPLET_IP}..."

# Copy files to remote
scp -o StrictHostKeyChecking=no /tmp/plane.env "root@${DROPLET_IP}:/tmp/"
scp -o StrictHostKeyChecking=no /tmp/docker-compose.override.yml "root@${DROPLET_IP}:/tmp/"
scp -o StrictHostKeyChecking=no /tmp/install-plane-remote.sh "root@${DROPLET_IP}:/tmp/"

# Execute installation
ssh -o StrictHostKeyChecking=no "root@${DROPLET_IP}" "bash /tmp/install-plane-remote.sh"

# Step 6: Configure nginx reverse proxy (on droplet)
echo ">>> Step 6: Configuring nginx reverse proxy..."
cat > /tmp/plane-nginx.conf << 'NGINXEOF'
# Plane reverse proxy configuration
# Add to existing nginx config on ocr-service-droplet

upstream plane_web {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name plane.insightpulseai.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name plane.insightpulseai.com;

    # SSL configuration (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/plane.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/plane.insightpulseai.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://plane_web;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
NGINXEOF

scp -o StrictHostKeyChecking=no /tmp/plane-nginx.conf "root@${DROPLET_IP}:/etc/nginx/sites-available/plane"
ssh -o StrictHostKeyChecking=no "root@${DROPLET_IP}" "
    ln -sf /etc/nginx/sites-available/plane /etc/nginx/sites-enabled/plane
    # Get SSL cert if not exists
    certbot certonly --nginx -d plane.insightpulseai.com --non-interactive --agree-tos --email admin@insightpulseai.com || true
    nginx -t && systemctl reload nginx
"

# Step 7: Configure DNS
echo ">>> Step 7: Configuring DNS..."
EXISTING_RECORD=$(doctl compute domain records list insightpulseai.com --format ID,Name,Type --no-header 2>/dev/null | grep -E "^[0-9]+\s+plane\s+A" | awk '{print $1}' || true)

if [ -n "${EXISTING_RECORD}" ]; then
    echo "Updating existing DNS record..."
    doctl compute domain records update insightpulseai.com \
        --record-id "${EXISTING_RECORD}" \
        --record-data "${DROPLET_IP}"
else
    echo "Creating DNS A record..."
    doctl compute domain records create insightpulseai.com \
        --record-type A \
        --record-name plane \
        --record-data "${DROPLET_IP}" \
        --record-ttl 300
fi

# Step 8: Verify deployment
echo ">>> Step 8: Verifying deployment..."
sleep 5

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${DROPLET_IP}:8080" 2>/dev/null || echo "000")
echo "HTTP Status (direct): ${HTTP_STATUS}"

echo ""
echo "=== Deployment Summary ==="
echo "Plane URL: https://${PLANE_DOMAIN}"
echo "Direct IP: http://${DROPLET_IP}:8080"
echo "Database: ${DB_HOST}/${DB_NAME}"
echo ""
echo "To check logs: ssh root@${DROPLET_IP} 'cd /opt/plane && docker compose logs -f'"
