# Worktree Classification Audit

**Branch**: `fix/foundry-endpoint-audit`
**Base**: `main` (commit `94819d8f2b`)
**Date**: 2026-03-14
**Total dirty entries**: 939 (12 modified, 927 untracked)

---

## Branch Commit Scope

The branch has exactly **1 commit** ahead of main:

```
8b9eaa2b2f fix(enterprise-bridge): align Foundry config with Azure endpoint taxonomy and add MCP audit
```

**Committed files (6)**:
- `addons/ipai/ipai_enterprise_bridge/models/foundry_provider_config.py`
- `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py`
- `addons/ipai/ipai_enterprise_bridge/tests/test_foundry_config.py`
- `addons/ipai/ipai_enterprise_bridge/views/foundry_provider_config_views.xml`
- `addons/ipai/ipai_enterprise_bridge/views/res_config_settings_views.xml`
- `docs/audits/AZURE_FOUNDRY_MCP_AUDIT.md`

**Staging area**: Empty (`git diff --cached` is clean).

---

## Category 1: Post-PR Working Tree Edits (Modified, Unstaged)

**Count**: 12 files
**Status**: ` M` (modified but not staged)
**Nature**: Further development work done AFTER the PR commit. These are NOT part of PR #586 scope.

| File | Overlap with PR commit? | Description |
|------|------------------------|-------------|
| `addons/ipai/ipai_enterprise_bridge/models/foundry_provider_config.py` | YES — further edit | Changes `auth_audience` default from `cognitiveservices` to `ai.azure.com` |
| `addons/ipai/ipai_odoo_copilot/__manifest__.py` | No | Unified API Gateway manifest changes |
| `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | No | Config parameter updates |
| `addons/ipai/ipai_odoo_copilot/models/__init__.py` | No | New model import |
| `addons/ipai/ipai_odoo_copilot/models/foundry_service.py` | No | +333 lines — Foundry service model |
| `addons/ipai/ipai_odoo_copilot/models/res_config_settings.py` | No | Settings extension |
| `addons/ipai/ipai_odoo_copilot/views/res_config_settings_views.xml` | No | Settings view extension |
| `docs/architecture/UNIFIED_API_GATEWAY_TARGET_STATE.md` | No | Gateway target state doc |
| `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | No | Contract index update |
| `spec/unified-api-gateway/plan.md` | No | Gateway plan doc |
| `spec/unified-api-gateway/tasks.md` | No | Gateway tasks doc |
| `ssot/api/unified-api-gateway.yaml` | No | Gateway SSOT YAML |

**Total diff**: +413 / -73 lines

**Recommended action**:
- The 1 file that overlaps with the PR commit (`foundry_provider_config.py`) should either be committed as a follow-up fix or stashed to keep the PR clean.
- The other 11 files belong to a **separate feature** (Unified API Gateway). They should be **stashed** or moved to a new branch (`feat/unified-api-gateway`).

---

## Category 2: Untracked Files — Worktree Contamination (927 entries)

These files exist on disk but have **never been committed** to `main` or this branch. They are NOT "merged PR residue" — the reflog confirms the branch was created cleanly from `main` at `94819d8f2b`. These files predate the branch creation and were already present in the working tree.

**Root cause**: The `odoo/` repo's `.gitignore` uses `!addons/ipai/**` (un-ignore), making hundreds of local-only files visible to git. Combined with accumulated docs, scripts, specs, and config from development sessions that were never committed.

### 2a. Untracked Docs (624 entries)

**Count**: 588 in `docs/` + 36 in `"docs/design/Vector *.png"` (paths with spaces)
**Examples**:
- `docs/architecture/` — 160+ architecture docs (ADRs, ERDs, schemas, contracts)
- `docs/modules/` — 130+ module docs (per-module markdown files)
- `docs/evidence/` — 90+ evidence bundles (timestamped audit trails)
- `docs/design/` — 40+ design system images (PNG files with spaces in names)
- `docs/contracts/` — 25+ contract docs
- `docs/agents/` — 15+ agent framework docs
- Various: `docs/ai/`, `docs/analytics/`, `docs/api/`, `docs/auth/`, `docs/ci/`, etc.

**Recommended action**: **Triage individually**. Most docs are legitimate project artifacts that should be committed in batched PRs by domain. The design PNGs (Vector 4702-*.png, Vector 4703-*.png) should be evaluated — they may be Figma exports better stored externally.

### 2b. Untracked Addons (117 entries)

**Count**: 117 entries across ~80 addon directories
**Examples**:
- `addons/ipai/cts_theme_rozz/` — Third-party theme (contains 100+ images)
- `addons/ipai/ipai_agent/` — Agent framework module
- `addons/ipai/ipai_ai_copilot/` — AI copilot module
- `addons/ipai/ipai_bir_tax_compliance/` — BIR tax compliance
- `addons/ipai/ipai_enterprise_bridge/` (partial — files not tracked by main)
- `addons/ipai/ipai_finance_ppm/` — Finance PPM module
- `addons/ipai/ipai_slack_connector/` — Slack connector
- `addons/ipai/ipai_zoho_mail/` — Zoho mail module
- ...and ~70 more

**Context**: Main tracks only 4 addon directories (`ipai_enterprise_bridge`, `ipai_odoo_copilot`, `ipai_project_seed`, `ipai_theme_copilot`). The other ~80 directories are development artifacts from previous sessions.

**Recommended action**:
- **`cts_theme_rozz`**: Discard — third-party theme with 100+ static images, bloats the repo.
- **Core modules** (agent, copilot, finance, BIR, etc.): Commit in domain-specific PRs after quality gates pass.
- **Deprecated modules** (ipai_ai_widget, ipai_mailgun_smtp, ipai_mattermost_connector): Discard — per CLAUDE.md deprecation list.

### 2c. Untracked CI Workflows (45 entries)

**Count**: 45 workflow files
**Current on main**: Only 6 workflows exist on main
**Examples**:
- `addons-manifest-guard.yml`, `ci-runbot.yml`, `deploy-odoo-prod.yml`
- `e2e-playwright.yml`, `secrets-audit.yml`, `ssot-validate.yml`
- `parity-gate-tier0.yml`, `repo-structure-gate.yml`
- `unified-api-gateway-ssot-check.yml`

**Recommended action**: **Triage and commit in a CI-focused PR**. These are likely legitimate workflow files developed but never merged. Some may be stale.

### 2d. Untracked Scripts (36 entries)

**Count**: 36
**Examples**:
- `scripts/odoo/install-oca-modules.sh`, `scripts/odoo/validate_addons_manifest.py`
- `scripts/ci/check_deprecated_provider_defaults.py`
- `scripts/azure/deploy-bot-service.sh`, `scripts/dns/`
- `scripts/agents/`, `scripts/audit/`, `scripts/benchmark/`

**Recommended action**: Commit in domain-specific PRs.

### 2e. Untracked SSOT Files (22 entries)

**Count**: 22
**Examples**:
- `ssot/agents/capability_manifest.json`, `ssot/agents/skills/`, `ssot/agents/tools/`
- `ssot/azure/`, `ssot/databricks/`, `ssot/github/`
- `ssot/odoo/addons.manifest.yaml`, `ssot/parity/`
- `ssot/api/unified-api-gateway.schema.json`

**Recommended action**: Commit — these are SSOT artifacts that SHOULD be tracked.

### 2f. Untracked Spec Bundles (14 entries)

**Count**: 14
**Examples**:
- `spec/azure-target-state/`, `spec/enterprise-target-state/`
- `spec/lakehouse/`, `spec/odoo-copilot/`, `spec/odoo-erp-saas/`
- `spec/well-architected/`, `spec/platform-auth/`
- `spec/odoo-copilot-benchmark/` (benchmark config + scenarios)

**Recommended action**: Commit in a spec consolidation PR.

### 2g. Root-Level Files (27 entries)

**Count**: ~27
**Examples**:
- Build/config: `Dockerfile`, `Makefile`, `pyproject.toml`, `package.json`, `turbo.json`, `pnpm-lock.yaml`
- Requirements: `requirements-ai.txt`, `requirements-dev.txt`, `requirements-oca.txt`, `requirements-odoo.txt`
- Docs: `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `GEMINI.md`, `SECURITY.md`
- Linting: `.flake8`, `.yamllint.yml`, `.pre-commit-config.yaml`, `.markdownlint-cli2.jsonc`
- Data: `addons.manifest.json`, `oca-aggregate.yml`, `oca.lock.json`, `llms.txt`
- Env: `.env.example`, `.agentignore`, `.cursorignore`

**Recommended action**:
- **Commit**: `pyproject.toml`, `requirements-*.txt`, `.pre-commit-config.yaml`, `SECURITY.md`, `CONTRIBUTING.md`
- **Gitignore**: `.env.example` (or commit without secrets), `.agentignore`, `.cursorignore`
- **Evaluate**: `Dockerfile` (may conflict with `docker/` structure), `package.json`/`pnpm-*` (verify workspace setup)

### 2h. Other Directories (28 entries)

| Directory | Count | Description | Action |
|-----------|-------|-------------|--------|
| `config/` | 4 | dev config, GWS config, odoo mail config | Commit |
| `automations/n8n/` | 4 | n8n workflow JSONs | Commit (ensure no secrets) |
| `supabase/` | 5 | Edge functions + migrations | Commit |
| `docs-site/` | 5 | HR processes, module guides | Commit |
| `tests/` | 2 | test_install_oca_from_ssot.py, test_ssot_odoo_contract.py | Commit |
| `docker/` | 1 dir | Compose files, Dockerfiles | Commit |
| `apps/` | 1 dir | Application code | Evaluate |
| `ops/` | 1 dir | Operations tools | Evaluate |
| `evidence/` | 1 dir | Root-level evidence (outside docs/) | Move to `docs/evidence/` |
| `compose/` | 1 dir | Compose configs | May overlap with `docker/` |
| `bin/` | 1 dir | Binary/script wrappers | Evaluate |
| `data/` | 1 dir | Data files | Evaluate |
| `marketplace/` | 1 dir | Marketplace assets | Evaluate |
| `mcp/` | 1 dir | MCP configs | Commit |
| `patches/` | 1 dir | Patch files | Commit |
| `pipelines/` | 1 dir | Pipeline configs | Commit |
| `skills/` | 1 dir | Agent skills | Commit |
| `odoo-schema-mirror/` | 1 dir | Schema mirror | Evaluate |

---

## Category 3: Generated/Cache Files

**Count**: 0 visible (`.gitignore` already excludes `__pycache__/`, `*.pyc`, `node_modules/`, `build/`, etc.)

No generated or cache files appear in `git status`. The `.gitignore` is working correctly for these patterns.

---

## Category 4: Config Drift

**Count**: 0 tracked config files modified

`.vscode/` and `.claude/` files do not appear in this working tree's status. No config drift detected.

---

## Category 5: Stashes

**Count**: 3 stashes exist

| Stash | Branch | Description |
|-------|--------|-------------|
| `stash@{0}` | `spec/docs-platform` | WIP: unit tests for Foundry, Doc Digitization |
| `stash@{1}` | `chore/billing-smoke` | WIP: billing smoke workflow |
| `stash@{2}` | `claude/developer-ux-capabilities-mSxNW` | WIP: align CLAUDE.md with Azure-native target |

**Recommended action**: Review and drop after extracting any needed changes.

---

## Summary Table

| Category | Count | Action |
|----------|-------|--------|
| PR #586 committed scope (clean) | 6 files | None needed — committed |
| Post-PR working tree edits | 12 files | Stash or branch (`feat/unified-api-gateway`) |
| Untracked docs | 624 | Batch-commit by domain |
| Untracked addons/ipai | 117 | Triage: commit core, discard deprecated/theme |
| Untracked CI workflows | 45 | Triage and commit |
| Untracked scripts | 36 | Commit by domain |
| Untracked root files | 27 | Commit essentials, gitignore rest |
| Untracked SSOT | 22 | Commit |
| Untracked specs | 14 | Commit |
| Untracked other dirs | 28 | Triage per table above |
| Generated/cache | 0 | N/A |
| Config drift | 0 | N/A |
| **Total** | **939** | |

---

## Is PR #586 Clean?

**Yes, for its committed scope.** The 6 committed files are correct. However:

1. **1 post-commit edit** to `foundry_provider_config.py` changes the `auth_audience` default — this is a follow-up fix that should be committed separately or amended into the PR.
2. **11 unrelated files** from the Unified API Gateway feature are modified in the working tree. These do NOT affect PR #586 but will be confusing during review if not stashed.

**Recommendation**: Before PR review, run:
```bash
git stash push -m "WIP: unified-api-gateway and foundry follow-up" -- \
  addons/ipai/ipai_odoo_copilot/ \
  docs/architecture/UNIFIED_API_GATEWAY_TARGET_STATE.md \
  docs/contracts/PLATFORM_CONTRACTS_INDEX.md \
  spec/unified-api-gateway/ \
  ssot/api/unified-api-gateway.yaml \
  addons/ipai/ipai_enterprise_bridge/models/foundry_provider_config.py
```

---

## Root Cause: Why 927 Untracked Files?

The `.gitignore` has `!addons/ipai/**` which un-ignores ALL ipai files, but main only tracks 4 addon directories. The remaining ~80 addon directories plus hundreds of docs, scripts, specs, and SSOT files were created during development sessions but never committed. They accumulated across multiple branches and sessions.

**This is not from stash contamination** — the reflog confirms a clean checkout from main. These files pre-exist in the filesystem from prior work.

**Long-term fix**: Either commit these files in organized PRs, or add specific `.gitignore` rules for directories that should remain local-only.

---

*Generated: 2026-03-14 | Branch: fix/foundry-endpoint-audit | Auditor: Claude Opus 4.6*
