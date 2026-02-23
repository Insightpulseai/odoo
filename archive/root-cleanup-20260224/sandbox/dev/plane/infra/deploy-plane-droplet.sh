#!/bin/bash
# Deploy Plane CE to DigitalOcean Droplet
# Target: New droplet or existing ocr-service-droplet
# Uses: External PostgreSQL (odoo-db-sgp1), DO Spaces for storage

set -euo pipefail

# Configuration
DROPLET_NAME="${PLANE_DROPLET_NAME:-plane-ppm}"
DROPLET_SIZE="${PLANE_DROPLET_SIZE:-s-2vcpu-4gb}"  # 4GB RAM minimum
DROPLET_REGION="${PLANE_DROPLET_REGION:-sgp1}"
DROPLET_IMAGE="${PLANE_DROPLET_IMAGE:-ubuntu-24-04-x64}"

# Domain configuration
PLANE_DOMAIN="${PLANE_DOMAIN:-plane.insightpulseai.com}"

# External PostgreSQL (odoo-db-sgp1)
# Format: postgresql://user:password@host:port/database
DB_HOST="${PLANE_DB_HOST:-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com}"
DB_PORT="${PLANE_DB_PORT:-25060}"
DB_USER="${PLANE_DB_USER:-doadmin}"
DB_NAME="${PLANE_DB_NAME:-plane}"
# DB_PASSWORD must be set in environment

# DO Spaces for file storage
SPACES_REGION="${SPACES_REGION:-sgp1}"
SPACES_BUCKET="${SPACES_BUCKET:-plane-uploads-ipai}"
# SPACES_KEY and SPACES_SECRET must be set in environment

echo "=== Plane CE Deployment to DigitalOcean ==="
echo "Domain: ${PLANE_DOMAIN}"
echo "Droplet: ${DROPLET_NAME} (${DROPLET_SIZE})"
echo "Region: ${DROPLET_REGION}"
echo "Database: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""

# Validate required secrets
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${SPACES_KEY:?SPACES_KEY is required}"
: "${SPACES_SECRET:?SPACES_SECRET is required}"

# Step 1: Create database on external PostgreSQL
echo ">>> Step 1: Creating Plane database..."
PGPASSWORD="${DB_PASSWORD}" psql \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d defaultdb \
  -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || echo "Database may already exist"

# Step 2: Create DO Spaces bucket
echo ">>> Step 2: Creating Spaces bucket..."
doctl compute spaces create "${SPACES_BUCKET}" --region "${SPACES_REGION}" 2>/dev/null || echo "Bucket may already exist"

# Configure CORS for Spaces bucket
cat > /tmp/cors.json << 'EOF'
{
  "CORSRules": [{
    "AllowedOrigins": ["https://plane.insightpulseai.com"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }]
}
EOF

# Step 3: Create droplet (if not using existing)
echo ">>> Step 3: Creating/updating droplet..."
DROPLET_EXISTS=$(doctl compute droplet list --format Name --no-header | grep -c "^${DROPLET_NAME}$" || true)

if [ "${DROPLET_EXISTS}" -eq 0 ]; then
  echo "Creating new droplet: ${DROPLET_NAME}"
  doctl compute droplet create "${DROPLET_NAME}" \
    --size "${DROPLET_SIZE}" \
    --image "${DROPLET_IMAGE}" \
    --region "${DROPLET_REGION}" \
    --vpc-uuid "$(doctl vpcs list --region ${DROPLET_REGION} --format ID --no-header | head -1)" \
    --ssh-keys "$(doctl compute ssh-key list --format ID --no-header | tr '\n' ',' | sed 's/,$//')" \
    --wait

  echo "Waiting for droplet to be ready..."
  sleep 30
fi

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get "${DROPLET_NAME}" --format PublicIPv4 --no-header)
echo "Droplet IP: ${DROPLET_IP}"

# Step 4: Deploy Plane via SSH
echo ">>> Step 4: Deploying Plane to droplet..."

# Generate secrets
SECRET_KEY=$(openssl rand -hex 32)

# Create remote deployment script
cat > /tmp/plane-install.sh << REMOTE_EOF
#!/bin/bash
set -euo pipefail

echo "Installing Docker..."
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

echo "Installing Plane CE..."
curl -fsSL https://prime.plane.so/install/ | sh -

echo "Configuring Plane..."
cd /opt/plane

# Update plane.env with external services
cat > plane.env << 'ENVEOF'
# Domain
WEB_URL=https://${PLANE_DOMAIN}
CORS_ALLOWED_ORIGINS=https://${PLANE_DOMAIN}

# External PostgreSQL
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require

# Redis (internal - installer creates this)
REDIS_URL=redis://plane-redis:6379/

# RabbitMQ (internal - installer creates this)
AMQP_URL=amqp://plane:plane@plane-mq:5672/plane

# S3 Storage (DO Spaces)
USE_MINIO=0
AWS_REGION=${SPACES_REGION}
AWS_ACCESS_KEY_ID=${SPACES_KEY}
AWS_SECRET_ACCESS_KEY=${SPACES_SECRET}
AWS_S3_BUCKET_NAME=${SPACES_BUCKET}
AWS_S3_ENDPOINT_URL=https://${SPACES_REGION}.digitaloceanspaces.com

# Security
SECRET_KEY=${SECRET_KEY}
DEBUG=0

# Ports
LISTEN_HTTP_PORT=80
LISTEN_HTTPS_PORT=443
ENVEOF

echo "Starting Plane..."
docker compose up -d

echo "Plane deployment complete!"
docker compose ps
REMOTE_EOF

# Copy and execute remote script
scp -o StrictHostKeyChecking=no /tmp/plane-install.sh "root@${DROPLET_IP}:/tmp/"
ssh -o StrictHostKeyChecking=no "root@${DROPLET_IP}" "bash /tmp/plane-install.sh"

# Step 5: Configure DNS
echo ">>> Step 5: Configuring DNS..."
# Check if A record exists
EXISTING_RECORD=$(doctl compute domain records list insightpulseai.com --format ID,Name,Type --no-header | grep -E "^[0-9]+\s+plane\s+A" | awk '{print $1}' || true)

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

# Step 6: Verify deployment
echo ">>> Step 6: Verifying deployment..."
sleep 10

# Health check
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${DROPLET_IP}" || echo "000")
echo "HTTP Status: ${HTTP_STATUS}"

if [ "${HTTP_STATUS}" -eq 200 ] || [ "${HTTP_STATUS}" -eq 302 ]; then
  echo "=== Deployment Successful ==="
  echo "URL: https://${PLANE_DOMAIN}"
  echo "IP: ${DROPLET_IP}"
else
  echo "=== Deployment may need more time ==="
  echo "Check: ssh root@${DROPLET_IP} 'cd /opt/plane && docker compose logs'"
fi
