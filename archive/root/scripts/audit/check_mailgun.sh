#!/usr/bin/env bash
set -euo pipefail

: "${MAILGUN_API_KEY:?Set MAILGUN_API_KEY}"
: "${MAILGUN_DOMAIN:?Set MAILGUN_DOMAIN}"
MAILGUN_REGION="${MAILGUN_REGION:-us}"

BASE="https://api.mailgun.net/v3"
if [ "$MAILGUN_REGION" = "eu" ]; then
  BASE="https://api.eu.mailgun.net/v3"
fi

OUT_JSON="${1:-out/mailgun_audit.json}"
mkdir -p "$(dirname "$OUT_JSON")"

curl -sS -u "api:${MAILGUN_API_KEY}" \
  "${BASE}/domains/${MAILGUN_DOMAIN}" \
  | python3 - <<'PY' "$OUT_JSON"
import json, sys
out_path=sys.argv[1]
data=json.load(sys.stdin)

# distill key verification signals
dist={
  "domain": data.get("domain", {}).get("name") or data.get("name"),
  "state": data.get("domain", {}).get("state") or data.get("state"),
  "smtp_login": data.get("domain", {}).get("smtp_login") or data.get("smtp_login"),
  "require_tls": data.get("domain", {}).get("require_tls") or data.get("require_tls"),
  "skip_verification": data.get("domain", {}).get("skip_verification") or data.get("skip_verification"),
  "receiving_dns_records": data.get("receiving_dns_records") or data.get("domain", {}).get("receiving_dns_records"),
  "sending_dns_records": data.get("sending_dns_records") or data.get("domain", {}).get("sending_dns_records"),
  "raw": data,
}
with open(out_path,"w",encoding="utf-8") as f:
  json.dump(dist, f, indent=2)
print(f"Wrote {out_path}")
PY
