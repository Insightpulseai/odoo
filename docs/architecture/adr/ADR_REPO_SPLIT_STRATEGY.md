# ADR: Repository Split Strategy

| Field | Value |
|-------|-------|
| **Status** | Proposed |
| **Date** | 2026-03-30 |
| **Author** | Architecture Team |
| **Authority** | `ssot/governance/org-repo-target-state.yaml` |
| **Deciders** | Platform lead, Org owner |

---

## Context

### Current State

The InsightPulse AI codebase is a monorepo at `Insightpulseai/Insightpulseai` containing all 12 target planes plus legacy/archive directories. Key metrics:

| Metric | Value |
|--------|-------|
| Total top-level directories | ~36 (including archive, legacy) |
| Tracked files (est.) | 10,000+ |
| Repo size on disk | ~15 GB (mostly `odoo/` at 13 GB and `web/` at 2.2 GB) |
| CI workflows | 42 files in `.github/workflows/` |
| Target repos per SSOT | 12 core + 2 satellite |

### Existing GitHub Repos

All 12 target repos already exist in the `Insightpulseai` GitHub org as separate repositories:

| Repo | Exists | Has Content |
|------|--------|-------------|
| `.github` | Yes | Org governance, reusable workflows |
| `odoo` | Yes | Separate nested git repo at `odoo/` |
| `platform` | Yes | Description set, content TBD |
| `data-intelligence` | Yes | Separate nested git repo at `data-intelligence/` |
| `agent-platform` | Yes | Description set, content TBD |
| `web` | Yes | Description set, content TBD |
| `infra` | Yes | Description set, content TBD |
| `automations` | Yes | Description set, content TBD |
| `agents` | Yes | Description set, content TBD |
| `design` | Yes | Description set, content TBD |
| `docs` | Yes | Description set, content TBD |
| `templates` | Yes | Description set, content TBD |
| `landing.io` | Yes | Satellite redirect shell |
| `ugc-mediaops-kit` | Yes | Satellite OSS toolkit |

### Nested Git Repos Already Present

Three directories already have their own `.git`:

- `odoo/` (13 GB) -- largest plane, has its own commit history
- `data-intelligence/` (1.3 MB) -- already a nested repo
- `documentaion/` (legacy, misspelled) -- archive candidate
- `web-site/` -- legacy, superseded by `web/`

### Cross-Cutting Directories (Not Yet Assigned)

These monorepo directories serve multiple planes and need decomposition:

| Directory | Size | Files | Assignment Challenge |
|-----------|------|-------|---------------------|
| `scripts/` | 728 KB | ~50 | Mixed: odoo scripts, CI scripts, platform scripts |
| `spec/` | 1.6 MB | ~80 | Mixed: spec bundles reference multiple planes |
| `ssot/` | 1.6 MB | ~100 | Mixed: governance, odoo, release, business |
| `config/` | 88 KB | ~10 | Mostly odoo config, some platform |
| `apps/` | 104 KB | ~10 | Belongs to platform per target state |
| `packages/` | - | ~10 | Shared packages, belongs to platform |
| `databricks/` | 120 KB | ~20 | Belongs to data-intelligence |
| `lakehouse/` | - | - | Legacy, replaced by data-intelligence |
| `eval/` | - | - | Belongs to agents or agent-platform |
| `foundry/` | - | - | Belongs to agent-platform |
| `marketplace/` | - | - | Belongs to platform or web |
| `prompts/` | - | - | Belongs to agents |
| `skills/` | - | - | Belongs to agents |
| `supabase/` | - | - | Deprecated, archive only |
| `ops-platform/` | - | - | Legacy, replaced by platform |
| `archive/` | - | - | Dead weight, do not migrate |

### Three-Way Boundary Doctrine

The SSOT defines a critical three-way split that is the hardest boundary to enforce in the current monorepo:

- **platform** = control plane, operator surfaces, shared APIs
- **agent-platform** = deployable agent runtime and orchestration
- **agents** = personas, skills, judges, evals, schemas

In the current monorepo, `agent-platform/`, `agents/`, and `platform/` directories already exist as top-level directories, which is a structural advantage.

---

## Options Analyzed

### Option A: Full Split (Big Bang)

Split all 12 planes into separate GitHub repos in a single coordinated effort.

**How it works**:
1. Use `git filter-repo` to extract each plane's history from the monorepo
2. Push each extracted history to its corresponding GitHub repo
3. Set up cross-repo CI/CD and contract testing
4. Archive the monorepo

**Pros**:
- Clean break, no ambiguity about which repo owns what
- Each repo gets independent CI/CD, release cadence, and access control
- Matches the SSOT target state exactly
- Eliminates the 15 GB monorepo download problem

**Cons**:
- High risk of breaking cross-plane imports discovered too late
- Requires all 12 repos to be production-ready simultaneously
- CI/CD duplication across 12 repos (42 workflows to redistribute)
- Cross-repo contract testing infrastructure must exist before the split
- History extraction for deeply entangled directories (`scripts/`, `ssot/`, `spec/`) is complex
- Team must context-switch across 12 repos for any cross-cutting change
- Estimated effort: 3-4 weeks of focused work

**Verdict**: Too risky for a team of this size. The cross-cutting directories (`scripts/`, `ssot/`, `spec/`) and the 42 CI workflows make a clean simultaneous split infeasible.

---

### Option B: Hybrid Monorepo with Enforced Boundaries

Keep the monorepo but enforce plane boundaries via CODEOWNERS, CI path filters, and directory-level contracts.

**How it works**:
1. Add `CODEOWNERS` file mapping each plane's directories to responsible teams/individuals
2. Enforce path-scoped CI (each workflow triggers only on its plane's paths)
3. Add a CI job that validates no cross-plane imports exist (using `analyze-dependencies.sh`)
4. Use `ssot/governance/org-repo-target-state.yaml` as the living boundary contract
5. External repos (`odoo`, `data-intelligence`) remain separate (already split)

**Pros**:
- No migration risk -- current state continues working
- Cross-cutting changes remain easy (single PR, single CI run)
- CODEOWNERS provides ownership visibility without repo overhead
- Already have the SSOT manifest to define boundaries
- Existing nested repos (`odoo/`, `data-intelligence/`) stay as-is

**Cons**:
- Monorepo download is still 15 GB (dominated by `odoo/` and `web/`)
- Does not achieve independent release cadence per plane
- CODEOWNERS is advisory (GitHub can enforce reviews but not prevent merges by admins)
- CI workflows remain entangled -- a change to `agents/` still triggers the full workflow matrix
- Does not match the already-created 12-repo GitHub org structure
- Team already invested in creating separate repos; this option abandons that direction

**Verdict**: Pragmatic short-term option, but does not resolve the 15 GB repo size problem or achieve independent release cadence. The fact that 12 repos already exist in the org signals intent to split -- a hybrid model would waste that work.

---

### Option C: Gradual Extraction (Recommended)

Extract repos one at a time, starting with the most independent planes, while maintaining the monorepo as a coordination hub until all planes are extracted.

**How it works**:
1. Identify extraction order based on independence (fewest cross-plane dependencies first)
2. Extract one plane at a time using `git subtree split` or `git filter-repo`
3. After extraction, replace the monorepo directory with a symlink/README pointing to the new repo
4. Update CI workflows to reference the extracted repo
5. Add cross-repo contract tests as each extraction completes
6. Monorepo shrinks with each extraction until only coordination files remain

**Pros**:
- Low risk per extraction -- only one plane changes at a time
- Validates the contract testing strategy incrementally
- Each extraction is independently reversible
- Takes advantage of the 12 repos that already exist in the org
- Largest plane (`odoo/` at 13 GB) already has its own `.git` -- extraction is trivial
- Team learns from each extraction and applies lessons to the next

**Cons**:
- Longer total elapsed time than a big bang
- Transitional state has some planes in monorepo and some extracted -- coordination overhead
- Cross-cutting directories (`scripts/`, `ssot/`, `spec/`) require careful decomposition
- Need to maintain backward compatibility during the transition

**Verdict**: Best balance of risk, effort, and outcome. The existing nested repos (`odoo/`, `data-intelligence/`) prove this approach already works.

---

## Decision

**Option C: Gradual Extraction** is the recommended strategy.

### Rationale

1. **Two planes are already extracted** (`odoo/` and `data-intelligence/` have their own `.git`), proving the pattern works.
2. **All 12 target repos exist** in the GitHub org, so no repo creation is needed.
3. **The monorepo is dominated by two planes**: `odoo/` (13 GB) and `web/` (2.2 GB) account for 98% of repo size. Extracting just these two solves the download problem.
4. **Cross-cutting directories** (`scripts/`, `ssot/`, `spec/`) need per-file assignment before extraction, which is best done incrementally.
5. **42 CI workflows** must be redistributed; doing this incrementally reduces blast radius.

---

## Migration Plan

### Phase 0: Preparation (Week 1)

1. **Run dependency analysis**:
   ```bash
   chmod +x scripts/repo-split/analyze-dependencies.sh
   ./scripts/repo-split/analyze-dependencies.sh > docs/evidence/$(date +%Y%m%d-%H%M)/repo-split/dependency-analysis.txt
   ```

2. **Decompose cross-cutting directories** -- create assignment map:

   | Source Path | Target Repo | Rationale |
   |-------------|-------------|-----------|
   | `scripts/ci/` | `.github` | CI validation scripts |
   | `scripts/azure/` | `infra` | Azure infrastructure scripts |
   | `scripts/odoo/` | `odoo` | Already Odoo-specific |
   | `scripts/repo-split/` | `docs` (then delete) | Migration tooling, temporary |
   | `spec/ipai-odoo-*` | `odoo` | Odoo spec bundles |
   | `spec/finance-*` | `odoo` | Finance domain specs |
   | `ssot/odoo/` | `odoo` | Odoo SSOT |
   | `ssot/governance/` | `platform` or `docs` | Cross-repo governance |
   | `ssot/release/` | `platform` | Release gates |
   | `ssot/contracts/` | `platform` | Platform contracts |
   | `ssot/business/` | `platform` | Business rules |
   | `ssot/google-workspace/` | `agents` or `platform` | Integration contracts |
   | `ssot/microsoft-marketplace/` | `platform` | Marketplace contracts |
   | `ssot/microsoft365/` | `platform` | M365 contracts |
   | `ssot/external/` | `platform` | External integration contracts |
   | `config/` | `odoo` | Odoo configuration |
   | `databricks/` | `data-intelligence` | Databricks bundles |
   | `lakehouse/` | Archive (deprecated) | Replaced by data-intelligence |
   | `eval/` | `agents` | Eval content |
   | `foundry/` | `agent-platform` | Foundry runtime |
   | `marketplace/` | `platform` | Marketplace assets |
   | `prompts/` | `agents` | Agent prompts |
   | `skills/` | `agents` | Skill definitions |
   | `supabase/` | Archive (deprecated) | Fully deprecated |
   | `ops-platform/` | Archive (deprecated) | Replaced by platform |
   | `apps/` | `platform` | Platform applications |
   | `packages/` | `platform` | Shared packages |
   | `archive/` | Do not migrate | Dead history |
   | `docker/` | `infra` | Docker base images |
   | `db/` | `odoo` or `data-intelligence` | Database migrations |

3. **Create CODEOWNERS** in the monorepo as a transitional ownership map:
   ```
   /odoo/               @erp-team
   /addons/             @erp-team
   /web/                @web-team
   /agents/             @agent-team
   /agent-platform/     @agent-team
   /infra/              @infra-team
   /data-intelligence/  @data-team
   /platform/           @platform-team
   ```

4. **Set up cross-repo contract testing template** -- a reusable GitHub Actions workflow that validates interface contracts between repos.

### Phase 1: Extract Already-Split Planes (Week 2)

These planes already have their own `.git` or are trivially independent.

**Extraction order**:

| # | Repo | Monorepo Path | Size | Method | Difficulty |
|---|------|---------------|------|--------|------------|
| 1 | `odoo` | `odoo/` | 13 GB | Already has `.git` -- push to `Insightpulseai/odoo` | Trivial |
| 2 | `data-intelligence` | `data-intelligence/` + `databricks/` | 1.4 MB | Already has `.git` -- merge `databricks/` content, push | Easy |
| 3 | `design` | `design/` | 37 MB | `git subtree split` -- no cross-plane deps expected | Easy |
| 4 | `templates` | `templates/` | 180 KB | `git subtree split` -- fully independent | Trivial |

**Commands for extraction** (example for `design`):

```bash
# Extract subtree with history
cd /path/to/monorepo
git subtree split --prefix=design -b split-design

# Push to target repo
cd /tmp && git clone git@github.com:Insightpulseai/design.git
cd design
git pull ../monorepo split-design --allow-unrelated-histories
git push origin main
```

**Post-extraction for each repo**:
- Add `README.md` per the SSOT `readme_contract`
- Add `.github/workflows/` with repo-specific CI
- Add `docs/`, `spec/`, `ssot/`, `scripts/`, `tests/` per completeness gate
- Replace monorepo directory with a `README.md` pointing to the new repo

### Phase 2: Extract Medium-Complexity Planes (Weeks 3-4)

| # | Repo | Monorepo Paths | Dependencies | Difficulty |
|---|------|----------------|--------------|------------|
| 5 | `web` | `web/`, `web-site/`, `docs-site/` | Consumes design tokens | Medium |
| 6 | `infra` | `infra/`, `docker/` | Referenced by CI workflows | Medium |
| 7 | `docs` | `docs/` + cross-repo governance from `ssot/governance/` | Cross-cutting references | Medium |
| 8 | `automations` | `automations/` | Connectors reference odoo/infra | Medium |

**Key tasks per extraction**:
1. Run `analyze-dependencies.sh` to verify no new cross-plane imports appeared
2. Move relevant `spec/`, `ssot/`, `scripts/` files into the target repo
3. Update CI workflows: move plane-specific workflows, update path triggers
4. Add contract tests that validate the interfaces this plane consumes/provides
5. Test that the monorepo CI still passes after extraction

### Phase 3: Extract Entangled Planes (Weeks 5-6)

| # | Repo | Monorepo Paths | Dependencies | Difficulty |
|---|------|----------------|--------------|------------|
| 9 | `agents` | `agents/`, `eval/`, `prompts/`, `skills/` | Consumed by agent-platform | Hard |
| 10 | `agent-platform` | `agent-platform/`, `foundry/` | Consumes agents, platform | Hard |
| 11 | `platform` | `platform/`, `apps/`, `packages/`, `marketplace/` + governance SSOT | Hub for contracts | Hard |
| 12 | `.github` | `.github/` (org-level only) | Reusable workflows consumed by all | Hard |

**Special handling for the three-way split** (`platform` / `agent-platform` / `agents`):
- Extract `agents` first (it is consumed, does not consume runtime)
- Extract `agent-platform` second (consumes `agents` contracts only)
- Extract `platform` last (owns cross-plane contracts, needs all interfaces stable)

**Special handling for `.github`**:
- Only org-wide workflows and actions move to `.github` repo
- Repo-specific workflows stay with their respective repos
- Reusable workflow references change from local paths to `Insightpulseai/.github/.github/workflows/reusable-*.yml@main`

### Phase 4: Monorepo Retirement (Week 7)

1. Verify all 12 repos pass their CI independently
2. Verify cross-repo contract tests pass
3. Archive the monorepo:
   - Rename to `Insightpulseai/monorepo-archive` (read-only)
   - Or keep as `Insightpulseai/Insightpulseai` with only coordination files:
     - `CLAUDE.md` (updated to point to child repos)
     - `ssot/governance/org-repo-target-state.yaml`
     - `docs/architecture/adr/ADR_REPO_SPLIT_STRATEGY.md`
     - Cross-repo CI orchestration (optional)
4. Update all development documentation and onboarding guides

---

## CI/CD Migration Per Repo

### Current State
- 42 GitHub Actions workflows in `.github/workflows/`
- Azure DevOps Pipelines for Odoo/Databricks/infra deploy lanes

### Target State

| Repo | CI (GitHub Actions) | CD (Deploy) |
|------|--------------------|----|
| `.github` | Org governance checks | N/A |
| `odoo` | Odoo module tests, lint | Azure DevOps Pipelines |
| `platform` | TypeScript build + test | GitHub Actions + ACA deploy |
| `data-intelligence` | Databricks bundle validation | Azure DevOps Pipelines |
| `agent-platform` | Runtime tests, eval hooks | Azure DevOps Pipelines |
| `web` | Build + lighthouse + e2e | GitHub Actions + ACA deploy |
| `infra` | Terraform plan + validate | Azure DevOps Pipelines |
| `automations` | Job contract tests | Azure DevOps Pipelines |
| `agents` | Schema validation, eval suites | GitHub Actions (no deploy) |
| `design` | Token export validation | GitHub Actions (publish pkg) |
| `docs` | Docs build + link check | GitHub Actions (docs-site deploy) |
| `templates` | Template render tests | GitHub Actions (no deploy) |

### Workflow Redistribution Strategy

1. **Inventory** all 42 workflows and map each to its target repo
2. **Identify reusable workflows** (setup steps, deploy patterns) -- move to `.github` repo
3. **Move plane-specific workflows** to their target repo
4. **Update path triggers** to match the new repo root (e.g., `addons/**` becomes the repo root in `odoo`)
5. **Add cross-repo dispatch** for workflows that need to trigger on changes in another repo

---

## Cross-Repo Contract Testing Strategy

### Contract Types

| Contract | Source Repo | Consumer Repo(s) | Validation |
|----------|------------|-------------------|------------|
| Addon manifest | `odoo` | `data-intelligence` | Schema validation against `addons.manifest.yaml` |
| Agent schema | `agents` | `agent-platform` | JSON Schema validation |
| Design tokens | `design` | `web`, `odoo` | Token export + consumer build |
| Platform API | `platform` | `agent-platform`, `web` | OpenAPI contract test |
| Infra topology | `infra` | `odoo`, `web`, `platform` | Resource inventory check |
| Release gates | `platform` | All | Gate check before deploy |

### Implementation

1. **Contract files** live in the source repo under `ssot/contracts/`
2. **Consumer repos** pull contracts via:
   - Git submodule (for schema files)
   - GitHub Actions `repository_dispatch` (for CI triggers)
   - Published npm/PyPI package (for SDK contracts)
3. **Contract tests** run in both repos:
   - Source repo: "Did I break the contract?"
   - Consumer repo: "Does my code still conform?"
4. **Contract versioning**: Semantic versioning on contract files. Breaking changes require a major version bump and consumer acknowledgment.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cross-plane imports not detected by static analysis | Medium | High | Run `analyze-dependencies.sh` before each extraction. Add runtime import guards. |
| CI workflow fails after extraction due to missing path | High | Medium | Test each workflow in the target repo before removing from monorepo. Keep monorepo workflows active during transition. |
| `scripts/`, `ssot/`, `spec/` decomposition creates ownership disputes | Medium | Low | Use the assignment table (Phase 0) as SSOT. Disputed files go to `platform` by default. |
| Team productivity drops during transition | Medium | Medium | Extract one plane per week max. Keep monorepo functional as fallback. |
| Secrets/environment variables scattered across repos | Low | High | Centralize secrets in Azure Key Vault. Each repo documents its required env vars in `.env.example`. |
| Cross-repo PRs become painful (change spans 2+ repos) | High | Medium | Use GitHub's "linked PRs" feature. Document which contracts span repos. For the transition period, accept that some changes need coordinated PRs. |
| `odoo/` nested repo history diverges from monorepo history | Medium | Low | Already diverged -- accept this. The nested `.git` is the source of truth for Odoo history. |
| 15 GB monorepo clone remains slow during transition | Low | Low | Use `git clone --filter=blob:none` for shallow clones. Prioritize extracting `odoo/` (13 GB) in Phase 1 to immediately reduce clone size. |

---

## Success Criteria

- [ ] All 12 repos pass CI independently
- [ ] No cross-plane import violations detected by `analyze-dependencies.sh`
- [ ] Each repo has the completeness gate surfaces: `README.md`, `.github/workflows/`, `docs/`, `spec/`, `ssot/`, `scripts/`, `tests/`
- [ ] Cross-repo contract tests exist for all contract types listed above
- [ ] Monorepo is archived or reduced to coordination-only
- [ ] Developer onboarding docs updated with multi-repo workflow
- [ ] Clone time for any single repo is under 60 seconds

---

## References

- `ssot/governance/org-repo-target-state.yaml` -- 12-repo target state
- `docs/architecture/TARGET_ORG_REPO_MAP.md` -- Architecture map with L3 trees
- `scripts/repo-split/analyze-dependencies.sh` -- Dependency analysis tool
- `docs/architecture/adr/ADR_PLATFORM_TRANSFORMATION_DECISION.md` -- Prior platform transformation ADR
