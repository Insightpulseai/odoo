#!/usr/bin/env bash
# scripts/ci/check_iceberg_etl_smoke.sh
#
# DuckDB Iceberg smoke gate — CI-blocking (T2-8)
#
# Exits 0 and prints "PASS" when:
#   - row_count > 0
#   - latest_event is within the last 60 seconds
#
# Exits 1 and prints "FAIL: <reason>" when:
#   - row_count = 0
#   - lag >= 60 seconds
#   - Iceberg read error (malformed scan, missing files)
#   - Any required ICEBERG_* env var is missing
#
# Required env vars (injected from GitHub Actions Secrets):
#   ICEBERG_WAREHOUSE         — warehouse root  (e.g. s3://ipai-warehouse/odoo)
#   ICEBERG_S3_ENDPOINT       — DO Spaces or MinIO endpoint
#   ICEBERG_REGION            — S3 region (e.g. sgp1)
#   ICEBERG_ACCESS_KEY_ID     — S3 access key
#   ICEBERG_SECRET_ACCESS_KEY — S3 secret key
#
# Usage:
#   bash scripts/ci/check_iceberg_etl_smoke.sh
#
# SSOT: spec/supabase-maximization/tasks.md § 2.10
# Workflow: .github/workflows/supabase-etl-expense.yml

set -euo pipefail

# ── Env var validation ──────────────────────────────────────────────────────
REQUIRED_VARS=(
  ICEBERG_WAREHOUSE
  ICEBERG_S3_ENDPOINT
  ICEBERG_REGION
  ICEBERG_ACCESS_KEY_ID
  ICEBERG_SECRET_ACCESS_KEY
)

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "FAIL: missing required env var: $var"
    exit 1
  fi
done

# ── DuckDB availability ─────────────────────────────────────────────────────
if ! command -v duckdb &>/dev/null; then
  echo "FAIL: duckdb not found — install with: pip install duckdb or brew install duckdb"
  exit 1
fi

ICEBERG_PATH="${ICEBERG_WAREHOUSE}/odoo_ops/expense"

# ── DuckDB smoke query ──────────────────────────────────────────────────────
RESULT=$(duckdb -csv -noheader <<SQL 2>&1
INSTALL iceberg;
LOAD iceberg;
SET s3_region='${ICEBERG_REGION}';
SET s3_endpoint='${ICEBERG_S3_ENDPOINT}';
SET s3_access_key_id='${ICEBERG_ACCESS_KEY_ID}';
SET s3_secret_access_key='${ICEBERG_SECRET_ACCESS_KEY}';
SET s3_url_style='path';

SELECT
  count(*)                                              AS row_count,
  max(_sdc_received_at)                                 AS latest_event,
  epoch_ms(now()) - epoch_ms(max(_sdc_received_at))    AS lag_ms
FROM iceberg_scan('${ICEBERG_PATH}/');
SQL
)

DUCKDB_EXIT=$?

if [ $DUCKDB_EXIT -ne 0 ]; then
  echo "FAIL: DuckDB Iceberg read error — ${RESULT}"
  exit 1
fi

# ── Parse CSV row: row_count,latest_event,lag_ms ────────────────────────────
ROW_COUNT=$(echo "$RESULT"  | cut -d',' -f1)
LAG_MS=$(echo "$RESULT"     | cut -d',' -f3)

# Guard: numeric check
if ! [[ "$ROW_COUNT" =~ ^[0-9]+$ ]]; then
  echo "FAIL: unexpected DuckDB output (row_count not numeric): ${RESULT}"
  exit 1
fi

if [ "$ROW_COUNT" -eq 0 ]; then
  echo "FAIL: row_count = 0 — no data in Iceberg table at ${ICEBERG_PATH}"
  exit 1
fi

LAG_S=$(( ${LAG_MS%.*} / 1000 ))

if [ "$LAG_S" -ge 60 ]; then
  echo "FAIL: lag = ${LAG_S}s >= 60s — ETL pipeline may be stalled"
  exit 1
fi

echo "PASS: row_count=${ROW_COUNT}, lag=${LAG_S}s (< 60s threshold)"
exit 0
