# Plan — OdooSH Azure Equivalent

## Architecture

### Control Plane
Azure Pipelines (or GitHub Actions) for CI/CD orchestration: YAML templates, environments, approvals/checks, variable groups, service connections.

### Runtime Plane
Azure Container Apps:
- `ipai-odoo-{env}-web` — Odoo web server
- `ipai-odoo-{env}-worker` — Background job processing
- `ipai-odoo-{env}-cron` — Scheduled actions
- `ipai-mailpit-{env}` — Non-prod mail catcher
- Revisions/labels for rollout control

### Data Plane
Azure Database for PostgreSQL Flexible Server:
- PITR/restore for recovery
- Optional read replica for BI access
- HA for production (when justified)
- 35-day backup retention

### Edge Plane
Azure Front Door Standard/Premium:
- Public ingress, TLS termination, WAF
- Custom domains (`erp.insightpulseai.com`)
- Health probes for origin monitoring

### Security Plane
- Azure Key Vault for secrets
- Managed Identity for runtime auth
- Entra ID for human access
- Key Vault-backed variable groups for pipeline secrets

### Ops Plane
- Application Insights for traces/metrics
- Log Analytics for centralized logs
- Azure Monitor for alerts
- Deployment history via environments

## Environment Model

| Environment | Workers | Data | Integrations | Mail | Cron | Domain |
|-------------|---------|------|-------------|------|------|--------|
| **dev** | Low (1 web) | Demo/test | All active | Mailpit | Limited | `*.azurecontainerapps.io` |
| **staging** | Prod-like | Sanitized prod copy | Disabled/sandboxed | Mailpit | Mostly off | `staging.insightpulseai.com` |
| **production** | Full (auto-scale) | Live | Active | Zoho SMTP | Active | `erp.insightpulseai.com` |
| **preview** | Minimal (1 web) | Shared dev DB | Dev mode | Mailpit | Off | `ipai-odoo-pr-{N}.*.azurecontainerapps.io` |

## Deployment Model

### Dev
- Auto-deploy on push to dev branch
- No approvals required
- Uses `odoo_dev` database

### Staging
- Deployed via promotion from dev
- Staging refresh: `refresh_staging.sh` (prod → sanitize → staging)
- Uses `odoo_staging` database
- Approval required before prod promotion

### Production
- Deployed via promotion from staging
- Required reviewers (environment protection)
- Uses `odoo` database (never `odoo_prod`)
- Health check gate post-deploy
- Rollback via ACA revision revert

### Preview
- Created per PR via `pr-preview.yml`
- ACA revision with unique name: `ipai-odoo-pr-{N}`
- Auto-deleted on PR close
- Uses shared `odoo_dev` database

## Delivery Flow

```
1. Developer pushes branch / opens PR
2. CI builds + tests (ci-odoo.yml)
3. Image pushed to ACR with SHA tag
4. PR preview deployed (pr-preview.yml)
5. Developer tests preview URL
6. PR merged to main
7. Deploy to staging (deploy-azure.yml, staging target)
8. Staging refresh if needed (refresh_staging.sh)
9. Approval gate (environment protection rules)
10. Deploy to production (deploy-azure.yml, prod target)
11. Health check passes
12. Traffic locked to new revision
13. Evidence pack recorded
```

## Edge and Certificate Strategy

- Use Front Door Standard/Premium at the edge
- Cloudflare as upstream DNS (CNAME to Front Door)
- **Caveat**: ACA managed certificates may not issue/renew cleanly when Cloudflare is intermediate proxy. Use Front Door managed certs instead.
- Custom SSL certificates supported (unlike Odoo.sh)

## Secret and Authorization Model

- Key Vault-backed variable groups for pipeline inputs
- Environment names and service connections are compile-time stable
- Managed identities for runtime secret access
- `ODOO_STAGE` env var injected per container

## Maturity Roadmap

### Interfaces Roadmap

1. Remove custom/team-specific request paths for environment setup and diagnostics.
2. Establish standard documentation/templates and common tooling across all platform workflows.
3. Add self-service for preview creation, staging refresh initiation, promotion requests, and diagnostic access.
4. Later: integrate platform capabilities directly into CLI/IDE/other normal workflows (integrated services).

### Provisioning Roadmap

1. Eliminate manual one-off provisioning for core workflows.
2. Standardize on IaC templates and formal request workflows.
3. Add automated provisioning via CI/CD and controlled self-service.
4. Later: add predictive/adaptive allocation logic.

### TVP Maturity Boundary

**Required in TVP**:
- Standard tooling for environment setup
- Standard diagnostic path
- Paved provisioning
- Automated provisioning for the top Odoo.sh-equivalent workflows
- Centralized allocation visibility

**Deferred**:
- Fully integrated platform capabilities across all engineering tools
- Predictive/adaptive resource provisioning/deallocation

### Workflow Classification

| Workflow | Maturity Target |
|----------|----------------|
| Preview environment create/destroy | Automated provisioning + self-service |
| Staging refresh/scrub | Automated provisioning + self-service request path |
| Prod promote | Automated provisioning with approvals/checks |
| Developer environment bootstrap | Standard tooling first, self-service if repeated enough |
| Logs/diagnostics access | Standard tooling first, integrated services later |

### Reference Implementation Inventory

Use these as pattern sources (not normative doctrine):

| Source | Pattern |
|--------|---------|
| microsoft-foundry/foundry-samples | Docs/sample structure and onboarding patterns |
| microsoft-foundry/mcp-foundry | MCP/provider abstraction pattern |
| microsoft-foundry/foundry-agent-webapp | Webapp + Entra ID + Foundry Agents integration pattern |
| microsoft/Foundry-Local | Local dev / offline / OpenAI-compatible API pattern |
| Azure-Samples AI Foundry baseline | Production architecture pattern (hardened before use) |
| Azure-Samples azd starter basic | Bootstrap/IaC starter pattern (non-production without hardening) |

### Explicit Exclusions

- Do not treat `foundry-rs/foundry` or `foundry-rs/foundry-toolchain` as Azure-platform reference material. They are Ethereum/Solidity toolchain repos (naming collision).
- They may only be revisited if there is a separate smart-contract/EVM delivery track.

---

## Explicit Deviations from Odoo.sh

| Odoo.sh | Azure | Reason |
|---------|-------|--------|
| Auto weekly source refresh | Pinned base images + upgrade pipelines | Deterministic |
| Auto stage safety | Post-restore automation (`sanitize_staging.sql`) | Explicit and auditable |
| Addon auto-detect | `addons.manifest.yaml` SSOT | Reproducible |
| GCP-only hosting | Azure SEA (extensible) | Our cloud |
| No PG extensions | pgvector, PostGIS supported | Better capability |
| 10K table limit | No limit | No restriction |
