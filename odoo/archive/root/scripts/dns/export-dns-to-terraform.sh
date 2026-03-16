#!/usr/bin/env bash
set -euo pipefail

# Export DNS Configuration to Terraform Format
# Purpose: Generate Terraform configuration from current DNS state
# Usage: ./scripts/dns/export-dns-to-terraform.sh [output-file]

DOMAIN="insightpulseai.com"
OUTPUT_FILE="${1:-infra/terraform/dns.tf}"

echo "════════════════════════════════════════════════════════════════"
echo "Exporting DNS to Terraform Format"
echo "════════════════════════════════════════════════════════════════"
echo

# Check prerequisites
if ! command -v doctl &> /dev/null; then
    echo "❌ ERROR: doctl CLI not found"
    exit 1
fi

if ! doctl account get &> /dev/null; then
    echo "❌ ERROR: doctl not authenticated"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ ERROR: jq not found (required for JSON parsing)"
    exit 1
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "Fetching DNS records..."
RECORDS=$(doctl compute domain records list "$DOMAIN" --output json)

# Start Terraform file
cat > "$OUTPUT_FILE" << 'EOF'
# DNS Configuration for insightpulseai.com
# Generated from DigitalOcean DNS state
# Last updated: TIMESTAMP
# 
# Apply with:
#   cd infra/terraform
#   terraform init
#   terraform plan
#   terraform apply

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

variable "droplet_ip" {
  description = "Primary droplet IP address"
  type        = string
  default     = "178.128.112.214"
}

resource "digitalocean_domain" "main" {
  name = "insightpulseai.com"
}

EOF

# Replace timestamp
sed -i "s/TIMESTAMP/$(date -u +"%Y-%m-%d %H:%M:%S UTC")/" "$OUTPUT_FILE"

echo "Generating Terraform resources..."

# Counter for resource names
declare -A type_counters

# Process each record
echo "$RECORDS" | jq -c '.[]' | while read -r record; do
    id=$(echo "$record" | jq -r '.id')
    type=$(echo "$record" | jq -r '.type')
    name=$(echo "$record" | jq -r '.name')
    data=$(echo "$record" | jq -r '.data')
    priority=$(echo "$record" | jq -r '.priority // ""')
    ttl=$(echo "$record" | jq -r '.ttl')
    
    # Skip NS and SOA records (managed by DigitalOcean)
    if [ "$type" = "NS" ] || [ "$type" = "SOA" ]; then
        continue
    fi
    
    # Generate resource name (sanitized)
    resource_name=$(echo "${name}_${type}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_]/_/g' | sed 's/__*/_/g' | sed 's/^_//;s/_$//')
    
    # Handle @ (root) records
    if [ "$name" = "@" ]; then
        resource_name="root_${type,,}"
    fi
    
    # Make resource name unique
    base_name="$resource_name"
    counter=1
    while grep -q "resource \"digitalocean_record\" \"$resource_name\"" "$OUTPUT_FILE" 2>/dev/null; do
        resource_name="${base_name}_${counter}"
        counter=$((counter + 1))
    done
    
    # Write Terraform resource
    cat >> "$OUTPUT_FILE" << EOF

# $type record: $name → $data
resource "digitalocean_record" "$resource_name" {
  domain = digitalocean_domain.main.name
  type   = "$type"
  name   = "$name"
EOF
    
    # Add data field (handle @ for CNAME)
    if [ "$type" = "CNAME" ] && [ "$data" = "@" ]; then
        echo "  value  = digitalocean_domain.main.name" >> "$OUTPUT_FILE"
    else
        echo "  value  = \"$data\"" >> "$OUTPUT_FILE"
    fi
    
    # Add priority for MX records
    if [ -n "$priority" ] && [ "$priority" != "null" ]; then
        echo "  priority = $priority" >> "$OUTPUT_FILE"
    fi
    
    # Add TTL
    echo "  ttl    = $ttl" >> "$OUTPUT_FILE"
    echo "}" >> "$OUTPUT_FILE"
done

echo "✅ Terraform configuration generated"
echo

echo "════════════════════════════════════════════════════════════════"
echo "Export Complete!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Output file: $OUTPUT_FILE"
echo
echo "Next steps:"
echo "  1. Review: cat $OUTPUT_FILE"
echo "  2. Initialize: cd infra/terraform && terraform init"
echo "  3. Plan: terraform plan"
echo "  4. Apply: terraform apply"
echo
echo "⚠️  Note: This is a snapshot. Manual changes to DNS won't be reflected"
echo "    until you re-run this export script."
echo
