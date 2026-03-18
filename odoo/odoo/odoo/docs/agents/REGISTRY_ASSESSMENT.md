# Agent Registry Framework Assessment

**Date:** 2026-02-20
**Status:** DRAFT
**Scope:** Agent orchestration, skills/tools binding, knowledge base integration

---

## Executive Summary

This assessment evaluates the current agent registry framework across three dimensions:
1. **Agent Orchestration:** Routing, delegation, fallbacks, run lifecycle
2. **Skills/Tools Binding:** Capability model, tool contracts, permissions, secrets
3. **Knowledge Base Integration:** RAG sources, indexing, provenance, drift controls

**Key Findings:**
- ✅ **Strengths:** Spec Kit bundle model provides structured governance; Supabase SSOT enables centralized run/event tracking
- ⚠️ **Gaps:** No machine-readable agent registry; tool permissions not formally declared; knowledge source drift not monitored
- 🔴 **Risks:** Non-deterministic agent selection; unclear tool secret handling; RAG index staleness

**Recommendation:** Implement formal registry schema with CI validation gates and audit trail enforcement.

---

## 1. Current State Architecture

### 1.1 Discovered Components

**Agent Registry Artifacts:**
```
.specify/                          # Spec Kit state
├── templates/                     # Spec bundle scaffolding
└── memory/                        # Session context (transient)

spec/                              # Spec bundles (governance layer)
├── odoo-ee-parity-seed/
│   ├── constitution.md            # Invariants + boundaries
│   ├── prd.md                     # Functional requirements
│   ├── plan.md                    # Implementation phases
│   └── tasks.md                   # DoD-style tasks
└── odoo-sh/
    └── [similar structure]

scripts/                           # No formal agent registry scripts found
web/ai-control-plane/             # Platform Kit integration layer
```

**Tool Binding Points:**
- Supabase Edge Functions (`/supabase/functions/`)
- Platform Kit routes (`web/ai-control-plane/app/api/`)
- No formal tool capability schema discovered

**Knowledge Sources:**
- Drive, Notion, Slack integrations referenced in docs
- No centralized indexing strategy discovered
- No provenance/drift tracking found

### 1.2 Agent Types Inventory

**Identified Personas/Modes** (from project memory):
- Analyzer, Architect, Frontend, Backend, Security
- Performance, QA, Refactorer, DevOps, Mentor, Scribe
- Orchestrator, Task Manager, Introspection modes

**Registry Storage:** Not found (likely implicit in Claude Code system prompts + CLAUDE.md)

### 1.3 Skills Catalog

**Discovered Skills** (from `.claude/skills/`):
- composition-patterns, creative-web-manual, design-system-cli
- meta-analysis-pipeline, notion-code, odoboo-workspace
- react-best-practices, web-design-guidelines, ui-ux-pro-max
- Spec Kit commands (specify, plan, implement, tasks, etc.)

**Binding Mechanism:** Skill-specific SKILL.md frontmatter + trigger keywords

**Permissions Model:** Not explicitly declared (inferred from allowed-tools lists)

### 1.4 Knowledge Base Connectors

**Integration Points:**
- Notion MCP (via @notion-developer skills)
- Google Drive (referenced but no formal connector found)
- Slack (ipai_slack_connector module)

**Indexing Strategy:** Not discovered (likely ad-hoc per integration)

**Provenance Tracking:** Not implemented

---

## 2. Gap Analysis

### 2.1 Orchestration Gaps

| **Capability** | **Current State** | **Gap** | **Risk** |
|---------------|-------------------|---------|----------|
| Agent routing | Implicit (system prompts) | No machine-readable routing rules | Non-deterministic selection |
| Delegation | Manual via Task tool | No formal delegation policy | Unclear fallback behavior |
| Run lifecycle | Supabase ops.runs/run_events | No agent_id foreign key | Unclear agent→run lineage |
| Fallbacks | Not discovered | No fallback chains defined | Single point of failure |

**Critical Gap:** Agent selection relies on natural language system prompts, making routing non-deterministic and difficult to audit.

### 2.2 Tools Binding Gaps

| **Capability** | **Current State** | **Gap** | **Risk** |
|---------------|-------------------|---------|----------|
| Tool capabilities | Implicit in tool descriptions | No formal capability model | Unclear tool→task matching |
| Permissions | RLS for Supabase, not for tools | No tool permission schema | Privilege escalation risk |
| Secret handling | Vault + env vars (good) | No tool→secret binding map | Secret leakage potential |
| Scopes | User-scoped vs service-scoped | Not formally declared per tool | Unclear authorization |

**Critical Gap:** Tools (Edge Functions, routes) lack formal capability declarations and permission scopes, making security audits manual.

### 2.3 Knowledge Base Gaps

| **Capability** | **Current State** | **Gap** | **Risk** |
|---------------|-------------------|---------|----------|
| RAG sources | Notion, Drive, Slack (scattered) | No centralized source registry | Unclear coverage |
| Indexing | Likely per-integration | No unified embedding strategy | Inconsistent retrieval quality |
| Provenance | Not discovered | No source→response tracing | Hallucination risk |
| Drift detection | Not implemented | No staleness monitoring | Outdated retrieval results |

**Critical Gap:** Knowledge sources lack provenance tracking and drift detection, making it impossible to validate retrieval quality.

---

## 3. Recommended Target Model

### 3.1 Registry Schema Components

**Proposed Layers:**
1. **Agent Registry** (agents.yaml)
   - Agent types, capabilities, routing rules, delegation policies
2. **Tool Registry** (tools.yaml)
   - Tool capabilities, permission scopes, secret bindings, rate limits
3. **Knowledge Registry** (knowledge.yaml)
   - Source types, indexing strategies, provenance schemas, refresh cadences

### 3.2 SSOT/SOR Alignment

**Supabase SSOT:**
- Agent registry metadata (types, capabilities)
- Run lifecycle (ops.runs, ops.run_events with agent_id FK)
- Tool execution audit (ops.tool_invocations)
- Knowledge source metadata (sources, last_indexed_at, embedding_model)

**Odoo SOR:**
- None (agent orchestration is operational control-plane, not ERP record-keeping)

**Conflict Policy:**
- Agent registry owns orchestration; Odoo irrelevant for this domain

### 3.3 Policy Gates

**CI Validation:**
- Schema validation for agent/tool/knowledge registries
- Baseline tolerance for existing unregistered agents/tools
- Drift detection for knowledge source freshness

**Runtime Enforcement:**
- Agent selection must emit correlation_id + agent_id to ops.runs
- Tool execution must check permission scopes before execution
- Knowledge retrieval must log provenance (source_id, chunk_id, confidence)

---

## 4. Migration Strategy

### Phase 1: Discovery + Baseline (Week 1-2)
**Deliverables:**
- Complete inventory of existing agents, tools, knowledge sources
- Baseline tolerance file for unregistered items (grandfathered)
- Registry schema definitions (YAML + JSON Schema)

### Phase 2: Schema Implementation (Week 3-4)
**Deliverables:**
- agents.yaml, tools.yaml, knowledge.yaml in repo root
- CI validation scripts for schema compliance
- Migration guide for registering new agents/tools/sources

### Phase 3: Runtime Integration (Week 5-8)
**Deliverables:**
- ops.runs/run_events enhanced with agent_id FK
- ops.tool_invocations table for audit trail
- ops.knowledge_sources table for provenance tracking
- Evidence artifacts for all agent/tool executions

### Phase 4: Governance Hardening (Week 9-12)
**Deliverables:**
- CI gates enforce schema compliance (no exceptions)
- Monthly registry review (first Monday)
- Automated staleness alerts for knowledge sources
- Security audit for tool permissions

---

## 5. Open Questions

**Agent Orchestration:**
- [ ] How are agent routing rules currently encoded? (System prompts? Code?)
- [ ] What fallback behavior is expected when primary agent fails?
- [ ] Should agent delegation be explicit (registry-defined) or implicit (LLM-based)?

**Tools Binding:**
- [ ] Which tools require service_role vs user-scoped permissions?
- [ ] Are there tool rate limits or quota requirements?
- [ ] How are tool secrets rotated? (Manual vs automated)

**Knowledge Base:**
- [ ] Which embedding model is canonical for RAG? (OpenAI, local, Supabase)
- [ ] What is acceptable staleness for different knowledge sources? (Drive: 24h, Notion: 1h?)
- [ ] Should knowledge retrieval be cached? (If so, where? Supabase? Redis?)

---

## 6. Success Metrics

**Target State (3 months):**
- ✅ 100% of agents registered in agents.yaml
- ✅ 100% of tools declared in tools.yaml with permission scopes
- ✅ 100% of knowledge sources tracked in knowledge.yaml
- ✅ 100% of agent executions emit agent_id to ops.runs
- ✅ 100% of tool executions logged to ops.tool_invocations
- ✅ 100% of knowledge retrievals include provenance (source_id, confidence)
- ✅ Zero unregistered agents/tools/sources in new code (CI enforced)
- ✅ <24h knowledge source staleness for critical sources (Drive, Notion)

**Measurement:**
- Weekly CI reports on registry compliance
- Monthly security audits for tool permissions
- Quarterly knowledge freshness reports

---

## 7. Cross-References

- **Complete taxonomy:** `docs/agents/REGISTRY_SCHEMA.md` (proposed)
- **Spec Kit bundle:** `spec/agent-registry/` (proposed)
- **SSOT policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article: Supabase SSOT)
- **Tool contracts:** TBD (no formal contracts discovered yet)
- **Knowledge provenance:** TBD (not implemented yet)
