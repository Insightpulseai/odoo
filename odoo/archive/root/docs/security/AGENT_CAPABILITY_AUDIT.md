# Agent Capability Audit

**Audit Date**: 2026-03-18
**Auditor**: Claude Opus 4.6 (1M context)
**Repo**: Insightpulseai/odoo (main branch)
**Method**: Full filesystem scan of agents, tools, models, workflows, connectors, runtimes, and solution bundles

---

## 1. Executive Summary

The InsightPulse AI platform contains **73 distinct agent-related artifacts** spanning 10 categories. The platform is mid-migration from a fragmented multi-provider AI architecture (OpenAI direct, Gemini, Supabase LLM) to a consolidated **Microsoft Foundry** gateway model. Key findings:

- **1 canonical AI gateway**: `ipai_odoo_copilot` (Azure Foundry bridge) -- the single active AI module
- **7 deprecated AI modules**: Former direct-call modules (ipai_ai_widget, ipai_ask_ai_azure, ipai_ai_platform, ipai_llm_supabase_bridge, ipai_ai_channel_actions, ipai_ai_copilot, ipai_ai_oca_bridge) all set to `installable=False`
- **1 MCP coordinator**: FastAPI-based router at `agents/mcp/coordinator/` with A2A context propagation
- **1 n8n MCP bridge**: TypeScript client with 3 AI agent tools
- **1 RAG/docs-assistant**: Self-hosted answer engine using Anthropic Claude + OpenAI embeddings
- **~80 agent skills**: Mix of Odoo-specific, CLI-safe wrappers, and ported Anthropic skills
- **~70 n8n workflow definitions**: Finance, BIR compliance, GitHub ops, OCR, MCP bridge workflows
- **6 MCP servers configured** in `.mcp.json`: GitHub Copilot, Microsoft Learn, Azure, Figma, Supabase, Playwright
- **19 GitHub Actions workflows**: CI, CodeQL, deployment, SSOT validation guards
- **1 Azure DevOps pipeline**: 4-stage CI/CD (Lint, Build, Deploy Dev, Deploy Staging)
- **Mature SSOT governance**: `ssot/ai/` contains agents.yaml, models.yaml, tools.yaml, policies.yaml, prompts.yaml, sources.yaml, topics.yaml

**Top risks**: (1) docs-assistant has hardcoded Anthropic/OpenAI client initialization that violates the Foundry consolidation doctrine, (2) ops-console has stale Vercel/Google AI SDK dependencies, (3) nested `odoo/odoo/` directory contains full duplicate of agents/platform trees (orphaned), (4) several pyc files exist without source (eval, rag, agents scripts deleted but cache remains).

---

## 2. Audit Method

1. Filesystem scan via Glob patterns across all documented paths (packages/, apps/, agents/, mcp/, automations/, addons/ipai/, .claude/, .github/, ssot/, platform/)
2. Source file reads of `__manifest__.py` for all Odoo modules, `package.json` for Node apps, Python source for all agents/tools
3. YAML reads of all SSOT governance files under `ssot/ai/`, `ssot/governance/`, `ssot/platform/`
4. Cross-reference against CLAUDE.md, .claude/rules/, and ssot/governance/ai-consolidation-foundry.yaml

---

## 3. Capability Inventory Table

### 3.1 AI/Agent Modules (Odoo)

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 1 | ipai_odoo_copilot | agent | native_repo | self_hosted | insightpulseai_owned | full_control | core_runtime | managed_identity | read_only | prod | canonical |
| 2 | ipai_enterprise_bridge | connector | native_repo | self_hosted | insightpulseai_owned | full_control | core_runtime | managed_identity | bounded_write | prod | canonical |
| 3 | ipai_ai_copilot | agent | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |
| 4 | ipai_ai_widget | ui_surface | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |
| 5 | ipai_ask_ai_azure | ui_surface | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |
| 6 | ipai_ai_platform | connector | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |
| 7 | ipai_ai_channel_actions | agent | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |
| 8 | ipai_llm_supabase_bridge | connector | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | bounded_write | dev | legacy |
| 9 | ipai_workspace_core | solution | native_repo | self_hosted | insightpulseai_owned | full_control | important | managed_identity | bounded_write | prod | canonical |

### 3.2 MCP Servers & Coordinators

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 10 | MCP Coordinator | agent | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | metadata_only | dev | canonical |
| 11 | n8n API Bridge | tool | native_repo | repo_local | insightpulseai_owned | full_control | important | api_key | bounded_write | dev | canonical |
| 12 | GitHub MCP (Copilot) | tool | provider_managed | provider_hosted | github_owned | api_consumer_only | optional | oauth | read_only | shared | canonical |
| 13 | Microsoft Learn MCP | tool | provider_managed | provider_hosted | microsoft_owned | api_consumer_only | optional | none | read_only | shared | canonical |
| 14 | Azure MCP | tool | provider_managed | provider_hosted | microsoft_owned | api_consumer_only | important | managed_identity | admin_control | shared | canonical |
| 15 | Figma MCP | tool | provider_managed | provider_hosted | third_party_vendor_owned | api_consumer_only | optional | oauth | read_only | shared | canonical |
| 16 | Supabase MCP | tool | provider_managed | provider_hosted | third_party_vendor_owned | api_consumer_only | optional | api_key | full_write | shared | canonical |
| 17 | Playwright MCP | tool | provider_managed | local_only | third_party_vendor_owned | config_only | optional | none | no_data | dev | canonical |

### 3.3 AI Model Deployments

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 18 | GPT-4.1 (Azure OpenAI) | model | provider_managed | cloud_managed | microsoft_owned | config_only | core_runtime | managed_identity | no_data | prod | canonical |
| 19 | Claude 3 Sonnet (docs-assistant) | model | provider_managed | provider_hosted | anthropic_owned | api_consumer_only | experimental | api_key | no_data | dev | legacy |
| 20 | OpenAI Embeddings (docs-assistant) | model | provider_managed | provider_hosted | openai_owned | api_consumer_only | experimental | api_key | no_data | dev | legacy |
| 21 | Google AI SDK (ops-console) | model | provider_managed | provider_hosted | third_party_vendor_owned | api_consumer_only | experimental | api_key | no_data | dev | legacy |

### 3.4 Self-Hosted Services

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 22 | Docs Assistant API | agent | native_repo | self_hosted | insightpulseai_owned | full_control | experimental | api_key | read_only | dev | transitional |
| 23 | OCR Service | tool | native_repo | self_hosted | insightpulseai_owned | full_control | important | none | no_data | prod | canonical |
| 24 | Ops Console | ui_surface | native_repo | self_hosted | insightpulseai_owned | full_control | important | oauth | read_only | prod | canonical |

### 3.5 Agent Skills (agents/skills/)

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 25 | Odoo 19 skills (16 skills: ORM, QWeb, testing, etc.) | skill | native_repo | repo_local | insightpulseai_owned | full_control | important | none | no_data | dev | canonical |
| 26 | CLI-safe wrappers (odoo-cli-safe, github-cli-safe, azure-cli-safe) | skill | native_repo | repo_local | insightpulseai_owned | full_control | important | local_secret | bounded_write | dev | canonical |
| 27 | Business skills (finance-month-end, expense-processing, bir-tax-filing) | skill | native_repo | repo_local | insightpulseai_owned | full_control | important | none | no_data | dev | canonical |
| 28 | OdooOps skills (deploy, test, logs, status) | skill | native_repo | repo_local | insightpulseai_owned | full_control | aspirational | api_key | bounded_write | dev | reference_only |
| 29 | Marketplace skills (app-development, ecommerce, custom-web-design, etc.) | skill | native_repo | repo_local | insightpulseai_owned | full_control | aspirational | none | no_data | dev | reference_only |
| 30 | OCR bridge configure | skill | native_repo | repo_local | insightpulseai_owned | full_control | optional | none | no_data | dev | canonical |
| 31 | Deep research | skill | native_repo | repo_local | insightpulseai_owned | full_control | optional | none | no_data | dev | canonical |

### 3.6 n8n Workflows

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 32 | Finance workflows (8: BIR, month-end, PPM, expense OCR) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | bounded_write | prod | canonical |
| 33 | GitHub operations workflows (5: deploy, events, router) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | important | oauth | bounded_write | prod | canonical |
| 34 | Claude AI MCP workflows (10: read-only + write-path + test) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | experimental | api_key | bounded_write | dev | transitional |
| 35 | Control plane workflows (3: backup, deploy, health) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | bounded_write | prod | canonical |
| 36 | Integration workflows (6: asset, event, expense, finance handlers) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | bounded_write | prod | canonical |
| 37 | PPM Clarity workflows (4: bidirectional Plane-Odoo sync) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | bounded_write | prod | canonical |
| 38 | Notion monthly-close workflows (7: legacy Notion-era) | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | bounded_write | dev | legacy |
| 39 | Vercel drain handler | workflow | native_repo | self_hosted | insightpulseai_owned | full_control | deprecated | api_key | read_only | dev | legacy |

### 3.7 SuperClaude Framework (~/.claude/)

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 40 | SuperClaude agents (17: backend-architect, security-engineer, etc.) | prompt_pack | local_custom | local_only | insightpulseai_owned | full_control | optional | none | no_data | dev | canonical |
| 41 | SuperClaude commands (20+: analyze, build, deploy, etc.) | skill | local_custom | local_only | insightpulseai_owned | full_control | optional | none | no_data | dev | canonical |
| 42 | SuperClaude modes (7: Brainstorming, DeepResearch, etc.) | prompt_pack | local_custom | local_only | insightpulseai_owned | full_control | optional | none | no_data | dev | canonical |
| 43 | Design System Agent | agent | local_custom | local_only | insightpulseai_owned | full_control | experimental | none | no_data | dev | transitional |
| 44 | Universal Design Platform agents (10: Designer, Coder, Architect, etc.) | agent | local_custom | local_only | insightpulseai_owned | full_control | aspirational | none | no_data | dev | reference_only |

### 3.8 CI/CD Pipelines

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 45 | Azure DevOps CI/CD pipeline | runtime | native_repo | cloud_managed | insightpulseai_owned | full_control | core_runtime | managed_identity | bounded_write | prod | canonical |
| 46 | GitHub Actions (19 workflows) | runtime | native_repo | cloud_managed | insightpulseai_owned | full_control | core_runtime | oauth | bounded_write | shared | canonical |
| 47 | CodeQL analysis | tool | third_party | provider_hosted | github_owned | config_only | important | oauth | read_only | shared | canonical |

### 3.9 Docker/Runtime

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 48 | Devcontainer (Odoo) | runtime | native_repo | local_only | insightpulseai_owned | full_control | important | none | full_write | dev | canonical |
| 49 | MCP Coordinator container | runtime | native_repo | self_hosted | insightpulseai_owned | full_control | important | api_key | metadata_only | dev | canonical |
| 50 | Docs Assistant container | runtime | native_repo | self_hosted | insightpulseai_owned | full_control | experimental | api_key | read_only | dev | transitional |
| 51 | OCR service container | runtime | native_repo | self_hosted | insightpulseai_owned | full_control | important | none | no_data | prod | canonical |
| 52 | Odoo production container | runtime | native_repo | cloud_managed | insightpulseai_owned | full_control | core_runtime | managed_identity | full_write | prod | canonical |

### 3.10 SSOT Governance Artifacts

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 53 | ssot/ai/agents.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 54 | ssot/ai/models.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 55 | ssot/ai/tools.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 56 | ssot/ai/policies.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 57 | ssot/ai/prompts.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 58 | ssot/ai/sources.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 59 | ssot/governance/ai-consolidation-foundry.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | core_runtime | none | no_data | shared | canonical |
| 60 | ssot/platform/apps.manifest.yaml | other | native_repo | repo_local | insightpulseai_owned | full_control | important | none | no_data | shared | canonical |

### 3.11 Memory / Knowledge Systems

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 61 | .claude/project_memory.db | memory | native_repo | local_only | insightpulseai_owned | full_control | optional | none | metadata_only | dev | canonical |
| 62 | Azure AI Search index (srch-ipai-dev) | memory | native_repo | cloud_managed | insightpulseai_owned | config_only | important | managed_identity | read_only | prod | canonical |
| 63 | Supabase pgvector (docs-assistant) | memory | native_repo | self_hosted | insightpulseai_owned | full_control | experimental | api_key | read_only | dev | transitional |

### 3.12 External API Connectors

| # | Artifact | Type | Origin | Hosting | Ownership | Control | Criticality | Auth | Data Access | Env | Canonicality |
|---|----------|------|--------|---------|-----------|---------|-------------|------|------------|-----|-------------|
| 64 | Plane API client (agents/scripts/plane/) | connector | native_repo | repo_local | insightpulseai_owned | full_control | important | api_key | bounded_write | dev | canonical |
| 65 | Zoho SMTP (mail) | connector | native_repo | provider_hosted | third_party_vendor_owned | config_only | core_runtime | api_key | bounded_write | prod | canonical |

---

## 4. Native vs User-Generated vs Provider-Managed Breakdown

| Origin | Count | Examples |
|--------|-------|---------|
| **native_repo** | 48 | ipai_odoo_copilot, MCP coordinator, n8n workflows, CI/CD pipelines |
| **local_custom** | 4 | SuperClaude agents/commands/modes, Design System Agent |
| **provider_managed** | 10 | Azure MCP, GitHub MCP, GPT-4.1, Figma MCP, Supabase MCP |
| **third_party** | 1 | CodeQL |

---

## 5. Local vs Self-Hosted vs Provider-Hosted Breakdown

| Hosting | Count | Examples |
|---------|-------|---------|
| **repo_local** | 18 | Agent skills, SSOT YAML files, Plane API client |
| **local_only** | 6 | SuperClaude framework, project_memory.db, devcontainer |
| **self_hosted** | 14 | MCP coordinator, docs-assistant, n8n workflows, OCR service |
| **cloud_managed** | 7 | Azure DevOps, GitHub Actions, GPT-4.1, Odoo prod container, AI Search |
| **provider_hosted** | 10 | MCP servers (GitHub, Azure, Figma, Supabase), Claude/OpenAI APIs |
| **hybrid** | 0 | -- |

---

## 6. Canonical vs Transitional vs Legacy Breakdown

| Canonicality | Count | Notes |
|-------------|-------|-------|
| **canonical** | 42 | Active, documented, governed by SSOT |
| **transitional** | 4 | docs-assistant, Design System Agent, Claude AI MCP workflows, Supabase pgvector |
| **legacy** | 11 | 7 deprecated AI modules, Notion workflows, Vercel drain handler, legacy model refs |
| **reference_only** | 3 | OdooOps skills, marketplace skills, Universal Design Platform agents |
| **orphaned** | 3 | Nested odoo/odoo/ duplicate tree, stale pyc files without source |

---

## 7. Duplicate / Shadow / Orphan Report

### Duplicates
1. **`odoo/odoo/agents/`** -- Full copy of `agents/` tree exists at `odoo/odoo/agents/` (Dockerfiles, MCP coordinator, skills). This is a nested duplicate from a prior repo structure.
2. **`odoo/odoo/platform/`** -- Full copy of `platform/` tree (OCR service, runtime configs) duplicated at `odoo/odoo/platform/`.
3. **`odoo/odoo/web/`** -- Full copy of `web/` tree (control-room-api, ops-console) at `odoo/odoo/web/`.

### Orphans
4. **Stale `.pyc` files** without source at:
   - `agents/scripts/eval/__pycache__/corpus_retriever.cpython-311.pyc`
   - `agents/scripts/eval/__pycache__/audit_envelope.cpython-311.pyc`
   - `agents/scripts/rag/__pycache__/supabase_upsert.cpython-311.pyc`
   - `agents/scripts/rag/__pycache__/smoke_query.cpython-311.pyc`
   - `agents/scripts/agents/__pycache__/sync_agent_instructions.cpython-311.pyc`

   The source `.py` files have been deleted but compiled caches remain.

### Shadows
5. **`apps/org-docs-kb/`** -- Has a `__pycache__/service.cpython-311.pyc` but the source structure is unclear (no package.json or __manifest__.py found at expected location).

---

## 8. Security / Over-Permission Findings

1. **docs-assistant hardcodes client init**: `answer_engine.py` lines 60-61 initialize `openai.OpenAI()` and `Anthropic()` at module level. While keys are read from env, the direct provider clients violate the Foundry consolidation doctrine and create provider lock-in.

2. **MCP Coordinator API key is a single shared secret**: `verify_api_key()` in `main.py` compares against a single `coordinator_api_key` from settings. No per-client auth, no rate limiting per caller, no audit trail.

3. **Supabase MCP has `full_write` access**: The Supabase MCP server in `.mcp.json` uses `SUPABASE_ACCESS_TOKEN` which grants full write access to the Supabase project. This is broader than needed for read-only agent queries.

4. **Azure MCP has `admin_control` access**: The Azure MCP tool has access to all Azure resource management operations. No explicit scope restrictions are configured in `.mcp.json`.

5. **docs-assistant CORS is `allow_origins=["*"]`**: Line 41 of `answer_engine.py` allows all origins. Noted in code as "Configure for production" but not restricted.

6. **ops-console includes Vercel analytics**: `@vercel/analytics` and `@vercel/speed-insights` packages are still in dependencies despite Vercel being deprecated. These send telemetry to Vercel.

---

## 9. Provider Lock-In Findings

1. **Microsoft Foundry (HIGH -- accepted/strategic)**: The platform has deliberately chosen Microsoft Foundry as the single AI gateway. This is a strategic decision, not accidental lock-in. Model deployment (GPT-4.1), AI Search, managed identity, and Agent Framework are all Azure-native. Migration cost would be high.

2. **Anthropic/OpenAI direct (LOW -- being eliminated)**: The docs-assistant still uses direct Anthropic and OpenAI API calls. The Foundry consolidation plan (phase 2) explicitly targets eliminating these.

3. **GitHub Copilot MCP (MEDIUM)**: The `.mcp.json` points to `api.githubcopilot.com/mcp/` which is GitHub Copilot's hosted MCP. This creates a dependency on GitHub Copilot subscription.

4. **n8n (LOW)**: Self-hosted n8n with workflow JSON exported to repo. Portable to other automation platforms.

5. **Plane (LOW)**: API client is a thin HTTP wrapper. Easily replaceable.

---

## 10. Missing Documentation / Missing SSOT Findings

1. **No SSOT entry for docs-assistant**: `agents/docs-assistant/` has no corresponding SSOT YAML in `ssot/agents/` or `ssot/ai/`. It uses Anthropic Claude 3 Sonnet and OpenAI embeddings, which contradicts the Foundry consolidation doctrine.

2. **No SSOT entry for MCP coordinator**: `agents/mcp/coordinator/` has no corresponding SSOT YAML. The routing logic (MCPTarget enum, A2AContext) is defined in code but not documented in `ssot/`.

3. **No SSOT for SuperClaude framework**: The `~/.claude/agents/`, `~/.claude/commands/`, and `~/.claude/modes/` are user-local and have no repo-level SSOT governance.

4. **skills/ directory not in SSOT tree**: `agents/skills/` contains ~80 skills but no registry YAML in `ssot/`. Skills are documented only in individual SKILL.md files.

5. **ops-console AI dependencies undocumented**: `@ai-sdk/google`, `@google/generative-ai`, `openai`, and `ai` packages in ops-console's package.json are not reflected in `ssot/ai/models.yaml`.

6. **n8n workflow inventory stale**: `automations/automations-inventory.json` exists but the scan referenced in memory (commit f4f31af31) identified 42 stray workflows not in the canonical set.

---

## 11. Recommended Normalization Plan

### Phase 1: Cleanup (immediate)
1. Remove `odoo/odoo/` nested duplicate tree
2. Delete stale `.pyc` files under `agents/scripts/*/`
3. Remove `@vercel/analytics`, `@vercel/speed-insights` from ops-console dependencies
4. Remove `@ai-sdk/google`, `@google/generative-ai` from ops-console if unused

### Phase 2: SSOT Registration (1 week)
5. Create `ssot/agents/capability_inventory.yaml` (this audit generates the initial version)
6. Create SSOT entries for docs-assistant and MCP coordinator
7. Document SuperClaude framework usage in `ssot/agents/local_tools.yaml`
8. Create `ssot/agents/skill_registry.yaml` from agents/skills/ content

### Phase 3: Consolidation (2-4 weeks)
9. Migrate docs-assistant from Anthropic/OpenAI direct to Foundry (per ai-consolidation-foundry.yaml phase 2)
10. Restrict Supabase MCP token scope to read-only
11. Add per-client auth to MCP coordinator
12. Configure Azure MCP allowed operations

### Phase 4: Governance (ongoing)
13. Add CI guard for `ssot/agents/` YAML validity (like existing ssot-ai-validate.yml)
14. Add CI guard to prevent new direct model provider dependencies
15. Regular audit schedule (quarterly)

---

## 12. Proposed Machine-Readable SSOT Additions

See companion files:
- `ssot/agents/capability_inventory.yaml` -- Full inventory with classifications
- `ssot/agents/tool_registry.yaml` -- Tool-specific registry
- `ssot/agents/model_registry.yaml` -- Model provider registry
- `ssot/agents/runtime_registry.yaml` -- Runtime/container registry
- `ssot/agents/solution_registry.yaml` -- Solution bundle registry
