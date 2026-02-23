#!/usr/bin/env bash
# Configure n8n SMTP for password reset and email notifications
# Uses Zoho Mail (no-reply@insightpulseai.com)

set -euo pipefail

echo "🔧 n8n SMTP Configuration"
echo "========================="
echo ""

# Variables
DROPLET_IP="178.128.112.214"
COMPOSE_FILE="/opt/ipai/odoo/infra/stack/compose.stack.yml"
BACKUP_FILE="/opt/ipai/odoo/infra/stack/compose.stack.yml.backup.$(date +%Y%m%d-%H%M%S)"

# SMTP Settings (Zoho Mail)
SMTP_HOST="smtp.zoho.com"
SMTP_PORT="587"
SMTP_USER="no-reply@insightpulseai.com"
SMTP_FROM="no-reply@insightpulseai.com"
SMTP_PASS_VAR="ZOHO_APP_PASSWORD"  # Environment variable name

# Check if ZOHO_APP_PASSWORD is set
if [[ -z "${ZOHO_APP_PASSWORD:-}" ]]; then
  echo "❌ Error: ZOHO_APP_PASSWORD environment variable not set"
  echo ""
  echo "Please set it first:"
  echo "  export ZOHO_APP_PASSWORD='your_zoho_app_password'"
  echo ""
  echo "Get app password from:"
  echo "  https://accounts.zoho.com/home#security/security"
  echo "  → App-Specific Passwords → Generate New Password"
  exit 1
fi

echo "✅ ZOHO_APP_PASSWORD found"
echo ""

# Step 1: Backup compose file
echo "1. Backing up compose file..."
ssh root@${DROPLET_IP} "cp ${COMPOSE_FILE} ${BACKUP_FILE}"
echo "   ✅ Backup created: ${BACKUP_FILE}"
echo ""

# Step 2: Update compose file with SMTP config
echo "2. Adding SMTP configuration to compose file..."

# Create temporary file with SMTP config
cat > /tmp/n8n-smtp-config.txt << 'EOF'

      # SMTP Configuration (Zoho Mail)
      - N8N_EMAIL_MODE=smtp
      - N8N_SMTP_HOST=${N8N_SMTP_HOST}
      - N8N_SMTP_PORT=${N8N_SMTP_PORT}
      - N8N_SMTP_USER=${N8N_SMTP_USER}
      - N8N_SMTP_PASS=${N8N_SMTP_PASS}
      - N8N_SMTP_SENDER=${N8N_SMTP_FROM}
      - N8N_SMTP_SSL=false
EOF

# Copy to droplet
scp /tmp/n8n-smtp-config.txt root@${DROPLET_IP}:/tmp/

# Insert SMTP config after N8N_ENCRYPTION_KEY line
ssh root@${DROPLET_IP} "
  # Insert SMTP config
  sed -i '/N8N_ENCRYPTION_KEY/r /tmp/n8n-smtp-config.txt' ${COMPOSE_FILE}

  # Clean up temp file
  rm /tmp/n8n-smtp-config.txt
"

echo "   ✅ SMTP configuration added"
echo ""

# Step 3: Update N8N_DOMAIN from .net to .com
echo "3. Updating N8N_DOMAIN from .net to .com..."

ssh root@${DROPLET_IP} "
  # Check if .net domain is present
  if grep -q 'n8n.insightpulseai.net' ${COMPOSE_FILE}; then
    echo '   Found .net domain references'
  fi
"

echo "   ⚠️  Note: N8N_DOMAIN is set via environment variable \${N8N_DOMAIN}"
echo "   Will set it during docker-compose up"
echo ""

# Step 4: Export environment variables and recreate service
echo "4. Recreating n8n service with SMTP..."

ssh root@${DROPLET_IP} "
  cd /opt/ipai/odoo/infra/stack

  # Export required variables
  export N8N_DOMAIN='n8n.insightpulseai.com'
  export N8N_IMAGE='n8nio/n8n:latest'
  export N8N_TIMEZONE='Asia/Manila'
  export N8N_ENCRYPTION_KEY=\$(openssl rand -hex 32)

  # SMTP variables
  export N8N_SMTP_HOST='${SMTP_HOST}'
  export N8N_SMTP_PORT='${SMTP_PORT}'
  export N8N_SMTP_USER='${SMTP_USER}'
  export N8N_SMTP_FROM='${SMTP_FROM}'
  export N8N_SMTP_PASS='${ZOHO_APP_PASSWORD}'

  # Stop and recreate n8n service
  docker-compose -f compose.stack.yml stop n8n
  docker-compose -f compose.stack.yml rm -f n8n
  docker-compose -f compose.stack.yml up -d n8n

  echo ''
  echo 'Waiting for n8n to start...'
  sleep 10

  # Check health
  docker-compose -f compose.stack.yml ps n8n
"

echo ""
echo "   ✅ n8n service recreated"
echo ""

# Step 5: Verify configuration
echo "5. Verifying n8n configuration..."

# Check health
HEALTH=$(curl -s https://n8n.insightpulseai.com/healthz 2>/dev/null || echo "error")

if [[ "$HEALTH" == *"ok"* ]]; then
  echo "   ✅ n8n is healthy"
else
  echo "   ❌ Health check failed"
  exit 1
fi

# Check SMTP variables in container
echo ""
echo "   Checking SMTP configuration in container..."
ssh root@${DROPLET_IP} "docker exec ipai-n8n env | grep -i smtp | sed 's/PASS=.*/PASS=***REDACTED***/'"

echo ""
echo "================================================"
echo "✅ n8n SMTP Configuration Complete"
echo "================================================"
echo ""
echo "Configuration:"
echo "- SMTP Host: ${SMTP_HOST}:${SMTP_PORT}"
echo "- SMTP User: ${SMTP_USER}"
echo "- SMTP From: ${SMTP_FROM}"
echo "- Domain: n8n.insightpulseai.com"
echo ""
echo "Next Steps:"
echo "1. Visit https://n8n.insightpulseai.com"
echo "2. Try password reset (should now work)"
echo "3. Or create new admin account if first-time setup"
echo "4. Admin email: devops@insightpulseai.com"
echo ""
echo "Rollback (if needed):"
echo "  ssh root@${DROPLET_IP} 'cp ${BACKUP_FILE} ${COMPOSE_FILE}'"
echo "  ssh root@${DROPLET_IP} 'cd /opt/ipai/odoo/infra/stack && docker-compose up -d n8n'"
