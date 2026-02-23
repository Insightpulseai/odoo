#!/usr/bin/env bash
# Finish n8n setup with correct DO database password
# Usage: ./finish-n8n-setup.sh <DO_DATABASE_PASSWORD>

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "❌ Error: Database password required"
    echo ""
    echo "Usage: ./finish-n8n-setup.sh <DO_DATABASE_PASSWORD>"
    echo ""
    echo "Get password from:"
    echo "  https://cloud.digitalocean.com/databases"
    echo "  → odoo-db → Connection Details → doadmin password"
    exit 1
fi

DO_PASSWORD="$1"

echo "🔧 Finishing n8n Setup"
echo "====================="
echo ""

# Update .env file with correct password
echo "1. Updating database password..."
ssh root@178.128.112.214 "
cd /opt/ipai/odoo/infra/stack
sed -i 's/^DO_PG_PASSWORD=.*/DO_PG_PASSWORD=${DO_PASSWORD}/' .env
echo '✅ Password updated in .env'
"

# Restart n8n
echo ""
echo "2. Restarting n8n..."
ssh root@178.128.112.214 "
cd /opt/ipai/odoo/infra/stack
docker-compose -f compose.stack.yml restart n8n
echo '✅ n8n restarted'
"

# Wait for startup
echo ""
echo "3. Waiting for n8n to start (30 seconds)..."
sleep 30

# Verify health
echo ""
echo "4. Checking n8n health..."
HEALTH=$(curl -s https://n8n.insightpulseai.com/healthz 2>/dev/null || echo "error")

if [[ "$HEALTH" == *"ok"* ]]; then
    echo "✅ n8n is healthy!"
else
    echo "⚠️  Health check response: $HEALTH"
    echo "Checking logs..."
    ssh root@178.128.112.214 "docker logs ipai-n8n --tail 20"
    exit 1
fi

# Verify SMTP
echo ""
echo "5. Verifying SMTP configuration..."
ssh root@178.128.112.214 "docker exec ipai-n8n env | grep -E '(EMAIL|SMTP)' | grep -v PASS"

echo ""
echo "================================================"
echo "✅ n8n Setup Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Visit: https://n8n.insightpulseai.com"
echo "2. Create new admin account:"
echo "   - Email: devops@insightpulseai.com"
echo "   - First Name: DevOps"
echo "   - Last Name: Admin"
echo "   - Password: (generate strong password)"
echo ""
echo "3. IMMEDIATELY store credentials in Supabase Vault:"
echo "   - n8n_admin_email: devops@insightpulseai.com"
echo "   - n8n_admin_password: (your generated password)"
echo ""
echo "SMTP is now configured for:"
echo "- Password reset emails"
echo "- User invitation emails"
echo "- Workflow notification emails"
echo ""
echo "All system emails sent from: no-reply@insightpulseai.com"
