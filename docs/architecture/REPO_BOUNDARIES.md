# Repository Boundaries

## Purpose
Define canonical ownership for each repository in the InsightPulseAI organization.

## Status
Canonical.

## Repository Ownership Map

### `.github`
**Scope**: Org governance, reusable workflows, policy.
- GitHub Actions reusable workflow definitions
- Org-level issue/PR templates
- Policy documents that apply across all repos
- CODEOWNERS defaults

### `odoo`
**Scope**: ERP/runtime, modules, OCA, IPAI bridge, config, scripts.
- Odoo CE 19.0 runtime and configuration
- Custom `ipai_*` modules
- OCA submodule references and integration
- Odoo-specific scripts (`scripts/odoo/*.sh`)
- ERP data models, views, security, reports
- Odoo devcontainer configuration

### `web`
**Scope**: Public sites, advisory copilot UI, frontend integration with Workers.
- Landing pages and public-facing web properties
- Advisory copilot browser-side components (launcher, chat panel, prompt chips)
- Frontend assets consuming Cloudflare Worker endpoints
- Next.js / static site generators for public content
- Browser-side integration code

### `agents`
**Scope**: Foundry contracts, prompts, evals, orchestration metadata.
- Azure AI Foundry integration contracts
- Prompt templates and versioned prompt libraries
- Evaluation harnesses and scoring rubrics
- Agent orchestration metadata and mode definitions
- Model selection and routing configuration

### `infra`
**Scope**: IaC, Azure provisioning, Cloudflare config, Workers deployment, DNS/WAF.
- Terraform / Bicep / IaC definitions
- Azure Container Apps provisioning
- Cloudflare DNS, WAF, and Workers deployment configuration
- Azure Front Door configuration
- SSL/TLS certificate management references
- Environment provisioning scripts

### `ops-platform`
**Scope**: Control-plane services, internal admin APIs, secrets registry refs.
- Internal administration APIs
- Control-plane service definitions
- Secrets registry references (not secrets themselves)
- Platform health and status services
- Internal tooling APIs

### `automations`
**Scope**: n8n, cron, scheduled jobs, webhook-triggered flows, workflow contracts.
- n8n workflow definitions and exports
- Cron job definitions
- Scheduled task configurations
- Webhook-triggered flow definitions
- Workflow contracts and interface definitions

### `lakehouse`
**Scope**: CDC, bronze/silver/gold, analytics models, Tableau publication.
- Change Data Capture pipeline definitions
- Medallion architecture layer definitions (bronze/silver/gold)
- Analytics data models and transformations
- Tableau publication configurations and data source definitions
- Data quality rules and validation

### `design-system`
**Scope**: Tokens, shared UI components, icons, brand.
- Design tokens (colors, spacing, typography)
- Shared UI component library
- Icon sets and brand assets
- Style guides and component documentation

### `templates`
**Scope**: Scaffolds, bootstrap starters.
- Project scaffold generators
- Bootstrap starter templates
- Cookiecutter / yeoman / custom generators
- Boilerplate configurations for new services

## Cloudflare Workers Boundary Rules

### Canonical Home
Worker deployment configuration and infrastructure-as-code lives in `infra`. This includes:
- `wrangler.toml` or equivalent configuration
- Route and hostname bindings
- Environment variable declarations (not values)
- Deployment scripts and CI integration

### Consumer Repos
- **`web`**: Consumes Worker endpoints as API facades. Owns the browser-side code that calls Worker URLs. Does not own Worker deployment.
- **`automations`**: May use Worker ingress for webhook intake (e.g., external service webhooks routed through a Worker before reaching n8n). Does not own Worker deployment.
- **`agents`**: Should not default to Workers as runtime. Agent orchestration runs on self-hosted infrastructure. Workers may act as an optional edge proxy in front of agent endpoints, but this is an `infra` concern, not an `agents` concern.

### Cross-Repo Contract
- `infra` publishes Worker endpoint URLs and route contracts
- `web` and `automations` consume those contracts
- Changes to Worker routes require `infra` PR, not consumer repo PRs
- Worker secrets are managed via `infra` deployment pipelines, never committed to any repo
