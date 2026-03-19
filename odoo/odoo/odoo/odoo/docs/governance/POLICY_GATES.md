# Policy Gates — Governance SSOT

> **These CI gates are the enforcement mechanism for this repository.**
> No human reviewer approval is required when all gates pass.
> No CODEOWNERS file is maintained. Gates are the gatekeepers.

---

## Rationale

Human code review is valuable for architecture, design, and knowledge transfer. It is not
a reliable mechanism for enforcing structural policies (secret hygiene, API conventions,
service deprecations). Policy gates make enforcement deterministic, fast, and auditable.

**Trade**: Human reviewer as merge blocker → CI gate as merge blocker.
**Preserved**: Human review as a voluntary, value-add activity via PR comments.

---

## Gate Registry

All gates live in `.github/workflows/policy-gates.yml` and run on every PR.

| # | Gate | Trigger | Blocking |
|---|------|---------|---------|
| 1 | [Spec Bundle Presence](#gate-1--spec-bundle-presence) | `feat/*` branches with >3 scoped file changes | Warn (upgrade to block after adoption) |
| 2 | [Secret Pattern Diff](#gate-2--secret-pattern-diff) | All PRs — changed source/config lines | **Yes** |
| 3 | [Odoo 19 View Convention](#gate-3--odoo-19-view-convention) | Changed `addons/**/*.xml` files | **Yes** |
| 4 | [Migration RLS Contract](#gate-4--migration-rls-contract) | New `supabase/migrations/*.sql` files | **Yes** |
| 5 | [Deprecated Reference Block](#gate-5--deprecated-reference-block) | All PRs — changed source/config lines | **Yes** |

---

## Gate 1 — Spec Bundle Presence

**Purpose**: Ensure significant feature work is spec-driven.

**Trigger**: `feat/*` branches where >3 files in scoped directories change.

**Scoped directories**:
```
addons/ipai/    platform/    web/         infra/
automations/    agents/      design/      analytics/
```

**Check**: A spec bundle must exist at `spec/<branch-slug>/plan.md`.

**Example**: Branch `feat/odoo-expense-v2` → must have `spec/odoo-expense-v2/plan.md`.

**Create a spec bundle**:
```bash
SLUG=my-feature
mkdir -p spec/$SLUG
touch spec/$SLUG/{constitution.md,prd.md,plan.md,tasks.md}
```

**Status**: Warning-only. Will become blocking after Q1 2026 adoption period.

---

## Gate 2 — Secret Pattern Diff

**Purpose**: Prevent hardcoded credentials from entering the codebase.

**Trigger**: All PRs. Scans added lines (`+`) in changed source and config files.

**Patterns blocked**:
- `password = "..."`, `secret = "..."`, `api_key = "..."`
- `sk-<20+ alphanum>` (OpenAI/Anthropic-style keys)
- `SUPABASE_SERVICE_ROLE_KEY = <literal>` (not a variable reference)

**Complementary gate**: `secret-scan.yml` runs a full repo scan on push to `main`.

**Fix**: Use environment variables or Supabase Vault. Never hardcode credentials.

```python
# Wrong
API_KEY = "sk-abc123def456ghi789jkl"

# Right
import os
API_KEY = os.environ["ANTHROPIC_API_KEY"]
```

---

## Gate 3 — Odoo 19 View Convention

**Purpose**: Enforce Odoo 19 API — `<list>` replaces `<tree>`.

**Trigger**: Changed XML files under `addons/`.

**Blocked pattern**: `<tree` (opening tag, any variant)

**Fix**:
```bash
# In-place replacement
sed -i 's/<tree\b/<list/g; s/<\/tree>/<\/list>/g' addons/your_module/views/*.xml
```

**Reference**: [Odoo 19 Views Documentation](https://www.odoo.com/documentation/19.0/developer/reference/views.html)

---

## Gate 4 — Migration RLS Contract

**Purpose**: All new Supabase tables must have Row Level Security enabled.

**Trigger**: Newly added files matching `supabase/migrations/*.sql`.

**Check**: Any `CREATE TABLE` statement must be accompanied by:
```sql
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;
```

**Template**:
```sql
CREATE TABLE public.my_table (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id),
  created_at timestamptz DEFAULT now()
);

ALTER TABLE public.my_table ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own rows" ON public.my_table
  FOR ALL USING (auth.uid() = user_id);
```

**Full RLS checks**: `supabase-sql-rls-checks.yml` runs against the live DB on `supabase/**` changes.

---

## Gate 5 — Deprecated Reference Block

**Purpose**: Prevent reintroduction of deprecated domains and services.

**Trigger**: All PRs. Scans added lines in source/config/docs files.

**Blocked patterns** (from `CLAUDE.md § Deprecated`):

| Blocked | Replacement |
|---------|-------------|
| `insightpulseai.net` | `insightpulseai.com` |
| `mattermost.insightpulseai.com` | Slack |
| `ipai_mattermost*` | `ipai_slack_connector` |
| `ipai_mailgun_bridge` | Zoho Mail SMTP |
| `xkxyvboeubffxxbebsll` | (removed Supabase project) |
| `ublqmilcjtpnflofprkr` | (removed Supabase project) |
| `odoo-ce.insightpulseai.com` | `erp.insightpulseai.com` |

---

## Complementary Gates

These existing workflows enforce additional policies (not duplicated in `policy-gates.yml`):

| Workflow | Enforces |
|----------|---------|
| `secret-scan.yml` | Full repo secret scan (all PRs to main) |
| `canonical-gate.yml` | Odoo module structure + view syntax audit |
| `odoo-qweb-lint.yml` | XML/QWeb linting |
| `supabase-sql-rls-checks.yml` | Live DB RLS validation |
| `agent-instructions-drift.yml` | Agent instruction SSOT consistency |
| `all-green-gates.yml` | Spec kit, policy-check.sh, OCA allowlist |
| `spec-gate.yml` | Spec bundle structural validation |

---

## Adding a New Gate

1. Add a new job to `.github/workflows/policy-gates.yml`
2. Add a row to the Gate Registry table above
3. Write a section in this document with: purpose, trigger, blocked pattern, and fix
4. Open a PR — the gate itself is the evidence of correctness

---

## Emergency Override

In a production incident, a gate may be bypassed by a **repository admin** using:

```
GitHub → Settings → Branches → Branch protection rules → main
→ "Temporarily allow bypassing branch protection"
```

This action is logged in the GitHub audit log. Document the bypass reason in the PR
description and re-enable protection immediately after merge.

**Never add `--no-verify` to git commits in this repo. Pre-commit hooks enforce local policy.**

---

## History

| Date | Change |
|------|--------|
| 2026-02-20 | Initial policy-gates.yml + this document (replaces CODEOWNERS model) |

---

*This document is the SSOT for governance enforcement in this repository.*
*Related: `.github/workflows/policy-gates.yml` · `CLAUDE.md § Critical Rules`*
