# GitHub Enterprise Cloud — Governance Contract

**SSOT**: `ssot/github/enterprise-cloud.yaml`
**CI validator**: `scripts/ci/check_github_enterprise_ssot.py`
**Schema**: `ssot.github.enterprise.v1`
**Last updated**: 2026-03-01

---

## Track A: Personal Accounts

InsightPulse AI uses **Track A** (personal GitHub accounts + organizational membership), not
GitHub Enterprise Managed Users (EMU / Track B).

**Rationale**:
- Contributors use pre-existing personal GitHub accounts; no dedicated IdP-provisioned machine
  accounts are required.
- SAML SSO at the org level provides SSO enforcement without the complexity of EMU
  account provisioning.
- Track A is sufficient for a startup-scale team where individual developer identity is
  stable and contributors are not enterprise-directory-managed employees.
- Switching to EMU later (if required by compliance) is a documented migration path;
  the SSOT file schema supports adding `enterprise.type: managed_users` at that point.

---

## SAML SSO

**Requirement**: SAML SSO is enabled and enforced at the **org level**.

```yaml
policy:
  sso:
    enabled: true
    mode: saml
    enforcement_target: org
```

**What this means**:
- All org members must complete SAML authentication before accessing org resources.
- Non-SAML sessions are blocked by GitHub for any protected resource.
- The IdP (e.g., Okta, Azure AD, Google Workspace) must be configured in
  **GitHub Org Settings → Authentication security → SAML single sign-on**.

**Official docs**: [Configuring SAML SSO for your organization](https://docs.github.com/en/enterprise-cloud@latest/organizations/managing-saml-single-sign-on-for-your-organization/configuring-saml-single-sign-on-for-your-organization)

---

## Two-Factor Authentication (2FA)

**Requirement**: All org members must have 2FA enabled on their personal GitHub accounts.

```yaml
policy:
  auth:
    require_2fa: true
    restrict_third_party_oauth_apps: true
```

- `require_2fa`: GitHub will remove members who do not have 2FA enabled when org-level
  2FA enforcement is activated. Members receive a grace period before removal.
- `restrict_third_party_oauth_apps`: Members cannot authorize third-party OAuth apps
  without org owner approval. This reduces supply-chain OAuth risk.

**Official docs**: [Requiring 2FA in your organization](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization)

---

## Repository Rulesets

**Requirement**: Default branch on all org repos is protected by a ruleset with the
following invariants (minimum):

```yaml
policy:
  repo_rulesets:
    default_branch_protection:
      require_pull_request: true
      required_approving_reviews: 1
      dismiss_stale_reviews_on_push: true
      require_status_checks: true
      require_linear_history: true
```

**Controls explained**:

| Control | Enforcement |
|---------|-------------|
| `require_pull_request` | Direct pushes to default branch are blocked; all changes via PR |
| `required_approving_reviews: 1` | At least 1 approving review required before merge |
| `dismiss_stale_reviews_on_push` | Force-re-approval on new pushes to PR branch |
| `require_status_checks` | Required CI checks must pass before merge |
| `require_linear_history` | Merge commits blocked; rebase or squash only |

`require_linear_history` keeps the git history bisectable and suitable for automated
audit tooling. Merge commits that obscure individual commit authorship are prohibited.

**Official docs**: [Managing rulesets for repositories in your organization](https://docs.github.com/en/enterprise-cloud@latest/organizations/managing-organization-settings/managing-rulesets-for-repositories-in-your-organization)

---

## Security Defaults

**Requirement**: The following GitHub Advanced Security (GHAS) features are in desired-state
enabled for all org repos:

```yaml
policy:
  security:
    dependabot_alerts: true
    dependabot_security_updates: true
    secret_scanning: true
    push_protection: true
```

| Feature | Purpose |
|---------|---------|
| `dependabot_alerts` | Alerts on known CVEs in dependency graph |
| `dependabot_security_updates` | Auto-PRs to patch vulnerable deps |
| `secret_scanning` | Scans commits for credential patterns (API keys, tokens) |
| `push_protection` | Blocks pushes containing detected secrets before they land |

**Plan-gated note**: `secret_scanning` and `push_protection` require the GitHub Advanced
Security (GHAS) add-on on GHEC, or are included in some GHEC tiers. Verify current
entitlements on the org billing page. Entries in the SSOT represent **desired-state**;
CI validates key presence and value, not live API enforcement.

**Official docs**:
- [GitHub Enterprise Cloud overview](https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud)
- [About secret scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [Protecting pushes with secret scanning](https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations)

---

## CI Enforcement

The CI validator (`scripts/ci/check_github_enterprise_ssot.py`) enforces structural
invariants on `ssot/github/enterprise-cloud.yaml` at every PR that touches `ssot/github/**`.

**Invariants checked**:

| Check | Expected value |
|-------|---------------|
| File exists | `ssot/github/enterprise-cloud.yaml` present |
| `enterprise.type` | `"personal_accounts"` |
| `policy.sso.enabled` | `true` |
| `policy.sso.mode` | `"saml"` |
| `policy.repo_rulesets.default_branch_protection.require_status_checks` | `true` |
| `policy.repo_rulesets.default_branch_protection.require_pull_request` | `true` |
| `policy.auth.require_2fa` | `true` |

The gate runs as part of `ssot-gates.yml` (job `github-enterprise-ssot`). Exit 0 = pass,
exit 1 = fail with detailed error to stderr.

**What CI does NOT check**:
- Live GitHub API state (actual org settings)
- Whether GHAS features are actually enabled (plan-gated)
- IdP configuration completeness

Human review of GitHub Org Settings remains required for full assurance.

---

## Audit Log

```yaml
audit:
  source: github_enterprise_audit_log
  ingestion: optional
  ingest_target_table: ops.audit_events
```

GitHub Enterprise Cloud exposes audit events at:
`https://github.com/organizations/insightpulseai/settings/audit-log`

Event categories relevant to this contract:
- `org.saml_sso_*` — SAML session events
- `protected_branch.*` — Ruleset bypass attempts
- `secret_scanning.*` — Secret scanning alerts and dismissals
- `member.*` — Org membership changes

**Optional ingestion path**: When a SIEM or Supabase `ops.audit_events` pipeline is
operational, configure GitHub audit log streaming to that endpoint. Until then, manual
review of the GitHub audit log UI satisfies audit requirements.

**Table**: `ops.audit_events` (append-only, see SSOT platform rules §Rule 5)

---

## Deviation Process

Any deviation from the desired-state values in `ssot/github/enterprise-cloud.yaml` must:

1. Have a documented technical reason in `docs/architecture/adr/`.
2. Be approved by the org owner.
3. Be reflected in the SSOT file with a `deviation_note` key on the affected field.
4. Have a remediation date set.

Unnanounced deviations detected in audit log review should be treated as security incidents.
