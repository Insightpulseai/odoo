# Common Workflows

## Verification Commands

```bash
# Before any commit
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

## Module Development

```bash
# Create new IPAI module
mrbob bobtemplates.odoo:addon
mv <module_name> addons/ipai/

# Test module
./scripts/ci/run_odoo_tests.sh <module_name>

# Deploy module
docker compose exec odoo-core odoo -d odoo_core -u <module_name> --stop-after-init
```

## Git Operations

```bash
# Standard commit
git add . && git commit -m "feat(scope): description"

# Push to feature branch
git push -u origin claude/<feature>-<session_id>

# Create PR
gh pr create --title "feat: description" --body "## Summary\n..."
```

## Evidence Generation

```bash
# Create evidence pack
EVIDENCE_DIR="docs/evidence/$(date +%Y%m%d-%H%M)/<scope>"
mkdir -p "$EVIDENCE_DIR"

# Capture git state
git log -1 --format="%H %s" > "$EVIDENCE_DIR/git_state.txt"
git diff --stat HEAD~1 >> "$EVIDENCE_DIR/git_state.txt"

# Capture health check
curl -s http://localhost:8069/web/health > "$EVIDENCE_DIR/health.json"
```

## Marketplace Integrations

```bash
# Log webhook event
SELECT marketplace.log_webhook_event(
    'github', 'workflow_run', 'event-123', '{"data": "..."}'::JSONB
);

# Check sync status
SELECT * FROM marketplace.v_recent_syncs LIMIT 10;

# Check integration health
SELECT * FROM marketplace.v_integration_health;
```
