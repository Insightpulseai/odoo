# Pulser Scrum Master — Current State Audit

**Rev:** 2026-04-16
**Auditor:** Claude Explore agent
**Branch:** feat/ado-pulser-scrum-extension
**Topline grade:** **65/100 — SCAFFOLDED (ready for integration tests, blocked on 3 items)**

---

## Executive summary

Spec and design **100% complete**. Code scaffold + infrastructure **50% complete**. Control & approvals **missing** (blocks production release). Ready for integration testing once Blockers 1 + 3 clear. Cannot ship to production until Blocker 1 (human-gate) is implemented.

---

## 10-Axis readiness assessment

| # | Axis | Status | Score | Evidence |
|---|---|---|---|---|
| 1 | Skill specification | ✅ COMPLETE | 20/20 | `agents/skills/scrum_master/SKILL.md` — 439 lines, 6 patterns, safe-action L1-L4, evidence contract, cadence, success metrics |
| 2 | Agent Card (A2A v0.2.0) | ✅ COMPLETE | 20/20 | `agents/pulser-scrum-master/.well-known/agent-card.json` — validates spec, 4 skills, OAuth2 auth |
| 3 | Interop matrix entry | ✅ COMPLETE | 20/20 | `ssot/governance/agent-interop-matrix.yaml` — role=specialist_worker, invoked_by=[supervisor], dispatches=[], MCP tools scoped |
| 4 | Doctrine compliance | ✅ COMPLETE | 20/20 | Three-protocol ✅, supervisor-mediated ✅, stateless ✅, two-mode ✅, Azure-native ✅, R2 baseline gpt-4.1 ✅ |
| 5 | Research documentation | ✅ COMPLETE | 20/20 | `docs/research/ado-pulser-scrum-extension.md` (248 lines) + addendum-a2a (146 lines) + appendix.json — all design decisions locked |
| 6 | Code & client | 🟡 SCAFFOLDED | 10/20 | Agent Card + SKILL.md done; ACA app + ADO extension + MCP clients partial |
| 7 | Infrastructure & deployment | 🟡 PARTIAL | 10/20 | Entra Agent ID + KV + ACA running; Bicep IaC + Foundry config + staging blockers |
| 8 | Evaluation suite | 🟡 PARTIAL | 10/20 | 50 golden scenarios + 3 judges specified; implementation + CI gate partial |
| 9 | Observability & operations | 🟡 PARTIAL | 8/20 | Evidence artifacts + App Insights events defined; dashboards + runbook missing |
| 10 | Control & approvals | ❌ MISSING | 0/20 | L2-L4 human-gate not implemented; BLOCKS production release |
| | **OVERALL** | **SCAFFOLDED** | **65/100** | |

---

## Detail per axis

### 1. Skill spec (20/20)
SKILL.md covers:
- 6 operational patterns (daily standup, weekly velocity, sprint retro, doctrine drift, orphan/stale triage, 9-area-path enforcement)
- Safe-action contract L1 auto / L2 propose / L3 human / L4 human-mass
- Evidence contract — artifacts to `docs/evidence/<YYYYMMDD-HHMM>/scrum-<type>/` (run.log, output.md, query.sql, artifacts.json, drift-violations.csv, safe-output-decisions.json)
- Cadence: daily 09:00 Asia/Manila standup, weekly Mon velocity, manual retro, daily 10:00 drift, hourly triage
- Success metrics: sprint on-time %, orphan lifetime <48h, drift caught >95%, SLA 100%, retro actions >70% closed

### 2. Agent Card (20/20)
A2A v0.2.0 compliant. 4 skills (standup, velocity, retro, drift). OAuth2 with Entra issuer + tokenUrl. Protocol version pinned. Example invocations included.

### 3. Interop matrix entry (20/20)
- role: specialist_worker (correct)
- backing_model: prod=foundry/gpt-4.1, dev=foundry-local/phi-4
- identity: mi-pulser-scrum-agent in kv-ipai-dev-sea
- mcp_tools: [mcp/ado-rest, mcp/foundry-gpt-4.1, mcp/key-vault-proxy, mcp/app-insights]
- m365_surface: n/a (ADO extension goes direct)
- invoked_by: [pulser_supervisor] — no peer paths
- dispatches: [] — correct for worker

### 4. Doctrine compliance (20/20)
Three protocols aligned, supervisor-mediated, stateless (envelope-in/envelope-out, no carryover), two modes, Azure-native only, R2 gpt-4.1, Safe Outputs referenced.

### 5. Research documentation (20/20)
Main doc sections A-F complete. Addendum §7 corrects peer-delegation → orchestrator-mediated. Appendix.json pins deps (azure-devops-extension-sdk@4.0.2, azure-devops-ui@2.259.0, tfx-cli@0.21.1).

### 6. Code & client (10/20)
**Complete:** Agent Card JSON, SKILL.md, research docs.
**Partial:** `apps/pulser-scrum-agent/` ACA app — referenced in Agent Card URL but full integration test not verified. ADO extension vss-extension.json + npm deps not verified. `a2aClient.ts` rename status unclear. MCP tool clients unclear.
**Not started:** `safe_output_filter.py`, Content Safety MCP integration.

### 7. Infrastructure (10/20)
**Complete:** Entra Agent ID provisioned, KV scoped, ACA container running (Agent Card URL reachable), Azure Pipelines CI referenced.
**Partial:** Bicep IaC "agentCardUrl output" referenced but not verified. FOUNDRY_BACKING_MODE env var not verified. APIM GenAI Gateway staging unclear. Memory #5364 — PostgreSQL Flex + cross-sub MI role pending.
**Not complete:** Prod scaling config, monitoring/alerting, DR.

### 8. Evaluation (10/20)
**Complete:** 50 golden scenarios (20 standup/10 velocity/10 retro/10 drift), 3 judges (accuracy/safety/helpfulness) with rubrics, CI gate logic spec, Batch API 50% discount, baseline-per-release-tag policy.
**Partial:** PII scrubber impl status unclear. Judges in interop matrix but eval pipeline integration not verified. No single-CLI test runner. No metric dashboard.
**Not complete:** Live staging eval run, regression detection automation.

### 9. Observability (8/20)
**Complete:** Evidence artifact structure, App Insights event taxonomy (pulser.scrum.hub.viewed, pulser.scrum.worker.run, pulser.scrum.write.proposed, pulser.scrum.write.blocked), safe-output decision logging.
**Partial:** Kill-switch KV flag referenced but runtime check not verified. Runbook not found in docs/. Performance dashboard not verified. Synthetic tests not found.
**Not complete:** Distributed tracing spans, cost tracking, SLA dashboard.

### 10. Control & approvals (0/20)
**Not found:** control.approvals envelope/handoff, L2/L3/L4 escalation, approval-request API to ADO approvals, manager routing logic.
**Implication:** Scrum Master is scoped to **L1 auto-exec only** (post markdown, tag items). Cannot reparent or close WI without manual intervention. **Blocks production merge.**

---

## Top 3 blockers to reach VERIFIED

### BLOCKER 1 (CRITICAL): control.approvals infrastructure missing
- **Impact:** Cannot execute L2 (reparent) or L3 (close) actions without human gate. Scoped to L1 only.
- **Dependency:** agent-platform orchestration team — approval-request envelope + handoff contract integration + manager routing in `agent-platform/orchestration/approvals/`.
- **Effort:** 40-60 hours, 2-3 sprints.

### BLOCKER 2 (HIGH): Evaluation suite CI gate not wired
- **Impact:** No automated gate blocking merge on eval score drop. 50 golden scenarios defined, not integrated.
- **Missing:** `scripts/test_scrum_master_evals.sh`, `azure-pipelines/pulser-scrum-eval.yml`, metric regression detection.
- **Dependency:** Judges as A2A servers + orchestrator integration.
- **Effort:** 50-60 hours (30-40h orchestrator + 20h CI + dashboard).

### BLOCKER 3 (MEDIUM): Staging infrastructure incomplete
- **Impact:** Cannot run full integration test. ACA app up but cannot reach Foundry cloud (MI role missing) or Odoo ERP DB (PostgreSQL Flex not ready).
- **Dependency:** Azure infrastructure team — MI federation + cross-sub role assignment + PG Flex provisioning + VNet.
- **Effort:** 30-40 hours, 1-2 sprints.

---

## Verdict

- Spec and design: **100% complete**
- Code scaffold + infrastructure: **~50% complete**
- Control & approvals: **missing — blocks production release**
- **Ready for integration testing** once Blockers 1 + 3 clear
- **Cannot ship to production** until Blocker 1 resolves

## Anchors

- `agents/skills/scrum_master/SKILL.md`
- `agents/pulser-scrum-master/.well-known/agent-card.json`
- `ssot/governance/agent-interop-matrix.yaml` (v2)
- `docs/research/ado-pulser-scrum-extension.md` + `.addendum-a2a.md` + `.appendix.json`
- `docs/architecture/agent-orchestration-model.md`
- `docs/architecture/three-protocol-model.md`
- Memory: `project_r2_model_baseline_20260415.md`, `feedback_supervisor_mediated_orchestration_20260415.md`, `feedback_two_operating_modes_20260415.md`, `feedback_no_custom_branding_for_pulser_odoo_20260415.md`
