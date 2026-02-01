#!/usr/bin/env bash
# =============================================================================
# Master Integration Audit Runner
# =============================================================================
# Runs all integration checks and produces evidence pack
#
# Usage:
#   ./scripts/audit/run_integration_audit.sh [--dry-run] [--integration NAME]
#
# Environment:
#   See config/integrations/integration_manifest.yaml for required env vars
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP="$(date -u '+%Y%m%d-%H%M%S')"
OUTPUT_DIR="${AUDIT_OUTPUT_DIR:-$REPO_ROOT/artifacts/audit/$TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SINGLE_INTEGRATION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --integration)
            SINGLE_INTEGRATION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create output directories
mkdir -p "$OUTPUT_DIR/raw"

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Master Integration Audit${NC}"
echo -e "${BLUE}  Timestamp: $TIMESTAMP${NC}"
echo -e "${BLUE}  Output: $OUTPUT_DIR${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Track results
declare -A RESULTS
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_SKIP=0

# Function to run a check
run_check() {
    local name="$1"
    local script="$2"

    if [[ -n "$SINGLE_INTEGRATION" && "$name" != "$SINGLE_INTEGRATION" ]]; then
        echo -e "  ${YELLOW}⏭️  Skipping $name (not selected)${NC}"
        RESULTS[$name]="SKIP"
        ((TOTAL_SKIP++)) || true
        return 0
    fi

    echo -e "${BLUE}▶ Running $name checks...${NC}"

    if [[ ! -f "$script" ]]; then
        echo -e "  ${YELLOW}⚠️  Script not found: $script${NC}"
        RESULTS[$name]="SKIP"
        ((TOTAL_SKIP++)) || true
        return 0
    fi

    local output_file="$OUTPUT_DIR/raw/${name}_audit.json"

    if $DRY_RUN; then
        echo -e "  ${YELLOW}[DRY RUN] Would execute: $script${NC}"
        RESULTS[$name]="SKIP"
        ((TOTAL_SKIP++)) || true
        return 0
    fi

    # Run the check script
    if python3 "$script" "$output_file" 2>&1 | tee -a "$OUTPUT_DIR/audit.log"; then
        # Check the output for status
        if [[ -f "$output_file" ]]; then
            local status
            status=$(python3 -c "import json; print(json.load(open('$output_file')).get('status', 'UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
            RESULTS[$name]="$status"
            case $status in
                PASS)
                    echo -e "  ${GREEN}✅ $name: PASS${NC}"
                    ((TOTAL_PASS++)) || true
                    ;;
                FAIL)
                    echo -e "  ${RED}❌ $name: FAIL${NC}"
                    ((TOTAL_FAIL++)) || true
                    ;;
                PARTIAL)
                    echo -e "  ${YELLOW}⚠️  $name: PARTIAL${NC}"
                    ((TOTAL_FAIL++)) || true
                    ;;
                *)
                    echo -e "  ${YELLOW}❓ $name: $status${NC}"
                    ((TOTAL_SKIP++)) || true
                    ;;
            esac
        else
            echo -e "  ${YELLOW}⚠️  No output file generated${NC}"
            RESULTS[$name]="SKIP"
            ((TOTAL_SKIP++)) || true
        fi
    else
        echo -e "  ${RED}❌ $name: Script failed${NC}"
        RESULTS[$name]="FAIL"
        ((TOTAL_FAIL++)) || true
    fi
    echo ""
}

# Check for required tools
echo -e "${BLUE}Checking prerequisites...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}python3 is required${NC}"; exit 1; }
echo -e "  ${GREEN}✓ python3 found${NC}"

# Check for requests library
if python3 -c "import requests" 2>/dev/null; then
    echo -e "  ${GREEN}✓ requests library found${NC}"
else
    echo -e "  ${YELLOW}⚠️  requests library not found, using urllib fallback${NC}"
fi
echo ""

# =============================================================================
# Run all integration checks
# =============================================================================

# Supabase
run_check "supabase" "$SCRIPT_DIR/checks/check_supabase.py"

# Vercel
run_check "vercel" "$SCRIPT_DIR/checks/check_vercel.py"

# GitHub
run_check "github" "$SCRIPT_DIR/checks/check_github.py"

# Odoo
run_check "odoo" "$SCRIPT_DIR/checks/check_odoo.py"

# DigitalOcean
run_check "digitalocean" "$SCRIPT_DIR/checks/check_digitalocean.py"

# Slack
run_check "slack" "$SCRIPT_DIR/checks/check_slack.py"

# Mailgun
run_check "mailgun" "$SCRIPT_DIR/checks/check_mailgun.py"

# n8n
run_check "n8n" "$SCRIPT_DIR/checks/check_n8n.py"

# Superset
run_check "superset" "$SCRIPT_DIR/checks/check_superset.py"

# Plane (optional)
if [[ -n "${PLANE_BASE_URL:-}" ]]; then
    run_check "plane" "$SCRIPT_DIR/checks/check_plane.py"
fi

# GCP (optional)
if [[ -n "${GCP_SERVICE_ACCOUNT_JSON:-}" || -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    run_check "gcp" "$SCRIPT_DIR/checks/check_gcp.py"
fi

# =============================================================================
# Aggregate results
# =============================================================================
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Generating Reports${NC}"
echo -e "${BLUE}=============================================${NC}"

# Aggregate all results into single JSON
python3 "$SCRIPT_DIR/aggregate_results.py" "$OUTPUT_DIR"

# Generate markdown report
python3 - <<'PYEOF' "$OUTPUT_DIR"
import json
import os
import sys
from datetime import datetime, timezone

output_dir = sys.argv[1]
results_file = os.path.join(output_dir, "integration_results.json")
report_file = os.path.join(output_dir, "integration_results.md")

if not os.path.exists(results_file):
    print("No results file found, skipping report generation")
    sys.exit(0)

with open(results_file) as f:
    data = json.load(f)

# Generate markdown
lines = [
    "# Integration Audit Report",
    "",
    f"**Generated:** {data.get('timestamp', datetime.now(timezone.utc).isoformat())}",
    f"**Duration:** {data.get('duration_seconds', 'N/A')} seconds",
    "",
    "## Summary",
    "",
    f"- **Total Integrations:** {data.get('total_integrations', 0)}",
    f"- **Passed:** {data.get('pass_count', 0)}",
    f"- **Failed:** {data.get('fail_count', 0)}",
    f"- **Skipped:** {data.get('skip_count', 0)}",
    "",
    "## Results by Integration",
    "",
    "| Integration | Status | Checks | Latency (avg) | Risk |",
    "|-------------|--------|--------|---------------|------|"
]

for result in data.get("results", []):
    status = result.get("status", "UNKNOWN")
    emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "SKIP": "⏭️"}.get(status, "❓")
    checks = result.get("checks", [])
    passed = sum(1 for c in checks if c.get("status") == "PASS")
    latency = result.get("latency_avg_ms", "N/A")
    risk = result.get("risk_tier", "unknown")
    lines.append(f"| {result.get('name', 'Unknown')} | {emoji} {status} | {passed}/{len(checks)} | {latency}ms | {risk} |")

lines.extend(["", "## Detailed Results", ""])

for result in data.get("results", []):
    name = result.get("name", "Unknown")
    status = result.get("status", "UNKNOWN")
    lines.extend([
        f"### {name}",
        "",
        f"**Status:** {status}  ",
        f"**Risk Tier:** {result.get('risk_tier', 'unknown')}  ",
        f"**Access Level:** {result.get('access_level', 'unknown')}  ",
        ""
    ])

    checks = result.get("checks", [])
    if checks:
        lines.append("#### Checks")
        lines.append("")
        for check in checks:
            cs = check.get("status", "UNKNOWN")
            emoji = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "SKIP": "⏭️"}.get(cs, "❓")
            lines.append(f"- {emoji} **{check.get('name', 'Unknown')}**: {check.get('description', '')}")
            if check.get("error"):
                lines.append(f"  - Error: `{check['error']}`")
        lines.append("")

    recs = result.get("recommendations", [])
    if recs:
        lines.append("#### Recommendations")
        lines.append("")
        for rec in recs:
            lines.append(f"- {rec}")
        lines.append("")

# Missing inputs section
missing = data.get("missing_inputs", {})
if missing:
    lines.extend(["## Missing Inputs", ""])
    for integration, vars in missing.items():
        if vars:
            lines.append(f"### {integration}")
            for var in vars:
                lines.append(f"- `{var}`")
            lines.append("")

with open(report_file, "w") as f:
    f.write("\n".join(lines))

print(f"Report written to {report_file}")
PYEOF

# Generate issues payload
python3 - <<'PYEOF' "$OUTPUT_DIR"
import json
import os
import sys

output_dir = sys.argv[1]
results_file = os.path.join(output_dir, "integration_results.json")
issues_file = os.path.join(output_dir, "issues_to_create.json")

if not os.path.exists(results_file):
    print("No results file found, skipping issues generation")
    sys.exit(0)

with open(results_file) as f:
    data = json.load(f)

issues = []
for result in data.get("results", []):
    if result.get("status") in ["FAIL", "PARTIAL"]:
        failed_checks = [c for c in result.get("checks", []) if c.get("status") == "FAIL"]

        severity = "critical" if result.get("risk_tier") == "critical" else "warning"
        labels = ["integration", "audit", severity]

        body_lines = [
            f"## Integration Audit Failure: {result.get('name', 'Unknown')}",
            "",
            f"**Status:** {result.get('status')}",
            f"**Risk Tier:** {result.get('risk_tier', 'unknown')}",
            f"**Timestamp:** {data.get('timestamp', 'unknown')}",
            "",
            "### Failed Checks",
            ""
        ]

        for check in failed_checks:
            body_lines.extend([
                f"#### {check.get('name', 'Unknown')}",
                f"- **Description:** {check.get('description', '')}",
                f"- **Error:** `{check.get('error', 'Unknown error')}`",
                ""
            ])

        recs = result.get("recommendations", [])
        if recs:
            body_lines.extend(["### Recommendations", ""])
            for rec in recs:
                body_lines.append(f"- {rec}")

        issues.append({
            "title": f"[Audit] {result.get('name', 'Unknown')} integration {result.get('status')}",
            "body": "\n".join(body_lines),
            "labels": labels,
            "component": result.get("name", "unknown").lower().replace(" ", "_"),
            "severity": severity
        })

with open(issues_file, "w") as f:
    json.dump(issues, f, indent=2)

print(f"Issues payload written to {issues_file} ({len(issues)} issues)")
PYEOF

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}  Audit Complete${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $TOTAL_PASS"
echo -e "  ${RED}Failed:${NC}  $TOTAL_FAIL"
echo -e "  ${YELLOW}Skipped:${NC} $TOTAL_SKIP"
echo ""
echo -e "  ${BLUE}Output directory:${NC} $OUTPUT_DIR"
echo ""

# List output files
echo "Generated files:"
ls -la "$OUTPUT_DIR/"
echo ""
echo "Raw audit files:"
ls -la "$OUTPUT_DIR/raw/" 2>/dev/null || echo "  (none)"

# Exit with error if any failures
if [[ $TOTAL_FAIL -gt 0 ]]; then
    echo ""
    echo -e "${RED}❌ Audit completed with failures${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ Audit completed successfully${NC}"
    exit 0
fi
