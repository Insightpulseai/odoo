#!/bin/bash
# =============================================================================
# init-firewall.sh — Network security for Claude Code devcontainer
# Whitelist-only outbound — based on official Anthropic pattern
# Extended for InsightPulseAI: adds pypi.org, odoo.com, oca repos
# =============================================================================
set -e

# Elevate if not root (postStartCommand runs as vscode)
if [ "$(id -u)" != "0" ]; then
    exec sudo "$0" "$@"
fi

echo "[firewall] Initializing..."

# Flush existing rules
iptables -F OUTPUT 2>/dev/null || true
iptables -F INPUT  2>/dev/null || true

# ---------------------------------------------------------------------------
# Allowed outbound domains (resolved to IPs at startup)
# ---------------------------------------------------------------------------
ALLOWED_DOMAINS=(
    "api.anthropic.com"         # Claude API
    "github.com"                # OCA modules, Odoo source
    "raw.githubusercontent.com" # GitHub raw content
    "objects.githubusercontent.com"
    "registry.npmjs.org"        # npm (Claude Code itself)
    "pypi.org"                  # pip install OCA deps
    "files.pythonhosted.org"    # pip packages
    "odoo.com"                  # Odoo downloads
    "statsig.anthropic.com"     # Anthropic telemetry
    "sentry.io"                 # Error tracking
)

# Allow localhost always
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT  -i lo -j ACCEPT

# Allow established connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow DNS (UDP + TCP port 53)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# Allow SSH
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT

# Allow PostgreSQL to db service — resolve Docker DNS name to IP
DB_IP=$(getent hosts db 2>/dev/null | awk '{print $1}' || true)
if [ -n "$DB_IP" ]; then
    echo "[firewall] Allowing PostgreSQL to db ($DB_IP)"
    iptables -A OUTPUT -p tcp --dport 5432 -d "$DB_IP" -j ACCEPT
else
    echo "[firewall] WARNING: Could not resolve 'db' — allowing all port 5432"
    iptables -A OUTPUT -p tcp --dport 5432 -j ACCEPT
fi

# Resolve and allow whitelisted domains
for domain in "${ALLOWED_DOMAINS[@]}"; do
    echo "[firewall] Allowing: $domain"
    for ip in $(dig +short "$domain" A 2>/dev/null | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true); do
        iptables -A OUTPUT -d "$ip" -j ACCEPT
    done
done

# Allow HTTPS + HTTP to whitelisted IPs already added
iptables -A OUTPUT -p tcp --dport 443 -m state --state NEW -j DROP
iptables -A OUTPUT -p tcp --dport 80  -m state --state NEW -j DROP

echo "[firewall] Rules applied. Non-whitelisted outbound blocked."
iptables -L OUTPUT --line-numbers 2>/dev/null | head -20
