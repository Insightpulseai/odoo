# Constitution — OdooSH Azure Equivalent

## Mission

Deliver an Azure-native platform that behaves like Odoo.sh for Odoo operations, without depending on Odoo.sh itself. The behavioral contract is Odoo.sh; the implementation substrate is Azure.

## Non-Negotiables

1. **Branch-aware CI/CD**: Every protected branch and PR must have deterministic pipeline behavior. Pushes build, PRs preview, merges promote.

2. **Immutable runtime**: Dependencies are baked into Docker images at build time. No mutable runtime package installs. No system package changes post-deploy.

3. **Explicit environment contract**: Only `dev`, `staging`, `production` are valid public stages. Database names: `odoo_dev`, `odoo_staging`, `odoo`. Never `odoo_prod`.

4. **Safe non-prod by default**: Non-prod environments must have:
   - Outbound mail trapped (Mailpit)
   - All `ir.mail_server` deactivated
   - Risky integrations removed or sandboxed (payment, social, calendar, IAP)
   - Cron jobs reduced or disabled
   - `/robots.txt` disabled
   - `ODOO_STAGE` env var set correctly

5. **Promotion, not rebuild, to prod**: Production consumes a previously built and tested artifact/image. Never build directly for production.

6. **Rollback is first-class**: App rollback via ACA revisions/labels. DB rollback via PostgreSQL PITR. Both must be documented and rehearsed.

7. **Odoo-aware runtime discipline**: No implicit addon discovery. Addon inventory and `addons_path` are machine-defined from `config/addons.manifest.yaml`.

8. **Evidence-first operations**: Each promotion records: artifact/image digest, DB state, approvals, smoke check results, post-deploy health.

## Hard Implementation Constraints

- **Front Door Standard/Premium only**. Do not use Front Door Classic for new work.
- **ACA managed certificates and Cloudflare can conflict** when Cloudflare is used as intermediate CNAME/proxy. Document and resolve in edge design.
- **Azure DevOps environments are logical deployment/audit targets**, not ACA-native resource registrations. Use them for history and approvals, with ACA as the actual runtime.
- **Service connections and environment names must be compile-time stable**. Do not make them runtime-variable-driven. Azure authorizes resources before a stage starts.
- **Key Vault-backed variable groups** for pipeline secrets. Never hardcode secrets in YAML.

## Odoo.sh Behaviors Replicated

| Odoo.sh Behavior | Azure Implementation |
|-------------------|---------------------|
| Auto-build on push/PR | Azure Pipelines triggers or GitHub Actions |
| Staging built with prod data | `refresh_staging.sh` + `sanitize_staging.sql` |
| Staging mail captured | Mailpit + `ir.mail_server` disabled |
| Staging crons disabled | `sanitize_staging.sql` disables non-essential crons |
| Staging integrations off | `sanitize_staging.sql` strips payment/social/calendar/IAP tokens |
| `ODOO_STAGE` env var | ACA environment variable |
| Feature branch instant test | PR preview via ACA revision |
| Dev→Staging→Production flow | Multi-stage pipeline with approvals |
| Daily backups, 3-month retention | Azure PG PITR, 35-day retention |
| Shell access | `az containerapp exec` |
| Mail catcher | Mailpit container |
| Custom domains + SSL | Cloudflare DNS → Azure Front Door → ACA |

## Interface Doctrine

1. The platform must evolve interfaces from ad hoc team-specific processes toward consistent standard tooling and then self-service solutions. Standard tooling means consistent interfaces plus documentation/templates and paved roads. Self-service means autonomy with consistent, discoverable user experiences.

2. The first acceptable maturity target is not fully integrated services everywhere. The first acceptable target is broad consistency and reduced support burden through standard tooling and selective self-service.

3. Development-environment setup and application diagnosis are first-class platform interfaces, not side concerns. These are the concrete focal examples for interface maturity.

## Provisioning Doctrine

1. Provisioning must move from manual/coordinated patterns to paved and then automated workflows using IaC templates, formalized processes, structured request paths, and centralized metrics.

2. Core provisioning workflows must be integrated into CI/CD with governance and compliance checks in-line.

3. Authorized users must be able to provision dedicated or shared standardized environments through controlled self-service, not only through ticket escalation.

4. Predictive/adaptive allocation is a future capability, not a prerequisite for the first release.

**Guardrail**: The platform must avoid the coordinated trap where requests are centralized through ticketing/manual approval but still bottleneck on the platform team. That phase is necessary for consistency but slow and overhead-heavy; the goal is to move through it, not stay in it.

## Source Governance Doctrine

1. Normative sources define behavior and doctrine: Odoo.sh docs + Microsoft platform-engineering/devops guidance + Azure Well-Architected Framework.

2. Reference implementations may influence shape and examples but do not override doctrine.

3. Naming-collision repos must not be mistaken for normative sources. In particular, `foundry-rs/*` is unrelated to Microsoft Foundry and must stay out of the Azure/Odoo.sh platform baseline unless an explicit blockchain/EVM workstream is added.

4. The OKR/goal-tracking layer must remain tool-agnostic. Viva Goals was retired December 31, 2025 -- do not name it as a future operating surface.

## AI Platform Extension Doctrine

1. The platform may support AI workload extensions through provider-based integration, MCP surfaces, local development, and production reference architectures derived from Microsoft Foundry examples.

2. Local-first AI development is allowed as an implementation mode because Foundry Local runs models on local hardware without requiring an Azure subscription and exposes an OpenAI-compatible API.

3. Production AI paths must align to hardened reference architecture patterns (network isolation, controlled dependencies, security controls) as shown by Microsoft's Azure AI Foundry baseline.

4. Bootstrap/starter templates accelerate onboarding but must be marked as non-production baselines unless explicitly hardened.

## Odoo.sh Behaviors Intentionally Changed

| Odoo.sh Behavior | Azure Change | Reason |
|-------------------|-------------|--------|
| Weekly auto-source refresh | Pinned base images + scheduled upgrade pipelines | Deterministic, not surprise updates |
| Auto addon folder detection | Explicit `addons.manifest.yaml` | Reproducible, auditable |
| Single worker on staging/dev | Configurable per environment | More flexibility |
| 10,000 table/sequence limit | No limit | Azure PG has no cap |
| No system packages | Install anything via Dockerfile | Docker gives full control |
| No PostgreSQL extensions | pgvector, PostGIS, etc. supported | Azure PG supports extensions |
