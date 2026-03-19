# Learning Measurement Model — Agent Guided Learning Paths

> Defines learning levels, persona lanes, OKRs, KPIs, assessment evidence,
> and promotion/readiness gates for the AI agent learning paths program.
>
> Cross-references:
>   - `ssot/governance/azdo-execution-hierarchy.yaml` (OBJ-003/FEAT-003-03)
>   - `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md` (agent architecture)
>   - `ssot/governance/enterprise_okrs.yaml` (operational OKRs)

---

## 1. Learning Levels

Progressive competency model for building and operating AI agents on the
InsightPulse AI platform.

| Level | Name | Description | Prerequisite |
|-------|------|-------------|-------------|
| L0 | **Observer** | Understands what agents do, can use existing agents via chat | None |
| L1 | **Practitioner** | Can configure existing agents (prompts, tools, guardrails) | L0 |
| L2 | **Builder** | Can create new agents using Foundry project + builder factory | L1 |
| L3 | **Architect** | Can design multi-agent systems, tool chains, and orchestration | L2 |
| L4 | **Operator** | Can deploy, monitor, troubleshoot, and govern agents in production | L3 |

### Level Progression Timeline

| Transition | Estimated Duration | Key Activity |
|-----------|-------------------|-------------|
| L0 → L1 | 1 week | Complete guided learning path 1 |
| L1 → L2 | 2 weeks | Build and deploy first custom agent |
| L2 → L3 | 4 weeks | Design and implement multi-agent workflow |
| L3 → L4 | 4 weeks | Operate agents in production with evidence |

---

## 2. Persona Lanes

Each persona follows a tailored path through the levels based on their role.

### Platform Operator

**Target level**: L4 (Operator)
**Focus**: Deployment, monitoring, governance, incident response

| Level | Focus Areas |
|-------|------------|
| L0 | Understand agent architecture, Foundry console navigation |
| L1 | Configure guardrails, manage model deployments, review traces |
| L2 | Create operational agents (monitoring, alerting, runbook execution) |
| L3 | Design agent-to-agent handoff patterns, tool authorization boundaries |
| L4 | Production deployment, App Insights monitoring, incident playbooks |

### Developer

**Target level**: L3 (Architect)
**Focus**: Agent building, tool implementation, integration

| Level | Focus Areas |
|-------|------------|
| L0 | Use ipai-odoo-copilot-azure for code assistance |
| L1 | Configure agent prompts, add/remove tools, adjust parameters |
| L2 | Build custom agents with Odoo tool integration (FastAPI endpoints) |
| L3 | Design multi-agent architectures, implement MCP tool layer |

### Business User

**Target level**: L1 (Practitioner)
**Focus**: Agent usage, prompt engineering, result interpretation

| Level | Focus Areas |
|-------|------------|
| L0 | Interact with copilot in Odoo, understand advisory vs transactional modes |
| L1 | Craft effective prompts, use preset configurations, interpret agent responses |

---

## 3. OKRs / KPIs

### Objective: Establish Agent Competency Across Platform Team

**Key Results**:

| KR | Metric | Target | Timeline |
|----|--------|--------|----------|
| KR-1 | Platform operator reaches L4 | 1 person | Q2 2026 |
| KR-2 | Developer reaches L3 | 1 person | Q3 2026 |
| KR-3 | Guided learning paths published | 3 paths | Q2 2026 |
| KR-4 | Custom agents deployed to production | 2 agents | Q3 2026 |
| KR-5 | Agent-related incidents resolved within SLA | 100% | Ongoing |

### KPIs (Operational)

| KPI | Definition | Target | Measurement |
|-----|-----------|--------|-------------|
| Path completion rate | % of started paths completed | ≥80% | Learning path tracker |
| Time to first agent | Days from L0 to first deployed agent | ≤21 days | Git commit history |
| Agent success rate | % of agent invocations returning useful result | ≥90% | App Insights |
| Agent error rate | % of agent invocations failing | <5% | App Insights |
| Guardrail trigger rate | % of invocations hitting content safety | <2% | Foundry metrics |
| Mean time to resolve | Avg time to resolve agent-related incidents | <4 hours | Incident log |

---

## 4. Assessment Evidence

Each level transition requires concrete evidence, not self-assessment.

### L0 → L1 Evidence

| Evidence | Format | Location |
|----------|--------|----------|
| Completed learning path 1 | Checklist + screenshots | `docs/evidence/<stamp>/learning/` |
| Configured 1 agent parameter change | PR diff | GitHub PR |
| Explained agent architecture in own words | Written summary | Learning log |

### L1 → L2 Evidence

| Evidence | Format | Location |
|----------|--------|----------|
| Completed learning path 2 | Checklist + screenshots | `docs/evidence/<stamp>/learning/` |
| Created new agent in Foundry | Agent spec + deployment evidence | Foundry project + PR |
| Agent passes basic evaluation | Evaluation results | Foundry evaluations |
| Documented agent purpose and constraints | Agent README | `spec/<agent-name>/` |

### L2 → L3 Evidence

| Evidence | Format | Location |
|----------|--------|----------|
| Completed learning path 3 | Checklist + screenshots | `docs/evidence/<stamp>/learning/` |
| Designed multi-agent workflow | Architecture diagram + spec | `spec/<workflow>/` |
| Implemented 2+ MCP tools | Code + tests | PR + CI evidence |
| Conducted agent evaluation (systematic) | Evaluation report | `docs/evidence/<stamp>/evaluation/` |

### L3 → L4 Evidence

| Evidence | Format | Location |
|----------|--------|----------|
| Deployed agent to production | Deployment evidence | `docs/evidence/<stamp>/deploy/` |
| Configured monitoring + alerting | App Insights + alerts | Azure portal screenshot + IaC |
| Resolved 1 agent-related incident | Incident report | `docs/evidence/<stamp>/incident/` |
| Documented operational runbook | Runbook | `docs/runbooks/<agent>/` |

---

## 5. Promotion / Readiness Gates

### Gate Criteria

| Gate | Assessor | Method | Pass Criteria |
|------|----------|--------|--------------|
| L0 → L1 | Self + peer | Evidence review | All L0→L1 evidence present |
| L1 → L2 | Engineering lead | Evidence review + code review | All L1→L2 evidence present, agent functional |
| L2 → L3 | Platform lead | Architecture review | Multi-agent design reviewed and approved |
| L3 → L4 | Platform lead | Production readiness review | Production deployment + monitoring + incident resolution proven |

### Readiness Checklist (L4 — Production Operator)

- [ ] Can deploy agents via AzDo pipeline (no manual portal steps)
- [ ] Can diagnose agent failures using App Insights traces
- [ ] Can modify guardrails in response to content safety incidents
- [ ] Can rotate agent credentials via Key Vault
- [ ] Can explain agent cost model and optimize token usage
- [ ] Has documented operational runbook for at least 1 production agent
- [ ] Has resolved at least 1 agent-related incident with evidence

---

## 6. Guided Learning Paths

### Path 1: Agent Fundamentals (L0 → L1)

| Module | Topic | Duration |
|--------|-------|----------|
| 1.1 | What are AI agents? Architecture overview | 1 hour |
| 1.2 | Azure AI Foundry console walkthrough | 1 hour |
| 1.3 | Using ipai-odoo-copilot-azure (hands-on) | 2 hours |
| 1.4 | Configuring agent parameters and guardrails | 2 hours |
| 1.5 | Assessment: Configure and test a parameter change | 1 hour |

### Path 2: Agent Building (L1 → L2)

| Module | Topic | Duration |
|--------|-------|----------|
| 2.1 | Agent design patterns and tool architecture | 2 hours |
| 2.2 | Creating an agent in Foundry (step-by-step) | 3 hours |
| 2.3 | Building MCP tools for Odoo integration | 4 hours |
| 2.4 | Testing and evaluating agents | 2 hours |
| 2.5 | Assessment: Build and deploy a custom agent | 4 hours |

### Path 3: Multi-Agent Architecture (L2 → L3)

| Module | Topic | Duration |
|--------|-------|----------|
| 3.1 | Multi-agent patterns (router, chain, parallel) | 2 hours |
| 3.2 | Tool authorization and security boundaries | 2 hours |
| 3.3 | Agent-to-agent communication protocols | 3 hours |
| 3.4 | Monitoring multi-agent workflows | 2 hours |
| 3.5 | Assessment: Design and implement a multi-agent workflow | 6 hours |

---

*Last updated: 2026-03-17*
