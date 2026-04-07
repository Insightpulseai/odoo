# Deployment Evidence: Pulser Assistant Stack

**Timestamp**: 2026-04-01T07:48:00Z
**PR**: #668 (squash-merged)
**Merge commit**: `2eba31a0542c4e707c998deeee55977c975afef8`
**Branch**: `feat/pulser-spec-bundles-tax-guru-ph` -> `main`

---

## A. What Changed

### Repos/Files Touched

| File | Type | Description |
|------|------|-------------|
| `spec/pulser-platform/prd.md` | New | Control plane PRD: formations, capability packages, grounding registry, 6-tier PH hierarchy, evidence schema |
| `spec/pulser-platform/plan.md` | New | Control plane plan: Phases P1-P6 including PH grounding registration |
| `spec/pulser-platform/tasks.md` | New | Control plane task checklist |
| `spec/pulser-agents/prd.md` | New | Runtime layer PRD: agent/workflow templates, 5 answer types, source selection policy |
| `spec/pulser-agents/plan.md` | New | Runtime layer plan: Phases R1-R6 including PH citation engine |
| `spec/pulser-agents/tasks.md` | New | Runtime layer task checklist |
| `spec/pulser-web/prd.md` | New | Experience layer PRD: chat surface, workbench, 5 UI card models |
| `spec/pulser-web/plan.md` | New | Experience layer plan: Phases W1-W5 |
| `spec/pulser-web/tasks.md` | New | Experience layer task checklist |
| `spec/pulser-odoo/prd.md` | New | Odoo adapter PRD: embedded UI, record context, safe actions, execution benchmark |
| `spec/pulser-odoo/plan.md` | New | Odoo adapter plan: Phases O1-O5 |
| `spec/pulser-odoo/tasks.md` | New | Odoo adapter task checklist |
| `docs/architecture/tax/TAX_GURU_CONSOLIDATION.md` | New | 68-asset tax/BIR consolidation report |

### Modules Touched
None (spec-only deployment — no Python/TypeScript changes).

### Workflows Touched
None (spec files do not trigger `azure-pipelines/odoo-deploy.yml` or `.github/workflows/ipai-copilot-publish.yml`).

### Assumptions
- Spec bundles are architecture artifacts defining target state, not runtime code
- Existing Odoo Copilot implementation (`ipai_odoo_copilot`, `ipai_ai_copilot`) is already live and aligned with Tier 1 of spec
- Tax Guru sub-agent is spec-only; no runtime implementation exists yet
- Odoo localization Tier 5 benchmark requires future `l10n_ph`-style module

---

## B. Deployment Result

### Spec Bundle Deployment (Main)
- **Status**: MERGED
- **PR**: https://github.com/Insightpulseai/odoo/pull/668
- **Commit**: `2eba31a0`
- **13 files, 2,179 lines added**
- **No runtime impact** (spec changes only, no trigger paths matched)

### Existing Odoo Copilot (Production — Validated)
- **Status**: LIVE
- **URL**: https://erp.insightpulseai.com
- **Health**: `/web/health` → HTTP 200 (18 bytes, 274ms)
- **Login**: `/web/login` → HTTP 200, title "Odoo"
- **Copilot endpoint**: `/ipai/copilot/chat` → HTTP 405 (method not allowed — correct for GET, expects POST)
- **Container App**: `ipai-odoo-dev-web` in `rg-ipai-dev-odoo-runtime`
- **Image**: `acripaiodoo.azurecr.io/ipai-odoo:19.0-copilot`
- **Pipeline**: `azure-pipelines/odoo-deploy.yml` (AzDO)

### Foundry Agent (Production — Configured)
- **Agent**: `ipai-odoo-copilot-azure` v1.0.0
- **Capabilities**: navigational, informational, transactional, compliance_intel
- **Write policy**: default `read_only` (aligned with spec `suggest_only` default)
- **Model**: gpt-4.1
- **Knowledge grounding**: `srch-ipai-dev` / `ipai-knowledge-index`
- **Pipeline**: `.github/workflows/ipai-copilot-publish.yml`

### Release Identifiers
- Spec bundle: commit `2eba31a0` on `main`
- Odoo Copilot: image `acripaiodoo.azurecr.io/ipai-odoo:19.0-copilot` (latest AzDO build)
- Foundry Agent: `ipai-odoo-copilot-azure` v1.0.0

---

## C. Validation Summary

### Infrastructure Checks

| Check | Result | Evidence |
|-------|--------|----------|
| Odoo ERP health | PASS | `/web/health` → HTTP 200 |
| Odoo login page | PASS | `/web/login` → HTTP 200, title "Odoo" |
| Copilot endpoint exists | PASS | `/ipai/copilot/chat` → HTTP 405 (POST expected) |
| Spec bundle merged | PASS | PR #668 squash-merged, commit `2eba31a0` |
| No runtime regression | PASS | Spec-only changes, no trigger paths matched |

### Architecture Alignment

| Check | Result | Notes |
|-------|--------|-------|
| Odoo = adapter, not control plane | PASS | `ipai_odoo_copilot` is tool executor adapter, not registry |
| Capability taxonomy in Foundry agent | PASS | navigational, informational, transactional in metadata.yaml |
| Write policy defaults to read_only | PASS | metadata.yaml `default: read_only` |
| Tool executor has blocked models | PASS | `_BLOCKED_MODELS` frozenset in tool_executor.py |
| Rate limiting on copilot gateway | PASS | 20 req/user/60s in copilot_gateway.py |
| TaxPulse-PH-Pack = bounded pack | PASS | Spec positions it as domain pack, not whole system |

### Implementation Gap Analysis

| Component | Spec Status | Implementation Status | Gap |
|-----------|:-----------:|:--------------------:|-----|
| Odoo embedded assistant | Spec complete | LIVE (`ipai_odoo_copilot`) | Aligned |
| Record context assembly | Spec complete | LIVE (tool_executor.py) | Aligned |
| Safe action modes | Spec complete | LIVE (read_only default) | Aligned |
| Foundry agent | Spec complete | LIVE (metadata.yaml) | Aligned |
| **PH grounding registry** | Spec complete | NOT IMPLEMENTED | **Gap: Phase P6** |
| **5 answer type contracts** | Spec complete | NOT IMPLEMENTED | **Gap: Phase R6** |
| **Source selection engine** | Spec complete | NOT IMPLEMENTED | **Gap: Phase R6** |
| **UI card models** | Spec complete | NOT IMPLEMENTED | **Gap: Phase W5** |
| **Odoo localization mapping** | Spec complete | NOT IMPLEMENTED | **Gap: Phase O5** |
| **Tax Guru sub-agent** | Spec complete | NOT IMPLEMENTED | **Gap: Phases P5/R5** |

### Open Risks

1. **Tax Guru is spec-only** — no runtime implementation. Requires Phases P5/R5/W5/O5 execution.
2. **PH grounding sources not registered** — BIR/CGPA/Odoo localization sources need ingestion pipelines.
3. **Foundry project `proj-ipai-claude` has 0 deployments** (per memory) — agent publish may need first deployment.
4. **ATC code divergence** (W-series vs WI/WC-series) — critical P0 blocker from consolidation report, not yet resolved.
5. **Copilot gateway pipeline not automated** — `Dockerfile.gateway` builds but no AzDO pipeline deploys it.

---

## D. Rollback Note

### Spec Bundle Rollback
```bash
git revert 2eba31a0542c4e707c998deeee55977c975afef8
git push origin main
```
No runtime impact — spec changes only.

### Odoo Copilot Rollback
```bash
# Via AzDO pipeline — redeploy previous image tag
# Or manually:
az containerapp update \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/ipai-odoo:<previous-tag>
```

### Foundry Agent Rollback
```bash
# Via GitHub Actions — re-run ipai-copilot-publish.yml on previous commit
# Or: scripts/foundry/sync_agent.py --dry-run (verify before rollback)
```

---

## Summary

**Deployed**: 4 Pulser spec bundles + tax consolidation report merged to main (13 files, 2,179 LOC).

**Production Odoo Copilot**: Already LIVE and aligned with Tier 1 spec (embedded assistant, tool executor, read-only default, rate limiting, blocked models).

**Not yet deployed**: Tax Guru sub-agent, PH grounding engine, answer type contracts, UI card models, Odoo localization mapping — all spec-complete but implementation-pending (Phases P5-P6, R5-R6, W5, O5).

**No runtime regression**: Spec-only merge, no deployment pipelines triggered.
