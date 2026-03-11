#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$REPO_ROOT/catalog/ee_surface"
mkdir -p "$OUT_DIR"

TMP_JSON="$(mktemp)"
trap 'rm -f "$TMP_JSON"' EXIT

chmod +x "$REPO_ROOT/scripts/ee_surface/generate_ee_surface_catalog.py"
"$REPO_ROOT/scripts/ee_surface/generate_ee_surface_catalog.py" > "$TMP_JSON"

# Minimal curation:
# - Keep only items that are very likely "surfaces" (exclude pure app names like "Accounting", "CRM" etc.)
# - You will apply final enterprise_only marking via ipai scope overlay (below).

python3 - <<'PY' "$TMP_JSON" "$OUT_DIR/ee_surface_candidates.json"
import json, sys, re
src, dst = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(src))
    c = data["candidates"]

    # Filter out top-level app names that are almost certainly modules rather than surfaces.
    # We keep "↳ ..." style subfeatures and common cross-cutting features (AI, OCR, Spreadsheet, Sign, etc.).
    keep = []
    drop_exact = {
      "Accounting","Invoicing","Expenses","CRM","Sales","Point of Sale","Subscriptions","Rental",
      "Website Builder","eCommerce","Blog","Forum","Live Chat","eLearning",
      "Inventory","Manufacturing (MRP)","PLM","Purchase","Maintenance","Quality"
    }
    for s in c:
        label = s["label"].strip()
        if label in drop_exact:
            continue
        # keep subfeatures and notable cross-cutting surfaces
        if label.startswith("↳") or any(k in label.lower() for k in ["ai","ocr","spreadsheet","sign","sso","studio","voip","iot","upgrade","hosting"]):
            keep.append(s)

    out = {
      "source": data["source"],
      "generated_at": "generated-by-curate_surface_catalog.sh",
      "surfaces": keep
    }
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"Wrote {len(keep)} curated candidates -> {dst}")
except Exception as e:
    print(f"Error processing JSON: {e}", file=sys.stderr)
    sys.exit(1)
PY

echo "OK"
