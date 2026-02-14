#!/usr/bin/env bash
# =============================================================================
# Mailgun Domain Setup & DNS Export Script
# Automates domain creation, verification, and DNS record export
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Required - set via environment or modify here
MAILGUN_API_KEY="${MAILGUN_API_KEY:-}"
MAILGUN_REGION="${MAILGUN_REGION:-us}"  # us|eu

# Domains
MAILGUN_DOMAIN_OLD="${MAILGUN_DOMAIN_OLD:-mg.insightpulseai.net}"
MAILGUN_DOMAIN_NEW="${MAILGUN_DOMAIN_NEW:-mg.insightpulseai.com}"

# Derived base URL (region-aware)
if [ "$MAILGUN_REGION" = "eu" ]; then
  MAILGUN_BASE="https://api.eu.mailgun.net"
else
  MAILGUN_BASE="https://api.mailgun.net"
fi

# Output directory
DNS_OUTPUT_DIR="${DNS_OUTPUT_DIR:-infra/dns/mailgun}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# Validation
# =============================================================================

if [ -z "$MAILGUN_API_KEY" ]; then
    echo -e "${RED}Error: MAILGUN_API_KEY environment variable is not set${NC}"
    echo "Usage: MAILGUN_API_KEY=key-xxx ./mailgun-domain-setup.sh"
    exit 1
fi

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}Mailgun Domain Setup${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo -e "Region:     ${GREEN}${MAILGUN_REGION}${NC}"
echo -e "Base URL:   ${GREEN}${MAILGUN_BASE}${NC}"
echo -e "New Domain: ${GREEN}${MAILGUN_DOMAIN_NEW}${NC}"
echo -e "Old Domain: ${YELLOW}${MAILGUN_DOMAIN_OLD}${NC} (to deprecate)"
echo ""

# =============================================================================
# Functions
# =============================================================================

check_domain() {
    local domain="$1"
    echo -e "${BLUE}--- Checking domain: ${domain} ---${NC}"

    response=$(curl -sS -u "api:${MAILGUN_API_KEY}" \
        "${MAILGUN_BASE}/v3/domains/${domain}" 2>/dev/null || echo '{"error": "not found"}')

    if echo "$response" | jq -e '.domain' > /dev/null 2>&1; then
        state=$(echo "$response" | jq -r '.domain.state')
        echo -e "${GREEN}Domain exists. State: ${state}${NC}"
        return 0
    else
        echo -e "${YELLOW}Domain not found or error${NC}"
        return 1
    fi
}

create_domain() {
    local domain="$1"
    echo -e "${BLUE}--- Creating domain: ${domain} ---${NC}"

    response=$(curl -sS -u "api:${MAILGUN_API_KEY}" \
        "${MAILGUN_BASE}/v3/domains" \
        -F "name=${domain}" \
        -F "smtp_password=auto" 2>/dev/null)

    if echo "$response" | jq -e '.domain' > /dev/null 2>&1; then
        echo -e "${GREEN}Domain created successfully${NC}"
        echo "$response" | jq '.domain | {name, state, created_at}'
    else
        echo -e "${YELLOW}Domain may already exist or error occurred:${NC}"
        echo "$response" | jq . 2>/dev/null || echo "$response"
    fi
}

get_domain_details() {
    local domain="$1"
    echo -e "${BLUE}--- Getting domain details: ${domain} ---${NC}"

    curl -sS -u "api:${MAILGUN_API_KEY}" \
        "${MAILGUN_BASE}/v3/domains/${domain}"
}

export_dns_records() {
    local domain="$1"
    local output_file="${DNS_OUTPUT_DIR}/${domain//./_}.records.json"

    echo -e "${BLUE}--- Exporting DNS records to: ${output_file} ---${NC}"

    mkdir -p "${DNS_OUTPUT_DIR}"

    curl -sS -u "api:${MAILGUN_API_KEY}" \
        "${MAILGUN_BASE}/v3/domains/${domain}" \
    | jq '{
        domain: .domain.name,
        state: .domain.state,
        region: .domain.region,
        created_at: .domain.created_at,
        smtp_login: .domain.smtp_login,
        receiving_dns_records: .receiving_dns_records,
        sending_dns_records: .sending_dns_records
    }' > "${output_file}"

    echo -e "${GREEN}DNS records exported to: ${output_file}${NC}"
    cat "${output_file}" | jq '.sending_dns_records'
}

verify_domain() {
    local domain="$1"
    echo -e "${BLUE}--- Verifying domain: ${domain} ---${NC}"

    response=$(curl -sS -u "api:${MAILGUN_API_KEY}" \
        -X PUT "${MAILGUN_BASE}/v3/domains/${domain}/verify" 2>/dev/null)

    echo "$response" | jq '.domain | {name, state}' 2>/dev/null || echo "$response"
}

send_test_email() {
    local domain="$1"
    local to_email="$2"

    echo -e "${BLUE}--- Sending test email via: ${domain} ---${NC}"

    response=$(curl -sS -u "api:${MAILGUN_API_KEY}" \
        "${MAILGUN_BASE}/v3/${domain}/messages" \
        -F "from=InsightPulse AI Test <postmaster@${domain}>" \
        -F "to=${to_email}" \
        -F "subject=Mailgun Configuration Test - ${domain}" \
        -F "text=If you received this email, the domain ${domain} is properly configured and active.

Configuration Details:
- Domain: ${domain}
- Region: ${MAILGUN_REGION}
- Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)

This is an automated test from the Mailgun setup script." 2>/dev/null)

    if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
        echo -e "${GREEN}Test email sent successfully!${NC}"
        echo "$response" | jq '{id, message}'
    else
        echo -e "${RED}Failed to send test email:${NC}"
        echo "$response" | jq . 2>/dev/null || echo "$response"
    fi
}

check_dns_local() {
    local domain="$1"
    echo -e "${BLUE}--- Local DNS Check: ${domain} ---${NC}"

    echo -n "MX Records: "
    dig +short MX "${domain}" 2>/dev/null || echo "not found"

    echo -n "TXT Records: "
    dig +short TXT "${domain}" 2>/dev/null || echo "not found"

    echo -n "DKIM (smtp._domainkey): "
    dig +short TXT "smtp._domainkey.${domain}" 2>/dev/null || echo "not found"
}

# =============================================================================
# Main Execution
# =============================================================================

case "${1:-status}" in
    create)
        create_domain "$MAILGUN_DOMAIN_NEW"
        ;;

    status)
        check_domain "$MAILGUN_DOMAIN_NEW"
        ;;

    details)
        get_domain_details "$MAILGUN_DOMAIN_NEW" | jq .
        ;;

    export)
        export_dns_records "$MAILGUN_DOMAIN_NEW"
        ;;

    verify)
        verify_domain "$MAILGUN_DOMAIN_NEW"
        ;;

    test)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}Error: Please provide email address${NC}"
            echo "Usage: $0 test your-email@example.com"
            exit 1
        fi
        send_test_email "$MAILGUN_DOMAIN_NEW" "$2"
        ;;

    dns-check)
        check_dns_local "$MAILGUN_DOMAIN_NEW"
        ;;

    full)
        echo -e "${BLUE}=== Full Setup Workflow ===${NC}"
        echo ""

        # Step 1: Check if domain exists
        if check_domain "$MAILGUN_DOMAIN_NEW"; then
            echo -e "${GREEN}Domain already exists, skipping creation${NC}"
        else
            echo -e "${YELLOW}Creating domain...${NC}"
            create_domain "$MAILGUN_DOMAIN_NEW"
        fi
        echo ""

        # Step 2: Export DNS records
        export_dns_records "$MAILGUN_DOMAIN_NEW"
        echo ""

        # Step 3: Show DNS check
        check_dns_local "$MAILGUN_DOMAIN_NEW"
        echo ""

        echo -e "${YELLOW}Next Steps:${NC}"
        echo "1. Add DNS records from ${DNS_OUTPUT_DIR}/${MAILGUN_DOMAIN_NEW//./_}.records.json to your DNS provider"
        echo "2. Wait for DNS propagation (5-60 minutes)"
        echo "3. Run: $0 verify"
        echo "4. Run: $0 test your-email@example.com"
        ;;

    *)
        echo "Usage: $0 {create|status|details|export|verify|test|dns-check|full}"
        echo ""
        echo "Commands:"
        echo "  create    - Create new domain in Mailgun"
        echo "  status    - Check if domain exists and its state"
        echo "  details   - Get full domain details (JSON)"
        echo "  export    - Export DNS records to JSON file"
        echo "  verify    - Trigger domain verification in Mailgun"
        echo "  test      - Send test email (requires email address)"
        echo "  dns-check - Check DNS records locally via dig"
        echo "  full      - Run full setup workflow"
        ;;
esac
