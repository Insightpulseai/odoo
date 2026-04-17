# agents/ Repo — Desired End State Audit

**Rev:** 2026-04-16
**Auditor:** Claude Explore agent
**Branch:** feat/ado-pulser-scrum-extension
**Topline grade:** **D (44/100) — FAILING**

---

## Canonical location declaration

`agents/` (inside monorepo `Insightpulseai/odoo`) is the definitive Pulser agent definition repository. Anchor: CLAUDE.md Cross-Repo Invariant #1 (Repo Map line 136: *"agents/ | Canonical agent/skill assets"*), reinforced in `docs/architecture/agent-orchestration-model.md` §1: *"agents/ = definitions (runtime-free). agent-platform/ = execution."*

**Core principle:** agents/ MUST remain runtime-free. Orchestration logic, supervisors, dispatchers, workflow state, tool execution belong in `agent-platform/` only.

---

## Directory inventory — current vs desired

Current: **51 directories + 18 root files**.

### KEEP (22 canonical) — runtime-free definitions
`capabilities/`, `ci/` (agent-validation scripts only), `claude/`, `docs/`, `evals/`, `judges/`, `knowledge/`, `library/`, `mcp/` (tool contracts/schemas ONLY), `passports/`, `personas/`, `policies/`, `prompts/`, `registry/`, `skills/`, `spec/`, `ssot/`, `tests/`, `.well-known/`, plus standard repo files (CLAUDE.md, README.md, LICENSE, CONTRIBUTING.md, .gitignore).

### MOVE → agent-platform/ (12 directories)
1. `ap-invoice-surface/` → `agent-platform/surfaces/`
2. `bank-recon-surface/` → `agent-platform/surfaces/`
3. `doc-intel-surface/` → `agent-platform/surfaces/`
4. `finance-close-surface/` → `agent-platform/surfaces/`
5. `foundry/` (runtime portions) → `agent-platform/runtime/foundry/` (keep specs/policies in place)
6. `mcp/coordinator/` → `agent-platform/runtime/mcp-coordinator/`
7. `docs-assistant/` → `agent-platform/surfaces/docs-assistant/`
8. `workflows/` → `agent-platform/orchestration/workflows/`
9. `commands-subagents/` (if runtime) → `agent-platform/`
10. `agent-samples/` (if scaffolding) → `agent-platform/samples/`
11. `studio/` → `agent-platform/dev-tools/` or `docs/`
12. `loops/` (if judge-loop impl) → `agent-platform/orchestration/judge-loop/`

### REMOVE (17 directories) — deprecated / consolidate
- `.venv/` (never commit virtualenvs; add to .gitignore)
- `antigravity/` (historical/exploratory)
- `knowledge-base/` (consolidate with `knowledge/`)
- `library-pack/` (consolidate with `library/`)
- `templates/` (consolidate into `prompts/` or `library/`)
- `third_party/` (move to `docs/references/` or `agent-platform/deps/`)
- `workflow-samples/` (consolidate into `evals/` or `docs/examples/`)
- Other legacy dirs requiring case-by-case review

---

## Boundary violations — detailed

### Violation 1: Runtime code in agents/
- `agents/mcp/coordinator/infra/do/mcp-coordinator.yaml` — full MCP server + DigitalOcean IaC
- **Fix:** Move coordinator → `agent-platform/runtime/mcp-coordinator/`. Keep `agents/mcp/` with **interface specs only**. Delete DigitalOcean IaC (doctrine violation #2 Azure-native).

### Violation 2: Deprecated platform references (613 occurrences across 157 files)

| Platform | Occurrences | Top offender |
|---|---|---|
| Supabase | 33 | `agents/registry/AGENT_SKILLS_REGISTRY.yaml` (15) |
| Odoo 19 / odoo-ce | 23 | `agents/skills/odoo/bir-eservices/SKILL.md` (6) |
| n8n | 23 | `agents/PRIORITIZED_ROADMAP.md` (10) |
| Vercel | 16 | `agents/PRIORITIZED_ROADMAP.md` (5) |
| DigitalOcean | 6 | `agents/mcp/coordinator/infra/do/mcp-coordinator.yaml` |
| Cloudflare / Wix / Mailgun / Mattermost | 5 | scattered |

**Zero cleanup in place. Grade: F.**

### Violation 3: Odoo version mismatch (CRITICAL)
`agents/skills/odoo/` references "Odoo 19" and "odoo-ce". CLAUDE.md #4 mandates **CE 18.0 only** for R2. Must change all refs to `ce-18.0`.

### Violation 4: Wrong IaC platform
`agents/mcp/coordinator/infra/do/mcp-coordinator.yaml` uses DigitalOcean Terraform. Violates Azure-native invariant. Delete; re-implement in `agent-platform` with Azure Bicep.

### Violation 5: Incomplete skill specs
~30% of skills missing `safe-output-decisions` or `evidence-contract` sections. Scrum Master SKILL.md is the reference standard; others should match.

### Violation 6: Agent Card presence inconsistent
`pulser_scrum_master` has Agent Card. `tax_guru`, `bank_recon`, judges: not verified. Cards MAY live with the ACA deployment in `agent-platform/`, but registration back to `agents/registry/` must be documented.

---

## CI validation gates — 2/5 present

| # | Gate | Status |
|---|---|---|
| 1 | Agent Card A2A v0.2.0 schema validation | **MISSING** |
| 2 | Boundary enforcement (runtime + deprecated grep) | **MISSING** |
| 3 | Skill spec completeness gate | **MISSING** |
| 4 | Integrated test runner (single CLI) | **MISSING** |
| 5 | Eval readiness gate | Partial (evals exist, no CI block) |

Existing: `scripts/validate_agents.py` — incomplete. Some `azure-pipelines/*.yml` exist but no dedicated `pulser-agent-interop-validate.yml`.

**CI coverage: 40%.**

---

## Scorecard

| Category | Score | Grade |
|---|---|---|
| Directory Conformance | 12/20 | D |
| Boundary Enforcement | 2/20 | F |
| Deprecated Platform Cleanup | 0/15 | F |
| Spec Contract Completeness | 17/20 | B |
| CI Validation Gates | 3/15 | D |
| Documentation | 10/10 | A |
| **OVERALL** | **44/100** | **D** |

---

## 4-Wave migration plan to reach A (100/100)

### Wave 1 — Boundary enforcement (Week 1–2)
Move 12 ACA app dirs + `mcp/coordinator/` + `workflows/` impl → `agent-platform/`.
**Effort:** 40–50h. **Risk:** high (large refactor).
**Exit:** Directory Conformance 18/20, Boundary Enforcement 10/20.

### Wave 2 — Deprecated platform cleanup (Week 3–4)
Remove/upgrade 613 deprecated refs. Priority: Supabase (33) → Odoo 19 (23) → n8n (23) → Vercel (16) → DigitalOcean (6).
**Effort:** 50–60h. **Risk:** medium (regex mistakes; peer review critical).
**Exit:** Boundary Enforcement 18/20, Deprecated Cleanup 15/15.

### Wave 3 — Spec contracts + CI gates (Week 5–7)
Finalize 30% incomplete SKILL.md; create 3 missing CI gates + integrated test runner.
**Effort:** 60–70h. **Risk:** low (additive).
**Exit:** Spec Completeness 20/20, CI Gates 15/15.

### Wave 4 — Documentation + final audit (Week 8–9)
`agents/STRUCTURE.md`, `agents/CI_GATES.md`, update CONTRIBUTING.md, final audit.
**Effort:** 20–30h. **Risk:** low.
**Exit:** 100/100 (A+).

**Total:** 170–210 hours, 9 weeks. Waves 2 + 3 can parallelize after Wave 1.
