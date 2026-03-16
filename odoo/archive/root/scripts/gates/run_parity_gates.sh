#!/usr/bin/env bash
#
# Tier-0 Parity Gate Runner
#
# Reproduces CI Tier-0 gates locally with artifact generation.
# Usage: bash scripts/gates/run_parity_gates.sh [seed-audit|install-smoke|docs-build|forbidden-scan|all]
#
# Exit codes:
#   0 = all gates passed
#   1 = one or more gates failed
#   2 = usage error / prerequisites missing
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ARTIFACTS_DIR="$REPO_ROOT/artifacts"
GATE_START_TIME=$(date +%s)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create artifacts directory
mkdir -p "$ARTIFACTS_DIR"

# Initialize gate summary
GATE_SUMMARY_FILE="$ARTIFACTS_DIR/gate_run_summary.json"
cat > "$GATE_SUMMARY_FILE" << EOF
{
  "run_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "gates": {},
  "overall_status": "pending"
}
EOF

# Gate status tracking
GATES_PASSED=0
GATES_FAILED=0
GATES_TOTAL=0

# Helper: Update gate summary
update_gate_summary() {
  local gate_name=$1
  local status=$2
  local duration=$3
  local artifact_path=$4

  python3 << PYEOF
import json
with open("$GATE_SUMMARY_FILE", "r") as f:
    data = json.load(f)
data["gates"]["$gate_name"] = {
    "status": "$status",
    "duration_seconds": $duration,
    "artifact": "$artifact_path"
}
with open("$GATE_SUMMARY_FILE", "w") as f:
    json.dump(data, f, indent=2)
PYEOF
}

# Helper: Print gate status
print_gate_status() {
  local gate_name=$1
  local status=$2

  if [ "$status" = "PASS" ]; then
    echo -e "${GREEN}✓ $gate_name${NC}"
  else
    echo -e "${RED}✗ $gate_name${NC}"
  fi
}

# Helper: Update overall summary
finalize_summary() {
  local overall_status=$1
  local total_duration=$2

  python3 << PYEOF
import json
with open("$GATE_SUMMARY_FILE", "r") as f:
    data = json.load(f)
data["overall_status"] = "$overall_status"
data["total_duration_seconds"] = $total_duration
data["gates_passed"] = $GATES_PASSED
data["gates_failed"] = $GATES_FAILED
data["gates_total"] = $GATES_TOTAL
with open("$GATE_SUMMARY_FILE", "w") as f:
    json.dump(data, f, indent=2)
PYEOF
}

# ======================
# GATE 1: SEED AUDIT
# ======================
gate_seed_audit() {
  echo "====================================="
  echo "GATE 1: Finance PPM Seed Audit"
  echo "====================================="

  local start_time=$(date +%s)
  local artifact_file="$ARTIFACTS_DIR/seed_audit.json"

  GATES_TOTAL=$((GATES_TOTAL + 1))

  # Run Python seed audit
  if python3 "$REPO_ROOT/scripts/generate_seed_audit_artifact.py" --output "$artifact_file"; then
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo
    echo "Seed audit passed. Artifact: $artifact_file"
    update_gate_summary "seed-audit" "PASS" "$duration" "$artifact_file"
    print_gate_status "Seed Audit" "PASS"
    GATES_PASSED=$((GATES_PASSED + 1))
    return 0
  else
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo
    echo "ERROR: Seed audit failed. See $artifact_file for details."
    update_gate_summary "seed-audit" "FAIL" "$duration" "$artifact_file"
    print_gate_status "Seed Audit" "FAIL"
    GATES_FAILED=$((GATES_FAILED + 1))
    return 1
  fi
}

# ======================
# GATE 2: INSTALL SMOKE
# ======================
gate_install_smoke() {
  echo "====================================="
  echo "GATE 2: Clean Install Smoke Test"
  echo "====================================="

  local start_time=$(date +%s)
  local artifact_file="$ARTIFACTS_DIR/install_proof.txt"

  GATES_TOTAL=$((GATES_TOTAL + 1))

  # Check if Docker is available
  if ! command -v docker &> /dev/null; then
    echo "WARNING: Docker not found. Skipping install smoke test."
    echo "Install smoke test requires Docker. Skipped due to missing dependency." > "$artifact_file"
    update_gate_summary "install-smoke" "SKIP" "0" "$artifact_file"
    print_gate_status "Install Smoke" "SKIP"
    return 0
  fi

  # Check if docker compose is running
  if ! docker compose ps &> /dev/null; then
    echo "WARNING: Docker Compose not running. Skipping install smoke test."
    echo "Install smoke test requires Docker Compose. Skipped due to service not running." > "$artifact_file"
    update_gate_summary "install-smoke" "SKIP" "0" "$artifact_file"
    print_gate_status "Install Smoke" "SKIP"
    return 0
  fi

  # Create fresh test database and install canonical modules
  {
    echo "Install Smoke Test - $(date)"
    echo "================================"
    echo
    echo "Database: odoo_fresh_test"
    echo "Modules: ipai_enterprise_bridge,ipai_scout_bundle,ipai_ces_bundle"
    echo
    echo "Installation log:"
    echo "---"

    # Drop and recreate test database
    docker compose exec -T db psql -U odoo -c "DROP DATABASE IF EXISTS odoo_fresh_test;" || true
    docker compose exec -T db psql -U odoo -c "CREATE DATABASE odoo_fresh_test;"

    # Install modules
    docker compose exec -T odoo odoo -d odoo_fresh_test \
      -i ipai_enterprise_bridge,ipai_scout_bundle,ipai_ces_bundle \
      --stop-after-init --log-level=error --without-demo=all 2>&1 | tail -50

    echo "---"
    echo
    echo "Exit code: $?"
    echo "Duration: $(($(date +%s) - start_time)) seconds"

  } > "$artifact_file"

  local exit_code=${PIPESTATUS[0]}
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))

  # Check for ERROR or CRITICAL in output
  if grep -qi "ERROR\|CRITICAL" "$artifact_file"; then
    exit_code=1
  fi

  if [ $exit_code -eq 0 ]; then
    echo
    echo "Install smoke test passed. Artifact: $artifact_file"
    update_gate_summary "install-smoke" "PASS" "$duration" "$artifact_file"
    print_gate_status "Install Smoke" "PASS"
    GATES_PASSED=$((GATES_PASSED + 1))

    # Cleanup test database
    docker compose exec -T db psql -U odoo -c "DROP DATABASE IF EXISTS odoo_fresh_test;" || true

    return 0
  else
    echo
    echo "ERROR: Install smoke test failed. See $artifact_file for details."
    update_gate_summary "install-smoke" "FAIL" "$duration" "$artifact_file"
    print_gate_status "Install Smoke" "FAIL"
    GATES_FAILED=$((GATES_FAILED + 1))
    return 1
  fi
}

# ======================
# GATE 3: DOCS BUILD
# ======================
gate_docs_build() {
  echo "====================================="
  echo "GATE 3: MkDocs Strict Build"
  echo "====================================="

  local start_time=$(date +%s)
  local artifact_dir="$ARTIFACTS_DIR/docs_site"

  GATES_TOTAL=$((GATES_TOTAL + 1))

  # Check if mkdocs is installed
  if ! command -v mkdocs &> /dev/null; then
    echo "Installing MkDocs requirements..."
    pip install -q -r "$REPO_ROOT/requirements-docs.txt" || {
      echo "ERROR: Failed to install MkDocs requirements"
      update_gate_summary "docs-build" "FAIL" "0" "$artifact_dir"
      print_gate_status "Docs Build" "FAIL"
      GATES_FAILED=$((GATES_FAILED + 1))
      return 1
    }
  fi

  # Build docs with strict mode
  cd "$REPO_ROOT"
  if mkdocs build --strict --site-dir "$artifact_dir" 2>&1 | tee "$ARTIFACTS_DIR/docs_build.log"; then
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo
    echo "Docs build passed. Artifact: $artifact_dir"
    update_gate_summary "docs-build" "PASS" "$duration" "$artifact_dir"
    print_gate_status "Docs Build" "PASS"
    GATES_PASSED=$((GATES_PASSED + 1))
    return 0
  else
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo
    echo "ERROR: Docs build failed. See $ARTIFACTS_DIR/docs_build.log for details."
    update_gate_summary "docs-build" "FAIL" "$duration" "$artifact_dir"
    print_gate_status "Docs Build" "FAIL"
    GATES_FAILED=$((GATES_FAILED + 1))
    return 1
  fi
}

# ======================
# GATE 4: FORBIDDEN PATTERNS
# ======================
gate_forbidden_scan() {
  echo "====================================="
  echo "GATE 4: Forbidden Patterns Scan"
  echo "====================================="

  local start_time=$(date +%s)
  local artifact_file="$ARTIFACTS_DIR/forbidden_scan.txt"

  GATES_TOTAL=$((GATES_TOTAL + 1))

  # Check if ripgrep is installed
  if ! command -v rg &> /dev/null; then
    echo "WARNING: ripgrep (rg) not found. Using grep fallback (slower)."
  fi

  {
    echo "Forbidden Patterns Scan - $(date)"
    echo "================================="
    echo

    # Scan for forbidden patterns
    local has_violations=0

    echo "1. Scanning for Mailgun references..."
    if command -v rg &> /dev/null; then
      rg -n "mailgun|mg\.insightpulseai" README.md docs/ 2>/dev/null && has_violations=1 || true
    else
      grep -rn "mailgun\|mg\.insightpulseai" README.md docs/ 2>/dev/null && has_violations=1 || true
    fi

    echo
    echo "2. Scanning for .net domain references..."
    if command -v rg &> /dev/null; then
      rg -n "insightpulseai\.net" README.md docs/ mkdocs.yml 2>/dev/null && has_violations=1 || true
    else
      grep -rn "insightpulseai\.net" README.md docs/ mkdocs.yml 2>/dev/null && has_violations=1 || true
    fi

    echo
    echo "3. Scanning for Odoo 18 references..."
    if command -v rg &> /dev/null; then
      rg -n "Odoo 18|odoo.*18" README.md docs/ mkdocs.yml 2>/dev/null && has_violations=1 || true
    else
      grep -rn "Odoo 18\|odoo.*18" README.md docs/ mkdocs.yml 2>/dev/null && has_violations=1 || true
    fi

    echo
    echo "4. Scanning for Plane references..."
    if command -v rg &> /dev/null; then
      rg -n "Plane" README.md docs/ 2>/dev/null && has_violations=1 || true
    else
      grep -rn "Plane" README.md docs/ 2>/dev/null && has_violations=1 || true
    fi

    echo
    echo "================================="
    if [ $has_violations -eq 0 ]; then
      echo "Result: No forbidden patterns found"
    else
      echo "Result: Forbidden patterns detected (see output above)"
    fi

    exit $has_violations

  } > "$artifact_file" 2>&1

  local exit_code=$?
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))

  if [ $exit_code -eq 0 ]; then
    echo
    echo "Forbidden patterns scan passed. Artifact: $artifact_file"
    update_gate_summary "forbidden-scan" "PASS" "$duration" "$artifact_file"
    print_gate_status "Forbidden Scan" "PASS"
    GATES_PASSED=$((GATES_PASSED + 1))
    return 0
  else
    echo
    echo "ERROR: Forbidden patterns detected. See $artifact_file for details."
    update_gate_summary "forbidden-scan" "FAIL" "$duration" "$artifact_file"
    print_gate_status "Forbidden Scan" "FAIL"
    GATES_FAILED=$((GATES_FAILED + 1))
    return 1
  fi
}

# ======================
# MAIN EXECUTION
# ======================
main() {
  local gate_command=${1:-all}

  echo
  echo "╔══════════════════════════════════════════════════════╗"
  echo "║       Tier-0 Parity Gate Runner                     ║"
  echo "║       Odoo.sh-Grade Quality Validation              ║"
  echo "╚══════════════════════════════════════════════════════╝"
  echo

  case "$gate_command" in
    seed-audit)
      gate_seed_audit || true
      ;;
    install-smoke)
      gate_install_smoke || true
      ;;
    docs-build)
      gate_docs_build || true
      ;;
    forbidden-scan)
      gate_forbidden_scan || true
      ;;
    all)
      gate_seed_audit || true
      gate_install_smoke || true
      gate_docs_build || true
      gate_forbidden_scan || true
      ;;
    *)
      echo "Usage: $0 [seed-audit|install-smoke|docs-build|forbidden-scan|all]"
      echo
      echo "Available gates:"
      echo "  seed-audit      - Validate Finance PPM seed determinism"
      echo "  install-smoke   - Clean DB install smoke test"
      echo "  docs-build      - MkDocs strict build"
      echo "  forbidden-scan  - Detect deprecated patterns"
      echo "  all             - Run all Tier-0 gates (default)"
      exit 2
      ;;
  esac

  # Finalize summary
  local gate_end_time=$(date +%s)
  local total_duration=$((gate_end_time - GATE_START_TIME))

  if [ $GATES_FAILED -eq 0 ]; then
    finalize_summary "PASS" "$total_duration"
  else
    finalize_summary "FAIL" "$total_duration"
  fi

  echo
  echo "====================================="
  echo "GATE RUN SUMMARY"
  echo "====================================="
  echo "Passed: $GATES_PASSED"
  echo "Failed: $GATES_FAILED"
  echo "Total:  $GATES_TOTAL"
  echo "Duration: ${total_duration}s"
  echo
  echo "Artifacts: $ARTIFACTS_DIR"
  echo "Summary: $GATE_SUMMARY_FILE"
  echo "====================================="

  if [ $GATES_FAILED -eq 0 ]; then
    echo -e "${GREEN}All gates passed!${NC}"
    exit 0
  else
    echo -e "${RED}$GATES_FAILED gate(s) failed!${NC}"
    exit 1
  fi
}

main "$@"
