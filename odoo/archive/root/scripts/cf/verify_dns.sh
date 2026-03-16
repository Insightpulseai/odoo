#!/usr/bin/env bash
set -euo pipefail

zone="${1:?Usage: verify_dns.sh <zone>}"
origin="${2:-}"

dig_cmd() { command -v dig >/dev/null 2>&1 && dig "$@" || true; }

echo "== A records =="
dig_cmd +short A "${zone}"
dig_cmd +short A "www.${zone}"
dig_cmd +short A "erp.${zone}"
dig_cmd +short A "n8n.${zone}"

echo "== MX records =="
dig_cmd +short MX "${zone}"

echo "== SPF (TXT @) =="
dig_cmd +short TXT "${zone}"

echo "== DMARC (TXT _dmarc) =="
dig_cmd +short TXT "_dmarc.${zone}"

if [[ -n "${origin}" ]]; then
  echo "== Checking apex A equals expected origin: ${origin} =="
  actual="$(dig_cmd +short A "${zone}" | head -n1 || true)"
  [[ "${actual}" == "${origin}" ]] && echo "OK" || (echo "WARN: ${actual} != ${origin}" && exit 1)
fi
