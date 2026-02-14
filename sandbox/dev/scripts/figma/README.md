# Figma Integration Scripts

Automated design token sync system for exporting Figma design artifacts with deterministic version tracking.

## Overview

This directory contains scripts for syncing Figma design tokens via:
- **Scheduled polling** (every 6 hours via GitHub Actions)
- **Manual triggers** (force sync workflow)
- **Future: Webhook relay** (near real-time via n8n - Phase 2)

## Architecture

```
Figma File → poll_file_version.sh (detect changes)
           → sync_figma_site.sh (orchestrate exports)
           → 6 artifact types (parallel export)
           → design-tokens/ directory
           → GitHub PR (review before merge)
```

## Scripts

### Core Scripts

#### `sync_figma_site.sh` (Orchestrator)
Master orchestrator that exports all Figma artifacts in parallel.

**Usage:**
```bash
source scripts/figma/load_figma_env.sh
./scripts/figma/sync_figma_site.sh
```

**Exports:**
1. `figma-styles.json` - Design styles (colors, text, effects)
2. `figma-components.json` - Component library metadata
3. `figma-variables.json` - Design variables (Enterprise only, graceful fail)
4. `figma-file.json` - Full file structure
5. `manifest.json` - Sites manifest (via Node.js script)
6. `figma-contract.json` - AI-first SDLC contract (via TypeScript script)

**Features:**
- Deterministic version tracking (skips if no changes)
- Parallel API calls for performance
- Graceful fallback for Enterprise-only endpoints
- Integration with existing Node.js/TypeScript export scripts

#### `poll_file_version.sh`
Deterministic change detection via Figma file version tracking.

**Usage:**
```bash
export FIGMA_ACCESS_TOKEN="..."
export FIGMA_FILE_KEY="7XCC5p6r9yDrMGCE9eI3LC"
./scripts/figma/poll_file_version.sh
```

**Outputs:**
- `artifacts/figma/poll_result.json` - Poll result with version info
- `artifacts/figma/figma_file_meta.json` - Full file metadata
- `.cache/figma_${FIGMA_FILE_KEY}_version.txt` - Cached version for comparison

**GitHub Actions Integration:**
Sets outputs: `FIGMA_FILE_NAME`, `FIGMA_VERSION`, `FIGMA_CHANGED`, etc.

### Setup Scripts

#### `setup_figma_token.sh`
One-time setup to store Figma token in macOS Keychain.

**Usage:**
```bash
./scripts/figma/setup_figma_token.sh
# Prompts for FIGMA_ACCESS_TOKEN interactively
```

**Keychain Storage:**
- Service: `ipai_figma`
- Account: `FIGMA_ACCESS_TOKEN`
- Password: Your Figma personal access token

#### `load_figma_env.sh`
Load Figma credentials from Keychain into environment.

**Usage:**
```bash
source scripts/figma/load_figma_env.sh
# Exports: FIGMA_ACCESS_TOKEN, FIGMA_FILE_KEY
```

**Security:**
- Never commits tokens to git
- Keychain access requires macOS authentication
- CI uses GitHub Secrets instead

## Environment Variables

### Required

| Variable | Source (Local) | Source (CI) | Purpose |
|----------|----------------|-------------|---------|
| `FIGMA_ACCESS_TOKEN` | macOS Keychain | GitHub Secrets | Figma API authentication |
| `FIGMA_FILE_KEY` | `load_figma_env.sh` | GitHub Vars | File identifier (e.g., `7XCC5p6r9yDrMGCE9eI3LC`) |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `DESIGN_TOKENS_DIR` | `design-tokens` | Output directory for artifacts |
| `CACHE_DIR` | `.cache` | Version cache directory |
| `FORCE_SYNC` | `false` | Skip change detection, force sync |

## GitHub Actions Workflows

### `figma-sync-scheduled.yml`
Automated sync every 6 hours with PR creation.

**Triggers:**
- Schedule: Every 6 hours (`0 */6 * * *`)
- Manual: `workflow_dispatch` with `force_sync` option

**Workflow:**
1. Poll Figma file version
2. Early exit if no changes (unless `force_sync=true`)
3. Export all artifacts via `sync_figma_site.sh`
4. Create PR with changes (if file diffs exist)
5. Upload artifacts for audit trail

**Secrets/Vars:**
- `FIGMA_ACCESS_TOKEN` (secret) - Figma API token
- `FIGMA_FILE_KEY` (var) - File key (not sensitive)

**Manual Trigger:**
```bash
gh workflow run figma-sync-scheduled.yml -f force_sync=true
```

## Local Testing

### Quick Test (with cached token)
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/sandbox/dev

# Load credentials
source scripts/figma/load_figma_env.sh

# Run orchestrator
./scripts/figma/sync_figma_site.sh

# Verify artifacts
ls -la design-tokens/
jq . design-tokens/figma-styles.json
jq . design-tokens/figma-contract.json
```

### Force Sync (ignore version check)
```bash
source scripts/figma/load_figma_env.sh
FORCE_SYNC=true ./scripts/figma/sync_figma_site.sh
```

### Test Individual Components
```bash
# Poll only
./scripts/figma/poll_file_version.sh

# Export styles only
curl -sS "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/styles" \
  -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" | jq .
```

## Output Structure

```
design-tokens/
├── figma-styles.json          # 6 KB - Design styles
├── figma-components.json      # 3 KB - Component metadata
├── figma-variables.json       # 1 KB - Variables (or {} if unavailable)
├── figma-file.json            # 250 KB - Full file structure
├── manifest.json              # 5 KB - Sites manifest
├── figma-contract.json        # 12 KB - SDLC contract
├── .figma-version             # Version string (e.g., "3925471892")
└── .figma-last-modified       # ISO timestamp
```

## Figma API Reference

### Endpoints Used

| Endpoint | Purpose | Rate Limit |
|----------|---------|------------|
| `GET /v1/files/{key}` | Full file metadata | 100 req/min |
| `GET /v1/files/{key}/styles` | Design styles | 100 req/min |
| `GET /v1/files/{key}/components` | Component library | 100 req/min |
| `GET /v1/files/{key}/variables/local` | Variables (Enterprise) | 100 req/min |

**Rate Limiting:**
- Free plan: 100 requests/min per token
- Enterprise: 500 requests/min per token
- Orchestrator makes 4 parallel calls = ~2.4 seconds total

**Authentication:**
- Header: `X-Figma-Token: {FIGMA_ACCESS_TOKEN}`
- Token type: Personal Access Token (Settings → Account → Personal Access Tokens)

## Troubleshooting

### Token Not Found
```
ERROR: FIGMA_ACCESS_TOKEN not found in macOS Keychain
Run: ./scripts/figma/setup_figma_token.sh
```

**Fix:** Run setup script and paste your Figma token when prompted.

### API Errors
```
ERROR: Figma API returned an error:
{"err":"Not found"}
```

**Possible causes:**
1. Invalid `FIGMA_FILE_KEY` - verify file key from Figma URL
2. Token lacks file access - check Figma file sharing permissions
3. Token expired - regenerate in Figma settings

### Variables Export Fails
```
⚠️ Variables unavailable (requires Enterprise plan)
```

**Expected behavior:** Non-Enterprise plans don't support Variables API.
The script gracefully writes `{}` to `figma-variables.json` and continues.

### No Changes Detected
```
✅ No changes detected. Skipping sync.
   Set FORCE_SYNC=true to force sync.
```

**Not an error:** Version hasn't changed since last poll.
Use `FORCE_SYNC=true` to override if needed.

## Future Enhancements (Phase 2)

### Webhook Infrastructure
- **Goal:** Near real-time sync (< 1 minute latency)
- **Architecture:** Figma → n8n webhook → GitHub `repository_dispatch`
- **Status:** Planned (requires n8n infrastructure)

**Components:**
- `create_webhook.sh` - Bootstrap n8n workflow
- `.github/workflows/figma-sync.yml` - Webhook-triggered workflow
- n8n workflow JSON - Relay webhook to GitHub

**Blockers:**
- n8n infrastructure issues (user reported errors)
- Figma Enterprise plan required for native webhooks ($45/user/mo)

### Design Token Transformation
- CSS custom properties
- Tailwind config generation
- MUI theme objects
- SCSS variables

### Monitoring
- Slack notifications on sync
- Metrics dashboard (sync frequency, artifact sizes)
- Error alerting

## Related Documentation

- [Figma REST API Docs](https://www.figma.com/developers/api)
- [Variables API (Enterprise)](https://developers.figma.com/docs/rest-api/variables-endpoints/)
- [GitHub Actions Workflows](../../.github/workflows/)
- [Design Token Strategy](../../docs/design-tokens.md) (if exists)

## Maintenance

### Token Rotation
```bash
# Update token in Keychain
security delete-generic-password -s ipai_figma -a FIGMA_ACCESS_TOKEN
./scripts/figma/setup_figma_token.sh

# Update GitHub Secret
gh secret set FIGMA_ACCESS_TOKEN
```

### File Key Update
```bash
# Update local env
export FIGMA_FILE_KEY="NEW_FILE_KEY"

# Update GitHub Var
gh variable set FIGMA_FILE_KEY --body "NEW_FILE_KEY"

# Update workflow trigger
gh workflow run figma-sync-scheduled.yml -f force_sync=true
```

### Audit Trail
All sync runs are archived as GitHub Actions artifacts (30-day retention):
- `figma-poll-{run_number}` - Poll results and metadata
- Viewable at: `https://github.com/{org}/{repo}/actions`

## Credits

**Implementation**: AI-assisted development following Figma official patterns
**Inspiration**: Figma Code Connect, design-to-code automation workflows
**License**: Internal use (InsightPulse AI)
