# Runbook — GitHub Enterprise Org Setup (`Insightpulse-ai` under `ipai`)

Canonical setup procedure for the primary operating org, derived from
[ssot/governance/github-enterprise-org-target-state.yaml](../../ssot/governance/github-enterprise-org-target-state.yaml).

**Enterprise**: `https://github.com/enterprises/ipai` (governance umbrella)
**Primary org**: `https://github.com/Insightpulse-ai` (operating)

---

## Preconditions

1. You are Enterprise Owner on `ipai`.
2. SAML SSO active (`GitHub Enterprise Cloud - Insightpulseai SAML SSO` per Entra enterprise apps).
3. Break-glass Entra account verified (per [ssot/identity/entra_target_state.yaml#members](../../ssot/identity/entra_target_state.yaml)).
4. `gh` CLI installed + authenticated against enterprise account.

---

## Phase 1 — Establish org baseline

### Step 1.1 Create `.github` repo + profile README

```bash
gh repo create Insightpulse-ai/.github --private --description "Org governance"
# Add profile/README.md (see README template below)
```

Profile README template:

```markdown
# Insightpulse-ai

Primary operating GitHub organization for InsightPulseAI.

## Purpose
Hosts canonical repositories, engineering workflows, and team boundaries
for InsightPulseAI's platform, ERP, analytics, agent runtime, web
surfaces, automations, and supporting documentation.

## Authority model
- GitHub: code and PR truth
- Azure Boards: planning truth
- Azure Pipelines: release truth
- Repo SSOT files: intended-state truth
- Runtime evidence/docs: live operational truth

## Canonical repositories
`.github`, `docs`, `odoo`, `platform`, `infra`, `web`,
`data-intelligence`, `agent-platform`, `agents`, `automations`,
`design`, `templates`

## Security baseline
- Branch protection required on production-bearing branches
- No plaintext secrets in repositories
- Least privilege by default
- CODEOWNERS and review gates on canonical repos

## Operating model
This org is part of the `ipai` enterprise, which provides governance,
security, billing, and policy oversight.
```

### Step 1.2 Set base permissions to read

```bash
gh api -X PATCH orgs/Insightpulse-ai \
  -f default_repository_permission=read \
  -f members_can_create_public_repositories=false \
  -f members_can_create_internal_repositories=false \
  -f members_can_create_private_repositories=true
```

### Step 1.3 Enable security baselines enterprise-wide

Enterprise admin settings → Code security:
- Secret scanning: ON
- Push protection: ON
- Dependabot: ON (alerts + security updates + version updates as applicable)
- Code scanning: evaluate per-repo (CodeQL)

### Step 1.4 Create 10 canonical teams

```bash
for team in platform odoo web data-intelligence agent-platform agents infra automations design docs; do
  gh api -X POST orgs/Insightpulse-ai/teams -f name="$team" -f privacy=closed
done
```

### Step 1.5 Create canonical repos (if not already present)

```bash
# Canonical set (12):
gh repo create Insightpulse-ai/.github         --private
gh repo create Insightpulse-ai/docs            --public
gh repo create Insightpulse-ai/odoo            --public
gh repo create Insightpulse-ai/platform        --private
gh repo create Insightpulse-ai/infra           --private
gh repo create Insightpulse-ai/web             --private
gh repo create Insightpulse-ai/data-intelligence --private
gh repo create Insightpulse-ai/agent-platform  --private
gh repo create Insightpulse-ai/agents          --public
gh repo create Insightpulse-ai/automations     --private
gh repo create Insightpulse-ai/design          --internal
gh repo create Insightpulse-ai/templates       --private
```

### Step 1.6 Set branch protection on `main`

```bash
# Apply to every canonical repo
for repo in .github docs odoo platform infra web data-intelligence agent-platform agents automations design templates; do
  gh api -X PUT repos/Insightpulse-ai/$repo/branches/main/protection \
    -f required_status_checks='{"strict":true,"contexts":[]}' \
    -F enforce_admins=true \
    -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
    -F restrictions=null \
    -F required_linear_history=true \
    -F allow_force_pushes=false \
    -F allow_deletions=false
done
```

### Step 1.7 Pin 6 canonical repos

Org settings → Pinned items:
- `odoo`, `platform`, `agent-platform`, `data-intelligence`, `web`, `docs`

### Step 1.8 Discussions

- `docs` repo: Discussions ON
- `agents` repo: Discussions ON
- All other repos: Discussions OFF by default

Evidence: `docs/evidence/<YYYYMMDD-HHMM>/github-org-setup-phase1/`

---

## Phase 2 — Canonical operating shape

### Step 2.1 Migrate repos from existing `Insightpulseai` to `Insightpulse-ai`

```bash
# For each repo, transfer ownership
gh api -X POST repos/Insightpulseai/<repo>/transfer -f new_owner=Insightpulse-ai
# Verify each transfer, update submodule URLs, update CI references
```

### Step 2.2 Align team ownership

```bash
# Assign teams as maintainers of their scope repos
gh api -X PUT orgs/Insightpulse-ai/teams/platform/repos/Insightpulse-ai/platform -f permission=maintain
gh api -X PUT orgs/Insightpulse-ai/teams/odoo/repos/Insightpulse-ai/odoo -f permission=maintain
# ... etc for all 10 teams
```

### Step 2.3 Protected environments for production-bearing repos

Production-bearing: `odoo`, `platform`, `infra`, `web`, `agent-platform`, `data-intelligence`, `automations`

For each:
- Repo settings → Environments → New environment
- Create `dev`, `staging`, `production`
- On `production`: required reviewer = `platform` team, wait timer = 5 min, restrict to `main`

### Step 2.4 Update local clones + CI references

```bash
# Update git remote URLs
git remote set-url origin git@github.com:Insightpulse-ai/<repo>.git

# Update Azure Pipelines service connections
# Update CLAUDE.md references
# Update SSOT cross-references
```

Evidence: `docs/evidence/<YYYYMMDD-HHMM>/github-org-setup-phase2/`

---

## Phase 3 — Governance hardening

### Step 3.1 Org rulesets

Create enterprise-level ruleset:
- Enforce on all repos under `Insightpulse-ai`
- Rules: branch naming (`main` / `feat/*` / `fix/*`), require PR, required reviewers, required status checks

### Step 3.2 CODEOWNERS

Each canonical repo gets `.github/CODEOWNERS`:

```
# Canonical CODEOWNERS pattern
* @Insightpulse-ai/platform

# Repo-specific overrides
/addons/ @Insightpulse-ai/odoo
/agents/ @Insightpulse-ai/agents
/infra/  @Insightpulse-ai/infra
```

### Step 3.3 Reusable workflows in `.github`

Create `.github/.github/workflows/`:
- `contract-checks-reusable.yml`
- `ruff-mypy-pytest-reusable.yml`
- `secret-scan-reusable.yml`

Consumer repos reference via `uses: Insightpulse-ai/.github/.github/workflows/<name>@main`.

### Step 3.4 Environment approvals for production

Per-repo production environment: require approval from `platform` team + 5-minute wait timer.

### Step 3.5 Security + compliance reporting

- Enable enterprise audit log streaming to Log Analytics (`log-ipai-dev-sea`)
- Verify Dependabot alerts flow to security team
- Verify secret scanning alerts paged to action group

Evidence: `docs/evidence/<YYYYMMDD-HHMM>/github-org-setup-phase3/`

---

## Verification checklist

- [ ] `github.com/enterprises/ipai` confirmed as enterprise
- [ ] `github.com/Insightpulse-ai` created as primary org
- [ ] 10 canonical teams created
- [ ] 12 canonical repos created with correct visibility
- [ ] `.github/profile/README.md` published
- [ ] Base permission = read
- [ ] Secret scanning + push protection + Dependabot ON enterprise-wide
- [ ] Branch protection on `main` for every canonical repo
- [ ] 6 pinned repos visible on org home
- [ ] Production-bearing repos have `dev` / `staging` / `production` environments
- [ ] `production` environment requires `platform` team review
- [ ] CODEOWNERS present on every canonical repo
- [ ] Audit log streaming to Log Analytics verified
- [ ] Old `Insightpulseai` org archived or redirected (post phase 2)

---

## Rollback

**Phase 1 rollback**: disable new settings, revert base permission to write (if previously write). No data loss.

**Phase 2 rollback**: transfer repos back to old org via `gh api -X POST repos/Insightpulse-ai/<repo>/transfer -f new_owner=Insightpulseai`. Update local clones + CI again.

**Phase 3 rollback**: remove rulesets, CODEOWNERS files, reusable workflow references. Remove environment approvals.

---

## Non-goals (explicit)

- Not splitting canonical repos across multiple sibling orgs
- Not moving deploy authority to GitHub Actions (Azure Pipelines stays)
- Not moving portfolio planning to GitHub Projects (Azure Boards stays)
- Not enabling Enterprise Managed Users on day one
- Not archiving transitional repos before replacement ships

---

## Related

- SSOT: [ssot/governance/github-enterprise-org-target-state.yaml](../../ssot/governance/github-enterprise-org-target-state.yaml)
- Enterprise migration: [ssot/governance/github-enterprise-migration.yaml](../../ssot/governance/github-enterprise-migration.yaml)
- Clean chain: [platform/ssot/architecture/github-azure-chain.yaml](../../platform/ssot/architecture/github-azure-chain.yaml)
- Identity target: [ssot/identity/entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml)
- GHA scoped exception: [ssot/governance/gha-scoped-exception.yaml](../../ssot/governance/gha-scoped-exception.yaml)
