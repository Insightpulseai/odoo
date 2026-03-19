#!/usr/bin/env bash
# backup_verify.sh — Verify PostgreSQL backup freshness and integrity
# Usage: ./scripts/backup_verify.sh [backup_dir]
# Exit 0 = backup is fresh and valid, Exit 1 = stale or missing
#
# Checks:
#   1. Most recent backup file exists
#   2. Backup age < MAX_AGE_HOURS (default 25)
#   3. Backup size > MIN_SIZE_BYTES (default 1MB — not empty/corrupt)
#
# For DO Spaces (S3), set S3_ENDPOINT + S3_BUCKET + S3_PREFIX env vars
# and the script will check S3 instead of local filesystem.
set -euo pipefail

MAX_AGE_HOURS="${MAX_AGE_HOURS:-25}"
MIN_SIZE_BYTES="${MIN_SIZE_BYTES:-1048576}"  # 1MB
BACKUP_DIR="${1:-/var/backups/postgresql}"
PASS=0
FAIL=0

echo "=== Backup Freshness Verification ==="
echo ""

# -----------------------------------------------
# S3 mode (DO Spaces)
# -----------------------------------------------
if [ -n "${S3_ENDPOINT:-}" ] && [ -n "${S3_BUCKET:-}" ]; then
  S3_PREFIX="${S3_PREFIX:-pg-backups}"
  echo "Mode: S3 (${S3_ENDPOINT}/${S3_BUCKET}/${S3_PREFIX}/)"

  LATEST=$(aws --endpoint-url "${S3_ENDPOINT}" s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" \
    --recursive 2>/dev/null | sort | tail -1 || echo "")

  if [ -z "$LATEST" ]; then
    echo "  FAIL  No backups found in S3"
    FAIL=$((FAIL + 1))
  else
    SIZE=$(echo "$LATEST" | awk '{print $3}')
    DATE_STR=$(echo "$LATEST" | awk '{print $1 " " $2}')
    KEY=$(echo "$LATEST" | awk '{print $4}')

    echo "  Latest backup: $KEY"
    echo "  Size: $SIZE bytes"
    echo "  Date: $DATE_STR"

    # Check size
    if [ "$SIZE" -ge "$MIN_SIZE_BYTES" ]; then
      echo "  PASS  Size >= ${MIN_SIZE_BYTES} bytes"
      PASS=$((PASS + 1))
    else
      echo "  FAIL  Size $SIZE < ${MIN_SIZE_BYTES} bytes (possibly corrupt)"
      FAIL=$((FAIL + 1))
    fi

    # Check age
    BACKUP_EPOCH=$(date -d "$DATE_STR" +%s 2>/dev/null || echo "0")
    NOW_EPOCH=$(date +%s)
    AGE_HOURS=$(( (NOW_EPOCH - BACKUP_EPOCH) / 3600 ))

    if [ "$AGE_HOURS" -le "$MAX_AGE_HOURS" ]; then
      echo "  PASS  Age ${AGE_HOURS}h <= ${MAX_AGE_HOURS}h"
      PASS=$((PASS + 1))
    else
      echo "  FAIL  Age ${AGE_HOURS}h > ${MAX_AGE_HOURS}h (stale)"
      FAIL=$((FAIL + 1))
    fi
  fi

# -----------------------------------------------
# Local filesystem mode
# -----------------------------------------------
else
  echo "Mode: Local filesystem ($BACKUP_DIR)"

  if [ ! -d "$BACKUP_DIR" ]; then
    echo "  FAIL  Backup directory $BACKUP_DIR does not exist"
    FAIL=$((FAIL + 1))
  else
    LATEST=$(find "$BACKUP_DIR" -name "*.dump*" -o -name "*.sql*" -o -name "*.gz" 2>/dev/null | sort | tail -1 || echo "")

    if [ -z "$LATEST" ]; then
      echo "  FAIL  No backup files found in $BACKUP_DIR"
      FAIL=$((FAIL + 1))
    else
      SIZE=$(stat -c%s "$LATEST" 2>/dev/null || stat -f%z "$LATEST" 2>/dev/null || echo "0")
      MOD_EPOCH=$(stat -c%Y "$LATEST" 2>/dev/null || stat -f%m "$LATEST" 2>/dev/null || echo "0")
      NOW_EPOCH=$(date +%s)
      AGE_HOURS=$(( (NOW_EPOCH - MOD_EPOCH) / 3600 ))

      echo "  Latest backup: $LATEST"
      echo "  Size: $SIZE bytes"
      echo "  Age: ${AGE_HOURS}h"

      # Check size
      if [ "$SIZE" -ge "$MIN_SIZE_BYTES" ]; then
        echo "  PASS  Size >= ${MIN_SIZE_BYTES} bytes"
        PASS=$((PASS + 1))
      else
        echo "  FAIL  Size $SIZE < ${MIN_SIZE_BYTES} bytes"
        FAIL=$((FAIL + 1))
      fi

      # Check age
      if [ "$AGE_HOURS" -le "$MAX_AGE_HOURS" ]; then
        echo "  PASS  Age ${AGE_HOURS}h <= ${MAX_AGE_HOURS}h"
        PASS=$((PASS + 1))
      else
        echo "  FAIL  Age ${AGE_HOURS}h > ${MAX_AGE_HOURS}h (stale)"
        FAIL=$((FAIL + 1))
      fi
    fi
  fi
fi

echo ""
echo "=== Results: PASS=$PASS  FAIL=$FAIL ==="

if [ "$FAIL" -gt 0 ]; then
  echo "STATUS: FAIL"
  exit 1
fi

echo "STATUS: PASS"
exit 0
