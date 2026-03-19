# Monorepo End-State — Constitution

> Governance principles for the InsightPulse AI monorepo end-state.
> These rules are non-negotiable and take precedence over implementation convenience.

---

## Governance Principles

### 1. SSOT Authority

The git repository (`Insightpulseai/odoo`) is the **sole authoritative source of truth**
for all infrastructure, configuration, code, and documentation.

- Any configuration that exists only in a SaaS console (Cloudflare, DigitalOcean, Supabase)
  and not in a corresponding repo file is a **SSOT violation**.
- Resolution: export configuration to the appropriate SSOT path and enforce via CI.

### 2. EE Parity via OCA — Not via Replication

No `ipai_*` module may replicate Odoo Enterprise Edition UI or business logic for the sole
purpose of feature parity.

- **Allowed**: Thin integration layers, OCA module configurations, IPAI bridge connectors.
- **Forbidden**: Copying or reimplementing Enterprise XML views, wizards, or business rules.
- **Allowed path**: OCA module → configure → `ipai_*` override if needed.

### 3. Bridge Contracts Are Mandatory

Any IPAI integration bridge (filling an EE feature gap with an external service) requires:

1. An entry in `ssot/bridges/catalog.yaml`
2. A contract document in `docs/contracts/<BRIDGE_NAME>_CONTRACT.md`
3. A corresponding secret entry in `ssot/secrets/registry.yaml` (identifiers only)

A bridge may not be marked `status: active` until all three artifacts exist.

### 4. No Odoo.sh References

This repo is self-hosted CE. All references to `odoo.sh`, `Odoo.sh`, or Odoo SaaS hosting
are prohibited in canonical files (`spec/`, `docs/`, `addons/ipai/`, `CLAUDE.md`).

- Exception: archived docs (`docs/99-Archive/`, `docs/XX-Archive/`)
- Replacement reference: `docs/ops/ODOO_SH_EQUIVALENT.md`

### 5. Domain Lock

All external-facing services MUST resolve under `*.insightpulseai.com`.

- `insightpulseai.net` references are prohibited (CI-enforced via `domain-lint.yml`)
- `.vercel.app` and `.ondigitalocean.app` URLs may not appear in canonical documentation
- Canonical subdomain registry: `ssot/domains/insightpulseai.com.yaml`

### 6. Spec-Driven Significant Changes

Any change touching ≥3 modules or introducing a new external service dependency requires
a spec bundle in `spec/<feature-slug>/` before implementation begins.

### 7. Secrets Never in Repo

Secret values never appear in any file tracked by git.

- Identifiers (env var names, secret names) ARE allowed: `ssot/secrets/registry.yaml`
- Values are NEVER allowed: `.env*`, workflow files, spec bundles, or documentation

---

## Violation Response

| Violation | CI Response | Human Action |
|-----------|------------|-------------|
| EE module import in `addons/ipai/` | Block merge | Remove import, use OCA path |
| Missing bridge contract | Block merge | Create contract doc |
| `.net` domain reference | Block merge | Replace with `.com` |
| Secret value in repo | Immediate rotation | Rotate + purge from git history |
| Unregistered subdomain | Warn | Add to SSOT YAML |
