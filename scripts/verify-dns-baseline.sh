#!/usr/bin/env bash
set -euo pipefail

DOMAIN="insightpulseai.com"
EXPECTED_IP="178.128.112.214"

echo "=== DNS Baseline Verification for $DOMAIN ==="
echo ""

# Verify nameservers
echo "1. Nameservers:"
NS=$(dig NS "$DOMAIN" +short)
echo "$NS"
echo ""

# Verify A records
echo "2. A Records (expecting $EXPECTED_IP):"
for service in erp n8n ocr auth; do
  fqdn="${service}.${DOMAIN}"
  ip=$(dig +short A "$fqdn" | head -1)
  if [[ "$ip" == "$EXPECTED_IP" ]]; then
    echo "  ✅ $fqdn → $ip"
  else
    echo "  ❌ $fqdn → $ip (expected $EXPECTED_IP)"
  fi
done
echo ""

# Verify CNAME records
echo "3. CNAME Records:"
for service in mcp superset; do
  fqdn="${service}.${DOMAIN}"
  cname=$(dig +short CNAME "$fqdn" | sed 's/\.$//')
  if [[ -n "$cname" ]]; then
    echo "  ✅ $fqdn → $cname"
  else
    echo "  ⚠️  $fqdn → (no CNAME found, may be A record)"
  fi
done
echo ""

# Verify no .net records exist
echo "4. Verify .net deprecation:"
for service in erp n8n ocr auth affine; do
  fqdn="${service}.insightpulseai.net"
  result=$(dig +short A "$fqdn" || true)
  if [[ -z "$result" ]]; then
    echo "  ✅ $fqdn → (no record, correctly deprecated)"
  else
    echo "  ❌ $fqdn → $result (should be removed)"
  fi
done
echo ""

# Mail records
echo "5. Mail (SPF/DMARC):"
dig +short TXT "$DOMAIN" | grep -E "v=spf1|v=DMARC1" || echo "  ⚠️  No SPF/DMARC found"
echo ""

echo "=== Verification Complete ==="
