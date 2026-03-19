# Insightpulseai Org Architecture Review & Refactor Plan

**Date**: 2026-03-16
**Author**: Platform Architecture Review (Claude)
**Scope**: Full org portfolio -- repos, governance, docs platform, design primitives
**Status**: Draft for review
**Classification**: Internal -- Architecture Decision Record

---

## Table of Contents

1. [Executive Verdict](#1-executive-verdict)
2. [Repo-by-Repo Decision Table](#2-repo-by-repo-decision-table)
3. [Target-State Repo Topology](#3-target-state-repo-topology)
4. [Documentation Platform Architecture](#4-documentation-platform-architecture)
5. [Standard Repo Contract](#5-standard-repo-contract)
6. [Azure DevOps-Aligned Operating Model](#6-azure-devops-aligned-operating-model)
7. [Claude/Coding-Agent Optimization Plan](#7-claudecoding-agent-optimization-plan)
8. [Documentation Rigor Gap Analysis](#8-documentation-rigor-gap-analysis)
9. [Deployed Resource Model & Design Primitives](#9-deployed-resource-model--design-primitives)
10. [Phased Refactor Plan](#10-phased-refactor-plan)
11. [Concrete Recommendation Matrix](#11-concrete-recommendation-matrix)
12. [Minimal First Wave](#12-minimal-first-wave)
13. [Final Target-State Recommendation](#13-final-target-state-recommendation)

---

## 1. Executive Verdict

### What Is Working

The `odoo` repo is the gravitational center of the entire organization. It has real governance: CLAUDE.md, 355 GitHub Actions workflows, 76 spec bundles, a functioning evidence directory, and active infrastructure-as-code. When a coding agent operates inside `odoo`, it has enough context to act deterministically. The Azure Container Apps deployment is coherent -- 13 ACA resources behind Front Door with proper Key Vault integration, and the three-environment model (dev/staging/prod) is sound. The Odoo module philosophy (Config > OCA > Delta) is well-articulated and enforced.

### What Is Fragmented

Six of ten active repos have NO CLAUDE.md. Five have NO .github/ directory. Six have NO docs/ directory. Seven have NO spec/ directory. This means coding agents operating outside the `odoo` repo are flying blind. There is no org-wide governance contract -- the `.github` org repo has CODEOWNERS and templates but no CLAUDE.md of its own, no standardized repo contract, and no enforcement mechanism for the standards that do exist.

### What Is Undocumented

Three repos are governance-free zones:

- **platform**: Contains SSOT files and Supabase config but has zero documentation, zero CI, zero agent guidance. It is a repo that exists but communicates nothing about why.
- **data-intelligence**: Contains Databricks DLT contracts but has no README, no docs, no CI. The decision to use Databricks JDBC extract over Supabase ETL is documented only in the user's Claude memory, not in the repo itself.
- **automations**: Contains 339KB of inventory JSON but no README, no docs, no CI. The n8n workflows and repo hygiene scripts are discoverable only by accident.

### What Is Structurally Wrong

The `odoo` repo is a monorepo that pretends to be decomposed. It contains:

- `addons/ipai/` -- 69 custom Odoo modules (legitimate)
- `apps/` -- 9 standalone applications including ops-console and mcp-jobs (does not belong)
- `infra/` -- Full Azure IaC (duplicates the `infra` repo)
- `spec/` -- 76 spec bundles (should be org-level or in respective repos)
- 355 workflows (many are not Odoo-specific)
- 1000+ scripts (many are platform-level, not Odoo-level)

Meanwhile, `infra` and `platform` exist as separate repos but are incomplete mirrors of what already lives in `odoo/infra/` and `odoo/apps/`. This creates three anti-patterns:

1. **Dual-source-of-truth**: Infrastructure definitions exist in both `odoo/infra/` and `infra/`. Which is canonical?
2. **Boundary violation**: `odoo` contains apps (ops-console) that have nothing to do with Odoo ERP.
3. **Governance asymmetry**: `odoo` is over-governed while satellite repos are under-governed.

### What Blocks Azure DevOps-Style Maturity

| Gap | Impact |
|-----|--------|
| No org-wide branch strategy | Each repo invents its own (or has none) |
| No required checks contract | PRs merge without gates in 7/10 repos |
| No environment promotion model | Only `odoo` has dev/staging/prod |
| No artifact naming convention | Container images, Edge Functions, workflows all named ad-hoc |
| No deployment evidence standard | Only `odoo` has `docs/evidence/` |
| No reusable workflow library | 355 workflows in `odoo`, zero shared workflows in `.github` |
| No rollback conventions | No documented rollback procedure for any service |

### What Blocks Coding-Agent Reliability

| Gap | Impact |
|-----|--------|
| 6/10 repos lack CLAUDE.md | Agents cannot determine scope, rules, or conventions |
| No cross-repo SSOT map | Agents cannot resolve which repo owns what |
| Infra duplication | Agents may modify the wrong infra definition |
| No spec bundle standard outside `odoo` | Agents cannot plan work in satellite repos |
| No deterministic render points | Agents cannot verify their own output |
| Naming inconsistency | `platform` vs `odoo/apps/ops-console` -- which is the ops surface? |

### What Blocks Documentation-Platform Rigor

| Gap | Impact |
|-----|--------|
| No docs build system | No mkdocs/docusaurus/hugo pipeline org-wide |
| `docs/mkdocs.yml` exists but is not wired to CI | Docs are written but never built or validated |
| No link validation | Cross-repo references are unchecked |
| No docs taxonomy standard | Each repo invents its own docs/ structure |
| No separation of normative vs generated vs evidence docs | All three are mixed in `docs/` |
| No ADR convention | Architecture decisions are scattered across 23 markdown files in `docs/architecture/` with no numbering, no status, no supersession chain |
| No onboarding docs | No "start here" path for new contributors or new agents |

### Bottom Line

The organization has outgrown its monorepo-plus-satellites structure. The `odoo` repo is doing the work of four repos. The satellite repos are either empty shells or governance-free dumps. Documentation exists but is not systematic. The platform has real Azure infrastructure with 13 container apps, 7 AI services, and multi-environment deployment -- but the repo structure does not reflect or govern this reality.

---

## 2. Repo-by-Repo Decision Table

### Active Repos

| # | Repo | Current Role | Boundary Correct? | Main Problems | Docs Rigor | Azure DevOps Alignment | Coding-Agent Issues | Decision | Priority |
|---|------|-------------|-------------------|---------------|------------|----------------------|-------------------|----------|----------|
| 1 | **odoo** | ERP + platform monorepo | NO -- contains infra/, apps/, specs for non-Odoo concerns | Boundary violation: apps/ and infra/ do not belong. 355 workflows includes non-Odoo CI. 1000+ scripts are partially platform-level. | Has docs/ but no build pipeline. Evidence dir is good. 23 architecture docs with no ADR numbering. | Has CI but no standardized gates. No environment promotion docs. No artifact naming. | CLAUDE.md is strong. But agents get confused by scope -- is this an Odoo repo or a platform repo? | SPLIT: Extract infra/, apps/, platform scripts. Odoo repo becomes pure ERP. | P0 |
| 2 | **platform** | SSOT + Supabase config | NO -- too thin to justify existence as separate repo | Zero governance. No README. No CI. No docs. Contains `ssot/` but unclear if this or `odoo/infra/ssot/` is canonical. | None | None | No CLAUDE.md. Agent lands here and has zero context. | MERGE into consolidated platform repo OR fully populate with governance. | P1 |
| 3 | **data-intelligence** | Databricks contracts | YES -- clear domain boundary | No README. No CI. No docs. Contracts exist but are not validated. Decision history (JDBC over Supabase ETL) is not recorded here. | None | None | No CLAUDE.md. No ADRs explaining Databricks choices. | KEEP but add full governance stack. | P1 |
| 4 | **agents** | AI agent definitions | YES -- clear domain boundary | Well-structured internally (capabilities/, knowledge/, skills/, etc.) but no CI, no CLAUDE.md, no docs/, no spec/. README exists but is the only governance artifact. | README only | None | No CLAUDE.md. Agents working on agent definitions have no meta-guidance. Ironic. | KEEP and add governance. High priority -- this repo defines agent behavior. | P0 |
| 5 | **infra** | Azure IaC | PARTIALLY -- overlaps with odoo/infra/ | Dual-source-of-truth problem. Has docs/ and spec/ but no CLAUDE.md, no .github/, no README. Which infra/ is canonical? | Has docs/ and spec/ -- better than most satellites. | Has terraform/bicep but no pipeline definitions. No environment promotion. | No CLAUDE.md. Agent cannot determine if this or odoo/infra/ is the source of truth. | KEEP as canonical infra repo. Remove odoo/infra/ and symlink or reference. | P0 |
| 6 | **web** | Vercel-era web apps | PARTIALLY -- README states Vercel is deprecated | 19 apps in apps/ -- unclear which are active post-Vercel deprecation. Contains ai-control-plane/, billing-site/, control-plane/, copilot/ -- some may be dead. | Has docs/ and spec/. README acknowledges deprecation. | No .github/. No CI. Dead apps mixed with live apps. | No CLAUDE.md. Agent cannot determine which apps are live. | AUDIT: Identify live apps, archive dead ones. Add CLAUDE.md. | P2 |
| 7 | **automations** | n8n + scripts | YES -- clear domain boundary | No README. No CI. No docs. 339KB inventory JSON is data, not documentation. | None | None | No CLAUDE.md. Agent cannot determine what automations are active. | KEEP and add governance. Wire inventory.json to validation. | P2 |
| 8 | **.github** | Org governance | YES -- this is the right place for org-level config | Has CODEOWNERS, templates, dependabot. But no CLAUDE.md, no README. copilot-instructions.md exists but is minimal. No reusable workflows despite 355 workflows in odoo. | Policies exist but are not linked to enforcement. | Has CI templates but they are not consumed by other repos. | No CLAUDE.md. Org-level agent guidance is missing. copilot-instructions.md is tool-gated, not comprehensive. | EXPAND: Add CLAUDE.md, README, reusable workflows, org governance docs. | P0 |
| 9 | **templates** | Bootstrap scaffolds | YES -- appropriate scope | Minimal exploration. Unknown if templates match current repo contract. | Unknown | Unknown | Unknown if templates produce repos that meet governance standards. | AUDIT and update to match repo contract defined in this review. | P3 |
| 10 | **design** | UI primitives | YES -- appropriate scope | Minimal content. Legacy location was design/. May not reflect current design token needs (Azure resource primitives, status indicators, etc.). | Unknown | Unknown | Unknown | AUDIT and expand with primitives defined in Section 9. | P3 |

### Archived Repos

| # | Repo | Salvage? | What to Extract | Destination | Delete After Salvage? |
|---|------|----------|----------------|-------------|----------------------|
| 1 | **template-factory** | MAYBE | Check if any templates are not in `templates` repo | `templates` | YES |
| 2 | **plugin-marketplace** | NO | Nothing -- concept was abandoned | N/A | YES |
| 3 | **plugin-agents** | MAYBE | Agent plugin patterns may inform `agents` repo | `agents` | YES |
| 4 | **learn** | NO | Training materials are stale | N/A | YES |
| 5 | **mcp-core** | YES | MCP protocol definitions, if any are not in `agents/mcp/` | `agents/mcp/` | YES after extraction |

### Detailed Repo Analysis

#### Repo 1: `odoo` -- The Gravity Well

**Current State**: This repo is the de facto monorepo for the entire organization. It was born as an Odoo CE deployment repo and has absorbed everything: infrastructure definitions, standalone web applications, MCP servers, platform automation, design system work, and 76 spec bundles covering non-Odoo concerns.

**What Is Legitimate**:
- `addons/ipai/` (69 custom modules) -- this is core Odoo development
- `addons/oca/` -- OCA community modules, properly managed
- `vendor/odoo/` -- upstream Odoo CE mirror
- `config/` -- Odoo-specific configuration
- `odoo19/` -- canonical Odoo 19 setup scripts
- Odoo-specific scripts in `scripts/`
- Odoo-specific CI workflows
- `.claude/` directory with comprehensive agent guidance

**What Does Not Belong**:
- `apps/ops-console/` -- a Next.js ops dashboard. This is not an Odoo module. It is a standalone web application that happens to monitor Odoo alongside other services.
- `apps/mcp-jobs/` -- a Next.js job orchestration system deployed to Vercel. It communicates with Supabase, not Odoo.
- `apps/colima-desktop-ui/`, `apps/odoo-mobile-ios/`, `apps/platform/`, `apps/slack-agent/`, `apps/web/`, `apps/workspace/`, `apps/docs/` -- seven additional apps of varying relevance.
- `infra/` -- complete Azure IaC that duplicates the standalone `infra` repo. Contains terraform, doctl templates, nginx configs, Superset setup.
- `packages/agents/`, `packages/taskbus/` -- shared packages that should be in a shared package repo or in `agents`.
- `mcp/servers/plane/` -- MCP server for Plane.so. Should be in `agents/mcp/`.
- `db/schema/`, `db/migrations/`, `db/seeds/`, `db/rls/` -- database management artifacts that are partly Odoo (legitimate) and partly Supabase (does not belong).
- `spec/` bundles covering non-Odoo concerns (platform-level, AI-level, web-level specs).
- ~200 of the 355 workflows that are not Odoo-specific (platform deployment, infrastructure validation, security scanning, docs generation).

**Anti-Patterns Present**:
1. **God Repo**: One repo owns everything. This makes it impossible to give a team ownership of a specific domain without granting them access to all domains.
2. **Phantom Decomposition**: The existence of `infra`, `platform`, and `web` as separate repos implies decomposition happened, but `odoo` was never cleaned up. The satellite repos are partial copies, not authoritative sources.
3. **Context Overload**: CLAUDE.md is 1500+ lines. It covers Odoo, BIR compliance, Vercel integration, MCP jobs, Supabase, n8n, GitHub Projects, Figma, design tokens, and more. An agent reading this CLAUDE.md gets context about 15 different systems when it may only need to modify one Odoo module.
4. **Workflow Explosion**: 355 workflows is not a sign of mature CI -- it is a sign that workflows are not composed from reusable pieces. Many of these are variations of the same pattern (lint, test, deploy) for different targets.

**Structural Debt Cost**: Every agent session in `odoo` loads CLAUDE.md that is 4x longer than it needs to be. Every PR touches a repo with 355 workflows, causing CI to take longer than necessary. Every infrastructure change could be applied to either `odoo/infra/` or `infra/`, with no mechanism to detect which is canonical.

#### Repo 2: `platform` -- The Ghost Repo

**Current State**: This repo exists but barely. It contains:
- `ssot/` -- SSOT files (service matrix, resources)
- `supabase/` -- Supabase configuration
- `.env.example` -- environment variable template

That is the complete inventory. No README, no CLAUDE.md, no CI, no docs, no spec, no tests.

**The Core Problem**: This repo was created to hold platform operational data, but it was never populated. The SSOT files it contains (`ssot/`) also exist in `odoo/infra/ssot/`, creating a dual-source-of-truth. The Supabase config also has a counterpart in `odoo`.

**Why It Must Not Continue**: A repo with no governance artifacts is a repo that cannot be safely operated on by any agent or developer. Its contents are small enough to merge into `infra` (where SSOT files naturally belong) without any loss of structure.

**One Exception**: If the org decides that SSOT files should live separately from IaC (a defensible position), then `platform` should be renamed to `ssot` and given full governance. But the current state -- a governance-free dump with 3 directories -- is not that.

#### Repo 3: `data-intelligence` -- The Undocumented Decision

**Current State**: Contains Databricks DLT contracts in `contracts/` directory. That is all.

**The Hidden Story**: The decision to use Databricks JDBC extract instead of Supabase ETL is recorded in the user's Claude memory (`project_supabase_etl_deprecated.md` and `project_data-intelligence_architecture.md`) but NOT in this repo. This means:
- A new developer landing in this repo has no idea why Databricks was chosen
- An agent operating here cannot explain the medallion architecture decisions
- The JDBC-over-Supabase-ETL decision has no ADR, no rationale, no trade-off analysis in the repo that implements it

**What This Repo Should Contain** (and currently does not):
- ADR explaining Databricks choice over alternatives
- ADR explaining JDBC extract over Supabase ETL
- Medallion layer documentation (Bronze/Silver/Gold/Platinum)
- Data quality rules
- Pipeline definitions (even if just contract stubs)
- DLT configuration
- CI that validates contracts against schemas

**Risk of Inaction**: Without governance, this repo will either (a) be forgotten and become stale, or (b) accumulate undocumented changes that no one can reason about.

#### Repo 4: `agents` -- The Ironic Governance Gap

**Current State**: This is the best-structured satellite repo. It has a logical directory layout:
- `capabilities/` -- what agents can do
- `knowledge/` -- knowledge bases and RAG sources
- `skills/` -- skill definitions
- `mcp/` -- MCP tool definitions
- `personas/` -- agent persona configurations
- `policies/` -- behavior policies
- `procedures/` -- step-by-step procedures
- `prompts/` -- prompt templates
- `library/` -- shared libraries
- `evals/` -- evaluation benchmarks
- `foundry/` -- Azure AI Foundry config
- `coordinator/` -- coordination logic

It also has a README. But no CLAUDE.md, no .github/, no docs/, no spec/.

**The Irony**: This repo defines how AI agents behave, but it has no instructions for AI agents operating ON it. A Claude Code session opening this repo has a README to read but no CLAUDE.md to guide its behavior. It does not know:
- Which files are auto-generated vs hand-authored
- What validation commands to run
- What naming conventions apply
- What other repos depend on these agent definitions
- How to test changes to agent capabilities

**Priority**: This is P0 specifically because of what this repo IS. If we cannot govern the repo that governs agents, we have a meta-governance failure.

#### Repo 5: `infra` -- The Should-Be SSOT

**Current State**: Comprehensive IaC repo with:
- `azure/` -- Azure-specific IaC (bicep, terraform)
- `cloudflare/` -- DNS configuration
- `databricks/` -- Workspace configuration
- `dns/` -- Subdomain registry (the YAML-first DNS workflow)
- `deploy/` -- Deployment scripts
- `entra/` -- Microsoft Entra ID configuration (for Keycloak-to-Entra migration)
- `identity/` -- Identity management
- `data-intelligence/` -- Lakehouse infrastructure (overlaps with `data-intelligence` repo)
- `observability/` -- Monitoring and alerting config
- `platform-kit/` -- Platform tooling

Has `docs/` and `spec/` but no CLAUDE.md, no .github/, no README.

**The Dual-Source Problem**: `odoo/infra/` contains terraform, doctl templates, Superset configs, and nginx configs. `infra/` contains azure, cloudflare, databricks, DNS, and deployment configs. Neither is complete. Neither references the other. An agent modifying infrastructure has a 50/50 chance of editing the wrong repo.

**Resolution**: `infra` must become the sole IaC repo. All infrastructure definitions in `odoo/infra/` must be migrated here. `odoo` should contain zero IaC.

**Complication**: `odoo/infra/` may contain Odoo-specific deployment configs (docker-compose, nginx for Odoo). These could arguably stay in `odoo` as "deployment config" rather than "infrastructure." The line between "how to deploy Odoo" and "infrastructure" is blurry. Recommendation: Odoo-specific docker-compose.yml and nginx.conf stay in `odoo/deploy/`. Everything else (terraform, Azure provisioning, DNS, Key Vault) goes to `infra`.

#### Repo 6: `web` -- The Deprecation Limbo

**Current State**: 19 apps in `apps/` from the Vercel era. README explicitly states Vercel is deprecated (replaced by Azure Container Apps as of 2026-03-11). But the apps are still here.

**The Unanswered Question**: Which of these 19 apps are live? Which are dead? The README does not say. The list includes:
- `ai-control-plane/` -- may be active (Azure AI Foundry integration)
- `billing-site/` -- likely dead (no billing system in current stack)
- `control-plane/` -- may overlap with `ai-control-plane/`
- `copilot/` -- may be active (Odoo copilot UI)
- Other apps: unknown status

Without CLAUDE.md or an inventory of active vs deprecated apps, an agent cannot determine what is safe to modify and what should be left alone.

**Post-Vercel Identity**: If Vercel is deprecated, this repo needs a new identity. It should become the web application repo for all non-Odoo web UIs, including `ops-console` (extracted from `odoo/apps/`). Its deployment target is now Azure Container Apps, not Vercel.

#### Repo 7: `automations` -- The Inventory Without Context

**Current State**: Contains:
- `n8n/` -- n8n workflow definitions
- `notion-monthly-close/` -- Notion integration scripts
- `repo_hygiene/` -- repository maintenance scripts
- `workflows/` -- additional workflow definitions
- `automations-inventory.json` (339KB) -- comprehensive inventory of all automations
- `automations-inventory.md` -- markdown version of inventory

**The Data-Without-Meaning Problem**: 339KB of JSON inventory is impressive in size but useless without:
- A README explaining what this inventory represents
- A schema for the inventory format
- CI validation that the inventory matches reality
- Documentation of which automations are active vs paused vs retired
- Owner information for each automation
- Dependency mapping (which automations depend on which services)

**Structural Issue**: The `n8n/` directory likely contains workflow JSON exports. These should be validated in CI (at minimum, JSON schema validation). The `notion-monthly-close/` and `repo_hygiene/` directories suggest this repo is a dumping ground for scripts that do not have a home elsewhere.

#### Repo 8: `.github` -- The Underutilized Governance Root

**Current State**: Has the right artifacts for org governance:
- `actions/` -- reusable composite actions
- `agents/` -- agent-related CI configurations
- `ci/` -- CI configurations
- `ISSUE_TEMPLATE/` -- issue templates
- `policies/` -- org-level policies
- `workflows/` -- workflow definitions
- `CODEOWNERS`
- `copilot-instructions.md`
- `dependabot.yml`
- `pull_request_template.md`
- `release.yml`
- `STATUS_TAXONOMY.md`

But no CLAUDE.md, no README.

**The Missed Opportunity**: This repo should be the governance brain of the org. It should contain:
- Reusable workflows consumed by all other repos (currently zero -- all 355 workflows are in `odoo`)
- Repo contract definitions (what every repo must have)
- REPO_MAP.md (which repo owns what)
- Org-level CLAUDE.md (cross-repo agent guidance)
- Documentation governance (taxonomy, templates, quality gates)

Currently, it has the skeleton but not the substance. The `copilot-instructions.md` is minimal and tool-gated (which is correct per Azure DevOps benchmark) but there is no equivalent depth for Claude Code agents.

#### Repo 9: `templates` -- The Unverified Scaffolds

**Current State**: Minimal exploration. Contains repo bootstrap templates.

**The Unknown Risk**: If templates produce repos that do not match the standard contract (no CLAUDE.md, no CODEOWNERS, wrong docs structure), then every new repo starts with governance debt. Templates must be updated to produce repos that match the contract defined in Section 5, and this must be validated in CI.

#### Repo 10: `design` -- The Empty Promise

**Current State**: Minimal content. Legacy location was `design/`.

**What It Should Contain** (per Section 9):
- Design tokens for environments, status states, deployment states, compliance states
- Foundation primitives (EnvironmentBadge, StatusIndicator, ResourceIdentifier, TimestampDisplay, OwnerBadge)
- Icon library for resource types
- Typography and spacing tokens
- Published as npm packages consumed by `web`

**Current Gap**: The ops-console (currently in `odoo/apps/`, target in `web/apps/`) needs design primitives to render Azure resources, deployment status, and operational data. Without a populated `design`, every web component invents its own colors, icons, and status indicators.

### Summary of Governance Gaps

| Artifact | odoo | platform | data-intelligence | agents | infra | web | automations | .github | templates | design |
|----------|------|-------------|-----------|--------|-------|-----|------------|---------|-----------|--------------|
| CLAUDE.md | YES | NO | NO | NO | NO | NO | NO | NO | NO | NO |
| README | YES | NO | NO | YES | NO | YES | NO | NO | ? | ? |
| .github/ | YES | NO | NO | NO | NO | NO | NO | YES (self) | NO | NO |
| docs/ | YES | NO | NO | NO | YES | YES | NO | NO | NO | NO |
| spec/ | YES | NO | NO | NO | YES | YES | NO | NO | NO | NO |
| CI workflows | YES | NO | NO | NO | NO | NO | NO | YES | NO | NO |

**9 out of 10 repos lack CLAUDE.md. This is the single most impactful governance gap for coding-agent reliability.**

---

## 3. Target-State Repo Topology

### Recommended Structure

The organization should adopt a **bounded multi-repo** model: each repo owns a clear domain with no overlap, and org-level governance is centralized in `.github`. The current model is a failing hybrid -- a monorepo (`odoo`) surrounded by governance-free satellites.

### Target Repos

| # | Repo | Owns | Must Never Own | Notes |
|---|------|------|---------------|-------|
| 1 | **odoo** | Odoo CE 19 ERP: addons/ipai/, addons/oca/, vendor/odoo/, Odoo-specific config, Odoo-specific CI, Odoo-specific docs | Infrastructure IaC, standalone apps (ops-console), platform-level scripts, non-Odoo specs | Extract apps/, infra/, platform scripts. This becomes a pure ERP repo. |
| 2 | **infra** | ALL infrastructure-as-code: Azure (bicep/terraform), Cloudflare DNS, Databricks workspace config, deployment scripts, environment definitions, SSOT files | Application code, business logic, Odoo modules | Absorb odoo/infra/. Absorb platform/ssot/. Becomes the canonical IaC repo. |
| 3 | **agents** | AI agent definitions: capabilities, knowledge bases, skills, MCP tool definitions, personas, policies, procedures, prompts, evals, foundry config | Infrastructure, deployment, application runtime code | Add governance stack. This is the agent brain -- it must have CLAUDE.md. |
| 4 | **web** | Web applications: ops-console (from odoo/apps/), active web UIs, design tokens consumed by web | Odoo modules, infrastructure, agent definitions | Absorb ops-console from odoo/apps/. Audit and archive dead Vercel-era apps. |
| 5 | **data-intelligence** | Data engineering: Databricks DLT contracts, medallion layer definitions, data quality rules, ETL pipeline definitions | Application code, infrastructure provisioning (that goes in infra/) | Add governance stack. ADRs for JDBC-over-Supabase-ETL decision. |
| 6 | **automations** | n8n workflows, scheduled jobs, repo hygiene scripts, Notion integrations, automation inventory | Infrastructure provisioning, application code, Odoo modules | Add governance stack. Wire inventory to CI validation. |
| 7 | **.github** | Org governance: reusable workflows, PR templates, issue templates, CODEOWNERS, dependabot, org-level CLAUDE.md, copilot-instructions.md, shared CI actions, repo contract definitions | Application code, infrastructure, business logic | Expand with reusable workflows extracted from odoo's 355 workflows. Add org CLAUDE.md. |
| 8 | **templates** | Repo scaffolds: cookiecutter/template repos that produce repos matching the standard contract | Application code, infrastructure | Update templates to produce repos that match Section 5 contract. |
| 9 | **design** | Design tokens, component primitives, icon sets, color palettes, typography, status indicators | Application runtime code, infrastructure | Expand with primitives defined in Section 9. Publish as npm package. |

### Repos to Eliminate

| Repo | Action | Rationale |
|------|--------|-----------|
| **platform** | MERGE `ssot/` into `infra/ssot/`, `supabase/` config into `infra/supabase/`. Delete repo. | Too thin to justify existence. SSOT belongs with infrastructure. |
| **template-factory** (archived) | Salvage into `templates`, delete | Redundant with `templates` |
| **plugin-marketplace** (archived) | Delete | Abandoned concept |
| **plugin-agents** (archived) | Salvage agent patterns into `agents`, delete | Redundant with `agents` |
| **learn** (archived) | Delete | Stale training materials |
| **mcp-core** (archived) | Salvage MCP definitions into `agents/mcp/`, delete | MCP is now part of agents |

### Dependency Graph (Target State)

```
.github (org governance)
   |
   +-- Reusable workflows consumed by all repos
   +-- Repo contract enforced by CI
   |
odoo (ERP) -------> infra (IaC) <------- web (UI)
   |                    |                    |
   |                    v                    |
   |              data-intelligence (data)           |
   |                    |                    |
   v                    v                    v
agents (AI) <---- automations (jobs) ----> design (tokens)
```

Key constraints:
- `odoo` depends on `infra` for deployment, never the reverse
- `web` depends on `infra` for deployment and `design` for tokens
- `agents` is consumed by `odoo` (via MCP tools) and `automations` (via n8n)
- `data-intelligence` consumes data from `odoo` (via JDBC) and `infra` (for workspace config)
- `automations` orchestrates across repos but owns no application logic
- `.github` is the governance root -- all repos consume its workflows and contracts

---

## 4. Documentation Platform Architecture

### Current State

Documentation is scattered, unbuilt, and ungoverned:

- `odoo/docs/` has 23 architecture documents with no ADR numbering, no status tracking, no supersession chain
- `odoo/docs/mkdocs.yml` exists but is not wired to any CI pipeline
- `odoo/docs/evidence/` is the only evidence directory in the org
- `infra/docs/` exists but is disconnected from `odoo/docs/`
- `web/docs/` exists but is disconnected
- 6 repos have no docs/ at all
- No org-wide docs portal, no docs search, no docs build pipeline
- No separation between normative docs (policies, contracts), generated docs (API refs), and evidence docs (test logs, deploy receipts)

### Target Documentation Model

#### 4.1 Org-Wide Docs Governance Location

The `.github` repo becomes the docs governance root:

```
.github/
  docs-governance/
    taxonomy.md              # Required docs categories
    quality-gates.md         # Lint rules, link validation, required metadata
    publishing.md            # Build and deploy pipeline spec
    ownership.md             # Who owns what docs
    templates/
      adr-template.md        # Architecture Decision Record template
      runbook-template.md    # Operational runbook template
      spec-template.md       # Spec bundle template
      release-notes-template.md
```

#### 4.2 Repo-Local Docs Model

Every repo with a docs/ directory must follow this structure:

```
docs/
  architecture/              # ADRs, target-state docs, system design
    adr/                     # Numbered: 0001-*.md, 0002-*.md
    target-state/            # Aspirational architecture documents
  operations/                # Runbooks, playbooks, incident response
  development/               # Contributing guides, setup, conventions
  evidence/                  # Build logs, test results, deploy receipts
    YYYY-MM-DD/              # Date-partitioned
  releases/                  # Release notes, changelog
  specs/                     # Spec bundles (or in spec/ at repo root)
  generated/                 # API docs, schema docs -- gitignored or CI-built
```

#### 4.3 Mandatory Docs Taxonomy

Every repo MUST have these documents (even if minimal):

| Document | Location | Purpose | Required For |
|----------|----------|---------|-------------|
| README.md | repo root | What this repo is, how to use it, who owns it | ALL repos |
| CLAUDE.md | repo root | Agent guidance: scope, rules, conventions, validation commands | ALL repos |
| CONTRIBUTING.md | repo root or docs/development/ | How to contribute, PR process, code standards | Product repos |
| CHANGELOG.md | repo root | Version history | Product repos |
| docs/architecture/adr/0001-*.md | docs/ | First ADR: why this repo exists, what it owns | ALL repos |
| docs/operations/runbook-*.md | docs/ | At least one operational runbook | Runtime repos |

#### 4.4 Normative vs Generated vs Evidence Separation

These three document classes have fundamentally different lifecycles and must never be mixed:

| Class | Examples | Authoring | Versioning | Retention | Location |
|-------|----------|-----------|------------|-----------|----------|
| **Normative** | ADRs, policies, contracts, specs, target-state docs | Human or agent, reviewed | Immutable once accepted (superseded, never edited) | Permanent | `docs/architecture/`, `docs/operations/`, `docs/development/` |
| **Generated** | API references, schema docs, dependency graphs, coverage reports | CI pipeline | Rebuilt every commit/release | Current only (overwritten) | `docs/generated/` (gitignored) or published to docs site |
| **Evidence** | Test logs, deploy receipts, audit trails, compliance reports | CI pipeline or agent | Append-only, date-partitioned | 90 days local, archive to blob | `docs/evidence/YYYY-MM-DD/` |

Anti-pattern observed: `odoo/docs/architecture/` mixes normative documents (PLATFORM_TARGET_STATE.md) with what should be ADRs (DATABASE_NAMING.md) with what should be generated (SEED_DATA_INVENTORY.md). This must be separated.

#### 4.5 ADR Convention

Architecture Decision Records follow the Michael Nygard format:

```
docs/architecture/adr/
  0001-use-odoo-ce-19-over-enterprise.md
  0002-azure-over-digitalocean.md
  0003-keycloak-transitional-to-entra.md
  0004-databricks-jdbc-over-supabase-etl.md
  0005-supabase-on-azure-vm-not-cloud.md
  ...
```

Each ADR contains:

```markdown
# ADR-NNNN: Title

**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
**Date**: YYYY-MM-DD
**Deciders**: [names]
**Supersedes**: ADR-XXXX (if applicable)

## Context
What is the issue that we are seeing that is motivating this decision?

## Decision
What is the change that we are proposing and/or doing?

## Consequences
What becomes easier or more difficult because of this change?
```

The current 23 documents in `odoo/docs/architecture/` should be retroactively numbered as ADRs or moved to `target-state/`.

#### 4.6 Runbook Convention

Runbooks are operational, not aspirational. They describe how to do something, not why.

```markdown
# Runbook: [Operation Name]

**Owner**: [team/person]
**Last verified**: YYYY-MM-DD
**Frequency**: On-demand | Daily | Weekly | On-incident

## Prerequisites
- [ ] Access to [resource]
- [ ] Tool [X] installed

## Procedure
1. Step one (command or action)
2. Step two
...

## Verification
How to confirm the operation succeeded.

## Rollback
How to undo if something goes wrong.

## Failure Modes
Known failure scenarios and responses.
```

#### 4.7 Release Notes Convention

```
docs/releases/
  v19.0.1.0.0.md
  v19.0.1.1.0.md
  ...
```

Each release note:

```markdown
# Release v19.0.X.Y.Z

**Date**: YYYY-MM-DD
**Type**: Major | Minor | Patch
**Scope**: [modules/services affected]

## Changes
- feat(scope): description
- fix(scope): description

## Breaking Changes
- [if any]

## Deployment Notes
- [environment-specific notes]

## Verification
- [how to confirm this release is live and working]
```

#### 4.8 Spec Bundle Convention

Spec bundles are the planning artifact that precedes implementation:

```
spec/
  SPEC-001-odoo-copilot/
    overview.md
    requirements.md
    architecture.md
    test-plan.md
    acceptance-criteria.md
  SPEC-002-data-intelligence-medallion/
    ...
```

The 76 spec bundles in `odoo/spec/` should be audited: Odoo-specific specs stay, platform specs move to their respective repos.

#### 4.9 Documentation Ownership Model

| Docs Domain | Owner Repo | Owner Role |
|-------------|-----------|------------|
| Org governance, repo contracts, taxonomy | `.github` | Platform team |
| Odoo ERP modules, OCA governance, Odoo ops | `odoo` | ERP team |
| Infrastructure, deployment, environments | `infra` | Platform team |
| Agent capabilities, MCP tools, prompts | `agents` | AI team |
| Web apps, UI components | `web` | Frontend team |
| Data pipelines, DLT, medallion | `data-intelligence` | Data team |
| n8n workflows, automation inventory | `automations` | Platform team |
| Design tokens, component library | `design` | Design team |

#### 4.10 Lint/Validation/Publishing Model

**Linting** (CI-enforced per repo):

| Check | Tool | Severity |
|-------|------|----------|
| Markdown lint | markdownlint-cli2 | Warning (not blocking initially) |
| Link validation | markdown-link-check | Error (blocking) |
| Required files exist | Custom script | Error (blocking) |
| ADR numbering sequential | Custom script | Warning |
| Frontmatter present | Custom script | Warning |
| No secrets in docs | gitleaks | Error (blocking) |

**Publishing**:

Phase 1: GitHub Pages per repo (docs/ served as-is)
Phase 2: Org-wide docs portal (mkdocs-material or similar) aggregating all repos
Phase 3: Search-enabled, versioned docs with API reference generation

**CI Pipeline** (reusable workflow in `.github`):

```yaml
# .github/workflows/docs-validate.yml (reusable)
# Called by each repo's CI
# Steps:
# 1. Check required files exist (README.md, CLAUDE.md, etc.)
# 2. Run markdownlint
# 3. Run link validation
# 4. Build docs site (if mkdocs.yml exists)
# 5. Check for secrets
```

#### 4.11 How Docs Serve Both Humans and Coding Agents

Humans and coding agents read docs differently:

| Aspect | Human Reader | Coding Agent |
|--------|-------------|--------------|
| Entry point | README.md, search, navigation | CLAUDE.md, then targeted file reads |
| Comprehension | Skims, follows links, reads prose | Reads entire files, needs structured data |
| Decision-making | Interprets nuance, asks questions | Needs explicit rules, decision trees |
| Verification | Manual testing, visual inspection | Deterministic commands, exit codes |

Therefore, every repo needs BOTH:

1. **CLAUDE.md** -- Agent-optimized: structured rules, validation commands, scope boundaries, naming conventions. Tables over prose. Commands over descriptions.
2. **README.md** -- Human-optimized: what this repo is, why it exists, how to get started, who to ask. Prose, diagrams, links.

These two files serve different audiences and must not be merged. CLAUDE.md is not a README. README is not agent instructions.

---

## 5. Standard Repo Contract

### 5.1 Repo Classes

Every repo in the org falls into one of these classes:

| Class | Definition | Examples |
|-------|-----------|----------|
| **Product/Runtime** | Deploys a running service | `odoo`, `web` |
| **Control Plane** | Manages deployment/operations of other services | `platform` (to be merged) |
| **Infrastructure** | Provisions and configures cloud resources | `infra` |
| **Agent/AI** | Defines agent behavior, knowledge, capabilities | `agents` |
| **Data** | Defines data pipelines, schemas, quality rules | `data-intelligence` |
| **Automation** | Contains workflow definitions and job scripts | `automations` |
| **Template** | Scaffolds new repos or modules | `templates` |
| **Design System** | UI tokens, components, patterns | `design` |
| **Governance** | Org-level policies, workflows, templates | `.github` |

### 5.2 Universal Contract (ALL Repos)

Every repo, regardless of class, MUST have:

```
repo-root/
  README.md                  # What, why, who, how-to-start
  CLAUDE.md                  # Agent scope, rules, conventions, validation
  CONTRIBUTING.md            # PR process, code standards (can be minimal)
  .github/
    CODEOWNERS               # Ownership map
    pull_request_template.md # PR checklist
  docs/
    architecture/
      adr/
        0001-why-this-repo-exists.md   # Foundational ADR
```

### 5.3 Class-Specific Contracts

#### Product/Runtime Repos (`odoo`, `web`)

```
repo-root/
  # Universal contract files (above)
  src/ or addons/            # Application source
  config/                    # Environment-specific config
  scripts/                   # Build, test, deploy scripts
  tests/                     # Test suites
  docs/
    architecture/            # ADRs, target-state
    operations/              # Runbooks
    development/             # Setup guide, coding standards
    evidence/                # Date-partitioned test/deploy logs
    releases/                # Release notes
  spec/                      # Spec bundles for planned work
  .github/
    workflows/               # CI/CD pipelines
    CODEOWNERS
    pull_request_template.md
  Dockerfile                 # Container build (if applicable)
  docker-compose.yml         # Local dev environment (if applicable)
```

Mandatory CI checks:
- Lint (language-specific)
- Unit tests
- Integration tests (if applicable)
- Security scan (gitleaks, trivy)
- Docs validation
- Required files check

#### Infrastructure Repos (`infra`)

```
repo-root/
  # Universal contract files
  azure/                     # Azure-specific IaC (bicep/terraform)
  cloudflare/                # DNS config
  databricks/                # Workspace config
  dns/                       # Subdomain registry
  deploy/                    # Deployment scripts
  ssot/                      # Single Source of Truth files
  environments/
    dev/
    staging/
    prod/
  docs/
    architecture/
    operations/              # Deployment runbooks
    evidence/
  .github/
    workflows/               # IaC validation, plan, apply
    CODEOWNERS
```

Mandatory CI checks:
- Terraform/Bicep validate
- Terraform/Bicep plan (on PR)
- DNS consistency check
- SSOT schema validation
- Security scan

#### Agent/AI Repos (`agents`)

```
repo-root/
  # Universal contract files
  capabilities/              # What agents can do
  knowledge/                 # Knowledge bases, RAG sources
  skills/                    # Skill definitions
  mcp/                       # MCP tool definitions
  personas/                  # Agent persona configs
  policies/                  # Agent behavior policies
  procedures/                # Step-by-step procedures
  prompts/                   # Prompt templates
  evals/                     # Evaluation benchmarks
  foundry/                   # Azure AI Foundry config
  docs/
    architecture/
    development/
  .github/
    workflows/               # Eval pipeline, lint
    CODEOWNERS
```

Mandatory CI checks:
- YAML/JSON schema validation
- Prompt lint (no secrets, no PII)
- Eval regression (if evals/ exists)

#### Data Repos (`data-intelligence`)

```
repo-root/
  # Universal contract files
  contracts/                 # Data contracts (schema, SLA, quality)
  pipelines/                 # DLT pipeline definitions
  models/                    # dbt models or equivalent
  quality/                   # Data quality rules
  docs/
    architecture/
      adr/                   # Data architecture decisions
    development/
  .github/
    workflows/               # Contract validation, pipeline CI
    CODEOWNERS
```

Mandatory CI checks:
- Contract schema validation
- Pipeline dry-run (if possible)
- Data quality rule lint

#### Automation Repos (`automations`)

```
repo-root/
  # Universal contract files
  n8n/                       # n8n workflow definitions
  workflows/                 # Other automation workflows
  scripts/                   # Utility scripts
  inventory/                 # Automation inventory (machine-readable)
  docs/
    architecture/
    operations/              # How to add/modify automations
  .github/
    workflows/               # Inventory validation
    CODEOWNERS
```

Mandatory CI checks:
- Inventory consistency (all automations documented)
- JSON schema validation for n8n workflows
- Script lint (shellcheck for bash)

#### Template Repos (`templates`)

```
repo-root/
  # Universal contract files
  templates/
    product-runtime/         # Template for product repos
    infra/                   # Template for infra repos
    agent/                   # Template for agent repos
    data/                    # Template for data repos
    automation/              # Template for automation repos
  docs/
    architecture/
    development/             # How to use templates
  .github/
    workflows/               # Template validation (render + check)
    CODEOWNERS
```

Mandatory CI checks:
- Template renders without errors
- Rendered output passes universal contract check

#### Design System Repos (`design`)

```
repo-root/
  # Universal contract files
  tokens/                    # Design tokens (JSON/YAML)
  components/                # Shared UI components
  icons/                     # Icon library
  docs/
    architecture/
    development/             # How to consume tokens/components
  package.json               # npm package definition
  .github/
    workflows/               # Token validation, component test, publish
    CODEOWNERS
```

Mandatory CI checks:
- Token schema validation
- Component tests (if applicable)
- Package build succeeds

#### Governance Repos (`.github`)

```
.github/
  # Universal contract files (README.md, CLAUDE.md)
  actions/                   # Reusable composite actions
  workflows/                 # Reusable workflow definitions
  ISSUE_TEMPLATE/
  policies/                  # Org-level policies
  docs-governance/           # Docs taxonomy, quality gates
  repo-contract/             # Repo class definitions, required files
  CODEOWNERS
  copilot-instructions.md
  dependabot.yml
  pull_request_template.md
  release.yml
  STATUS_TAXONOMY.md
```

### 5.4 Required Root Files Matrix

| File | Product | Infra | Agent | Data | Automation | Template | Design | Governance |
|------|---------|-------|-------|------|-----------|----------|--------|-----------|
| README.md | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ |
| CLAUDE.md | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ |
| CONTRIBUTING.md | REQ | OPT | OPT | OPT | OPT | OPT | OPT | REQ |
| CHANGELOG.md | REQ | OPT | OPT | OPT | OPT | OPT | REQ | OPT |
| LICENSE | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ |
| .github/CODEOWNERS | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ |
| .github/pull_request_template.md | REQ | REQ | REQ | REQ | REQ | OPT | REQ | REQ |
| docs/architecture/adr/0001-*.md | REQ | REQ | REQ | REQ | REQ | OPT | OPT | REQ |
| Dockerfile | REQ* | OPT | OPT | OPT | OPT | OPT | OPT | OPT |

REQ = Required, OPT = Optional, REQ* = Required if service is containerized

---

## 6. Azure DevOps-Aligned Operating Model

### 6.1 Branch Strategy

Adopt a simplified trunk-based development model:

| Branch | Purpose | Protection | Lifetime |
|--------|---------|-----------|----------|
| `main` | Production-ready code | Required reviews, required checks, no force push | Permanent |
| `staging` | Pre-production validation | Required checks, no force push | Permanent |
| `feat/*` | Feature development | None | Until merged |
| `fix/*` | Bug fixes | None | Until merged |
| `hotfix/*` | Emergency production fixes | Expedited review (1 reviewer) | Until merged |
| `release/v*` | Release candidates | Required checks | Until released, then tagged |

Rules:
- All work happens on feature/fix branches
- PRs target `main` by default
- `staging` is a deployment branch, not a merge target -- it is force-synced from `main` or cherry-picked
- No long-lived feature branches (> 5 days without merge)
- Rebase before merge (no merge commits)

### 6.2 PR Policy

| Policy | Value | Rationale |
|--------|-------|-----------|
| Required reviewers | 1 minimum, 2 for infra/security changes | Balance speed with oversight |
| Required checks | Lint + test + security scan + docs validation | No broken code merges |
| Auto-merge | Enabled when all checks pass and approved | Reduce merge ceremony |
| Stale PR | Auto-close after 14 days of inactivity with warning at 7 days | Prevent branch rot |
| PR size | Warning at > 500 lines changed, block at > 1000 lines | Force decomposition |
| PR template | Required, with checklist | Ensure completeness |
| Commit squash | Squash merge to main | Clean history |

PR template must include:

```markdown
## Summary
[What and why]

## Changes
- [ ] Change 1
- [ ] Change 2

## Testing
- [ ] Tests added/updated
- [ ] Manual verification performed

## Documentation
- [ ] Docs updated (if applicable)
- [ ] CHANGELOG updated (if applicable)

## Checklist
- [ ] No secrets committed
- [ ] CLAUDE.md still accurate
- [ ] Spec bundle referenced (if significant change)
```

### 6.3 Required Checks

Standardize across all repos using reusable workflows from `.github`:

| Check | Applies To | Blocking? | Reusable Workflow |
|-------|-----------|-----------|-------------------|
| `lint` | All repos | Yes | `.github/workflows/reusable-lint.yml` |
| `test` | Product, Agent, Design | Yes | `.github/workflows/reusable-test.yml` |
| `security-scan` | All repos | Yes | `.github/workflows/reusable-security.yml` |
| `docs-validate` | All repos | Yes (warning initially) | `.github/workflows/reusable-docs.yml` |
| `required-files` | All repos | Yes | `.github/workflows/reusable-contract.yml` |
| `iac-validate` | Infra | Yes | `.github/workflows/reusable-iac.yml` |
| `iac-plan` | Infra | Yes (must succeed, review plan) | `.github/workflows/reusable-iac-plan.yml` |
| `container-build` | Product (containerized) | Yes | `.github/workflows/reusable-container.yml` |
| `dns-consistency` | Infra | Yes | `.github/workflows/reusable-dns.yml` |

### 6.4 Pipeline Layering

```
Layer 0: Reusable workflows (.github repo)
   |
Layer 1: Repo-local CI (each repo's .github/workflows/)
   |       Calls Layer 0 workflows
   |       Adds repo-specific checks
   |
Layer 2: Environment promotion
   |       dev -> staging -> prod
   |       Gated by check results + approval
   |
Layer 3: Deployment
           Azure Container Apps revision management
           Blue/green or canary as appropriate
```

### 6.5 Reusable Workflow Strategy

The 355 workflows in `odoo` must be audited and decomposed:

| Category | Count (estimated) | Action |
|----------|-------------------|--------|
| Odoo-specific CI (module test, OCA lint) | ~100 | Keep in `odoo` |
| Generic CI (lint, security, docs) | ~50 | Extract to `.github` as reusable |
| Deployment (Azure, Docker) | ~80 | Extract to `.github` as reusable |
| Automation (scheduled, triggered) | ~75 | Move to `automations` or keep if Odoo-specific |
| Stale/duplicate | ~50 | Delete |

Target: `odoo` has < 100 repo-specific workflows that call reusable workflows from `.github`.

### 6.6 Environment Promotion

```
PR merged to main
   |
   v
[dev] Auto-deploy (ACA revision, dev slot)
   |
   v
[staging] Manual promotion (approval gate)
   |        Runs integration tests
   |        Runs smoke tests against staging DB
   |
   v
[prod] Manual promotion (2 approvals)
         Runs smoke tests against prod
         Creates deployment evidence in docs/evidence/
```

| Environment | Trigger | Approval | Database | ACA Slot |
|-------------|---------|----------|----------|----------|
| dev | Auto on merge to main | None | `odoo_dev` | Latest revision (100% traffic) |
| staging | Manual dispatch or schedule | 1 approval | `odoo_staging` | Staging revision |
| prod | Manual dispatch | 2 approvals | `odoo` | Blue/green swap |

### 6.7 Deployment Evidence

Every production deployment must produce:

```
docs/evidence/YYYY-MM-DD/deploy/
  deploy-manifest.json       # What was deployed (image, tag, commit, env)
  pre-deploy-health.json     # Health check results before deploy
  post-deploy-health.json    # Health check results after deploy
  smoke-test-results.json    # Smoke test output
  rollback-plan.md           # How to rollback this specific deployment
```

This is not optional. Deployments without evidence are not complete.

### 6.8 Rollback Conventions

| Scenario | Rollback Method | Time Target |
|----------|----------------|-------------|
| Bad ACA revision | `az containerapp revision activate --name <prev-revision>` | < 5 minutes |
| Bad database migration | Restore from pre-deploy snapshot | < 30 minutes |
| Bad Odoo module | `odoo-bin -u <module> --stop-after-init` with rollback migration | < 15 minutes |
| Bad infrastructure change | Terraform/Bicep rollback to previous state | < 30 minutes |
| Bad DNS change | Cloudflare revert (API or dashboard) | < 5 minutes |

Every production deployment must identify which rollback scenario applies and document the specific rollback command in the deployment evidence.

### 6.9 Secrets and Config Management

| Layer | Mechanism | Scope |
|-------|-----------|-------|
| Local dev | `.env` files (gitignored) | Developer machine |
| CI | GitHub Actions secrets + OIDC federation | Per-repo or org-level |
| Runtime (dev) | Azure Key Vault `kv-ipai-dev` | Dev environment |
| Runtime (staging) | Azure Key Vault `kv-ipai-staging` | Staging environment |
| Runtime (prod) | Azure Key Vault `kv-ipai-prod` | Prod environment |
| Odoo-specific | Azure Key Vault `ipai-odoo-dev-kv` | Odoo services |

Rules:
- Secrets NEVER appear in code, logs, or CI output
- Key Vault references in ACA environment variables, never raw values
- Secret rotation: 90-day maximum lifetime for all non-system secrets
- Break-glass: documented procedure for emergency secret access

### 6.10 Artifact Naming Convention

| Artifact Type | Pattern | Example |
|--------------|---------|---------|
| Container image | `<registry>/<service>:<env>-<git-sha-short>` | `ipaiodoodevacr.azurecr.io/odoo-web:dev-a1b2c3d` |
| ACA revision | `<app>--<git-sha-short>` | `ipai-odoo-dev-web--a1b2c3d` |
| Terraform state | `<env>-<component>.tfstate` | `dev-aca.tfstate` |
| GitHub release | `v<odoo-version>.<major>.<minor>.<patch>` | `v19.0.1.2.0` |
| Spec bundle | `SPEC-NNN-<kebab-case-title>` | `SPEC-042-data-intelligence-medallion` |
| ADR | `NNNN-<kebab-case-title>.md` | `0003-keycloak-transitional-to-entra.md` |
| Evidence pack | `YYYY-MM-DD/<scope>/` | `2026-03-16/deploy/` |

### 6.11 Traceability

Every production change must be traceable from:

```
Spec Bundle -> PR -> Commit -> CI Run -> Container Image -> ACA Revision -> Deployment Evidence
```

This chain is currently broken because:
- Specs are only in `odoo/spec/`, not in satellite repos
- PRs do not reference spec bundles consistently
- Deployment evidence is not linked to specific commits
- ACA revisions are not tagged with commit SHAs

Fix: Enforce spec reference in PR template, tag images with commit SHA, include commit SHA in deployment evidence.

### 6.12 CODEOWNERS

Every repo must have a CODEOWNERS file. Recommended pattern:

```
# Default owner
* @insightpulseai/platform-team

# Odoo modules
addons/ipai/ @insightpulseai/erp-team
addons/oca/ @insightpulseai/erp-team

# Infrastructure
infra/ @insightpulseai/platform-team
azure/ @insightpulseai/platform-team

# Docs
docs/ @insightpulseai/docs-team

# CI
.github/ @insightpulseai/platform-team

# Agent definitions
agents/ @insightpulseai/ai-team
capabilities/ @insightpulseai/ai-team
```

### 6.13 Service-Specific Pipeline Patterns

Each deployed service type has a distinct pipeline pattern:

#### Odoo ERP Pipeline

```
Trigger: PR merged to main touching addons/ipai/ or addons/oca/
    |
    v
[Lint] Python lint (black, isort, flake8) + OCA pre-commit
    |
    v
[Test] odoo-bin -d test_<module> -i <module> --test-enable --stop-after-init
    |
    v
[Build] Docker build (Dockerfile.unified or Dockerfile.seeded)
    |
    v
[Push] Push to ipaiodoodevacr.azurecr.io/odoo-web:dev-<sha>
    |
    v
[Deploy-Dev] Update ACA revision for ipai-odoo-dev-web, ipai-odoo-dev-worker, ipai-odoo-dev-cron
    |
    v
[Verify-Dev] Health check: curl erp.insightpulseai.com/web/health
    |          Module list: odoo-bin -d odoo_dev --list-db-tables
    |
    v
[Promote-Staging] Manual trigger, 1 approval
    |
    v
[Migrate-Staging] odoo-bin -d odoo_staging -u <changed_modules> --stop-after-init
    |
    v
[Verify-Staging] Full smoke test suite against staging
    |
    v
[Promote-Prod] Manual trigger, 2 approvals
    |
    v
[Backup-Prod] pg_dump odoo > pre-deploy-backup.sql
    |
    v
[Migrate-Prod] odoo-bin -d odoo -u <changed_modules> --stop-after-init
    |
    v
[Verify-Prod] Health check + smoke tests + evidence pack
```

#### Web Application Pipeline (ops-console, web UIs)

```
Trigger: PR merged to main touching apps/<app>/
    |
    v
[Lint] ESLint + TypeScript check
    |
    v
[Test] npm test / vitest
    |
    v
[Build] npm run build
    |
    v
[Container] Docker build + push to ipaiwebacr.azurecr.io/<app>:dev-<sha>
    |
    v
[Deploy-Dev] Update ACA revision
    |
    v
[Verify-Dev] curl <app-url>/health
    |
    v
[Promote] Same approval gates as Odoo
```

#### Infrastructure Pipeline

```
Trigger: PR opened touching azure/, cloudflare/, dns/
    |
    v
[Validate] terraform validate / az bicep build
    |
    v
[Plan] terraform plan -out=tfplan (posted as PR comment)
    |
    v
[Review] Human reviews plan diff in PR
    |
    v
[Apply-Dev] terraform apply tfplan (on merge to main)
    |
    v
[Verify-Dev] Resource health checks, DNS resolution tests
    |
    v
[Promote] Plan + apply for staging/prod with approval gates
```

#### Edge Function Pipeline (Supabase)

```
Trigger: PR merged to main touching supabase/functions/
    |
    v
[Lint] Deno lint
    |
    v
[Test] Deno test
    |
    v
[Deploy] supabase functions deploy <function-name>
    |
    v
[Verify] curl <supabase-url>/functions/v1/<function-name>
```

### 6.14 Monitoring and Alerting Contract

Every deployed service must have:

| Monitoring Aspect | Implementation | Alert Threshold |
|-------------------|---------------|----------------|
| Health endpoint | HTTP GET returning 200 | 3 consecutive failures = page |
| Response time | Azure Monitor metric | P95 > 5s = warning, P95 > 10s = page |
| Error rate | Log Analytics query | > 5% error rate = warning, > 10% = page |
| Container restarts | ACA metrics | > 3 restarts/hour = page |
| Database connections | PostgreSQL metrics | > 80% pool usage = warning, > 95% = page |
| Disk usage | VM metrics (Supabase) | > 80% = warning, > 90% = page |
| Certificate expiry | Front Door TLS | < 30 days = warning, < 7 days = page |

Alert routing:
- P1 (page): Slack #ops-alerts + email to on-call
- P2 (warning): Slack #ops-alerts
- P3 (info): Slack #ops-info

### 6.15 Incident Response Contract

```
1. DETECT   -- Alert fires or human reports
2. TRIAGE   -- Classify: P1 (service down), P2 (degraded), P3 (minor)
3. RESPOND  -- Follow service-specific runbook
4. MITIGATE -- Restore service (rollback, restart, failover)
5. RESOLVE  -- Root cause fix deployed
6. REVIEW   -- Incident report in docs/evidence/YYYY-MM-DD/incidents/
```

Incident report template:

```markdown
# Incident Report: [Title]

**Date**: YYYY-MM-DD HH:MM
**Duration**: X hours Y minutes
**Severity**: P1 / P2 / P3
**Affected Services**: [list]
**Impact**: [user-facing impact description]

## Timeline
- HH:MM -- Alert fired
- HH:MM -- Acknowledged by [person]
- HH:MM -- Root cause identified
- HH:MM -- Mitigation applied
- HH:MM -- Service restored

## Root Cause
[What broke and why]

## Mitigation
[What was done to restore service]

## Resolution
[What was done to prevent recurrence]

## Action Items
- [ ] Action 1 (owner, due date)
- [ ] Action 2 (owner, due date)
```

---

## 7. Claude/Coding-Agent Optimization Plan

### 7.1 Problem Statement

Coding agents (Claude, Copilot, Cursor, Windsurf) are only as reliable as the context they receive. Currently:

- 9/10 repos lack CLAUDE.md -- agents have no scope guidance
- Cross-repo boundaries are ambiguous -- agents may modify the wrong repo's files
- Infra definitions exist in two places -- agents may apply IaC to the wrong source
- Spec bundles are only in `odoo` -- agents cannot plan work in satellite repos
- Evidence directories are only in `odoo` -- agents cannot verify work elsewhere
- Naming is inconsistent -- `platform` vs `odoo/apps/ops-console` confuses agents

### 7.2 Repo-Local CLAUDE.md Requirements

Every CLAUDE.md must contain:

```markdown
# CLAUDE.md -- [Repo Name]

## Scope
What this repo owns. What it does NOT own (explicit exclusions).

## Rules
Numbered, enforceable rules. No prose.

## Conventions
Naming patterns, file organization, coding standards.

## Validation Commands
Deterministic commands an agent can run to verify its work.
Must return exit code 0 on success, non-zero on failure.

## Dependencies
What other repos this repo depends on.
What repos depend on this one.

## Quick Reference
Table of key values (paths, URLs, database names, etc.)

## Deprecated
What was removed and what replaced it.
```

Anti-patterns to avoid:
- CLAUDE.md that is just a copy of README.md
- CLAUDE.md with ambiguous language ("you should consider...")
- CLAUDE.md without validation commands
- CLAUDE.md that references files that do not exist

### 7.3 Spec Bundle Expectations

Agents need spec bundles to plan non-trivial work. Every repo that accepts feature work must support spec bundles:

```
spec/
  SPEC-NNN-title/
    overview.md              # What and why (1 page max)
    requirements.md          # Acceptance criteria (testable assertions)
    architecture.md          # How (optional for small changes)
    test-plan.md             # How to verify (required)
    acceptance-criteria.md   # Done-when list (required)
```

Spec bundles are referenced in PRs. PRs without spec references for significant changes should be flagged.

### 7.4 SSOT Files

Single Source of Truth files are machine-readable YAML/JSON that define the current state of the platform:

| SSOT File | Location (Target) | Content |
|-----------|-------------------|---------|
| `service-matrix.yaml` | `infra/ssot/azure/` | All deployed services, their ACA apps, databases, endpoints |
| `resources.yaml` | `infra/ssot/azure/` | All Azure resources with RG, region, SKU |
| `subdomain-registry.yaml` | `infra/dns/` | All DNS records with target, purpose, status |
| `addons.manifest.yaml` | `odoo/config/` | All Odoo modules with repo, tier, provenance |
| `automations-inventory.json` | `automations/inventory/` | All automation workflows with trigger, status, owner |
| `agent-capabilities.yaml` | `agents/` | All agent capabilities with MCP tools, knowledge bases |

SSOT files must be:
- Machine-readable (YAML or JSON, with schema)
- Validated in CI (schema check)
- Referenced by CLAUDE.md so agents can discover them
- Updated atomically with the changes they describe

### 7.5 Deterministic Render Points

Agents need to verify their work. Every repo must define "render points" -- deterministic commands that produce verifiable output:

| Repo | Render Point | Command | Success Criteria |
|------|-------------|---------|------------------|
| `odoo` | Module install | `odoo-bin -d test_<module> -i <module> --stop-after-init` | Exit code 0 |
| `odoo` | Module test | `odoo-bin -d test_<module> -i <module> --test-enable --stop-after-init` | Exit code 0, no ERROR in logs |
| `infra` | IaC validate | `terraform validate` or `az bicep build` | Exit code 0 |
| `infra` | IaC plan | `terraform plan -detailed-exitcode` | Exit code 0 or 2 (changes present) |
| `web` | Build | `npm run build` | Exit code 0 |
| `web` | Test | `npm test` | Exit code 0 |
| `agents` | Schema validate | `ajv validate -s schema.json -d *.yaml` | Exit code 0 |
| `data-intelligence` | Contract validate | `python validate_contracts.py` | Exit code 0 |
| `automations` | Inventory check | `python validate_inventory.py` | Exit code 0 |

### 7.6 Validation Gates

Agents must run validation before claiming success:

```
1. Lint check (language-specific)
2. Test suite (if tests exist)
3. Render point (repo-specific)
4. Docs validation (required files exist, links valid)
5. Security scan (no secrets committed)
```

The validation gate is codified in each repo's CLAUDE.md under "Validation Commands."

### 7.7 Evidence Packs

When an agent completes significant work, it must produce an evidence pack:

```
docs/evidence/YYYY-MM-DD/
  <scope>/
    summary.md               # What was done, by whom (human or agent)
    commands.log              # Commands executed
    test-results.log          # Test output
    verification.log          # Render point output
    diff-summary.md           # Files changed and why
```

The `odoo` repo already has this pattern. It must be extended to all repos.

### 7.8 Naming Cleanup

| Current Name | Problem | Target Name | Action |
|-------------|---------|-------------|--------|
| `platform` | Too vague, overlaps with `odoo/apps/ops-console` | Merge into `infra` | Merge SSOT, delete repo |
| `odoo/apps/ops-console` | Does not belong in Odoo repo | `web/apps/ops-console` | Move |
| `odoo/apps/mcp-jobs` | Does not belong in Odoo repo | `automations/mcp-jobs` or `agents/mcp-jobs` | Move |
| `odoo/infra/` | Duplicates `infra` repo | Remove from `odoo` | Move canonical to `infra`, remove from `odoo` |
| `automations-inventory.json` (339KB) | Data blob, not documentation | `automations/inventory/inventory.json` | Restructure |

### 7.9 Cross-Repo Confusion Reduction

The `.github` repo must maintain a `REPO_MAP.md` that agents can read to determine which repo to operate in:

```markdown
# Repo Map

| Domain | Repo | What Goes Here | What Does Not |
|--------|------|---------------|---------------|
| Odoo ERP | odoo | Odoo modules, OCA governance, ERP config | Apps, infra, platform scripts |
| Infrastructure | infra | Azure IaC, DNS, SSOT, deployment | Application code |
| AI Agents | agents | Agent definitions, MCP tools, evals | Infrastructure, deployment |
| Web Apps | web | Frontend applications, ops-console | Odoo modules, infra |
| Data | data-intelligence | DLT pipelines, data contracts | Application code |
| Automation | automations | n8n workflows, scheduled jobs | Infrastructure provisioning |
| Design | design | Tokens, components | Application logic |
| Governance | .github | Org policies, reusable workflows | Application code |
| Scaffolding | templates | Repo templates | Runtime code |
```

This file is referenced in every repo's CLAUDE.md so agents can navigate across repos.

### 7.10 Machine-Usable Docs

Documents intended for agent consumption must follow these rules:

1. **Use tables over prose** -- agents parse tables more reliably than paragraphs
2. **Use absolute statements** -- "MUST", "NEVER", "ALWAYS" instead of "should consider"
3. **Include validation commands** -- agents need to verify, not just read
4. **Use consistent headers** -- agents navigate by header structure
5. **No ambiguous cross-references** -- use full file paths, not "see the other doc"
6. **Keep files < 500 lines** -- agents have context limits
7. **Front-load critical information** -- put rules before explanations
8. **Use code blocks for commands** -- agents need copy-pasteable commands

---

## 8. Documentation Rigor Gap Analysis

### 8.1 Azure DevOps Docs Repo Benchmark

The Azure DevOps docs repo represents enterprise-grade documentation practices:

| Practice | Azure DevOps | IPAI Current | Gap Severity |
|----------|-------------|-------------|-------------|
| Publishing config (`.openpublishing.publish.config.json`) | YES -- governs docset boundaries, build rules | NO -- `mkdocs.yml` exists but is not wired | CRITICAL |
| Markdown lint (`.markdownlint.json`) | YES -- permissive (45 rules disabled), pragmatic | NO -- no lint at all | HIGH |
| Content governance (`.acrolinx-config.edn`) | YES -- branch/path governance | NO | MEDIUM (aspirational) |
| Separate docsets (docs/ vs release-notes/) | YES -- distinct build targets | NO -- everything in docs/ | HIGH |
| Stale issue automation | YES -- auto-close stale issues | PARTIAL -- dependabot exists | LOW |
| Incremental builds | YES -- only rebuild changed docs | NO -- no build pipeline | HIGH |
| PDF generation | YES -- automated | NO | LOW (not needed yet) |
| Version-aware redirection | YES -- 11 JSON redirect files | NO | LOW (single version) |
| Copilot instructions | YES -- minimal, tool-gated | PARTIAL -- exists in `.github` but not comprehensive | MEDIUM |
| Branch/path governance | YES -- per-docset branch rules | NO | HIGH |

### 8.2 What to Emulate from Azure DevOps

**Emulate immediately:**

1. **Publishing config**: Create an org-level docs build configuration that defines docset boundaries. Each repo's docs/ is a docset with its own build rules.

2. **Markdown lint**: Adopt markdownlint-cli2 with a permissive config (start with many rules disabled, tighten over time). The Azure DevOps approach of disabling 45 rules is pragmatic -- perfectionism kills adoption.

3. **Separate docsets**: Separate `docs/` (normative), `docs/releases/` (release notes), `docs/evidence/` (operational evidence). These have different audiences, lifecycles, and build rules.

4. **Stale automation**: Auto-close PRs after 14 days of inactivity. Auto-label stale issues.

**Emulate later:**

5. **Incremental builds**: Once a docs build pipeline exists, optimize for incremental rebuilds.

6. **Version-aware redirection**: Only needed when multiple product versions are supported simultaneously.

**Do NOT emulate:**

7. **Acrolinx**: Commercial content governance tool. Not appropriate for a small org. Use markdownlint instead.

8. **PDF generation**: Low priority. Focus on web-based docs first.

### 8.3 Where Rigor Is Missing

| Area | Current State | Required State | Fix |
|------|-------------|---------------|-----|
| Docs taxonomy | Each repo invents its own structure | Standardized per Section 4.2 | Enforce via CI check |
| ADR discipline | 23 unnumbered docs in `odoo/docs/architecture/` | Numbered, statused, linked ADRs | Retroactively number existing docs |
| Runbook coverage | Zero runbooks in the org | At least 1 per deployed service | Write runbooks for Odoo, Supabase, Keycloak |
| Release notes | None in any repo | Per-release notes per Section 4.7 | Start with next release |
| Onboarding docs | None | "Start here" for new contributors and new agents | Write for `odoo` first |
| Link validation | None | CI-enforced, blocking | Add markdown-link-check to reusable workflow |
| Required files check | None | CI-enforced, blocking | Add file-existence check to reusable workflow |
| Docs build | mkdocs.yml exists, not wired | CI builds and publishes docs | Wire mkdocs to GitHub Actions + GitHub Pages |
| Cross-repo links | Unchecked | Validated | Use relative links within repo, absolute URLs cross-repo |
| Secret scanning in docs | None | CI-enforced | Add gitleaks to docs validation |

### 8.4 First Mandatory Fixes

These must happen before any other docs work:

1. **Add CLAUDE.md to all 9 repos that lack it** -- this is the highest-impact single change for agent reliability
2. **Add README.md to all repos that lack it** -- `platform`, `data-intelligence`, `automations`, `infra`, `.github`
3. **Create `.github/workflows/reusable-docs.yml`** -- the reusable docs validation workflow
4. **Add `.markdownlint.json`** to the `.github` repo (permissive config, copied to all repos)
5. **Number the existing 23 architecture docs** in `odoo/docs/architecture/` as ADRs or move to `target-state/`
6. **Create `REPO_MAP.md`** in `.github` per Section 7.9

### 8.5 Cross-Repo Documentation Dependency Map

Some documentation topics span multiple repos. These cross-cutting concerns are the most likely to fall through cracks:

| Topic | Primary Repo | Secondary Repos | Current State | Risk |
|-------|-------------|----------------|---------------|------|
| Deployment architecture | `infra` | `odoo`, `web` | Partially in `odoo/docs/architecture/`, partially in `infra/docs/` | HIGH -- no single view of full deployment |
| Identity/auth flow | `infra` (identity/) | `odoo` (Keycloak config), `web` (auth UI) | Scattered, no unified doc | HIGH -- Keycloak-to-Entra migration needs clear cross-repo view |
| MCP tool catalog | `agents` (mcp/) | `odoo` (mcp/servers/), `automations` (n8n MCP) | `odoo` CLAUDE.md lists MCP servers, `agents` has definitions | MEDIUM -- agents may not find all MCP tools |
| DNS/domain mapping | `infra` (dns/) | `.github` (copilot-instructions), `odoo` (mail config) | `infra/dns/subdomain-registry.yaml` is good, but cross-refs are weak | LOW -- SSOT exists in infra |
| Data flow (Odoo to data-intelligence) | `data-intelligence` | `odoo` (source data), `infra` (JDBC config) | Not documented anywhere | HIGH -- critical data pipeline has no docs |
| Design tokens to web components | `design` | `web` (consumers) | Neither repo has substantive content | MEDIUM -- blocked until primitives exist |
| Automation dependencies | `automations` | `odoo` (n8n-to-Odoo workflows), `agents` (MCP jobs) | Inventory exists in `automations` but dependencies not mapped | MEDIUM |
| Secrets catalog | `infra` (Key Vault) | All repos (consumers) | Key Vault names documented in `infra`, but no cross-repo secret dependency map | HIGH -- changing a secret name breaks unknown consumers |

**Resolution Pattern**: Each cross-cutting topic needs a "contract doc" in the primary repo that explicitly lists the secondary repos and their integration points. This is already partially implemented in `odoo` (see `docs/contracts/`) but not extended to other repos.

### 8.6 Documentation Anti-Patterns Currently Present

| Anti-Pattern | Where Observed | Impact | Fix |
|-------------|---------------|--------|-----|
| **CLAUDE.md as README** | `odoo` | CLAUDE.md is 1500+ lines covering human-readable architecture, BIR compliance, Figma setup, n8n patterns. Agents load 1500 lines when they need 200. | Split: CLAUDE.md for agent rules (<500 lines), README.md for human context |
| **Aspirational docs as current state** | `odoo/docs/architecture/PLATFORM_TARGET_STATE.md` | 33KB document describes target state but does not clearly distinguish what IS deployed from what SHOULD BE deployed | Separate: current-state docs vs target-state docs |
| **Evidence mixed with normative docs** | `odoo/docs/` | Architecture docs, evidence packs, and operational docs all in `docs/` with no clear separation | Restructure per Section 4.4 |
| **Duplicate documentation** | `odoo` CLAUDE.md + `.claude/rules/` | Odoo coding conventions exist in both CLAUDE.md and `.claude/rules/odoo19-coding.md` | CLAUDE.md should reference rules files, not duplicate them |
| **Stale deprecation notices** | `odoo` CLAUDE.md references DigitalOcean, Vercel, Mailgun | These are deprecated per `~/.claude/rules/infrastructure.md` but CLAUDE.md still contains detailed DigitalOcean/Vercel integration docs | Remove deprecated integration docs from CLAUDE.md |
| **Orphaned specs** | `odoo/spec/` (76 bundles) | No status tracking. No way to know which specs are implemented, which are abandoned, which are in progress | Add status field to spec bundles, validate in CI |
| **Missing decision history** | `data-intelligence`, `agents`, `automations` | Key decisions (Databricks over X, n8n over Y, agent architecture choices) exist only in memory, not in repos | Write ADRs retroactively |
| **Generated content without generation script** | `odoo/docs/data-model/` | DBML, ERD, ORM maps exist but regeneration script may be broken or outdated | Validate generators in CI |
| **Unlinked cross-references** | Throughout | Docs reference other files with relative paths that may be broken after moves | CI link validation |

### 8.7 Documentation Maturity Score

Using a 5-level maturity model:

| Level | Definition | Requirements |
|-------|-----------|-------------|
| L0 | None | No documentation exists |
| L1 | Minimal | README exists, basic description |
| L2 | Functional | README + CLAUDE.md + at least one ADR |
| L3 | Governed | L2 + CI validation + docs build + runbooks |
| L4 | Systematic | L3 + cross-repo linking + SSOT references + evidence packs |
| L5 | Optimized | L4 + search-enabled portal + versioned docs + automated freshness checks |

**Current Scores**:

| Repo | Level | Rationale |
|------|-------|-----------|
| `odoo` | L2 (partial L3) | Has README, CLAUDE.md, architecture docs, evidence. But no docs build, no ADR numbering, no systematic validation. |
| `infra` | L1 (partial) | Has docs/ and spec/ but no README, no CLAUDE.md. |
| `web` | L1 | Has README (acknowledges deprecation), docs/, spec/. But no CLAUDE.md, no CI. |
| `agents` | L1 | Has README only. No CLAUDE.md, no docs/, no spec/. |
| `.github` | L1 (partial) | Has policies, templates. No README, no CLAUDE.md. |
| `data-intelligence` | L0 | No README, no CLAUDE.md, no docs/. |
| `automations` | L0 | No README, no CLAUDE.md, no docs/. Has inventory data but no documentation. |
| `platform` | L0 | Nothing. |
| `templates` | Unknown | Not explored in depth. |
| `design` | Unknown | Not explored in depth. |

**Target**: All repos at L3 within Phase 4 (Week 8). `odoo` and `infra` at L4 within Phase 5 (Week 10).

### 8.8 Specific Documentation Gaps to Close (Ranked)

| # | Gap | Repo | Impact if Not Closed | Effort | Priority |
|---|-----|------|---------------------|--------|----------|
| 1 | No CLAUDE.md in 9 repos | All except `odoo` | Agents cannot operate safely in any satellite repo | 2 hours each | P0 |
| 2 | No ADR for Databricks/JDBC decision | `data-intelligence` | Decision history lost, cannot be questioned or revisited | 2 hours | P0 |
| 3 | No ADR for Azure-over-DigitalOcean | `infra` | Major infra decision undocumented | 2 hours | P0 |
| 4 | No ADR for Keycloak-transitional-to-Entra | `infra` | Identity migration has no written plan in repo | 2 hours | P0 |
| 5 | No runbook for Odoo deployment | `odoo` | Production deployment is tribal knowledge | 4 hours | P0 |
| 6 | No runbook for database backup/restore | `odoo` or `infra` | Disaster recovery is undocumented | 3 hours | P0 |
| 7 | No runbook for Supabase operations | `infra` | VM-based Supabase has no operational playbook | 3 hours | P1 |
| 8 | No runbook for Keycloak admin | `infra` | SSO management is tribal knowledge | 3 hours | P1 |
| 9 | No docs build pipeline | `.github` (reusable) | Docs are never validated or published | 4 hours | P1 |
| 10 | No cross-repo secret dependency map | `infra` | Changing a Key Vault secret name may break unknown services | 4 hours | P1 |
| 11 | No active/deprecated app inventory in `web` | `web` | Cannot determine which of 19 apps are live | 2 hours | P1 |
| 12 | No automation dependency map | `automations` | Cannot determine impact of changing an automation | 3 hours | P2 |
| 13 | CLAUDE.md in `odoo` is too long | `odoo` | Agent context overload, slower processing | 4 hours | P2 |
| 14 | No onboarding docs | `odoo`, `.github` | New contributors/agents have no starting path | 6 hours | P2 |
| 15 | 76 spec bundles with no status tracking | `odoo` | Cannot determine project state | 3 hours | P2 |

---

## 9. Deployed Resource Model & Design Primitives

### 9A. Deployed Resource Model

The IPAI platform has real deployed infrastructure. The UI must represent these actual resources, not abstract concepts.

#### Entity Classes

| Class | Instances | Source of Truth | Lifecycle |
|-------|----------|----------------|-----------|
| **Environment** | dev, staging, prod | `infra/ssot/azure/` | Permanent (3 environments only) |
| **Container App** | 13 ACA resources | Azure Resource Manager | Long-lived, revised on deploy |
| **Container App Revision** | N per app | Azure Container Apps | Created on deploy, garbage collected |
| **Database Server** | 2 (ipai-odoo-dev-pg, pg-ipai-dev) | Azure Resource Manager | Long-lived |
| **Database** | 3 per server (dev, staging, prod) | PostgreSQL catalog | Long-lived |
| **Key Vault** | 4 (dev, staging, prod, odoo) | Azure Resource Manager | Long-lived |
| **Container Registry** | 3 (shared, odoo, web) | Azure Resource Manager | Long-lived |
| **Front Door Endpoint** | 1 (ipai-fd-dev) | Azure Resource Manager | Long-lived |
| **Front Door Route** | 12+ (one per subdomain) | Azure Front Door config | Long-lived |
| **DNS Record** | 12+ subdomains | Cloudflare API | Long-lived |
| **AI Service** | 7 (OpenAI, DocIntel, Vision, Language, Search, Databricks, AI Foundry) | Azure Resource Manager | Long-lived |
| **Virtual Machine** | 1 (Supabase) | Azure Resource Manager | Long-lived (exception to ACA model) |
| **Edge Function** | 42 | Supabase dashboard | Deployed independently |
| **Pipeline Run** | N per repo | GitHub Actions | Ephemeral |
| **Deployment** | N per service | Azure Container Apps / GitHub Actions | Ephemeral record, permanent evidence |
| **Odoo Module** | 69 ipai + N OCA | `config/addons.manifest.yaml` | Versioned with Odoo |
| **Spec Bundle** | 76+ | `spec/` directories | Lifecycle: proposed > accepted > implemented > closed |
| **ADR** | 23+ (to be numbered) | `docs/architecture/adr/` | Lifecycle: proposed > accepted > deprecated > superseded |
| **Automation Workflow** | 339+ | `automations/inventory/` | Active / paused / retired |
| **Identity Provider** | Keycloak (current), Entra ID (target) | `infra/identity/` | Transitional |
| **Team/Owner** | N | CODEOWNERS | Org-level |

### 9A.2 Entity Relationships

The deployed resources are not independent -- they form a dependency graph that the UI must represent:

```
Environment (dev/staging/prod)
  |
  +-- Container App (N per environment)
  |     |
  |     +-- Revision (N per app, 1 active)
  |     |     |
  |     |     +-- Container Image (from Container Registry)
  |     |     +-- Environment Variables (from Key Vault)
  |     |
  |     +-- Health Check (periodic)
  |     +-- Logs (continuous)
  |     +-- Metrics (continuous)
  |
  +-- Database Server (1-2 per environment)
  |     |
  |     +-- Database (N per server)
  |     +-- Backup (periodic)
  |     +-- Connection Pool (monitored)
  |
  +-- Key Vault (1 per environment)
  |     |
  |     +-- Secret (N per vault)
  |     +-- Access Policy (N per vault)
  |
  +-- Front Door Route (N per environment)
  |     |
  |     +-- Origin Group (1 per route)
  |     +-- Origin (1+ per group, maps to Container App)
  |     +-- WAF Policy (optional)
  |     +-- Cache Policy (optional)
  |
  +-- DNS Record (1 per subdomain)
        |
        +-- Mapped to Front Door Route
```

**Cross-Environment Relationships**:

```
Container Registry (shared across environments)
  |
  +-- Image:dev-<sha>    --> consumed by dev Container Apps
  +-- Image:staging-<sha> --> consumed by staging Container Apps
  +-- Image:prod-<sha>   --> consumed by prod Container Apps

Pipeline Run (triggers cross-environment promotion)
  |
  +-- Build Phase --> produces Container Image
  +-- Deploy-Dev Phase --> creates Revision in dev
  +-- Promote-Staging Phase --> creates Revision in staging
  +-- Promote-Prod Phase --> creates Revision in prod
```

**Identity Relationships**:

```
Keycloak (current IdP)
  |
  +-- Realm --> IPAI realm
  |     +-- Client (N per application)
  |     |     +-- Odoo client
  |     |     +-- Superset client
  |     |     +-- Plane client
  |     |     +-- n8n client
  |     +-- User (N)
  |     +-- Role (N)
  |     +-- Group (N)
  |
  +-- Transitioning to Entra ID
        +-- Same relationships, different representation
```

### 9A.3 Service Dependency Map

This map shows runtime dependencies between deployed services. The UI should visualize these dependencies.

| Service | Depends On | Depended On By |
|---------|-----------|---------------|
| Odoo Web | PostgreSQL (ipai-odoo-dev-pg), Keycloak, Key Vault, SMTP (Zoho) | Front Door, Odoo Worker, Odoo Cron |
| Odoo Worker | PostgreSQL (ipai-odoo-dev-pg), Key Vault | Odoo Web (async job processing) |
| Odoo Cron | PostgreSQL (ipai-odoo-dev-pg), Key Vault | Odoo Web (scheduled tasks) |
| Keycloak | PostgreSQL (pg-ipai-dev), Key Vault | Odoo, Superset, Plane, CRM, Shelf, n8n |
| Superset | PostgreSQL (pg-ipai-dev), Keycloak | None (end-user BI) |
| Plane | Keycloak | None (end-user project mgmt) |
| MCP Coordinator | Key Vault, Azure OpenAI | Agents, Automations |
| OCR Service | Azure Document Intelligence, Key Vault | Odoo (document processing) |
| Supabase VM | Disk storage, Network | n8n, Edge Functions, External integrations |
| Front Door | All Container Apps (as origins) | External users (ingress) |

**Failure Impact Analysis**:

| If This Fails | These Are Affected | Severity |
|--------------|-------------------|----------|
| PostgreSQL (ipai-odoo-dev-pg) | Odoo Web, Worker, Cron | CRITICAL -- ERP down |
| PostgreSQL (pg-ipai-dev) | Keycloak, Superset | CRITICAL -- auth and BI down |
| Keycloak | All apps with SSO | CRITICAL -- no one can log in |
| Front Door | All public-facing services | CRITICAL -- nothing reachable |
| Azure OpenAI | MCP Coordinator, AI features | HIGH -- AI features degraded |
| Supabase VM | Edge Functions, n8n integrations | MEDIUM -- integrations degraded |
| Zoho SMTP | Outbound email from Odoo | LOW -- email delayed, not blocking |

### 9B. Design Primitive Inventory

Each primitive maps to a real entity class and defines how that entity is rendered in UI.

#### B1. Foundation Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 1 | `EnvironmentBadge` | Identify which environment a resource belongs to | Environment entity | dev, staging, prod | name, color, isProduction | Badge/pill | design | Presentational |
| 2 | `ResourceIdentifier` | Display resource name with type icon | Any Azure resource | N/A | name, type, resourceGroup, region | Inline text with icon | design | Presentational |
| 3 | `StatusIndicator` | Show health/operational status | Health check result | healthy, degraded, unhealthy, unknown, maintenance | status, lastChecked, message | Dot + label | design | Presentational |
| 4 | `TimestampDisplay` | Show relative and absolute times | Any timestamped event | N/A | timestamp, format (relative/absolute/both) | Text | design | Presentational |
| 5 | `OwnerBadge` | Show team/person ownership | CODEOWNERS | N/A | owner, type (team/person), avatarUrl | Avatar + name | design | Presentational |

#### B2. Status/State Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 6 | `DeploymentStatus` | Show deployment pipeline state | GitHub Actions run / ACA revision | queued, in_progress, succeeded, failed, cancelled, rolling_back | runId, commitSha, environment, startedAt, completedAt | Status row | design | Domain |
| 7 | `HealthCard` | Composite health view for a service | ACA app + health endpoint | healthy, degraded, unhealthy, unknown | serviceName, endpoint, lastCheck, responseTime, uptime | Card | web | Composite |
| 8 | `PromotionIndicator` | Show environment promotion state | Deployment pipeline | ready_to_promote, promoting, promoted, blocked | sourceEnv, targetEnv, commitSha, approvals | Button + status | web | Domain |
| 9 | `DriftIndicator` | Show config drift between environments | IaC state comparison | in_sync, drifted, unknown | resource, expectedState, actualState, lastChecked | Warning badge | web | Domain |
| 10 | `ComplianceStatus` | Show compliance posture | Policy check results | compliant, non_compliant, not_evaluated, exempt | policy, resource, lastEvaluated, evidence | Badge with tooltip | design | Domain |

#### B3. Resource Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 11 | `ContainerAppCard` | Display ACA resource with status | Azure Container App | running, stopped, failed, provisioning, deprovisioning | name, fqdn, publicHostname, revisionCount, activeRevision, environment, resourceGroup | Card | web | Composite |
| 12 | `DatabaseCard` | Display database resource | Azure PostgreSQL | available, unavailable, maintenance | serverName, databaseName, size, connectionCount, environment | Card | web | Composite |
| 13 | `KeyVaultCard` | Display Key Vault with secret count | Azure Key Vault | available, unavailable | vaultName, secretCount, lastAccessed, environment | Card | web | Composite |
| 14 | `FrontDoorRouteRow` | Display a Front Door routing rule | Azure Front Door route | enabled, disabled | subdomain, originGroup, origin, cachePolicy, wafPolicy | Table row | web | Composite |
| 15 | `AIServiceCard` | Display an AI service | Azure AI resource | available, unavailable, quota_exceeded | serviceName, type (openai/docintel/vision/etc), region, model, quotaUsed | Card | web | Composite |
| 16 | `ContainerRegistryCard` | Display ACR with image count | Azure Container Registry | available, unavailable | registryName, imageCount, lastPush, storageMB | Card | web | Composite |
| 17 | `SubabaseVMCard` | Display Supabase VM (exception to ACA model) | Azure VM | running, stopped, deallocated | vmName, ip, edgeFunctionCount, storageGB | Card | web | Composite |
| 18 | `DNSRecordRow` | Display a DNS record | Cloudflare DNS | proxied, dns_only, pending | subdomain, type, target, ttl, proxied | Table row | web | Composite |
| 19 | `EdgeFunctionRow` | Display a Supabase Edge Function | Supabase Edge Functions | active, inactive, error | name, lastInvoked, invocationCount, runtime | Table row | web | Domain |
| 20 | `OdooModuleRow` | Display an Odoo module | addons.manifest.yaml | installed, uninstalled, to_upgrade, to_remove | name, version, tier (config/oca/ipai), depends | Table row | web | Domain |

#### B4. Delivery/Deployment Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 21 | `PipelineRunRow` | Display a CI/CD pipeline run | GitHub Actions workflow run | queued, in_progress, completed, failed, cancelled | runId, workflow, repo, branch, commitSha, triggeredBy, duration | Table row | web | Domain |
| 22 | `RevisionCard` | Display an ACA revision | Azure Container App revision | active, inactive, failed | revisionName, image, trafficWeight, createdAt, commitSha | Card | web | Composite |
| 23 | `RollbackButton` | Trigger rollback to previous revision | ACA revision management | idle, confirming, rolling_back, completed, failed | currentRevision, targetRevision, serviceName | Button with confirmation | web | Domain |
| 24 | `ApprovalGate` | Display and manage deployment approval | GitHub Environment protection | pending, approved, rejected, expired | environment, requester, approvers, expiresAt | Card with action buttons | web | Domain |
| 25 | `DeploymentTimeline` | Show deployment history for a service | Deployment evidence | N/A | deployments (array of DeploymentStatus) | Vertical timeline | web | Composite |

#### B5. Governance/Compliance Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 26 | `SpecBundleCard` | Display a spec bundle with status | spec/ directory | proposed, accepted, in_progress, implemented, closed | specId, title, owner, createdAt, linkedPRs | Card | web | Domain |
| 27 | `ADRCard` | Display an Architecture Decision Record | docs/architecture/adr/ | proposed, accepted, deprecated, superseded | adrNumber, title, status, date, supersededBy | Card | web | Domain |
| 28 | `PolicyCard` | Display a governance policy | .github/policies/ | active, draft, deprecated | policyName, scope, lastUpdated, owner | Card | web | Domain |
| 29 | `ChangeHistoryRow` | Display a change event | Git commits + deployment evidence | N/A | commitSha, author, message, timestamp, environment, type | Table row | web | Domain |
| 30 | `PermissionMatrix` | Display access control for a resource | CODEOWNERS + Key Vault RBAC | N/A | resource, teams, permissions | Matrix/grid | web | Composite |

#### B6. Observability/Ops Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 31 | `IncidentCard` | Display an active incident | Incident management (Plane/GitHub Issues) | investigating, identified, monitoring, resolved | incidentId, title, severity, affectedServices, startedAt, resolvedAt | Card | web | Domain |
| 32 | `AlertRow` | Display an alert rule or fired alert | Azure Monitor / custom | active, firing, acknowledged, resolved, silenced | alertName, severity, resource, lastFired, acknowledgedBy | Table row | web | Domain |
| 33 | `LogViewer` | Display structured logs | ACA logs / Azure Monitor | N/A | source, timeRange, level, query | Panel | web | Composite |
| 34 | `MetricSparkline` | Display a metric trend | Azure Monitor metrics | N/A | metricName, resource, timeRange, values | Inline sparkline chart | design | Presentational |
| 35 | `BackupStatusRow` | Display backup status for a database | Azure PostgreSQL backups | available, in_progress, failed, not_configured | databaseName, lastBackup, retentionDays, size | Table row | web | Domain |
| 36 | `UptimeBar` | Display uptime percentage over time | Health check history | N/A | serviceName, timeRange, uptimePercent, incidents | Horizontal bar | design | Presentational |

#### B7. Documentation/Spec/Evidence Primitives

| # | Primitive | Purpose | Backed By | Key States | Required Metadata | Form Factor | Repo Owner | Type |
|---|----------|---------|-----------|------------|-------------------|-------------|------------|------|
| 37 | `EvidencePackCard` | Display a deployment/test evidence pack | docs/evidence/ | complete, partial, missing | date, scope, files, linkedDeployment | Card | web | Domain |
| 38 | `RunbookCard` | Display a runbook with last-verified date | docs/operations/ | verified, stale (>90 days), unverified | title, owner, lastVerified, linkedServices | Card | web | Domain |
| 39 | `SSOTFileRow` | Display an SSOT file with validation status | infra/ssot/ | valid, invalid, stale | fileName, schema, lastValidated, lastModified | Table row | web | Domain |
| 40 | `AutomationInventoryRow` | Display an automation workflow | automations/inventory/ | active, paused, retired, broken | name, trigger, schedule, lastRun, owner | Table row | web | Domain |

### 9C. Primitive Taxonomy

#### Layer 1: Foundation (5 primitives)

These are the atoms. Everything else is built from these.

```
EnvironmentBadge
ResourceIdentifier
StatusIndicator
TimestampDisplay
OwnerBadge
```

#### Layer 2: Status/State (5 primitives)

These communicate operational state.

```
DeploymentStatus
HealthCard
PromotionIndicator
DriftIndicator
ComplianceStatus
```

#### Layer 3: Resource (10 primitives)

These represent deployed infrastructure and application resources.

```
ContainerAppCard
DatabaseCard
KeyVaultCard
FrontDoorRouteRow
AIServiceCard
ContainerRegistryCard
SubabaseVMCard
DNSRecordRow
EdgeFunctionRow
OdooModuleRow
```

#### Layer 4: Delivery/Deployment (5 primitives)

These represent the deployment lifecycle.

```
PipelineRunRow
RevisionCard
RollbackButton
ApprovalGate
DeploymentTimeline
```

#### Layer 5: Governance/Compliance (5 primitives)

These represent organizational governance.

```
SpecBundleCard
ADRCard
PolicyCard
ChangeHistoryRow
PermissionMatrix
```

#### Layer 6: Observability/Ops (6 primitives)

These represent operational monitoring.

```
IncidentCard
AlertRow
LogViewer
MetricSparkline
BackupStatusRow
UptimeBar
```

#### Layer 7: Documentation/Spec/Evidence (4 primitives)

These represent the documentation and evidence layer.

```
EvidencePackCard
RunbookCard
SSOTFileRow
AutomationInventoryRow
```

### 9D. Design-Token Implications

#### Environment Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-env-dev` | `#3B82F6` (blue) | Dev environment badge, borders |
| `--color-env-staging` | `#F59E0B` (amber) | Staging environment badge, borders |
| `--color-env-prod` | `#EF4444` (red) | Prod environment badge, borders |
| `--color-env-preview` | `#8B5CF6` (purple) | Preview/ephemeral environment |

#### Severity/Status Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-status-healthy` | `#10B981` (green) | Healthy, passing, available |
| `--color-status-degraded` | `#F59E0B` (amber) | Degraded, warning, partial |
| `--color-status-unhealthy` | `#EF4444` (red) | Unhealthy, failing, unavailable |
| `--color-status-unknown` | `#6B7280` (gray) | Unknown, not evaluated |
| `--color-status-maintenance` | `#6366F1` (indigo) | Maintenance mode |

#### Health State Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-health-up` | `#10B981` | Service up, responding |
| `--color-health-down` | `#EF4444` | Service down, not responding |
| `--color-health-flapping` | `#F59E0B` | Service intermittently available |

#### Promotion/Rollback Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-promote` | `#3B82F6` (blue) | Promote action button |
| `--color-rollback` | `#EF4444` (red) | Rollback action button |
| `--color-promote-ready` | `#10B981` | Ready to promote indicator |
| `--color-promote-blocked` | `#6B7280` | Promotion blocked indicator |

#### Compliance/Risk Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-compliant` | `#10B981` | Compliant status |
| `--color-non-compliant` | `#EF4444` | Non-compliant status |
| `--color-exempt` | `#6B7280` | Exempt from policy |
| `--color-not-evaluated` | `#D1D5DB` | Not yet evaluated |

#### Deployment State Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--color-deploy-queued` | `#D1D5DB` | Queued deployment |
| `--color-deploy-running` | `#3B82F6` | In-progress deployment |
| `--color-deploy-success` | `#10B981` | Successful deployment |
| `--color-deploy-failed` | `#EF4444` | Failed deployment |
| `--color-deploy-cancelled` | `#6B7280` | Cancelled deployment |
| `--color-deploy-rollback` | `#F59E0B` | Rolling back |

#### Resource-Type Iconography

| Resource Type | Icon Reference | Token |
|--------------|---------------|-------|
| Container App | Container/box icon | `--icon-resource-aca` |
| Database | Cylinder/database icon | `--icon-resource-db` |
| Key Vault | Lock/key icon | `--icon-resource-kv` |
| Container Registry | Package/registry icon | `--icon-resource-acr` |
| Front Door | Globe/shield icon | `--icon-resource-fd` |
| AI Service | Brain/sparkle icon | `--icon-resource-ai` |
| Virtual Machine | Server/computer icon | `--icon-resource-vm` |
| DNS Record | Link/chain icon | `--icon-resource-dns` |
| Edge Function | Lambda/function icon | `--icon-resource-fn` |
| Odoo Module | Puzzle piece icon | `--icon-resource-module` |
| Pipeline | Workflow/arrows icon | `--icon-resource-pipeline` |
| Spec Bundle | Document/spec icon | `--icon-resource-spec` |
| ADR | Decision/gavel icon | `--icon-resource-adr` |

#### Spacing and Size Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--size-badge-sm` | `20px` | Small badges (environment, status) |
| `--size-badge-md` | `28px` | Medium badges |
| `--size-card-min-width` | `320px` | Minimum card width |
| `--size-card-max-width` | `480px` | Maximum card width |
| `--size-icon-sm` | `16px` | Small icons (inline) |
| `--size-icon-md` | `24px` | Medium icons (card headers) |
| `--size-icon-lg` | `32px` | Large icons (page headers) |
| `--radius-badge` | `9999px` | Fully rounded badges |
| `--radius-card` | `8px` | Card corner radius |

### 9E. Repo Ownership for Primitives

| Primitive Location | What Lives There | Published As |
|-------------------|-----------------|-------------|
| `design/tokens/` | CSS custom properties, JSON token definitions | npm `@ipai/design-tokens` |
| `design/components/foundation/` | EnvironmentBadge, ResourceIdentifier, StatusIndicator, TimestampDisplay, OwnerBadge, MetricSparkline, UptimeBar | npm `@ipai/design-primitives` |
| `web/packages/ops-primitives/` | All Domain and Composite primitives (resource cards, deployment status, governance cards, etc.) | Internal package consumed by ops-console |
| `platform` (merged into `infra`) | N/A -- primitives do not live in infra | N/A |

The split is intentional:
- **Foundation primitives** (presentational, no domain knowledge) belong in `design`
- **Domain/composite primitives** (understand IPAI resources, states, workflows) belong in `web`
- Infrastructure repos never own UI primitives

### 9F. First-Wave Primitive Rollout

Prioritized by operational value -- what enables the ops-console to be useful first.

| Priority | Primitive | Layer | Rationale |
|----------|----------|-------|-----------|
| 1 | `EnvironmentBadge` | Foundation | Everything is environment-scoped. Needed by every other primitive. |
| 2 | `StatusIndicator` | Foundation | Health status is the most-viewed information in ops. |
| 3 | `ContainerAppCard` | Resource | 13 ACA resources are the primary managed entities. |
| 4 | `HealthCard` | Status | Composite health view is the ops-console landing page content. |
| 5 | `DeploymentStatus` | Status | Shows pipeline state -- the most common ops action. |
| 6 | `ResourceIdentifier` | Foundation | Names and icons for all resources. |
| 7 | `DatabaseCard` | Resource | 2 PostgreSQL servers are critical infrastructure. |
| 8 | `PipelineRunRow` | Delivery | Pipeline history is the second-most-viewed ops data. |
| 9 | `TimestampDisplay` | Foundation | Every event has a timestamp. |
| 10 | `RevisionCard` | Delivery | ACA revision management is core to deployment. |
| 11 | `DNSRecordRow` | Resource | 12 subdomains need visibility. |
| 12 | `FrontDoorRouteRow` | Resource | Front Door routing is the ingress layer. |
| 13 | `DeploymentTimeline` | Delivery | History view for deployments per service. |
| 14 | `OwnerBadge` | Foundation | Ownership visibility for incident response. |
| 15 | `RollbackButton` | Delivery | Operational action -- ability to rollback from UI. |

These 15 primitives enable a functional ops-console that can:
- Show all 13 ACA resources with health status
- Display deployment history and current state
- Show database and DNS resource status
- Enable rollback for failed deployments
- Identify resource ownership

---

## 10. Phased Refactor Plan

### Phase 0: Contracts and Inventory (Week 1)

**Objective**: Establish the governance baseline so all subsequent phases have clear standards.

**Repos Affected**: `.github`, all repos (inventory)

**Changes**:
1. Create repo contract definitions in `.github/repo-contract/`
2. Create `REPO_MAP.md` in `.github`
3. Audit all 10 repos against the contract (produce gap matrix)
4. Create ADR template in `.github/docs-governance/templates/`
5. Create CLAUDE.md template in `.github/docs-governance/templates/`
6. Define reusable workflow specifications (what will be extracted from `odoo`)

**Risks**:
- None. This is documentation-only work.

**Verification**:
- `REPO_MAP.md` exists and accurately maps all repos
- Repo contract definitions exist for all 8 repo classes
- Gap matrix shows current state vs target for each repo
- Templates exist and are usable

**Evidence**: `docs/evidence/2026-03-XX/phase-0/`

---

### Phase 1: Docs/Governance Baseline (Week 2)

**Objective**: Every repo has CLAUDE.md, README.md, CODEOWNERS, and at least one ADR.

**Repos Affected**: All 9 repos lacking CLAUDE.md, all 5 repos lacking README.md

**Changes**:
1. Add CLAUDE.md to: `platform`, `data-intelligence`, `agents`, `infra`, `web`, `automations`, `.github`, `templates`, `design`
2. Add README.md to: `platform`, `data-intelligence`, `automations`, `infra`, `.github`
3. Add `.github/CODEOWNERS` to repos lacking it
4. Add foundational ADR (`0001-why-this-repo-exists.md`) to repos with docs/
5. Create `.markdownlint.json` (permissive config) in `.github`, copy to all repos

**Risks**:
- CLAUDE.md for repos about to be merged (platform) may be wasted effort. Mitigation: write minimal CLAUDE.md for repos marked for merge -- they still need agent guidance until merged.

**Verification**:
- Every repo has CLAUDE.md (check with script)
- Every repo has README.md
- Every repo has CODEOWNERS
- markdownlint passes on all repos (permissive mode)

**Evidence**: `docs/evidence/2026-03-XX/phase-1/`

---

### Phase 2: Repo-Boundary Cleanup (Weeks 3-4)

**Objective**: Resolve the dual-source-of-truth problems and boundary violations.

**Repos Affected**: `odoo`, `infra`, `platform`, `web`, `automations`

**Changes**:
1. **Move `odoo/infra/` to `infra/`**: The `infra` repo becomes the canonical IaC location. `odoo/infra/` is removed. If `odoo` needs infra references, it uses cross-repo links or SSOT files.
2. **Move `odoo/apps/ops-console` to `web/apps/ops-console`**: Ops-console is a web application, not an Odoo module.
3. **Move `odoo/apps/mcp-jobs` to `automations/mcp-jobs`**: MCP jobs are automations, not Odoo modules.
4. **Merge `platform/ssot/` into `infra/ssot/`**: SSOT files belong with infrastructure.
5. **Merge `platform/supabase/` into `infra/supabase/`**: Supabase config is infrastructure.
6. **Archive `platform`**: After merge, repo becomes empty. Archive it.
7. **Audit remaining `odoo/apps/`**: Determine if other apps (7 remaining) belong in `odoo` or should move.
8. **Audit `odoo` workflows**: Identify non-Odoo workflows for extraction in Phase 3.

**Risks**:
- Moving `odoo/infra/` breaks any CI that references it. Mitigation: Update all workflow paths before moving.
- Moving apps breaks import paths. Mitigation: Update package.json / imports.
- `platform` merge breaks any references to it. Mitigation: Update REPO_MAP.md and all cross-repo links.

**Verification**:
- `odoo` repo contains ONLY: `addons/`, `vendor/`, `config/`, `scripts/` (Odoo-specific), `docs/` (Odoo-specific), `spec/` (Odoo-specific)
- `infra` repo contains ALL IaC including what was in `odoo/infra/` and `platform/ssot/`
- `web` repo contains `ops-console`
- `platform` is archived
- All CI pipelines pass after moves

**Evidence**: `docs/evidence/2026-03-XX/phase-2/`

---

### Phase 3: Pipeline/Environment Standardization (Weeks 5-6)

**Objective**: Extract reusable workflows, standardize CI across all repos, enforce environment promotion.

**Repos Affected**: `.github`, `odoo`, all repos

**Changes**:
1. **Extract reusable workflows from `odoo`**:
   - `reusable-lint.yml` (generic linting)
   - `reusable-test.yml` (generic test runner)
   - `reusable-security.yml` (gitleaks + trivy)
   - `reusable-docs.yml` (docs validation)
   - `reusable-contract.yml` (required files check)
   - `reusable-container.yml` (container build + push)
   - `reusable-iac.yml` (terraform/bicep validate)
   - `reusable-iac-plan.yml` (terraform/bicep plan)
2. **Wire all repos to consume reusable workflows**
3. **Standardize environment promotion** per Section 6.6
4. **Add artifact naming convention** per Section 6.10
5. **Delete duplicate/stale workflows from `odoo`** (estimated ~50)
6. **Add `required-checks` configuration** to all repo branch protection rules

**Risks**:
- Extracting workflows from `odoo` may break existing CI. Mitigation: Keep original workflows alongside reusable versions during transition. Remove originals only after reusable versions are verified.
- Standardizing environments may conflict with existing deployment scripts. Mitigation: Audit all deployment scripts first.

**Verification**:
- Reusable workflows exist in `.github`
- All repos call reusable workflows
- `odoo` workflow count reduced from 355 to < 150
- All repos have required checks configured on `main` branch
- Environment promotion works end-to-end for at least `odoo`

**Evidence**: `docs/evidence/2026-03-XX/phase-3/`

---

### Phase 4: Docs Platform Rollout (Weeks 7-8)

**Objective**: Build and publish org-wide documentation with validation.

**Repos Affected**: All repos, `.github`

**Changes**:
1. **Wire `mkdocs.yml` to CI** in `odoo` (it already exists, just not built)
2. **Create `mkdocs.yml` for other repos** that have docs/
3. **Create org-level docs aggregator** (mkdocs-material multi-repo setup or custom)
4. **Enable GitHub Pages** for docs publishing
5. **Add link validation** to `reusable-docs.yml`
6. **Restructure `odoo/docs/architecture/`**: Number existing docs as ADRs or move to `target-state/`
7. **Create first runbooks**: Odoo deployment, Supabase operations, Keycloak admin, database backup/restore
8. **Create first release notes template** and apply to next release
9. **Separate evidence from normative docs** per Section 4.4

**Risks**:
- mkdocs build may fail on existing malformed docs. Mitigation: Fix docs iteratively, start with permissive config.
- Restructuring `odoo/docs/architecture/` breaks existing links. Mitigation: Create redirect stubs.

**Verification**:
- Docs site builds and deploys for `odoo`
- Link validation passes (no broken links)
- At least 5 ADRs are properly numbered
- At least 4 runbooks exist (Odoo, Supabase, Keycloak, DB)
- Evidence docs are separated from normative docs

**Evidence**: `docs/evidence/2026-03-XX/phase-4/`

---

### Phase 5: SSOT/Template Consolidation (Weeks 9-10)

**Objective**: Machine-readable SSOT files validated in CI, templates updated to produce compliant repos.

**Repos Affected**: `infra`, `odoo`, `agents`, `automations`, `templates`

**Changes**:
1. **Validate SSOT files in CI**:
   - `infra/ssot/azure/service-matrix.yaml` -- JSON schema validation
   - `infra/ssot/azure/resources.yaml` -- JSON schema validation
   - `infra/dns/subdomain-registry.yaml` -- DNS consistency check
   - `odoo/config/addons.manifest.yaml` -- module manifest validation
   - `automations/inventory/inventory.json` -- automation inventory validation
   - `agents/agent-capabilities.yaml` -- agent capability validation
2. **Create JSON schemas** for each SSOT file
3. **Update `templates` repo** to produce repos matching the standard contract
4. **Validate templates in CI** -- render template, check output against contract

**Risks**:
- SSOT files may not exist yet in the expected locations. Mitigation: Create them during this phase.
- Schema definitions may not match actual file contents. Mitigation: Generate schemas from existing files, then tighten.

**Verification**:
- All SSOT files have JSON schemas
- CI validates SSOT files on every PR
- Templates produce repos that pass contract check
- At least 3 SSOT files exist and are valid

**Evidence**: `docs/evidence/2026-03-XX/phase-5/`

---

### Phase 6: Archive Salvage and Deletion (Week 11)

**Objective**: Extract useful content from archived repos, then delete them.

**Repos Affected**: 5 archived repos, `agents`, `templates`

**Changes**:
1. **`template-factory`**: Check for templates not in `templates` repo. Extract if any. Delete.
2. **`plugin-marketplace`**: Nothing to salvage. Delete.
3. **`plugin-agents`**: Check for agent patterns not in `agents` repo. Extract if any. Delete.
4. **`learn`**: Nothing to salvage. Delete.
5. **`mcp-core`**: Check for MCP definitions not in `agents/mcp/`. Extract if any. Delete.
6. **Update archive references** in `odoo` repo (if any reference archived repos).

**Risks**:
- Deleting repos with external references. Mitigation: Search all repos for references to archived repo names before deletion.

**Verification**:
- All useful content extracted and committed to target repos
- No remaining references to deleted repos in active repos
- Archived repos deleted (or GitHub-archived with clear deprecation notice)

**Evidence**: `docs/evidence/2026-03-XX/phase-6/`

---

### Phase 7: Design Primitive Rollout (Weeks 12-14)

**Objective**: Implement the first 15 design primitives per Section 9F.

**Repos Affected**: `design`, `web`

**Changes**:
1. **Create design token file** in `design/tokens/` with all tokens from Section 9D
2. **Implement 5 foundation primitives** in `design/components/foundation/`:
   - EnvironmentBadge, StatusIndicator, ResourceIdentifier, TimestampDisplay, OwnerBadge
3. **Implement 10 domain/composite primitives** in `web/packages/ops-primitives/`:
   - ContainerAppCard, HealthCard, DeploymentStatus, DatabaseCard, PipelineRunRow, RevisionCard, DNSRecordRow, FrontDoorRouteRow, DeploymentTimeline, RollbackButton
4. **Publish `@ipai/design-tokens`** as npm package
5. **Publish `@ipai/design-primitives`** as npm package
6. **Wire primitives into ops-console** (now in `web/apps/ops-console`)

**Risks**:
- Design system may not have a build pipeline. Mitigation: Set up during this phase.
- Primitives may not match actual API shapes. Mitigation: Derive types from Azure Resource Manager API responses.

**Verification**:
- Token file exists with all environment, status, deployment, compliance tokens
- 5 foundation primitives render correctly in Storybook or equivalent
- 10 domain primitives render with mock data
- npm packages publish successfully
- ops-console consumes at least 5 primitives

**Evidence**: `docs/evidence/2026-03-XX/phase-7/`

---

### Phase 8: Verification and Hardening (Weeks 15-16)

**Objective**: Verify the entire refactor, close gaps, harden governance.

**Repos Affected**: All repos

**Changes**:
1. **Re-run contract check across all repos** -- every repo must pass
2. **Verify all SSOT files are accurate** -- compare against actual Azure resources
3. **Verify all CI pipelines are green** across all repos
4. **Verify docs build and publish** across all repos with docs/
5. **Verify cross-repo references** -- REPO_MAP.md is accurate, no broken cross-repo links
6. **Harden branch protection** -- enforce required checks on all repos
7. **Create operational runbook** for the refactored org (how to add a new repo, how to add a new service, how to promote a deployment)
8. **Retrospective document** -- what worked, what did not, what to improve

**Risks**:
- Gaps discovered during verification may require re-work. Mitigation: Build buffer time into Phase 8.

**Verification**:
- All repos pass contract check
- All SSOT files match actual infrastructure
- All CI pipelines green
- Docs build and deploy for all repos
- No broken cross-repo references
- Operational runbook exists and is verified

**Evidence**: `docs/evidence/2026-03-XX/phase-8/`

---

### Phase 2 Detailed: File Movement Checklist

The largest risk in Phase 2 is moving files between repos. This checklist specifies exactly what moves where:

**From `odoo` to `infra`**:

| Source (odoo) | Destination (infra) | Reason |
|--------------|-------------------|--------|
| `infra/terraform/` | `infra/azure/terraform/` | IaC belongs in infra repo |
| `infra/doctl/` | `infra/legacy/doctl/` (deprecated) | DigitalOcean is deprecated, keep for reference |
| `infra/superset/` | `infra/superset/` | Superset config is infrastructure |
| `infra/ssot/` | `infra/ssot/` (merge with existing) | SSOT files belong with infrastructure |

**From `odoo` to `web`**:

| Source (odoo) | Destination (web) | Reason |
|--------------|------------------|--------|
| `apps/ops-console/` | `web/apps/ops-console/` | Standalone web app, not Odoo module |
| `apps/colima-desktop-ui/` | `web/apps/colima-desktop-ui/` | Desktop app, not Odoo module |

**From `odoo` to `automations`**:

| Source (odoo) | Destination (automations) | Reason |
|--------------|------------------------|--------|
| `apps/mcp-jobs/` | `automations/mcp-jobs/` | Job orchestration, not Odoo module |

**From `odoo` to `agents`**:

| Source (odoo) | Destination (agents) | Reason |
|--------------|---------------------|--------|
| `mcp/servers/plane/` | `agents/mcp/servers/plane/` | MCP server definition |
| `packages/agents/` | `agents/packages/agents/` | Agent framework |

**Staying in `odoo`**:

| Path | Reason to Keep |
|------|---------------|
| `addons/ipai/` | Core Odoo modules -- legitimate |
| `addons/oca/` | OCA modules -- legitimate |
| `vendor/odoo/` | Upstream mirror -- legitimate |
| `config/` | Odoo-specific config -- legitimate |
| `odoo19/` | Canonical setup -- legitimate |
| `docker/` | Odoo Docker configs -- legitimate |
| `deploy/docker-compose.yml` | Odoo deployment -- legitimate (deployment != infrastructure) |
| `deploy/nginx/` | Odoo-specific nginx -- legitimate |
| `scripts/odoo_*.sh` | Odoo-specific scripts -- legitimate |
| `scripts/ci/run_odoo_tests.sh` | Odoo-specific CI -- legitimate |
| `db/` | Database schemas/migrations for Odoo -- legitimate |
| `docs/` (Odoo-specific) | Odoo architecture, operations docs -- legitimate |
| `spec/` (Odoo-specific) | Odoo feature specs -- legitimate |
| `.claude/` | Odoo-specific agent guidance -- legitimate |

**Requires Audit (disposition TBD)**:

| Path | Options |
|------|---------|
| `apps/odoo-mobile-ios/` | Keep in `odoo` (it IS an Odoo frontend) or move to `web` (it IS a mobile app) |
| `apps/platform/` | Determine if Odoo-specific or platform-wide |
| `apps/slack-agent/` | Move to `agents` or `automations` |
| `apps/web/` | Move to `web` |
| `apps/workspace/` | Keep in `odoo` if it is an Odoo workspace module |
| `apps/docs/` | Move to `web` or delete if obsolete |
| `packages/taskbus/` | Move to `automations` or keep as shared package |
| `scripts/` (non-Odoo) | Audit each category -- platform scripts move, Odoo scripts stay |
| `spec/` (non-Odoo) | Move to respective repos |
| `.github/workflows/` (non-Odoo) | Extract to `.github` as reusable, keep Odoo-specific in `odoo` |

**From `platform` to `infra`**:

| Source (platform) | Destination (infra) | Reason |
|----------------------|-------------------|--------|
| `ssot/` | `infra/ssot/` (merge) | SSOT belongs with infrastructure |
| `supabase/` | `infra/supabase/` (merge) | Supabase config is infrastructure |
| `.env.example` | `infra/.env.example` (merge) | Environment template |

### Phase 3 Detailed: Workflow Categorization

The 355 workflows in `odoo` must be categorized before extraction. Estimated breakdown:

**Category A: Odoo-Specific (Keep in `odoo`) -- ~120 workflows**

| Pattern | Example | Count (est.) |
|---------|---------|-------------|
| Module CI/test | `ci-odoo-ce.yml`, `ci-odoo-oca.yml` | ~30 |
| Module deployment | `deploy-odoo-modules.sh` triggers | ~20 |
| OCA governance | `oca-lint.yml`, `oca-update.yml` | ~15 |
| EE parity checks | `ee-parity-gate.yml`, `spec-and-parity.yml` | ~10 |
| Odoo health checks | `health-check.yml`, `finance-ppm-health.yml` | ~15 |
| Seed data validation | `seeds-validate.yml` | ~5 |
| Odoo-specific builds | `build-seeded-image.yml`, `build-unified-image.yml` | ~10 |
| Module-specific workflows | Per-module CI for ipai_* modules | ~15 |

**Category B: Generic/Reusable (Extract to `.github`) -- ~80 workflows**

| Pattern | Reusable Workflow Name | Count (est.) |
|---------|----------------------|-------------|
| Python lint (black, isort, flake8) | `reusable-python-lint.yml` | ~10 |
| Node.js lint/test/build | `reusable-node-ci.yml` | ~10 |
| Docker build + push | `reusable-container-build.yml` | ~15 |
| Security scan (gitleaks, semgrep, trivy) | `reusable-security-scan.yml` | ~10 |
| Docs validation | `reusable-docs-validate.yml` | ~5 |
| Terraform validate/plan | `reusable-iac-validate.yml` | ~10 |
| GitHub release management | `reusable-release.yml` | ~5 |
| Dependency updates | Already handled by dependabot | ~5 |
| General deployment patterns | `reusable-aca-deploy.yml` | ~10 |

**Category C: Platform/Automation (Move to `automations` or respective repos) -- ~75 workflows**

| Pattern | Destination | Count (est.) |
|---------|------------|-------------|
| Scheduled health checks (non-Odoo) | `automations` | ~15 |
| Infrastructure validation | `infra` | ~15 |
| n8n workflow deployment | `automations` | ~10 |
| Report generation | `automations` | ~10 |
| Cross-repo sync | `automations` or `.github` | ~10 |
| Notification workflows | `automations` | ~15 |

**Category D: Stale/Duplicate (Delete) -- ~80 workflows**

These are workflows that:
- Reference deprecated services (DigitalOcean, Vercel, Mailgun, Mattermost)
- Are duplicates of other workflows with slightly different names
- Were created for one-time tasks and never cleaned up
- Reference paths or services that no longer exist

Each deletion must be verified: check if any other workflow depends on it, check if any branch protection rule references it.

### Phase Summary

| Phase | Weeks | Focus | Risk Level | Dependencies |
|-------|-------|-------|-----------|-------------|
| 0 | 1 | Contracts and inventory | None | None |
| 1 | 2 | Docs/governance baseline | Low | Phase 0 |
| 2 | 3-4 | Repo-boundary cleanup | Medium | Phase 1 |
| 3 | 5-6 | Pipeline standardization | Medium | Phase 2 |
| 4 | 7-8 | Docs platform rollout | Low | Phase 1 |
| 5 | 9-10 | SSOT/template consolidation | Low | Phase 2 |
| 6 | 11 | Archive salvage | Low | Phase 2 |
| 7 | 12-14 | Design primitives | Medium | Phase 2, 4 |
| 8 | 15-16 | Verification and hardening | Low | All phases |

Phases 4 and 5 can run in parallel with Phase 3. Phase 6 can run in parallel with Phase 5. Phase 7 can start as soon as Phase 2 completes (ops-console is in `web`).

---

## 11. Concrete Recommendation Matrix

| # | Repo | Action | Reason | Priority | Risk | Dependency | Owner |
|---|------|--------|--------|----------|------|-----------|-------|
| 1 | `.github` | Add CLAUDE.md, README.md, REPO_MAP.md, reusable workflows | Org governance root has no agent guidance, no reusable infrastructure | P0 | Low | None | Platform team |
| 2 | `agents` | Add CLAUDE.md, CODEOWNERS, .github/ with CI | Agent definitions repo has no agent guidance -- the irony must end | P0 | Low | None | AI team |
| 3 | `infra` | Add CLAUDE.md, README.md; absorb odoo/infra/ and platform/ssot/ | Must become sole IaC source of truth | P0 | Medium | Phase 1 complete | Platform team |
| 4 | `odoo` | Remove infra/, apps/ops-console, apps/mcp-jobs; reduce workflows from 355 | Boundary violation: monorepo pretending to be decomposed | P0 | High | infra ready to absorb | ERP team |
| 5 | `platform` | Merge ssot/ and supabase/ into infra; archive repo | Too thin, governance-free, causes confusion | P1 | Low | infra ready | Platform team |
| 6 | `data-intelligence` | Add CLAUDE.md, README.md, docs/architecture/adr/ with JDBC-over-ETL ADR | Governance-free data repo with undocumented decisions | P1 | Low | None | Data team |
| 7 | `web` | Add CLAUDE.md; absorb ops-console from odoo; audit and archive dead Vercel apps | Mixed live and dead apps, no agent guidance | P1 | Medium | odoo extraction | Frontend team |
| 8 | `automations` | Add CLAUDE.md, README.md; restructure inventory.json | Governance-free automation repo | P2 | Low | None | Platform team |
| 9 | `design` | Audit current state; expand with tokens and foundation primitives | Needed for ops-console primitives | P2 | Low | Primitive design complete | Design team |
| 10 | `templates` | Audit templates; update to produce contract-compliant repos | Templates may produce non-compliant repos | P3 | Low | Contract defined | Platform team |
| 11 | `template-factory` (archived) | Salvage templates if any; delete | Redundant with `templates` | P3 | None | None | Platform team |
| 12 | `plugin-marketplace` (archived) | Delete | Abandoned concept, no salvageable content | P3 | None | None | Platform team |
| 13 | `plugin-agents` (archived) | Salvage agent patterns; delete | May have patterns not in `agents` | P3 | None | None | AI team |
| 14 | `learn` (archived) | Delete | Stale training materials | P3 | None | None | Platform team |
| 15 | `mcp-core` (archived) | Salvage MCP definitions; delete | MCP is now in `agents/mcp/` | P3 | None | None | AI team |

---

## 12. Minimal First Wave

The smallest set of changes that produce the highest value without destabilizing delivery.

### First Wave Scope (Can be done in 1 week)

| # | Action | Repo | Effort | Impact | Risk |
|---|--------|------|--------|--------|------|
| 1 | Write CLAUDE.md for `.github` repo | `.github` | 2 hours | HIGH -- enables org-level agent guidance | None |
| 2 | Write CLAUDE.md for `agents` repo | `agents` | 2 hours | HIGH -- agent defs repo needs agent guidance | None |
| 3 | Write CLAUDE.md for `infra` repo | `infra` | 2 hours | HIGH -- IaC repo needs agent guidance | None |
| 4 | Write CLAUDE.md for `web` repo | `web` | 2 hours | MEDIUM -- web apps need agent guidance | None |
| 5 | Write CLAUDE.md for `data-intelligence` repo | `data-intelligence` | 1 hour | MEDIUM -- data repo needs agent guidance | None |
| 6 | Write CLAUDE.md for `automations` repo | `automations` | 1 hour | MEDIUM -- automation repo needs agent guidance | None |
| 7 | Write README.md for repos lacking it | `platform`, `data-intelligence`, `automations`, `infra`, `.github` | 3 hours | MEDIUM -- basic discoverability | None |
| 8 | Create REPO_MAP.md in `.github` | `.github` | 1 hour | HIGH -- cross-repo navigation for agents | None |
| 9 | Create `.markdownlint.json` (permissive) | `.github` | 30 min | MEDIUM -- docs quality baseline | None |
| 10 | Number top 5 architecture docs as ADRs | `odoo` | 2 hours | MEDIUM -- decision traceability | None |

**Total effort**: ~16 hours of focused work.

**What this buys**:
- Every repo has CLAUDE.md -- agents can operate in any repo with context
- Every repo has README.md -- humans can discover what each repo is
- REPO_MAP.md exists -- agents can navigate across repos
- First 5 ADRs are numbered -- decision history starts
- Markdown lint baseline exists -- docs quality can improve incrementally

### What This Does NOT Do (and why that is OK)

- Does not move files between repos (too risky for first wave)
- Does not change CI pipelines (requires careful coordination)
- Does not build docs platform (needs foundation first)
- Does not implement design primitives (needs repo boundaries settled first)

These are deferred to Phases 2-7 because they have cross-repo dependencies and higher risk. The first wave is deliberately low-risk and high-value.

### First Wave Docs-Platform Fixes Specifically

| Fix | Location | Why First |
|-----|----------|-----------|
| `.markdownlint.json` created | `.github` (then copied to repos) | Sets quality floor before more docs are written |
| 5 ADRs numbered | `odoo/docs/architecture/adr/` | Establishes ADR convention by example |
| REPO_MAP.md | `.github` | Prevents agents from guessing which repo to modify |
| CLAUDE.md in all repos | Each repo root | Prevents agents from operating without context |

---

## 13. Final Target-State Recommendation

### Repo Topology

**9 bounded repos, 0 monorepos, 0 governance-free repos.**

```
.github           Org governance, reusable workflows, repo contracts, REPO_MAP
odoo              Odoo CE 19 ERP ONLY: addons/ipai/, addons/oca/, vendor/odoo/, Odoo config/scripts/docs
infra             ALL IaC: Azure, Cloudflare, Databricks, SSOT, deployment, environments
agents            AI agent definitions: capabilities, knowledge, skills, MCP, personas, evals
web               Web applications: ops-console, active web UIs, ops-primitives package
data-intelligence  Data engineering: DLT contracts, medallion layers, data quality
automations        Workflow automation: n8n, scheduled jobs, automation inventory
design             Design tokens, foundation primitives, icon library
templates          Repo scaffolds matching standard contract
```

**Eliminated**: `platform` (merged into `infra`), 5 archived repos (salvaged and deleted).

### Docs Platform Model

- Each repo builds its own docs site via `mkdocs.yml` + GitHub Pages
- Org-level aggregation via `.github` docs governance
- Three doc classes strictly separated: normative, generated, evidence
- ADRs numbered sequentially per repo
- Runbooks required for every deployed service
- Link validation and markdown lint in CI (permissive initially, tighten over 6 months)
- CLAUDE.md and README.md mandatory in every repo, serving different audiences

### Governance Model

- CODEOWNERS in every repo
- Branch protection on `main` in every repo
- Required checks: lint, security scan, docs validation (minimum)
- PR template with spec reference, testing checklist, docs checklist
- Stale PR auto-close at 14 days
- PR size warning at 500 lines, block at 1000 lines

### Pipeline Model

- Layer 0: Reusable workflows in `.github` (8-10 workflows)
- Layer 1: Repo-specific CI calling Layer 0
- Layer 2: Environment promotion (dev > staging > prod) with approval gates
- Layer 3: Deployment via ACA revision management
- Deployment evidence required for every production deploy
- Rollback documented per-service

### Template/SSOT Model

- Templates produce repos matching standard contract (validated in CI)
- SSOT files are YAML with JSON schemas, validated in CI
- SSOT files live in the repo that owns the domain (service-matrix in `infra`, addons-manifest in `odoo`)
- Cross-repo references use SSOT files, not hardcoded values

### Design Primitive Model

- Foundation primitives (5) in `design` -- presentational, no domain knowledge
- Domain/composite primitives (35) in `web/packages/ops-primitives/` -- understand IPAI resources
- Design tokens published as `@ipai/design-tokens` npm package
- First 15 primitives rolled out in Phase 7, prioritized by ops-console needs
- Primitives derived from actual Azure resources, not generic patterns

### Disposition of Archived Repos

| Repo | Disposition | Timeline |
|------|------------|----------|
| template-factory | Salvage > delete | Phase 6 |
| plugin-marketplace | Delete | Phase 6 |
| plugin-agents | Salvage > delete | Phase 6 |
| learn | Delete | Phase 6 |
| mcp-core | Salvage > delete | Phase 6 |
| platform (active) | Merge into infra > archive | Phase 2 |

### Success Criteria for Completion

The refactor is complete when:

1. All 9 repos pass the standard contract check (CLAUDE.md, README.md, CODEOWNERS, docs/architecture/adr/)
2. `odoo` contains ONLY Odoo-related code (no infra/, no standalone apps)
3. `infra` is the sole IaC source of truth
4. All CI pipelines use reusable workflows from `.github`
5. Docs build and publish for all repos with docs/
6. All SSOT files have JSON schemas and pass CI validation
7. First 15 design primitives are implemented and consumed by ops-console
8. Environment promotion (dev > staging > prod) works end-to-end
9. No active references to archived/deleted repos
10. Every deployed service has at least one runbook

### Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| First Wave | Week 1 | All repos have CLAUDE.md + README.md |
| Phase 0-1 | Weeks 1-2 | Governance baseline complete |
| Phase 2 | Weeks 3-4 | Repo boundaries resolved |
| Phase 3 | Weeks 5-6 | Pipelines standardized |
| Phase 4-5 | Weeks 7-10 | Docs platform + SSOT live |
| Phase 6 | Week 11 | Archives cleaned up |
| Phase 7 | Weeks 12-14 | Design primitives live |
| Phase 8 | Weeks 15-16 | Verified and hardened |

**Total duration**: 16 weeks (4 months).

This is not a small effort. But the alternative is an org where one repo does everything, 6 repos have no governance, agents operate blind in 90% of the codebase, and infrastructure definitions exist in two places with no way to know which is correct. That state is not sustainable at the current rate of platform growth.

---

---

## Appendix A: CLAUDE.md Templates for Each Repo

These are concrete templates for the CLAUDE.md files that must be created in Phase 1. Each is scoped to the specific repo.

### A.1 CLAUDE.md for `.github` (Org Governance)

```markdown
# CLAUDE.md -- .github (Org Governance)

## Scope
This repo owns org-level governance: reusable workflows, PR templates, issue templates,
CODEOWNERS, repo contracts, documentation governance, and the REPO_MAP.

This repo does NOT own: application code, infrastructure, business logic, or deployment.

## Rules
1. Reusable workflows must be tested before release (use workflow_call trigger testing)
2. Changes to PR templates require review from platform team
3. REPO_MAP.md must be updated whenever a repo is added, renamed, or archived
4. Policy documents must have a Status header (Active, Draft, Deprecated)
5. Never add application-specific logic to reusable workflows

## Conventions
- Reusable workflows: `.github/workflows/reusable-<purpose>.yml`
- Composite actions: `.github/actions/<action-name>/action.yml`
- Policy docs: `.github/policies/<POLICY_NAME>.md`
- Templates: `.github/docs-governance/templates/<template-name>.md`

## Validation Commands
  # Validate all YAML files
  find . -name '*.yml' -o -name '*.yaml' | xargs yamllint

  # Check REPO_MAP.md lists all org repos
  gh repo list Insightpulseai --limit 100 --json name -q '.[].name'

## Dependencies
- Consumed by: ALL repos (reusable workflows, templates)
- Depends on: None
```

### A.2 CLAUDE.md for `agents` (AI Agent Definitions)

```markdown
# CLAUDE.md -- agents (AI Agent Definitions)

## Scope
This repo owns AI agent definitions: capabilities, knowledge bases, skills, MCP tool
definitions, personas, policies, procedures, prompts, evaluation benchmarks, and
Azure AI Foundry configuration.

This repo does NOT own: infrastructure provisioning, application runtime code,
deployment pipelines, or Odoo modules.

## Rules
1. Agent capability definitions must be YAML with a validated schema
2. MCP tool definitions must include input/output schemas
3. Prompt templates must not contain hardcoded secrets or PII
4. Evaluation benchmarks must be reproducible (deterministic inputs, measurable outputs)
5. Persona definitions must reference specific capabilities and policies
6. Knowledge base sources must be documented with provenance and freshness dates
7. Never store API keys or credentials in any file in this repo

## Conventions
- Capabilities: capabilities/<capability-name>.yaml
- Skills: skills/<skill-name>/skill.md + skill.yaml
- MCP tools: mcp/tools/<tool-name>/definition.yaml
- Personas: personas/<persona-name>.yaml
- Prompts: prompts/<domain>/<prompt-name>.md
- Evals: evals/<eval-suite>/<test-name>.yaml
- Knowledge: knowledge/<domain>/ (with README listing sources)

## Validation Commands
  # Validate YAML schemas
  find . -name '*.yaml' -o -name '*.yml' | xargs yamllint

  # Check for secrets
  gitleaks detect --source .

  # Validate capability schemas (when schema exists)
  ajv validate -s schemas/capability.json -d capabilities/*.yaml

## Dependencies
- Consumed by: odoo (MCP tools), automations (n8n agent workflows), web (agent UI)
- Depends on: None (definitions only, no runtime deps)

## Quick Reference
| Item | Value |
|------|-------|
| MCP transport | HTTP remote first (per MCP scope policy) |
| Foundry SDK | Azure AI Foundry (Responses API / Agents v2) |
| Primary LLM | Azure OpenAI (oai-ipai-dev, East US) |
| Eval framework | TBD |
```

### A.3 CLAUDE.md for `infra` (Infrastructure)

```markdown
# CLAUDE.md -- infra (Infrastructure as Code)

## Scope
This repo owns ALL infrastructure-as-code: Azure resource provisioning (Bicep/Terraform),
Cloudflare DNS management, Databricks workspace configuration, deployment scripts,
environment definitions, SSOT files, identity management (Entra), and observability config.

This repo does NOT own: application code, Odoo modules, business logic, web UI code.

## Rules
1. All infrastructure changes must be expressed as code (no console-only changes)
2. DNS changes follow YAML-first workflow: edit subdomain-registry.yaml, generate, apply
3. Terraform state is stored remotely (Azure Storage Account)
4. Key Vault secret NAMES may be referenced; secret VALUES never appear in code
5. Every IaC change must have a terraform plan or bicep what-if before apply
6. Environment-specific configs live in environments/<env>/
7. SSOT files must have JSON schemas and be validated in CI

## Conventions
- Azure resources: azure/<resource-type>/
- DNS: dns/subdomain-registry.yaml (SSOT), dns/generated/ (auto-generated)
- SSOT: ssot/azure/service-matrix.yaml, ssot/azure/resources.yaml
- Environments: environments/dev/, environments/staging/, environments/prod/
- Deployment scripts: deploy/<service>-deploy.sh

## Validation Commands
  # Terraform validate
  cd azure/terraform && terraform init && terraform validate

  # Bicep build
  az bicep build --file azure/bicep/main.bicep

  # DNS consistency check
  ./scripts/dns/validate-dns-consistency.sh

  # SSOT schema validation
  ajv validate -s schemas/service-matrix.json -d ssot/azure/service-matrix.yaml

## Dependencies
- Consumed by: odoo (deployment), web (deployment), all services (infrastructure)
- Depends on: None (IaC is the foundation)

## Quick Reference
| Item | Value |
|------|-------|
| Resource Group | rg-ipai-dev |
| Region | southeastasia |
| ACA Environment | cae-ipai-dev |
| Front Door | ipai-fd-dev |
| DNS Provider | Cloudflare (insightpulseai.com) |
| Key Vault (dev) | kv-ipai-dev |
| Key Vault (staging) | kv-ipai-staging |
| Key Vault (prod) | kv-ipai-prod |
| Container Registry | cripaidev, ipaiodoodevacr, ipaiwebacr |
```

### A.4 CLAUDE.md for `data-intelligence` (Data Engineering)

```markdown
# CLAUDE.md -- data-intelligence (Data Engineering)

## Scope
This repo owns data engineering artifacts: Databricks DLT pipeline contracts,
medallion layer definitions (Bronze/Silver/Gold/Platinum), data quality rules,
and data contract specifications.

This repo does NOT own: application code, infrastructure provisioning (use infra repo),
Odoo modules, or runtime services.

## Rules
1. Data contracts must specify schema, SLA, and quality rules
2. Medallion layer transitions must be documented (what transforms data from Bronze to Silver, etc.)
3. JDBC connection details are secrets -- reference by Key Vault name, never hardcode
4. Pipeline definitions must be idempotent (safe to re-run)
5. All contracts must have JSON schemas

## Conventions
- Contracts: contracts/<domain>/<contract-name>.yaml
- Pipeline definitions: pipelines/<pipeline-name>/
- Quality rules: quality/<domain>/<rule-name>.yaml
- Medallion: contracts/medallion/<layer>.md

## Key Decisions (see ADRs)
- ADR-0001: Databricks JDBC extract over Supabase ETL (Supabase ETL is Private Alpha, N/A for self-hosted)
- ADR-0002: Medallion architecture (Bronze > Silver > Gold > Platinum)
- ADR-0003: Catalog naming: ipai_<layer>.<domain>.<table>

## Validation Commands
  # Validate contract schemas
  python scripts/validate_contracts.py

  # Check YAML syntax
  find . -name '*.yaml' | xargs yamllint

## Dependencies
- Consumed by: Databricks workspace (infra provisions it)
- Depends on: odoo (source data via JDBC), infra (workspace config)

## Quick Reference
| Item | Value |
|------|-------|
| Databricks workspace | dbw-ipai-dev (rg-ipai-ai-dev, southeastasia) |
| Source DB | ipai-odoo-dev-pg (JDBC extract) |
| Catalog naming | ipai_<layer>.<domain>.<table> |
| ETL approach | Databricks JDBC extract (NOT Supabase ETL) |
```

### A.5 CLAUDE.md for `automations` (Workflow Automation)

```markdown
# CLAUDE.md -- automations (Workflow Automation)

## Scope
This repo owns automation definitions: n8n workflow exports, scheduled job scripts,
repo hygiene utilities, and the automation inventory.

This repo does NOT own: infrastructure provisioning, Odoo modules, application code.

## Rules
1. n8n workflow JSON must use credential references, never literal values
2. Every automation must be registered in inventory/inventory.json
3. Automation inventory must be validated in CI (all entries have required fields)
4. Scheduled jobs must document their cron schedule, owner, and dependencies
5. Repo hygiene scripts must be idempotent (safe to re-run)

## Conventions
- n8n workflows: n8n/workflows/<workflow-name>.json
- Scripts: scripts/<category>/<script-name>.sh
- Inventory: inventory/inventory.json (SSOT for all automations)
- Inventory schema: inventory/schema.json

## Validation Commands
  # Validate inventory
  python scripts/validate_inventory.py

  # Check n8n workflow JSON
  find n8n/ -name '*.json' | xargs python -m json.tool > /dev/null

  # Shellcheck for scripts
  find scripts/ -name '*.sh' | xargs shellcheck

## Dependencies
- Consumed by: n8n instance (imports workflow JSON)
- Depends on: odoo (Odoo XML-RPC for task creation), agents (MCP job definitions)
```

### A.6 CLAUDE.md for `web` (Web Applications)

```markdown
# CLAUDE.md -- web (Web Applications)

## Scope
This repo owns non-Odoo web applications: ops-console, active web UIs, and the
ops-primitives package that consumes design tokens.

This repo does NOT own: Odoo modules, infrastructure provisioning, agent definitions.

## Rules
1. Vercel is deprecated. Deployment target is Azure Container Apps.
2. Apps must have a health endpoint (GET /health returning 200)
3. Design tokens consumed from @ipai/design-tokens package
4. TypeScript required for all new code
5. Apps in apps/ must be listed in the app inventory (apps/README.md)
6. Dead/deprecated apps must be archived, not left in apps/

## Conventions
- Apps: apps/<app-name>/ (each with package.json, Dockerfile, README.md)
- Shared packages: packages/<package-name>/
- Design token consumption: import from @ipai/design-tokens

## Validation Commands
  # Build all apps
  npm run build --workspace=apps/<app-name>

  # Run tests
  npm test --workspace=apps/<app-name>

  # Lint
  npm run lint --workspace=apps/<app-name>

## Dependencies
- Consumed by: End users (via Front Door)
- Depends on: infra (deployment), design (tokens), agents (API for agent features)

## App Inventory
[Must be populated during Phase 2 audit]
| App | Status | Deployment | Purpose |
|-----|--------|-----------|---------|
| ops-console | Active | ACA | Operations dashboard |
| [other apps TBD] | | | |
```

---

## Appendix B: ADR Templates for Retroactive Documentation

The following ADRs should be created in Phase 1-2 to capture decisions currently living only in memory:

### ADR-0001 (infra): Azure Container Apps over DigitalOcean

```markdown
# ADR-0001: Azure Container Apps over DigitalOcean Droplets

**Status**: Accepted
**Date**: 2026-03-15
**Deciders**: Platform team

## Context
The platform was originally hosted on DigitalOcean droplets with self-managed
Docker and nginx. As the service count grew to 13+, managing containers on bare
VMs became operationally expensive: no automatic scaling, no managed TLS, no
WAF, manual deployment scripts.

## Decision
Migrate all services to Azure Container Apps (ACA) behind Azure Front Door.
Use managed PostgreSQL (Azure Database for PostgreSQL Flexible Server) instead
of self-managed PostgreSQL on droplets.

## Consequences
- Positive: Managed scaling, TLS, WAF, revision management, health checks
- Positive: No more SSH-based deployments or manual nginx config
- Positive: Native integration with Key Vault, ACR, Monitor
- Negative: Higher base cost than minimal DigitalOcean droplets
- Negative: Azure vendor dependency
- Negative: One exception: Supabase runs on a VM (no ACA option for self-hosted Supabase)
```

### ADR-0002 (infra): Keycloak as Transitional IdP to Entra ID

```markdown
# ADR-0002: Keycloak as Transitional IdP, Target Entra ID

**Status**: Accepted (transitional)
**Date**: 2026-03-15
**Deciders**: Platform team

## Context
The platform needs SSO across 6+ services (Odoo, Superset, Plane, n8n, CRM, Shelf).
Keycloak was deployed as a self-hosted IdP. Microsoft Entra ID is the target IdP
for Azure-native integration.

## Decision
Keep Keycloak operational until all migration gates pass:
1. OIDC/SAML parity with current Keycloak config
2. Group/role mapping for all services
3. Service-account replacement
4. Break-glass admin procedure
5. User provisioning automation
6. Per-app cutover (Odoo, Superset, Plane, n8n, Shelf, CRM)

Do NOT delete ipai-auth-dev until all gates pass.

## Consequences
- Positive: No disruption to current auth flows during migration
- Negative: Maintaining two IdP systems in parallel
- Negative: Risk of drift between Keycloak and Entra configurations
```

### ADR-0003 (data-intelligence): Databricks JDBC Extract over Supabase ETL

```markdown
# ADR-0003: Databricks JDBC Extract over Supabase ETL

**Status**: Accepted
**Date**: 2026-03-XX (retroactive, decision made ~2026-03)
**Deciders**: Data team

## Context
The data-intelligence needs to extract data from Odoo's PostgreSQL database into the
medallion architecture (Bronze > Silver > Gold > Platinum). Two approaches were
evaluated:
1. Supabase ETL (webhook-based replication)
2. Databricks JDBC extract (direct database read)

## Decision
Use Databricks JDBC extract. Supabase ETL is Private Alpha and not available
for self-hosted Supabase instances.

## Consequences
- Positive: Direct, reliable data extraction without intermediary
- Positive: Full control over extraction schedule and scope
- Negative: Requires JDBC connectivity from Databricks to Odoo PostgreSQL
- Negative: No real-time streaming (batch extracts only)
```

---

## Appendix C: Org-Level Scoring Rubric

For ongoing measurement of org health, use this rubric quarterly:

### Repo Governance Score (per repo, 0-100)

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| CLAUDE.md exists and is current | 15 | 15 = exists and <30 days old, 10 = exists, 0 = missing |
| README.md exists and is current | 10 | 10 = exists and accurate, 5 = exists but stale, 0 = missing |
| CODEOWNERS exists | 10 | 10 = exists and covers all paths, 5 = exists but incomplete, 0 = missing |
| CI pipeline exists and passes | 15 | 15 = required checks green, 10 = CI exists but some fail, 0 = no CI |
| docs/ exists with ADRs | 10 | 10 = ADRs current, 5 = docs exist but no ADRs, 0 = no docs |
| Spec bundles for in-progress work | 10 | 10 = all active work has specs, 5 = some work has specs, 0 = no specs |
| Evidence packs for deploys | 10 | 10 = last 3 deploys have evidence, 5 = some evidence, 0 = none |
| No stale branches (>30 days) | 5 | 5 = no stale branches, 3 = <5 stale, 0 = >5 stale |
| No secrets in code | 10 | 10 = gitleaks clean, 0 = secrets detected |
| Branch protection on main | 5 | 5 = required reviews + checks, 3 = partial, 0 = unprotected |

**Target**: All repos score >= 70 by end of Phase 4. All repos score >= 85 by end of Phase 8.

### Org-Wide Health Metrics

| Metric | Current | Target (Phase 4) | Target (Phase 8) |
|--------|---------|------------------|------------------|
| Repos with CLAUDE.md | 1/10 (10%) | 10/9 (100%) | 9/9 (100%) |
| Repos with CI | 2/10 (20%) | 9/9 (100%) | 9/9 (100%) |
| Repos with docs/ | 4/10 (40%) | 9/9 (100%) | 9/9 (100%) |
| Repos with CODEOWNERS | ~3/10 (30%) | 9/9 (100%) | 9/9 (100%) |
| Reusable workflows | 0 | 8+ | 10+ |
| Numbered ADRs | 0 | 15+ | 30+ |
| Operational runbooks | 0 | 4+ | 10+ |
| SSOT files with schemas | 0 | 3+ | 6+ |
| Design primitives implemented | 0 | 0 | 15+ |
| Average repo governance score | ~25 | >= 70 | >= 85 |

---

## Appendix D: Risk Register

| # | Risk | Probability | Impact | Mitigation | Owner |
|---|------|------------|--------|-----------|-------|
| R1 | Moving odoo/infra/ breaks CI pipelines | High | High | Update all workflow paths before move. Test in branch first. Keep symlinks temporarily. | Platform team |
| R2 | platform merge loses SSOT data | Low | High | Verify all SSOT files exist in infra before deleting platform | Platform team |
| R3 | Workflow extraction from odoo creates gaps | Medium | Medium | Keep original workflows alongside reusable versions during transition | Platform team |
| R4 | CLAUDE.md authoring takes longer than estimated | Medium | Low | Start with minimal CLAUDE.md (scope + rules + validation), expand later | All teams |
| R5 | Design primitive API shapes do not match Azure Resource Manager | Medium | Medium | Derive TypeScript types from ARM API response schemas | Frontend team |
| R6 | Team does not adopt new governance practices | Medium | High | Make governance checks blocking in CI. Automate what can be automated. | Platform team |
| R7 | Docs build pipeline is flaky | Low | Medium | Start with markdownlint only, add mkdocs build later | Platform team |
| R8 | Reusable workflows have version compatibility issues | Medium | Medium | Pin reusable workflow versions with tags | Platform team |
| R9 | Cross-repo moves cause import breakage | High | Medium | Update package.json/imports before or with the move. Test builds after. | All teams |
| R10 | ADR retroactive authoring captures wrong rationale | Low | Medium | Have original decision-makers review ADRs before accepting | All teams |

---

*End of review. This document is the SSOT for org refactoring decisions until superseded.*
