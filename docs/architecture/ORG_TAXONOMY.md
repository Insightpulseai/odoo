# Organization Taxonomy — InsightPulse AI GitHub Organization

> Single source of truth for repository classification, naming, and lifecycle management.
> Reference SSOT: `ssot/github/org_repos.yaml` (when created)
> Last updated: 2026-03-05

---

## Overview

The InsightPulse AI GitHub organization uses a **tier-based taxonomy** to classify repositories by purpose, visibility, and operational lifecycle. This taxonomy governs:

- Repository naming conventions
- Package scoping (`@ipai/*`)
- Data classification (public, confidential, restricted)
- Publication policy (which repos may be public)
- Lifecycle states (active, maintenance, deprecated, archived)

---

## Tier System

### Tier 0: Platform Core

**Purpose**: Mission-critical infrastructure and platform services

**Characteristics**:
- Production dependencies with uptime requirements
- Breaking changes require RFC and migration path
- 24/7 operational support required
- Strict RBAC and audit requirements

**Examples**:
- `odoo` (main monorepo)
- `ipai-ops-platform` (operational infrastructure)
- `ipai-supabase-functions` (Edge Functions)

**Naming Convention**: `{service-name}` (no prefix)

**Package Scope**: `@ipai/{service}`

**Data Classification**: Confidential (may contain business logic, internal APIs)

**Publication Policy**: Private by default, selective public release after security review

---

### Tier 1: Product Applications

**Purpose**: User-facing products and customer applications

**Characteristics**:
- Direct revenue generation or customer engagement
- Product roadmap driven
- Feature development active
- Customer support SLAs

**Examples**:
- `scout-dashboard` (expense intelligence)
- `finance-ssc-platform` (finance SSC automation)
- `ppm-clarity` (project management)

**Naming Convention**: `{product-name}`

**Package Scope**: `@ipai/{product}`

**Data Classification**: Confidential (contains business logic, customer workflows)

**Publication Policy**: Private

---

### Tier 2: Internal Tools

**Purpose**: Developer productivity, operational tooling, automation

**Characteristics**:
- Internal use only (not customer-facing)
- Stability requirements lower than Tier 0-1
- May have breaking changes without RFC
- Lightweight support model

**Examples**:
- `n8n-automation-library` (workflow templates)
- `mcp-orchestrator` (MCP server coordination)
- `repo-hygiene-bot` (repository maintenance)

**Naming Convention**: `{tool-name}`

**Package Scope**: `@ipai/{tool}`

**Data Classification**: Confidential (contains internal processes, credentials references)

**Publication Policy**: Private

---

### Tier 3: Experiments & Prototypes

**Purpose**: Research, proof-of-concepts, experimental features

**Characteristics**:
- No production dependencies
- May be abandoned without migration path
- Low or no support expectations
- Rapid iteration expected

**Examples**:
- `llm-eval-harness` (model evaluation experiments)
- `ai-code-reviewer` (automated PR review prototype)

**Naming Convention**: `exp-{experiment-name}` or `poc-{concept}`

**Package Scope**: `@ipai-labs/{experiment}`

**Data Classification**: Internal (may contain research data, unvalidated algorithms)

**Publication Policy**: May be public if no sensitive data or competitive advantage

---

### Tier 4: Archived & Legacy

**Purpose**: Deprecated repositories with historical value

**Characteristics**:
- No active development
- Read-only or archived state
- Preserved for reference or compliance
- Migration path documented

**Examples**:
- `mattermost-connector` (replaced by Slack integration)
- `mailgun-bridge` (replaced by Zoho Mail bridge)

**Naming Convention**: Original name retained

**Package Scope**: Original scope (unpublished from npm/PyPI)

**Data Classification**: Historical (may contain deprecated APIs, old credentials)

**Publication Policy**: Archived (no new issues/PRs accepted)

---

### Special: UI Libraries

**Purpose**: Shared UI components, design systems, frontend utilities

**Characteristics**:
- Shared across multiple products
- Follows semantic versioning strictly
- High test coverage required (>90%)
- Design system aligned

**Examples**:
- `@ipai/ui-components` (React component library)
- `@ipai/design-tokens` (Figma-synced tokens)

**Naming Convention**: `ui-{library-name}`

**Package Scope**: `@ipai/{library}`

**Data Classification**: Public (reusable components, no business logic)

**Publication Policy**: Public (published to npm)

---

### Special: Finance Domain

**Purpose**: Philippine Finance SSC compliance modules (BIR, PEZA, etc.)

**Characteristics**:
- Regulatory compliance required
- Audit trail mandatory
- Change control gated by Finance approval
- Multi-client isolation

**Examples**:
- `ipai-finance-bir` (BIR tax filing automation)
- `ipai-finance-ppm` (project portfolio management)

**Naming Convention**: `ipai-finance-{module}`

**Package Scope**: `@ipai/finance/{module}`

**Data Classification**: Restricted (contains tax logic, financial projections)

**Publication Policy**: Private

---

## Naming Conventions

### Repository Names

| Tier | Pattern | Example |
|------|---------|---------|
| Tier 0 | `{service}` | `odoo`, `supabase-functions` |
| Tier 1 | `{product}` | `scout-dashboard`, `ppm-clarity` |
| Tier 2 | `{tool}` | `n8n-library`, `mcp-orchestrator` |
| Tier 3 | `exp-{name}` or `poc-{name}` | `exp-llm-eval`, `poc-ai-reviewer` |
| Tier 4 | `{original-name}` | `mattermost-connector` |
| UI Libs | `ui-{library}` | `ui-components`, `ui-tokens` |
| Finance | `ipai-finance-{module}` | `ipai-finance-bir` |

### Package Scopes

| Tier | Scope | Visibility |
|------|-------|------------|
| Tier 0 | `@ipai/{service}` | Private npm |
| Tier 1 | `@ipai/{product}` | Private npm |
| Tier 2 | `@ipai/{tool}` | Private npm |
| Tier 3 | `@ipai-labs/{experiment}` | Private npm |
| UI Libs | `@ipai/{library}` | Public npm |
| Finance | `@ipai/finance/{module}` | Private npm |

---

## Data Classification

### Public

**Definition**: No competitive advantage, no sensitive data, reusable by community

**Allowed Content**:
- Open-source libraries (MIT/Apache-2.0 licensed)
- UI component libraries without business logic
- Public documentation and guides

**Examples**: `@ipai/ui-components`, `@ipai/design-tokens`

**SSOT Field**: `classification: public`

---

### Confidential

**Definition**: Contains business logic, internal APIs, customer workflows

**Allowed Content**:
- Product application code
- Internal tooling and automation
- Platform services and infrastructure

**Examples**: `odoo`, `scout-dashboard`, `n8n-library`

**SSOT Field**: `classification: confidential`

---

### Restricted

**Definition**: Contains regulated data, financial logic, compliance requirements

**Allowed Content**:
- Philippine BIR tax filing modules
- Financial projections and analytics
- Multi-client isolated systems

**Examples**: `ipai-finance-bir`, `ipai-finance-ppm`

**SSOT Field**: `classification: restricted`

---

## Lifecycle States

### Active

**Definition**: Under active development, accepting issues/PRs, production-deployed

**Characteristics**:
- Regular commits (at least monthly)
- Issue triage and response
- Security patches applied
- Documentation current

**SSOT Field**: `lifecycle: active`

---

### Maintenance

**Definition**: No new features, only bug fixes and security patches

**Characteristics**:
- Commits only for critical fixes
- Issues accepted but low priority
- Security patches only
- Documentation frozen

**SSOT Field**: `lifecycle: maintenance`

---

### Deprecated

**Definition**: Scheduled for archival, migration path documented, no new deployments

**Characteristics**:
- README banner with deprecation notice
- Migration guide to replacement
- No new issues/PRs accepted
- Archive date announced

**SSOT Field**: `lifecycle: deprecated`

**Required Metadata**:
```yaml
deprecation:
  deprecated_at: "2026-02-01"
  reason: "Replaced by Slack integration"
  replacement: "ipai-slack-connector"
  archive_after: "2026-06-01"
  migration_guide: "docs/migrations/mattermost-to-slack.md"
```

---

### Archived

**Definition**: Read-only, no maintenance, preserved for historical reference

**Characteristics**:
- GitHub archived status enabled
- No commits allowed
- Issues/PRs disabled
- Compliance retention period documented

**SSOT Field**: `lifecycle: archived`

---

## Publication Policy

### Public Repositories

**Criteria** (ALL must be met):
- ✅ Data classification: Public
- ✅ No hardcoded secrets or credentials
- ✅ Security scan passed (no high/critical vulnerabilities)
- ✅ Open-source license approved (MIT, Apache-2.0, BSD-3)
- ✅ README with usage examples and contribution guide

**Approval Process**:
1. Create PR changing `visibility: private` → `visibility: public` in `ssot/github/org_repos.yaml`
2. Security review by DevSecOps team
3. Legal review if commercial implications
4. Merge PR → CI applies visibility change via GitHub API

---

### Private Repositories (Default)

**Characteristics**:
- All repos start as private
- Access controlled via GitHub teams
- Require authentication for cloning
- No external contributors

---

## Cross-References

### Secrets Registry

**SSOT**: `ssot/secrets/registry.yaml`

**Contract**: Repository secrets (GitHub Actions, deploy keys) must be registered in secrets registry before use.

**Documentation**: `docs/architecture/SECRETS_POLICY.md`

---

### Integration Catalog

**SSOT**: `ssot/integrations/_index.yaml`

**Contract**: Integration-specific repositories must be registered in integration catalog.

**Documentation**: `docs/architecture/SSOT_BOUNDARIES.md §14`

---

### OCA Dependencies

**SSOT**: `ssot/oca/oca_repos.yaml`

**Contract**: Odoo Community Association (OCA) module dependencies tracked separately.

**Documentation**: `docs/architecture/OCA_HYDRATION.md`

---

## Maintenance Procedures

### Adding a New Repository

**Steps**:
1. **Create SSOT Entry**: Add row to `ssot/github/org_repos.yaml`
   ```yaml
   - id: new-repo
     name: new-repo
     tier: 1  # Product application
     classification: confidential
     lifecycle: active
     visibility: private
     package_scope: "@ipai/new-repo"
     description: "New product application"
   ```

2. **Create Repository**: Use GitHub CLI or API
   ```bash
   gh repo create Insightpulseai/new-repo --private --description "New product application"
   ```

3. **Apply Settings**: CI applies settings from SSOT via GitHub API

4. **Initialize**: Add standard files (README, LICENSE, CLAUDE.md, .gitignore)

5. **Register Package**: If publishable, add to npm/PyPI with correct scope

---

### Changing Lifecycle State

**Scenario**: Mark repository as deprecated

**Steps**:
1. **Update SSOT**: Edit `ssot/github/org_repos.yaml`
   ```yaml
   - id: old-repo
     lifecycle: deprecated
     deprecation:
       deprecated_at: "2026-03-05"
       reason: "Replaced by new-repo"
       replacement: "new-repo"
       archive_after: "2026-09-05"
       migration_guide: "docs/migrations/old-to-new.md"
   ```

2. **Add Deprecation Notice**: Update README
   ```markdown
   # [DEPRECATED] old-repo

   ⚠️ This repository is deprecated and will be archived on 2026-09-05.

   **Replacement**: [new-repo](https://github.com/Insightpulseai/new-repo)
   **Migration Guide**: [docs/migrations/old-to-new.md](docs/migrations/old-to-new.md)
   ```

3. **Update Documentation**: Create migration guide

4. **Notify Users**: Announce in Slack, email stakeholders

5. **Archive on Date**: After 6 months, change `lifecycle: archived` and GitHub archive

---

### Marking Repository as Public

**Prerequisites**:
- Data classification: public
- Security scan: passed
- No hardcoded secrets
- Open-source license approved

**Steps**:
1. **Security Scan**: Run `gitleaks` and `trivy` on repository
   ```bash
   gitleaks detect --source /path/to/repo --no-git
   trivy repo /path/to/repo
   ```

2. **Update SSOT**: Change `visibility: public` in `ssot/github/org_repos.yaml`

3. **Legal Review**: If commercial implications, request review

4. **Merge PR**: CI applies visibility change via GitHub API

5. **Publish Package**: If npm package, run `npm publish --access public`

---

## Examples

### Example 1: Adding a New Product Repository

**Scenario**: Create `expense-flow-api` repository for Tier 1 product

```yaml
# ssot/github/org_repos.yaml
- id: expense-flow-api
  name: expense-flow-api
  tier: 1
  classification: confidential
  lifecycle: active
  visibility: private
  package_scope: "@ipai/expense-flow-api"
  description: "Expense automation API for Scout Dashboard"
  tech_stack:
    - Node.js
    - TypeScript
    - Supabase
  owner_team: "@insightpulseai/backend"
```

**Result**: Private repository, confidential classification, active lifecycle

---

### Example 2: Deprecating Mattermost Connector

**Scenario**: Replace `mattermost-connector` with `slack-connector`

```yaml
# ssot/github/org_repos.yaml
- id: mattermost-connector
  name: mattermost-connector
  tier: 4  # Archived
  classification: confidential
  lifecycle: deprecated
  visibility: private
  package_scope: "@ipai/mattermost-connector"
  description: "[DEPRECATED] Mattermost integration (replaced by Slack)"
  deprecation:
    deprecated_at: "2026-01-28"
    reason: "Organization migrated to Slack"
    replacement: "slack-connector"
    archive_after: "2026-07-28"
    migration_guide: "docs/migrations/mattermost-to-slack.md"
```

**Actions**:
1. Add deprecation notice to README
2. Create migration guide
3. Archive after 6 months (2026-07-28)

---

### Example 3: Publishing UI Component Library

**Scenario**: Make `@ipai/ui-components` public on npm

**Prerequisites**:
- Security scan passed (no vulnerabilities)
- MIT license applied
- No hardcoded credentials
- Documentation complete

```yaml
# ssot/github/org_repos.yaml
- id: ui-components
  name: ui-components
  tier: ui_libs
  classification: public
  lifecycle: active
  visibility: public
  package_scope: "@ipai/ui-components"
  description: "InsightPulse AI UI Component Library (React + TypeScript)"
  license: "MIT"
  tech_stack:
    - React
    - TypeScript
    - Storybook
  owner_team: "@insightpulseai/frontend"
```

**Actions**:
1. Run security scan
2. Apply MIT license
3. Update SSOT `visibility: public`
4. Merge PR → CI makes repo public
5. Publish to npm: `npm publish --access public`

---

## Verification

### SSOT Compliance Check

```bash
# Verify all repositories are registered in SSOT
scripts/verify-repo-taxonomy.sh

# Output:
# ✅ All 47 repositories registered in ssot/github/org_repos.yaml
# ✅ All package scopes follow naming conventions
# ⚠️  2 deprecated repositories without migration guides
```

---

### CI Enforcement

**Workflow**: `.github/workflows/repo-taxonomy-guard.yml`

**Triggers**:
- Pull requests modifying `ssot/github/org_repos.yaml`
- Scheduled: Daily at 2 AM

**Checks**:
- All repositories in SSOT match GitHub org
- Visibility settings match SSOT
- Lifecycle states valid
- Deprecated repos have migration guides

---

## References

- **Secrets Registry**: `ssot/secrets/registry.yaml` + `docs/architecture/SECRETS_POLICY.md`
- **Integration Catalog**: `ssot/integrations/_index.yaml`
- **SSOT Boundaries**: `docs/architecture/SSOT_BOUNDARIES.md`
- **GitHub Enterprise Contract**: `docs/architecture/GITHUB_ENTERPRISE_CONTRACT.md`
