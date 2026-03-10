# Integration Provisioners

This directory contains provisioner scripts for marketplace integrations.

## Overview

Each integration in `registry/integrations/` references a `provisioner` script that handles:
1. Environment variable validation
2. Service configuration
3. Health checks
4. Audit event logging

## Provisioner Contract

All provisioner scripts must:

1. **Accept standard arguments:**
   ```bash
   ./install_<integration>.sh [--dry-run] [--verbose]
   ```

2. **Validate required environment variables:**
   - Exit with code 1 if required vars are missing
   - Print clear error message

3. **Be idempotent:**
   - Safe to run multiple times
   - Skip already-configured resources

4. **Output JSON status:**
   ```json
   {
     "status": "success|failed",
     "integration_id": "supabase",
     "timestamp": "2026-01-26T00:00:00Z",
     "details": {}
   }
   ```

5. **Log to audit trail:**
   - Write to `docs/evidence/<date>/provisioner/<integration>.json`

## Available Provisioners

| Script | Integration | Status |
|--------|-------------|--------|
| `install_playwright_ci.sh` | playwright-testing | TODO |
| `install_github_projects_templates.sh` | github-projects-v2 | TODO |
| `install_supabase.sh` | supabase | TODO |
| `install_n8n.sh` | n8n-workflow | TODO |
| `install_vercel_connector.sh` | vercel-observability | TODO |
| `install_mattermost.sh` | mattermost | TODO |
| `install_digitalocean.sh` | digitalocean | TODO |
| `install_superset.sh` | apache-superset | TODO |
| `install_keycloak.sh` | keycloak | TODO |
| `install_odoo_mcp.sh` | odoo-erp | TODO |
| `install_figma.sh` | figma | TODO |
| `install_claude.sh` | claude-ai | TODO |

## Template

```bash
#!/usr/bin/env bash
# Provisioner: <integration-id>
# Registry: registry/integrations/<integration-id>.json

set -euo pipefail

INTEGRATION_ID="<integration-id>"
REQUIRED_VARS=("VAR1" "VAR2")
DRY_RUN=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --verbose) VERBOSE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate environment
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: Required environment variable $var is not set"
        exit 1
    fi
done

# Execute provisioning
if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY-RUN] Would configure $INTEGRATION_ID"
else
    # TODO: Actual provisioning logic
    echo "Configuring $INTEGRATION_ID..."
fi

# Output status
cat <<EOF
{
  "status": "success",
  "integration_id": "$INTEGRATION_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "dry_run": $DRY_RUN
}
EOF
```
