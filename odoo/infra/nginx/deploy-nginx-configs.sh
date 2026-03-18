#!/usr/bin/env bash
set -euo pipefail

# Deploy nginx configurations for n8n and MCP
# Usage: ./deploy-nginx-configs.sh [--dry-run]

DROPLET_IP="178.128.112.214"
DROPLET_USER="root"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

echo "📦 Deploying nginx configurations to ${DROPLET_IP}..."

# Function to deploy a config file
deploy_config() {
    local config_file="$1"
    local site_name="$(basename "$config_file" .conf)"

    echo ""
    echo "📄 Deploying ${site_name}..."

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "   [DRY RUN] Would copy: ${config_file} → /etc/nginx/sites-available/${site_name}"
        echo "   [DRY RUN] Would symlink: /etc/nginx/sites-available/${site_name} → /etc/nginx/sites-enabled/${site_name}"
        return
    fi

    # Copy config to server
    scp "${config_file}" "${DROPLET_USER}@${DROPLET_IP}:/etc/nginx/sites-available/${site_name}"

    # Enable site (create symlink)
    ssh "${DROPLET_USER}@${DROPLET_IP}" "ln -sf /etc/nginx/sites-available/${site_name} /etc/nginx/sites-enabled/${site_name}"

    echo "   ✅ ${site_name} deployed and enabled"
}

# Deploy n8n config
if [[ -f "${SCRIPT_DIR}/n8n.insightpulseai.com.conf" ]]; then
    deploy_config "${SCRIPT_DIR}/n8n.insightpulseai.com.conf"
else
    echo "❌ n8n.insightpulseai.com.conf not found"
    exit 1
fi

# Deploy MCP config
if [[ -f "${SCRIPT_DIR}/mcp.insightpulseai.com.conf" ]]; then
    deploy_config "${SCRIPT_DIR}/mcp.insightpulseai.com.conf"
else
    echo "❌ mcp.insightpulseai.com.conf not found"
    exit 1
fi

# Test nginx configuration
echo ""
echo "🧪 Testing nginx configuration..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: nginx -t"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "nginx -t"
fi

# Reload nginx
echo ""
echo "🔄 Reloading nginx..."
if [[ "$DRY_RUN" == "true" ]]; then
    echo "   [DRY RUN] Would run: systemctl reload nginx"
else
    ssh "${DROPLET_USER}@${DROPLET_IP}" "systemctl reload nginx"
    echo "   ✅ nginx reloaded"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify HTTP access:"
echo "      curl -I http://n8n.insightpulseai.com"
echo "      curl -I http://mcp.insightpulseai.com"
echo ""
echo "   2. Set up HTTPS with certbot:"
echo "      ./setup-https.sh"
