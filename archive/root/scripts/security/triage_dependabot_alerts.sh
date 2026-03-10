#!/usr/bin/env bash
set -euo pipefail

# Triage Dependabot security alerts and generate actionable reports
# Converts GitHub's 119+ vulnerability alerts into structured backlog

REPO="${REPO:-Insightpulseai/odoo}"
OUTPUT_DIR="${OUTPUT_DIR:-docs/security/dependabot}"

echo "========================================="
echo "  Dependabot Alert Triage"
echo "  Repository: ${REPO}"
echo "========================================="

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Export alerts from GitHub API
echo ""
echo "Fetching Dependabot alerts from GitHub..."
ALERTS_FILE="${OUTPUT_DIR}/alerts_$(date +%Y%m%d-%H%M).json"

if gh api "repos/${REPO}/dependabot/alerts" --paginate > "${ALERTS_FILE}" 2>&1; then
  echo "✅ Alerts exported to: ${ALERTS_FILE}"
else
  echo "❌ Failed to fetch alerts. Check GitHub CLI auth and token scopes."
  echo "   Required scope: security_events (for Dependabot alerts)"
  echo "   Run: gh auth refresh -s security_events"
  exit 1
fi

# Generate severity summary
echo ""
echo "Analyzing severity distribution..."
SUMMARY_FILE="${OUTPUT_DIR}/summary_$(date +%Y%m%d-%H%M).txt"

python3 - <<PY > "${SUMMARY_FILE}"
import json
import sys
from collections import defaultdict

try:
    with open("${ALERTS_FILE}") as f:
        alerts = json.load(f)
except Exception as e:
    print(f"Error reading alerts file: {e}", file=sys.stderr)
    sys.exit(1)

# Severity breakdown
severity_counts = defaultdict(int)
ecosystem_counts = defaultdict(int)
state_counts = defaultdict(int)

for alert in alerts:
    # Get severity
    sev = alert.get("security_vulnerability", {}).get("severity", "unknown")
    severity_counts[sev] += 1

    # Get ecosystem (npm, pip, etc.)
    pkg = alert.get("security_vulnerability", {}).get("package", {})
    eco = pkg.get("ecosystem", "unknown")
    ecosystem_counts[eco] += 1

    # Get state (open, dismissed, fixed)
    state = alert.get("state", "unknown")
    state_counts[state] += 1

print("Dependabot Alert Summary")
print("=" * 60)
print(f"Total Alerts: {len(alerts)}")
print()

print("By Severity:")
for sev in ["critical", "high", "moderate", "low", "unknown"]:
    count = severity_counts.get(sev, 0)
    if count > 0:
        print(f"  {sev.upper():10s}: {count:3d}")
print()

print("By Ecosystem:")
for eco, count in sorted(ecosystem_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {eco:10s}: {count:3d}")
print()

print("By State:")
for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {state:10s}: {count:3d}")
print()

# Generate actionable list (critical and high severity, open state)
print("Critical & High Severity (Open):")
print("-" * 60)
priority_alerts = [
    a for a in alerts
    if a.get("state") == "open"
    and a.get("security_vulnerability", {}).get("severity") in ["critical", "high"]
]

for i, alert in enumerate(priority_alerts[:20], 1):  # Limit to top 20
    pkg = alert.get("security_vulnerability", {}).get("package", {})
    vuln = alert.get("security_vulnerability", {})

    pkg_name = pkg.get("name", "unknown")
    eco = pkg.get("ecosystem", "unknown")
    sev = vuln.get("severity", "unknown")
    cve = alert.get("security_advisory", {}).get("cve_id", "N/A")

    print(f"{i:2d}. [{sev.upper()}] {eco}/{pkg_name} - {cve}")

if len(priority_alerts) > 20:
    print(f"... and {len(priority_alerts) - 20} more")
PY

# Display summary
cat "${SUMMARY_FILE}"

# Save latest link for convenience
ln -sf "$(basename ${ALERTS_FILE})" "${OUTPUT_DIR}/latest.json"
ln -sf "$(basename ${SUMMARY_FILE})" "${OUTPUT_DIR}/latest.txt"

echo ""
echo "========================================="
echo "  ✅ Triage complete"
echo "========================================="
echo "  Raw alerts: ${OUTPUT_DIR}/latest.json"
echo "  Summary:    ${OUTPUT_DIR}/latest.txt"
echo ""
echo "Next steps:"
echo "  1. Review ${OUTPUT_DIR}/latest.txt for priority items"
echo "  2. Create GitHub issues: gh issue create --title 'CVE-...' --body-file ..."
echo "  3. Track remediation in Projects or task management system"
