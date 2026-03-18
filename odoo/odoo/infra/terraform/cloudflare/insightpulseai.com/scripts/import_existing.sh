#!/bin/bash
# =============================================================================
# Import existing Cloudflare DNS records into Terraform state
# =============================================================================
# Run this script ONCE after initial terraform init to import existing records.
# Record IDs were obtained from Cloudflare API on 2026-02-08.
#
# Usage: ./scripts/import_existing.sh
# =============================================================================

set -euo pipefail

ZONE_ID="73f587aee652fc24fd643aec00dcca81"

echo "Importing Cloudflare DNS records for insightpulseai.com..."

# A Records
terraform import cloudflare_record.root_a "${ZONE_ID}/d9aeb9df7eda89976253757fd64c8049"
terraform import cloudflare_record.www_a  "${ZONE_ID}/3abdc3d8fed045a64fa5a16c3f026c7a"
terraform import cloudflare_record.erp_a  "${ZONE_ID}/197c5ebd241ddb286675aa4f3f29a913"

# MX Records
terraform import cloudflare_record.mx1 "${ZONE_ID}/8cf99deed1458ae37c5e22438edfa0f3"
terraform import cloudflare_record.mx2 "${ZONE_ID}/b1c7bfe3a000878ffe51faebd32a2ca4"
terraform import cloudflare_record.mx3 "${ZONE_ID}/5ef159ed4fc160558f8ca87c23a9a2c5"

# TXT Records
terraform import cloudflare_record.spf       "${ZONE_ID}/6a27efff45acff7c74f91d57e666772f"
terraform import cloudflare_record.dmarc     "${ZONE_ID}/335f40f1714018ba41ab0db278d63c61"
terraform import cloudflare_record.dkim_zoho "${ZONE_ID}/be385c22ddf752750bd7baf45122618e"

echo "Import complete. Run 'terraform plan' to verify state matches configuration."
