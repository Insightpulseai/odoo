#!/bin/bash
# Create PR for EE Parity Test Runner
# Usage: ./scripts/create_parity_pr.sh

set -euo pipefail

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Create PR
gh pr create \
    --title "feat(parity): add Odoo 19 EE parity test runner framework" \
    --body "$(cat <<'EOF'
## Summary

Add automated parity testing framework to validate CE + OCA + ipai_* stack against Odoo Enterprise Edition features.

## Components

| File | Purpose |
|------|---------|
| `tools/parity/test_ee_parity.py` | Python test suite (14 tests) |
| `tools/parity/run_ee_parity.sh` | CLI wrapper |
| `tools/parity/PARITY_TESTING.md` | Feature checklist (76 items) |
| `tools/parity/superset_parity_dashboard.sql` | Superset SQL views |
| `.github/workflows/ee-parity-test-runner.yml` | CI workflow |
| `supabase/migrations/20260126_000001_ee_parity_tracking.sql` | Schema migration |
| `scripts/deploy_parity_schema.sh` | Manual deployment script |
| `docs/setup/PARITY_TEST_RUNNER_SECRETS.md` | Secrets documentation |

## Test Categories

| Category | Tests | Focus |
|----------|-------|-------|
| Accounting | 3 | GL, bank reconciliation, asset management |
| Payroll | 5 | SSS, PhilHealth, BIR withholding, 1601-C (PH) |
| Approvals | 2 | Request types, multi-level routing |
| Helpdesk | 2 | Tickets, SLA tracking |
| Planning | 2 | Shifts, conflict detection |

## Usage

```bash
# Run all parity tests
./tools/parity/run_ee_parity.sh

# Run specific category
./tools/parity/run_ee_parity.sh -c payroll

# Generate HTML report
./tools/parity/run_ee_parity.sh -f html -o /tmp/report.html

# Generate JSON for Superset
./tools/parity/run_ee_parity.sh -f json -o /tmp/report.json
```

## Required Secrets

See `docs/setup/PARITY_TEST_RUNNER_SECRETS.md` for full list:
- `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASS`
- `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`

## Test Plan

- [x] Python syntax validation
- [x] Bash script executable
- [x] CI workflow created
- [x] Supabase migration created
- [x] Deployment script created
- [x] Secrets documented
- [ ] Run against live Odoo instance
- [ ] Verify Superset dashboard views
EOF
)" \
    --base main

echo ""
echo "PR created successfully!"
