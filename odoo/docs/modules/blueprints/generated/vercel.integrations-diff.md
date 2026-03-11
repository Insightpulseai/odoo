<!-- AUTO-GENERATED from blueprints/vercel.integrations-diff.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Vercel Integrations Drift Detector

**ID**: `vercel.integrations-diff`  
**Category**: `ops-console`  
**Target**: `platform/vercel-integrations`

---

## Sources

- **doc** — [https://vercel.com/docs/integrations](https://vercel.com/docs/integrations) (catalog id: `vercel-docs-home`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_API_TOKEN` | Vercel API token scoped to the team(s) being monitored. | `` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key for reading ops.integrations_snapshots. | `` |
| `GH_TOKEN` | GitHub token with issues:write scope for drift issue management. | `` |
| `VERCEL_TEAM_IDS` | Comma-separated Vercel team IDs to monitor for integration drift. | `` |

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Optional Slack incoming webhook URL for drift notifications. | `` |

---

## Automation Steps

### Step 1: create_diff_engine

Create platform/vercel-integrations/ with diff, github_issues, slack_notify, run TypeScript files

### Step 2: create_ci_workflow

Create .github/workflows/vercel-integrations-diff.yml

### Step 3: create_runbook

Create docs/ops/VERCEL_INTEGRATIONS_DIFF.md

### Step 4: catalog_item_link

Ensure catalog item exists with blueprint_id=vercel.integrations-diff

---

## Verification

**Required CI checks:**

- `catalog-gate`
- `blueprint-gate`

**Preview expectations:**

- diff-ts-exists
- github-issues-ts-exists
- ci-workflow-exists

---

## Rollback

**Strategy**: `revert_pr`

---

## Minor Customization (manual steps after agent applies blueprint)

- Set VERCEL_TEAM_IDS secret in GitHub Actions before first run.
- Apply ops.integrations_snapshots migration if table does not exist.

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `vercel.integrations-diff` from docs/catalog/blueprints/vercel.integrations-diff.blueprint.yaml.

Variables to set before running:
  VERCEL_API_TOKEN: <value>
  SUPABASE_SERVICE_ROLE_KEY: <value>
  GH_TOKEN: <value>
  VERCEL_TEAM_IDS: <value>

Steps to execute in order:
  1. create_diff_engine: Create platform/vercel-integrations/ with diff, github_issues, slack_notify, run TypeScript files
  2. create_ci_workflow: Create .github/workflows/vercel-integrations-diff.yml
  3. create_runbook: Create docs/ops/VERCEL_INTEGRATIONS_DIFF.md
  4. catalog_item_link: Ensure catalog item exists with blueprint_id=vercel.integrations-diff

After completing all steps:
  - Verify required checks pass: catalog-gate, blueprint-gate
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
