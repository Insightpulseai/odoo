#!/usr/bin/env bash
# =============================================================================
# OCA Repository Sync Script
# =============================================================================
# Purpose: Deterministic sync of OCA submodules for Odoo 18.0
# Usage:
#   ./scripts/oca-update.sh --profile standard    # 14 repos (production)
#   ./scripts/oca-update.sh --profile parity      # 32 repos (full enterprise parity)
#   ./scripts/oca-update.sh --list               # List available repos
#
# OCA Repos Source: https://github.com/OCA
# Branch: 18.0 (Odoo 18.0 compatibility)
# =============================================================================

set -euo pipefail

PROFILE="${1:---profile}"
MODE="${2:-standard}"

# =============================================================================
# Standard Profile - 14 OCA Repos (Production)
# =============================================================================
STANDARD_REPOS=(
  "reporting-engine"
  "account-closing"
  "account-financial-reporting"
  "account-financial-tools"
  "account-invoicing"
  "project"
  "hr-expense"
  "purchase-workflow"
  "maintenance"
  "dms"
  "calendar"
  "web"
  "contract"
  "server-tools"
)

# =============================================================================
# Parity Profile - Additional 18 OCA Repos (Enterprise Parity)
# =============================================================================
PARITY_ADDITIONAL=(
  "account-reconcile"
  "bank-payment"
  "commission"
  "crm"
  "field-service"
  "helpdesk"
  "hr"
  "knowledge"
  "manufacture"
  "mis-builder"
  "partner-contact"
  "payroll"
  "sale-workflow"
  "server-ux"
  "social"
  "stock-logistics-warehouse"
  "stock-logistics-workflow"
  "timesheet"
)

# =============================================================================
# Functions
# =============================================================================

list_repos() {
  echo "=========================================="
  echo "Available OCA Repositories"
  echo "=========================================="
  echo ""
  echo "STANDARD PROFILE (14 repos):"
  for repo in "${STANDARD_REPOS[@]}"; do
    echo "  - $repo"
  done
  echo ""
  echo "PARITY ADDITIONAL (18 repos):"
  for repo in "${PARITY_ADDITIONAL[@]}"; do
    echo "  - $repo"
  done
  echo ""
  echo "TOTAL (32 repos)"
  echo "=========================================="
}

add_submodule() {
  local repo=$1
  local path="external-src/$repo"
  local url="https://github.com/OCA/$repo.git"

  if [ -d "$path" ]; then
    echo "  [EXISTS] $repo"
  else
    echo "  [ADD] $repo"
    git submodule add -b 18.0 "$url" "$path"
  fi
}

sync_repos() {
  local profile=$1

  echo "=========================================="
  echo "OCA Repository Sync - $profile"
  echo "=========================================="
  echo ""

  # Always include standard repos
  echo "Syncing STANDARD repos (14)..."
  for repo in "${STANDARD_REPOS[@]}"; do
    add_submodule "$repo"
  done

  # Add parity repos if requested
  if [ "$profile" == "parity" ]; then
    echo ""
    echo "Syncing PARITY ADDITIONAL repos (18)..."
    for repo in "${PARITY_ADDITIONAL[@]}"; do
      add_submodule "$repo"
    done
  fi

  echo ""
  echo "=========================================="
  echo "Sync Complete"
  echo "=========================================="
  echo ""

  # Update all submodules
  echo "Updating submodule references..."
  git submodule update --init --recursive

  # Show status
  echo ""
  echo "Submodule Status:"
  git submodule status | wc -l
  echo "  repos initialized"
}

verify_repos() {
  local profile=$1
  local expected_count=14

  if [ "$profile" == "parity" ]; then
    expected_count=32
  fi

  local actual_count=$(git submodule status | wc -l | tr -d ' ')

  echo ""
  echo "=========================================="
  echo "Verification"
  echo "=========================================="
  echo "Expected: $expected_count repos"
  echo "Actual:   $actual_count repos"

  if [ "$actual_count" -eq "$expected_count" ]; then
    echo "Status:   ✅ PASS"
    exit 0
  else
    echo "Status:   ❌ FAIL (mismatch)"
    exit 1
  fi
}

# =============================================================================
# Main
# =============================================================================

case "${PROFILE}" in
  --list)
    list_repos
    ;;
  --profile)
    if [ "$MODE" != "standard" ] && [ "$MODE" != "parity" ]; then
      echo "ERROR: Invalid profile. Use 'standard' or 'parity'"
      echo "Usage: ./scripts/oca-update.sh --profile standard|parity"
      exit 1
    fi
    sync_repos "$MODE"
    verify_repos "$MODE"
    ;;
  *)
    echo "Usage:"
    echo "  ./scripts/oca-update.sh --profile standard    # 14 repos"
    echo "  ./scripts/oca-update.sh --profile parity      # 32 repos"
    echo "  ./scripts/oca-update.sh --list               # List repos"
    exit 1
    ;;
esac
