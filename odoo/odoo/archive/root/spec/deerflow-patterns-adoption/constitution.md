# Constitution — DeerFlow Patterns Adoption
## spec/deerflow-patterns-adoption · Created 2026-03-02

---

## Purpose

Adopt ByteDance **deer-flow** architectural patterns to give every IPAI agent
(Pulser, FixBot, OpsAdvisor, and successors) a shared, observable, testable
execution harness.  The goal is **convergence, not rewrite**: transplant the
patterns that work, discard what doesn't fit Odoo/Supabase.

---

## Non-Negotiable Rules

| # | Rule | Rationale |
|---|------|-----------|
| 1 | **Skills are data, not code branches** | All agent capabilities are declared in `ssot/agents/skills.yaml` and stored in `ops.skills`; no `if skill == "X"` in runtime code. |
| 2 | **Every invocation produces a `run_id`** | Callers can always query `ops.runs` → `ops.run_events` → `ops.agent_errors` for full lineage. |
| 3 | **PLAN → PATCH → VERIFY → PR is the atomic state machine** | Agents may not skip states; each transition is logged as a `run_event`. |
| 4 | **Memory is scoped and queryable** | `ops.memory_entries` stores run-scoped, project-scoped, and org-scoped memory; no in-process globals. |
| 5 | **Failures have canonical codes** | `ssot/errors/failure_modes.yaml` defines every `AGENT.*` and `CI.*` failure code; runbooks live at `docs/runbooks/failures/<CODE>.md`. |
| 6 | **Benchmark scores are evidence** | `ops.agent_benchmark_results` records score per run; no agent is declared "production-ready" without ≥ 3 benchmark runs showing tier ≥ B. |
| 7 | **Supabase is the memory/event bus** | No Redis, no in-process caches for cross-run state; use `ops.memory_entries` and `ops.run_events`. |
| 8 | **Vercel Sandbox for patch/test loops; DO runner for heavy jobs** | Execution surface is declared per skill in `ssot/agents/skills.yaml`. |
| 9 | **No agent may call `service_role` directly from the browser** | Edge Functions hold service-role; Console forwards JWT only. |
| 10 | **Specs required before implementation** | Every new skill ≥ 50 lines of runtime code needs a spec bundle entry. |

---

## Out-of-Scope (Explicitly Excluded)

- LangGraph / LangChain adoption (not compatible with our Supabase-first stack)
- Anthropic Computer Use / browser automation (separate spec)
- Multi-tenant skill isolation (deferred to post-v1)
- Real-time streaming responses (deferred; current pattern is polling `ops.run_events`)
