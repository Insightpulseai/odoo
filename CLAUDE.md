# CLAUDE.md — InsightPulse AI Monorepo

> Slim index. All heavy detail lives in `.claude/rules/` files (auto-loaded by Claude Code).

---

## Pulser — canonical classification

**Core type:** Custom-engine agent
- Owns its own runtime, tools, policies, retrieval, and validators
- Not a declarative agent; not a host-product copilot

**Functional type:** Transactional and operational copilot
- System-of-action inside Odoo: prepares, validates, routes, summarizes, publishes
- Not a chatbot. Not a knowledge bot.

**Architecture type:** Multi-agent orchestrated system
- Planner/router + specialist agents (finance, project finance, research, ops)
- Fallback / self-heal policies
- Tool calling, retrieval, validators

**Governance type:** Policy-gated agent
- RBAC + approval bands + evidence scope + mutation safety + surface/domain/role behavior matrix
- Governed enterprise agent — not open autonomous

**Execution policy:** Mutating actions are explicit-approval by default
- Read-only tools may run approval-free where policy allows
- Write-capable tools and business-state mutations require explicit approval unless the active policy matrix allows safe auto-execution
- High-risk finance, tax, approval, and publish actions never run silently

**GTM label:** "Pulser is an AI operating copilot for Odoo."
**Technical label:** "Custom-engine, multi-agent, policy-gated enterprise copilot for Odoo-centered workflows."
**Architecture label:** "Custom-engine agent platform with planner/router, specialist agents, tool adapters, retrieval, validators, and policy-gated action execution."

---

## Operating Contract: Execute, Deploy, Verify (No Guides)

You are an execution agent. Do not provide deployment guides, scripts, or instructional snippets as the primary output.

1. **Execute** the change / deploy / run the migration / push the tag.
2. **Verify** the result with deterministic checks.
3. **Evidence** pack in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`.
4. **Commit** & push evidence and any code/config changes.

If you cannot execute due to missing credentials/tooling/access, say exactly what is missing in one sentence, then continue producing everything that *can* be executed without asking questions.

**Output format**: Outcome (1-3 lines) + Evidence + Verification (pass/fail) + Changes shipped. No "Next steps", no tutorials.

**Execution surfaces**: Git, GitHub Actions, SSH, Docker, Azure CLI.

**Banned**: "here's a guide", "run these commands", "you should...", asking for confirmation, time estimates, UI clickpaths.

---

## Engineering Execution Doctrine

**Reuse first, build the delta only.**

| Capability class | Action |
|---|---|
| Commodity (Odoo core, OCA, AVM, Agent Framework, Playwright, Workspace CLI, Azure DevOps MCP) | Adopt upstream as-is |
| Compositional (infra topology, naming/tag policy, CI/CD composition, test harnesses, release gates) | Configure |
| Business-specific (PH overlays, surface workflows, approval/audit guardrails, Pulser tools) | Build only the thinnest `ipai_*` layer |

**Odoo extension order (canonical):**
`Config → CE property fields → OCA → adjacent OCA composition → thin ipai_* delta`. Never fork Odoo core for standard integrations. See `docs/architecture/odoo-integrations-selfhosted-azure.md`.

**Claude Code execution doctrine:**
1. **Design first** — architecture/SSOT/adoption decisions land in `docs/architecture/`, `ssot/`, `spec/`.
2. **Codify second** — `CLAUDE.md` (enduring doctrine, keep ≤ 200 lines), `.claude/rules/*.md` (path-scoped), `.claude/skills/` (reusable workflows), `.mcp.json` (team-approved shared MCP servers).
3. **Execute third** — Claude Code (CLI / VS Code extension) is the preferred repo-local execution engine. It must follow repo doctrine; it does not invent platform choices ad hoc.

**Repo doctrine layering:**

| Layer | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Enduring repo doctrine (always loaded) | Committed |
| `.claude/rules/*.md` | Path-scoped rules, loaded on demand | Committed |
| `.claude/skills/` | Reusable workflows | Committed |
| `.mcp.json` | Team-approved shared MCP servers | Committed (no secrets) |
| `CLAUDE.local.md` | Personal/local overrides | Gitignored |
| Auto memory (`~/.claude/projects/<repo>/memory/`) | Learned operational notes | Machine-local, NOT canonical architecture |
| Branch protection / CI / tool permissions | Real hard enforcement | — |

`CLAUDE.md` and `.claude/rules/` shape behavior but do not hard-block; enforcement lives in CI gates, branch protection, and tool permissions.

**Verification contract:** Every meaningful task ends with at least one of — Odoo test run, Playwright smoke, schema/policy validation, CI workflow result, rendered artifact diff, runtime health check. Self-verification is mandatory; generation alone is not "done".

**Execution loop (Anthropic best practice):** `Explore → Plan → Implement → Verify → Commit/PR`. Use Plan Mode for non-trivial changes.

**Agent teams (experimental):** Default = single session. Subagents for focused delegation. Agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) only for parallel execution/review with separable file or plane ownership — never for architecture/SSOT drafting or tightly coupled refactors. 3–5 teammates, ~5–6 tasks each.

---

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | Odoo CE 18.0 + OCA + n8n + Slack + PostgreSQL 16 |
| **Domain** | `insightpulseai.com` (`.net` is deprecated) |
| **DNS** | Azure DNS (authoritative, delegated from Squarespace) |
| **Mail** | Zoho SMTP (`smtp.zoho.com:587`, domain: `insightpulseai.com`) |
| **Hosting** | Azure Container Apps (behind Azure Front Door) |
| **Node** | >= 18.0.0 (pnpm workspaces, Turborepo) |
| **Python** | 3.10+ (Odoo 18) |
| **Web/CMS** | Azure Container Apps (public + internal), Odoo website |
| **EE Parity** | Target >=80% via `CE + OCA + ipai_*` (current: ~35-45%, audited 2026-03-08) |
| **Repo** | `Insightpulseai/odoo` (renamed from `odoo-ce`) |

---

## Secrets Policy

Never hardcode, never echo, never ask user to paste. Secrets in `.env*` / env vars / Azure Key Vault only.
See `.claude/rules/security-baseline.md` for full policy (sections 2.1-2.6).

---

## Repo Map

| Path | Owns |
|------|------|
| `addons/ipai/` | 69 custom IPAI modules |
| `addons/oca/` | OCA community modules (hydrated at runtime, not tracked) |
| `apps/` | 9 applications (ops-console, mcp-jobs, slack-agent, etc.) |
| `packages/` | Shared packages (agents, taskbus) |
| `spec/` | 76 spec bundles |
| `scripts/` | 1000 automation scripts in 86 categories |
| `odoo18/` | Canonical Odoo 18 setup (config, scripts, backups) |
| `mcp/servers/` | MCP server implementations (plane is the only live one) |
| `.github/workflows/` | 355 CI/CD pipelines |
| `docker/`, `deploy/` | Docker configs and deployment |
| `platform/` | Canonical platform control-plane (replaces `ops-platform`) |
| `data-intelligence/`| Canonical lakehouse/Databricks code (replaces `lakehouse`) |
| `agents/` | Canonical agent/skill assets (personas, judges, skills) |
| `agent-platform/` | Canonical agent runtime/orchestration engine |
| `infra/` | Shared infrastructure and edge configuration |
| `design/` | Shared design tokens and assets (replaces `design-system`) |
| `ssot/` | Intended-state truth for platform and ERP runtime |

---

## Cross-Repo Invariants

- **Microsoft 365 Agents SDK** is a channel layer for enterprise delivery (Copilot, Teams, Web). It does NOT replace the canonical `agent-platform` runtime.
- **Service-to-service auth**: All internal flows must use Managed Identities + Azure Key Vault.

1. **Secrets**: `.env` files only, never hardcode. Azure Key Vault for runtime.
2. **Database**: Odoo uses PostgreSQL (local or Azure managed). All Azure-native.
3. **No Supabase**: Supabase is fully deprecated (2026-03-26). All services are Azure-native.
4. **CE Only**: No Enterprise modules, no odoo.com IAP dependencies.
5. **OCA First**: Prefer OCA modules over custom `ipai_*` when available. Config -> OCA -> Delta.
6. **Specs Required**: Significant changes must reference a spec bundle.
9. **Databricks Governance**: Databricks + Unity Catalog is the mandatory governed transformation, engineering, and serving plane.
10. **MCP First**: MCP is required for all reusable agent tools (Google Cloud contract).
11. **SaaS Authority**: The **Azure SaaS Workload Documentation** is the canonical design framework for the platform.
12. **Consumption**: **Power BI** is the primary mandatory business-facing reporting surface.
13. **Fabric Complement**: Fabric is for mirroring and OneLake integration; it never replaces Databricks engineering.
14. **Stateless Agents**: Session state must be stored externally (Stateless Application rule).
15. **Sequential Default**: Use Sequential orchestration for deterministic finance flows; Maker-Checker for gates.
16. **Release Gate**: All production releases must pass the [Feature Ship-Readiness Checklist](docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md) (5 gates: Product, Correctness, Runtime, Safety, Evidence). SSOT: `ssot/release/feature-ship-readiness-gates.yaml`.
17. **SAP Adapter Only**: SAP is an integrated external enterprise surface. Use Azure Functions or App Service with SAP Cloud SDK for adapter services. Do not adopt SAP infrastructure hosting templates (NetWeaver, HANA, LaMa, S/4HANA) as canonical platform architecture unless SAP runtime hosting is explicitly in scope.
18. **iOS Wrapper Skill Pack**: When working on the iOS native wrapper (`web/mobile/`), apply `docs/skills/ios-native-wrapper.md`. Prefer native auth (`AuthenticationServices`), native biometrics (`LocalAuthentication`), allowlist-based webview navigation, automated simulator smoke tests, and CI + `fastlane` release automation. No cross-platform frameworks.
19. **Apple Design Authority (iOS)**: For iOS wrapper UI, treat Apple's current App design and UI / Liquid Glass guidance as the visual system authority. Native shell chrome follows current Apple design language. `Icon Composer` for app icons, `SF Symbols` for native shell iconography. Liquid Glass applies to native shell surfaces, not arbitrary overlays on hosted web content.
20. **iOS Wrapper UI Contract**: For wrapper-shell changes (`WrapperViewController`, `BiometricAuth`, native chrome, auth handoff, icon assets), apply `docs/skills/ios-wrapper-ui-contract.md`. This contract is subordinate to `docs/skills/ios-native-wrapper.md` and defines enforceable code-review gates.
21. **iOS Wrapper Code Contract**: When editing wrapper-shell implementation files, also apply `docs/skills/ios-wrapper-code-contract.md`. File-level review emphasis: `WrapperViewController.swift` owns shell orchestration only, `BiometricAuth.swift` owns biometric policy/orchestration only, `Assets.xcassets` stays minimal and governed, `Environment.swift` remains the source of routing/environment configuration, `Info.plist` remains aligned with native auth/biometric requirements.
22. **Odoo Integration Adoption**: Check Odoo 18 native integrations first (payments, bank sync, EDI, commerce connectors, website). If native is insufficient, check OCA before creating `ipai_*`. Reserve `ipai_*` for thin bridges to external Azure/Foundry services only. SSOT: `ssot/odoo/integration_adoption.yaml`.
23. **Engineering Execution Doctrine**: Reuse upstream for commodity capability; configure for compositional concerns; build only the thinnest `ipai_*` layer for business-specific deltas. Design first (`docs/architecture/`, `ssot/`, `spec/`) → codify second (`CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.mcp.json`) → execute third (Claude Code follows doctrine, never invents platform choices). Auto memory is learned ops notes, not canonical architecture. See "Engineering Execution Doctrine" section above.

---

## Common Workflows

### Agent Pattern

```
explore -> plan -> implement -> verify -> commit
```

| Command | Purpose |
|---------|---------|
| `/project:plan` | Create detailed implementation plan |
| `/project:implement` | Execute plan with minimal changes |
| `/project:verify` | Run all verification checks |
| `/project:ship` | Orchestrate full workflow end-to-end |
| `/project:fix-github-issue` | Fix a specific GitHub issue |

### Verification (run before every commit)

```bash
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

### Agent Rules

1. **Never guess**: Read files first, then change them
2. **Simplicity first**: Prefer the simplest implementation
3. **Verify always**: Include verification after any mutation
4. **Minimal diffs**: Keep changes small and reviewable
5. **Update together**: Docs and tests change with code

### Common Commands

```bash
docker compose up -d                    # Start full stack
./scripts/deploy-odoo-modules.sh        # Deploy IPAI modules
./scripts/ci/run_odoo_tests.sh          # Run Odoo unit tests
pnpm install                            # Install Node dependencies
```

---

## Odoo extension and customization doctrine

When implementing new capability in Odoo, follow this decision order:

1. **Odoo CE 18 native capability first**
   - Prefer standard CE behavior before adding modules or code.

2. **Odoo property fields second, when the requirement is parent-scoped metadata**
   - Use property fields when the need is lightweight, configurable, form-level metadata tied to a parent record (e.g., project-specific task attributes, team-specific CRM qualifiers, category-scoped product enrichment).
   - Property fields are pseudo-fields, not stored as normal database columns, scoped by a parent record.
   - **NOT appropriate for:** core accounting logic, strong relational domain models, cross-parent canonical master data, heavy reporting, integration contracts, workflow-critical fields, fields needing robust server logic or DB-level consistency.

3. **OCA 18 same-domain modules third**
   - Search the primary OCA repository for the functional domain before writing custom code.

4. **Adjacent OCA 18 modules fourth**
   - Check neighboring OCA domains before concluding there is a gap.
   - Example: project need → also inspect `timesheet`, `project-reporting`, `knowledge`, `account-analytic`, `connector-*`, `l10n-*`.
   - Compose CE + property fields + OCA modules where possible.

5. **Custom `ipai_*` modules last**
   - Custom modules are a last-resort extension path only.
   - `ipai_*` must stay thin and bridge-oriented: integration bridges, orchestration glue, AI/copilot overlays, adapters, narrow opinionated extensions.
   - **Do not create `ipai_*` modules to duplicate viable CE/OCA parity.**

### Mandatory requirements for any approved custom `ipai_*` module

Every custom module is incomplete unless it includes:

- `README.md`
- `docs/MODULE_INTROSPECTION.md`
- `docs/TECHNICAL_GUIDE.md`

Required minimum structure:

```
addons/ipai/<module_name>/
  README.md
  docs/
    MODULE_INTROSPECTION.md
    TECHNICAL_GUIDE.md
  __manifest__.py
  models/
  views/
  security/
  data/
  tests/
```

### Required contents of `MODULE_INTROSPECTION.md`

- Why this module exists
- Business problem
- CE 18 coverage checked
- **Property-field assessment** (could properties solve this? If not, why not?)
- OCA 18 same-domain coverage checked
- Adjacent OCA modules reviewed
- Why CE + property fields + OCA composition was insufficient
- Why custom code is justified
- Module type: bridge / overlay / adapter / extension
- Functional boundaries
- Extension points used (`_inherit`, view inheritance, hooks, server actions, APIs)
- Blast radius
- Upgrade risk
- Owner
- Retirement / replacement criteria

### Required contents of `TECHNICAL_GUIDE.md`

- Architecture
- Models extended
- Fields added
- Methods overridden
- View inheritance points
- Security model
- Data files loaded
- Jobs / cron / queues / webhooks
- External integrations
- Test strategy
- Upgrade / rollback notes
- Known limitations and failure modes

### Implementation rules

- Prefer `_inherit`, view inheritance, additive extension, and modular composition over invasive overrides.
- Override CRUD/core methods only when necessary, and always preserve parent behavior via `super()`.
- A custom module is **not justified** if the requirement can be solved by CE 18, property fields, OCA 18, or composition of those layers.

### Canonical doctrine sentence

> Doctrine: CE 18 first → property fields for parent-scoped lightweight metadata → OCA 18 same-domain → adjacent OCA → compose CE + properties + OCA → custom `ipai_*` as last resort with mandatory module introspection and technical guide.

---

## Deprecated (Never Use)

| Item | Replacement | Date |
|------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| Mattermost (all) | Slack | 2026-01-28 |
| Appfine (all) | Removed | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |
| Supabase (all instances, all usage) | Azure-native services | 2026-03-26 |
| Cloudflare (DNS proxy) | Azure DNS (authoritative) | 2026-03-26 |
| `ipai_ai_widget` (global patches) | Native Odoo 18 Ask AI + `ipai_ai_copilot` | 2026-03-09 |
| DigitalOcean (all) | Azure (ACA + VM + managed PG) | 2026-03-15 |
| Public nginx edge | Azure Front Door | 2026-03-15 |
| Self-hosted runners | GitHub-hosted / Azure DevOps pool | 2026-03-15 |
| Mailgun (`mg.insightpulseai.com`) | Zoho SMTP | 2026-03-11 |
| Vercel deployment | Azure Container Apps | 2026-03-11 |
| GitHub Actions (blanket deprecation) | GitHub Actions = CI + website/docs deploy; Azure DevOps = Odoo/Databricks/Infra deploy (see `ssot/governance/platform-authority-split.yaml`) | 2026-03-30 |
| `ipai-odoo-dev-pg` (Burstable PG) | `pg-ipai-odoo` (General Purpose, Fabric mirroring) | 2026-03-21 |
| Superset (as canonical BI) | Power BI (primary) + Superset (supplemental only) | 2026-03-21 |
| Notion (as data source) | Removed from Databricks bundle | 2026-03-21 |
| Wix (all — hosting, CMS, DNS, API) | Azure DNS + Azure Container Apps + Odoo CMS | 2026-04-02 |

### Engineering & Delivery Authority (Option C)

Authoritative rule:
- **GitHub Actions** remains the default CI authority and the deploy authority for docs/web properties.
- **Azure DevOps** remains the deploy authority for Odoo, Databricks, and infra lanes requiring environment/service-connection gating.
- **Azure Boards** is the portfolio/planning system of record.
- **GitHub Issues** is the engineering execution backlog.
- See `ssot/governance/platform-authority-split.yaml`, `ssot/governance/ci-cd-authority-matrix.yaml`, and `ssot/governance/repo-delivery-disposition.yaml`.

### Engineering & Delivery Authority (REVISED 2026-04-14)

**Azure Pipelines is the sole CI/CD authority. GitHub Actions and Vercel are FORBIDDEN.**

| System | Role | Status |
|---|---|---|
| **Azure Pipelines** | Sole CI + deploy authority for ALL lanes (Odoo, Databricks, infra, docs, web, agents, tests) | ✅ Canonical |
| **Azure DevOps Boards** | Portfolio/planning system of record | ✅ Canonical |
| **GitHub** | Source control + PRs + Issues (engineering execution backlog) only | ✅ Source control only |
| **GitHub Actions** | **FORBIDDEN** — all workflows removed 2026-04-14 | ❌ REMOVED |
| **Vercel** | **FORBIDDEN** — deprecated 2026-04-07, fully removed | ❌ REMOVED |

**Rules:**
1. Do NOT create files under `.github/workflows/`. The directory is reserved for non-CI GitHub config only (templates, CODEOWNERS, dependabot).
2. ALL CI (lint, test, spec-bundle-validate, plugin-validate, CodeQL-equivalent) runs in Azure Pipelines under `azure-pipelines/` or `.azuredevops/`.
3. ALL deploys (Odoo containers, Databricks bundles, ACA apps, Bicep infra, docs sites) run in Azure Pipelines with environment/service-connection gating.
4. No `vercel.json`, no Vercel preview checks, no `@vercel/*` dependencies.
5. Branch protection on `main` requires Azure Pipelines success only — GitHub Actions contexts must be removed from required checks.

**Migration evidence (2026-04-14):**
- Deleted `.github/workflows/*.yml` (12 files) including claude-headless-pr-review, claude-headless-spec-check, deploy-erp-canonical, deploy-m365-bot-proxy, devcontainer-ci, foundry-name-guard, odoo-pr-preview, platform-restoration, post-deploy-smoke, spec-bundle-validate, validate-plugins
- Replacement Azure Pipelines: existing `azure-pipelines/*.yml` (26 files) + new pipelines for PR preview, spec-bundle-validate, foundry-name-guard, plugin-validate

### Agentic Workflow Security Doctrine (added 2026-04-14)

Per Microsoft's GitHub Agentic Workflows architecture paper + DevBlogs Agentic Platform Engineering, ALL Pulser mutating agents must adopt the **3-tier defense pattern** — implemented on **Azure Pipelines + ACA**, not GitHub Actions.

| Tier | Responsibility | IPAI implementation (Azure-native) |
|---|---|---|
| **Substrate** | OS/container isolation per agent invocation | ACA dedicated container (NOT GitHub Actions runner), read-only host fs, tmpfs overlay, chroot/userns |
| **Configuration** | Declarative policy (allowlists, firewall, zero-secret) | Per-agent manifest in repo, MCP allowlist, Azure Key Vault holds creds (agent ZERO direct access) |
| **Planning** | Runtime execution control + Safe Outputs | 3-stage vetting via Pulser middleware: filter ops → moderate content → remove secrets; rate limit per stage |

**Core rules:**
- **Zero-secret agents:** Pulser agents NEVER hold credentials directly; API proxy (ACA app) + Key Vault own auth.
- **Allowlisted MCPs only:** No dynamic tool acquisition. Each agent's MCP set declared in manifest.
- **Safe Outputs subsystem mandatory** for every mutating tool (filter / moderate / sanitize + rate-limit).
- **Microsoft Content Safety** integration for prompt-injection + bias detection.
- **Audit traceability** (who-acted-when + before/after diff + replay) per ADO Issue `#623`.

**GitHub Copilot Coding Agent positioning:**
- Routine code-gen (boilerplate, tests, docs, parity-record population) → **Coding Agent** generates PRs from Issues.
- Architecture / SSOT / multi-step / cross-doctrine work → **Claude Code** (per session execution).
- Coding Agent PRs are **validated by Azure Pipelines** (not GitHub Actions) before merge.
- Both consume same `.mcp.json` shared MCP servers.
- Both honor CLAUDE.md doctrine.

**No-GitHub-Actions clarification:** Adopting the GitHub Agentic Workflows *security pattern* (3-tier defense, Safe Outputs, zero-secret agents) does NOT mean adopting GitHub Actions as runtime. The pattern is implemented on Azure Pipelines + ACA. GitHub's blog is the architecture reference; the implementation is Azure-native.

**Anchors:**
- ADO Issues: #341/#628 (3-tier defense on ACA), #240/#629 (Coding Agent → Azure Pipelines validation), #524/#630 (Safe Outputs on Pulser middleware)
- GitHub blog (pattern reference only): agentic-workflows-security-architecture
- Microsoft DevBlogs (pattern reference only): agentic-platform-engineering-with-github-copilot
- `docs/research/ms-copilot-d365-m365-agents-catalog-for-ipai.md` (86-agent reference catalog)
- `ssot/governance/platform-authority-split.yaml` (canonical authority matrix)

---

## Deep Reference

| Topic | Location |
|-------|----------|
| Directory structure & inventory | `.claude/rules/repo-topology.md` |
| Architecture, Docker, integrations | `.claude/rules/platform-architecture.md` |
| Secrets policy, GHAS, allowed tools | `.claude/rules/security-baseline.md` |
| GitHub governance, CI/CD, PR rules | `.claude/rules/github-governance.md` |
| Enterprise parity strategy & tables | `.claude/rules/ee-parity.md` |
| Odoo CE 18 rules, modules, testing | `.claude/rules/odoo-rules.md` |
| Supabase usage & activation | `.claude/rules/supabase-usage.md` |
| BIR compliance (PH tax/payroll) | `.claude/rules/bir-compliance.md` |
| MCP Jobs system | `.claude/rules/mcp-jobs.md` |
| n8n automations & Claude integration | `.claude/rules/automations.md` |
| Spec kit structure & bundles | `.claude/rules/spec-kit.md` |
| Vercel observability & Figma | `.claude/rules/vercel-observability.md` |
| SSOT platform rules | `.claude/rules/ssot-platform.md` |
| Architecture & stack | `docs/ai/ARCHITECTURE.md` |
| IPAI module naming | `docs/ai/IPAI_MODULES.md` |
| OCA workflow | `docs/ai/OCA_WORKFLOW.md` |
| Testing recipes | `docs/ai/TESTING.md` |
| Docker commands | `docs/ai/DOCKER.md` |
| Troubleshooting | `docs/ai/TROUBLESHOOTING.md` |

---

*Last updated: 2026-03-30*
