# Security Remediation Lane

Tracks how Dependabot and other security findings are handled in this monorepo.
**Rule: dependency/security updates run in a dedicated lane — never mixed with infra, docs, or SSOT PRs.**

---

## Current Alert Volume

| Source | Total | Critical | High | Medium | Low |
|--------|-------|----------|------|--------|-----|
| Dependabot (npm/pnpm) | ~195 | 8 | 87 | 71 | 29 |

Last surfaced: 2026-02-22 (push to `claude/deploy-finance-ppm-odoo19-LbLm4`).

---

## Severity SLA

| Level | Response SLA | PR label | Batch policy |
|-------|-------------|----------|-------------|
| **Critical** | 3 business days | `security:critical` | Immediate dedicated PR per package |
| **High** | 7 business days | `security:high` | Batch by ecosystem (≤ 10 deps/PR) |
| **Medium** | 30 days | `security:medium` | Monthly sweep PR |
| **Low** | 90 days | `security:low` | Quarterly sweep PR |

---

## Ecosystems to Sweep (batch order)

1. **pnpm/npm** — `apps/ops-console/`, `web/apps/`, `packages/`
   - Command: `pnpm audit --fix` (review each bump for breaking changes)
   - CI gate: `pnpm audit --audit-level=critical` fails on Critical findings

2. **Python (pip)** — `scripts/`, `addons/` (Odoo)
   - Command: `pip-audit -r requirements*.txt`
   - Note: Odoo pinned deps require careful version alignment with OCA

3. **GitHub Actions** — `.github/workflows/`
   - Pin all `uses: actions/...` to SHA, not tag
   - Review: `dependabot[bot]` PRs for action version bumps

---

## Governance Rules

1. **No mixed PRs.** A PR touching `addons/**` or `apps/**` must not also bump dependencies.
2. **No suppressing without doc.** If a finding is suppressed (e.g. no patch available), document it in `.security/suppressions.yaml` with reason + owner + review date.
3. **Critical findings block main merge.** `pnpm audit --audit-level=critical` is a required CI check.
4. **ip@<=2.0.1 is a known accepted exception** — no patched version exists; documented in `web/apps/colima-desktop/`.

---

## Suppression Registry

Create `.security/suppressions.yaml` when first suppression is needed. Format:

```yaml
suppressions:
  - id: GHSA-xxxx-xxxx-xxxx
    package: example-pkg
    reason: No patched version available; functionality not exposed to external input
    owner: platform-team
    review_date: 2026-05-01
    pr: "#123"
```

---

## Remediation Workflow

```
1. gh issue create --label "security:critical" --title "Dependabot: critical deps sweep <date>"
2. git checkout -b security/critical-sweep-<date>
3. pnpm audit --fix (or manual bump for Odoo Python)
4. pnpm build && pnpm test (in affected workspace)
5. PR → review → merge (separate from infra/docs PRs)
6. Update alert counts table above
```

---

## References

- Dependabot alerts: `https://github.com/Insightpulseai/odoo/security/dependabot`
- Security policy: `SECURITY.md` (root)
- OCA dependency policy: `docs/ai/OCA_WORKFLOW.md`
