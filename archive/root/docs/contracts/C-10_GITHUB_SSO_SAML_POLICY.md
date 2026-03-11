# Contract C-10: GitHub Org SSO/SAML & Governance Policy

> Cross-domain contract: GitHub Org (H) ↔ Identity (B — Supabase Auth).
> SSOT: This file. Supabase Auth remains IdP SSOT per SSOT_BOUNDARIES.md §1.
> Last updated: 2026-02-22

---

## 1. Org Ownership & Access Tiers

| Role | GitHub Permission | Provisioned By | Review Cadence |
|------|-----------------|----------------|----------------|
| Org Owner | Owner | Manual — CTO + DevOps | Quarterly |
| Repo Admin | Admin on specific repos | DevOps ticket | Quarterly |
| Senior Dev | Maintain on feature repos | Team lead request | Bi-annually |
| Dev / Contributor | Write or Triage | Team lead request | Bi-annually |
| External / Bot | Write (scoped repos only) | DevOps — named token | Per-project |

**Invariant**: Org Owner count must be ≥ 2 and ≤ 4. Fewer = single point of failure. More = over-privilege.

## 2. Authentication Requirements

| Requirement | Status | Enforcement |
|-------------|--------|-------------|
| 2FA mandatory for all org members | Required | GitHub org setting |
| SAML SSO (when available) | Planned — requires GitHub Enterprise | Post-Enterprise upgrade |
| PAT expiry ≤ 90 days | Required | GitHub org PAT policy |
| Fine-grained PATs preferred | Recommended | Developer guidance |
| Machine accounts use GitHub Apps | Required for new integrations | DevOps review |

**Current status**: Organization is on GitHub Free/Pro (not Enterprise). SAML SSO
requires GitHub Enterprise Cloud. Until then, 2FA is the enforcement baseline.

## 3. SSO/SAML Posture (When Enterprise Available)

IdP hierarchy (consistent with SSOT_BOUNDARIES.md §1 — Supabase Auth as SSOT):

```
Supabase Auth (primary IdP)
    │
    └─► GitHub Enterprise (SAML SP)
            │
            └─► GitHub org membership
```

- SAML assertions issued by Supabase Auth
- GitHub Enterprise SAML configured with Supabase as IdP
- User provisioning: SCIM (when available) or manual sync script
- Forbidden: GitHub as IdP for Supabase (reverse direction violates SSOT)

## 4. Repository Governance

### Branch Protection (all repos, `main` branch)

- Require pull request reviews (minimum 1 for standard, 2 for `infra/`, `supabase/migrations/`)
- Require status checks to pass before merging (CodeQL, copilot-guardrails, test suite)
- Restrict force pushes (never allowed on `main`)
- Require linear history (squash or rebase merge)

### CODEOWNERS

Sensitive paths and their required approvers are defined in `.github/CODEOWNERS`.
At minimum:
```
addons/ipai/ipai_auth_*/     @devops-team
supabase/migrations/          @devops-team
.github/workflows/            @devops-team
infra/policy/                 @devops-team
docs/contracts/               @devops-team
```

### Secrets Management

- Repository secrets: set via GitHub Actions UI or `gh secret set`
- Org-level secrets: restricted to specific repos (not blanket-shared)
- No secrets in repo files (enforced by Secret Scanning push protection)

## 5. Access Review Cadence

| Review Type | Frequency | Owner | Evidence |
|-------------|-----------|-------|----------|
| Org Owner audit | Quarterly | CTO | GitHub org member export |
| Repo permissions audit | Bi-annually | DevOps | `gh api /orgs/.../members` export |
| Bot / service account audit | Quarterly | DevOps | GitHub App installations list |
| PAT expiry check | Monthly | DevOps | GitHub PAT settings review |

Evidence saved to: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/github-governance/`

## 6. Incident Response

| Event | Immediate Action | Owner |
|-------|-----------------|-------|
| Compromised PAT detected | Revoke via GitHub Settings + rotate in Supabase Vault | DevOps |
| Org Owner account compromised | Remove from Org → re-provision via 2FA recovery | CTO + DevOps |
| Unauthorized repo access | Audit org audit log → revoke + report | DevOps |
| Secret committed to repo | Revoke secret → push protection enabled → remediate | DevOps + Dev |

## 7. SSOT Drift Rule

Changes to this contract require:
1. PR with `docs/contracts/C-10_GITHUB_SSO_SAML_POLICY.md` in diff
2. DevOps team CODEOWNERS approval
3. If org settings changed manually: mirror in `infra/policy/` within 24 hours
