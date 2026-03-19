# Skill: Agentic SDLC — Microsoft Pattern

## Metadata

| Field | Value |
|-------|-------|
| **id** | `agentic-sdlc-msft-pattern` |
| **domain** | `sdlc` |
| **source** | https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896 |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, .github, infra, automations |
| **tags** | sdlc, spec-kit, coding-agent, sre, ci-cd, multi-agent |
| **framework_ref** | https://github.com/microsoft/agent-framework |

---

## Pattern Summary

5-phase closed loop: **Spec → Code → Quality → Deploy → Observe** → (back to Spec).

Each phase maps to a distinct agent or deterministic pipeline. The loop self-heals: SRE agents detect issues, create specs, trigger coding agents, which produce PRs that flow through quality gates and deploy automatically.

---

## Phase 1 — Spec-Driven Development

- **Entry**: Single user story or problem statement (natural language)
- **Tool**: Spec Kit (structured spec → plan → task breakdown)
- **Output**: Requirements + implementation plan + task list
- **Bridge**: Spec-to-issue tool → GitHub issue + auto-assign coding agent
- **Key principle**: Constitution file constrains agent behavior (tech stack, org standards, banned patterns)

### IPAI Mapping

| Concept | IPAI Implementation |
|---------|---------------------|
| Spec Kit | `/speckit.specify` slash command → `spec/` bundle |
| Constitution | `agents/foundry/agentic-sdlc-constitution.md` |
| Spec SSOT | Supabase `ops.specs` table |
| Issue bridge | GitHub Actions → `gh issue create` from spec tasks |

---

## Phase 2 — Coding Agent

- **Agent**: Autonomous code generation from scoped GitHub issue
- **Input**: GitHub issue with structured task (from Spec Kit)
- **Output**: Branch + PR + tests + screenshot evidence
- **Key principle**: Small, scoped tasks dramatically outperform open-ended prompts
- **Isolation**: Untrusted agent-generated code runs in sandboxed environments (ACA Dynamic Sessions)

### IPAI Mapping

| Concept | IPAI Implementation |
|---------|---------------------|
| Coding agent | Claude agents in `agents/` repo |
| Task input | Structured spec tasks as GitHub issues |
| PR output | Agent creates branch + PR with evidence |
| Sandbox | Azure Container Apps jobs (isolated revision) |

---

## Phase 3 — Code Quality Review

- **AI-assisted**: CodeQL + ESLint + AI PR summary
- **Metric**: 81% quality improvement rate (Qodo 2025 benchmark)
- **Metric**: 38.7% of AI review comments → actual code fixes
- **Principle**: Quality gate is deterministic — agents inform, CI decides

### IPAI Mapping

| Concept | IPAI Implementation |
|---------|---------------------|
| Quality gate | `.github/workflows/quality-gate.yml` (reusable) |
| CodeQL | GitHub Advanced Security (already enabled) |
| AI review | Claude Code PR review via `gh pr review` |
| Lint | Pre-commit hooks (ruff, eslint, xmllint) |

---

## Phase 4 — CI/CD (Deterministic, Not Agentic)

- **Principle**: CI/CD stays deterministic — agents invoke it, never the reverse
- **Deploy target**: Azure Container Apps (revision-based, zero-downtime)
- **Isolation**: ACA Dynamic Sessions for untrusted code execution
- **Preview**: PR → sandbox ACA revision URL for manual verification

### IPAI Mapping

| Concept | IPAI Implementation |
|---------|---------------------|
| CI pipeline | `.github/workflows/ci-odoo.yml` |
| Deploy | `.github/workflows/deploy-azure.yml` → ACA revision |
| Preview env | ACA revision per PR (planned) |
| Entry point | `infra/azure/modules/container-apps.bicep` |

---

## Phase 5 — SRE Agent (Day-2 Loop)

- **Continuously watches**: Logs, metrics, traces (Azure Monitor / OTLP)
- **Sub-agent pattern**: Primary SRE → GitHub sub-agent → creates issue → coding agent
- **Closes the loop**: Ops incident → spec → code → PR → review → merge → deploy
- **Key insight**: Sub-agents for narrow context tasks outperform one omnibus agent

### IPAI Mapping

| Concept | IPAI Implementation |
|---------|---------------------|
| SRE agent | `automations/` runbooks + `ops.run_events` in Supabase |
| Telemetry | Azure Monitor → `ops.platform_events` (append-only) |
| Incident → issue | n8n workflow → GitHub issue → coding agent |
| Sub-agents | `agents/subagents/` (devops-expert, git-expert, repo-expert) |

---

## Closed-Loop Execution Graph

```
problem-statement
  → ops.specs (Supabase SSOT)
  → GitHub issue (auto-created)
  → coding agent (PR)
  → quality gate (CI)
  → ACA deploy (infra/)
  → SRE agent observes
  → GitHub issue (ops incident)
  → ops.run_events (Supabase SSOT)
  → back to coding agent
```

---

## Key Principles (Preserve These)

1. **Spec Kit constitution = IPAI doctrine files** — constrains what agents can and cannot do
2. **Deterministic CI/CD is non-negotiable** even in fully agentic systems
3. **Human-in-the-loop at PR review**, not at every step
4. **Sub-agents for narrow tasks** > one omnibus agent
5. **ACA Dynamic Sessions = isolation boundary** for untrusted agent-generated code
6. **Small scoped tasks** dramatically outperform open-ended agent prompts
7. **Agents invoke pipelines**, pipelines never invoke agents autonomously

---

## Anti-Patterns (Avoid These)

1. Letting agents modify CI/CD pipelines directly
2. Open-ended "fix everything" prompts — always scope to a single issue
3. Skipping the quality gate for agent-generated code (it fails more often than human code)
4. Storing agent state in the agent itself — always externalize to Supabase `ops.*`
5. Running untrusted agent code without sandbox isolation
6. Treating AI PR review comments as authoritative — they inform, CI decides

---

## Microsoft Agent Framework Integration

The [microsoft/agent-framework](https://github.com/microsoft/agent-framework) (MIT, Python + .NET) provides:

| Capability | Status | IPAI Relevance |
|------------|--------|----------------|
| Graph-based workflows | Stable | Replace complex n8n reasoning chains |
| Multi-provider LLM | Stable | Claude as primary, Azure OpenAI fallback |
| Streaming + checkpointing | Stable | Wire to `ops.runs` / `ops.run_events` |
| Human-in-the-loop | Stable | PR review gates |
| Time-travel / replay | Stable | Debugging agent failures |
| OTLP observability | Stable | Azure Monitor integration |
| DevUI | Stable | Local agent debugging |

### Adoption path

- **Phase 1**: Local DevUI against existing Supabase `ops.*` schema
- **Phase 2**: Deploy as ACA alongside `ipai-odoo-dev-*` in `rg-ipai-dev`
- **Phase 3**: Migrate complex n8n reasoning chains to AF graph workflows

### Architecture fit

```
Agent Framework (orchestration — stateless executor)
        ↓ emits run events / artifacts
Supabase ops.* (SSOT / control plane)
        ↓ posts accounting artifacts
Odoo (SOR / ledger)
```

AF runs stateless. Supabase owns all checkpoint/event state. Odoo is the system of record for business transactions.

---

## Related Skills

- [spec-driven-development](../spec-driven-development/SKILL.md) — Phase 1 deep dive
- [sre-feedback-loop](../sre-feedback-loop/SKILL.md) — Phase 5 deep dive
