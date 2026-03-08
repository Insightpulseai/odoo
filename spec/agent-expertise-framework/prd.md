# Agent Expertise Framework — PRD

## Problem

Agent capability is currently undefined. There is no skill taxonomy, no progression path, no lab infrastructure, and no certification. This leads to:
- Uneven quality of agent-built artifacts
- No clear ownership of agent platform decisions
- No sandbox discipline (risk of production incidents)
- No way to assess readiness for agent-heavy workflows

## Users

| Persona | Level range | Primary need |
|---------|-------------|--------------|
| Business analyst | L0-L1 | Use agents safely, validate outputs |
| Developer | L1-L3 | Build and deploy agents |
| DevOps engineer | L1-L3 | Deploy, monitor, rollback agents |
| Platform engineer | L3-L4 | Build shared agent infrastructure |
| Solution architect | L4-L5 | Design multi-agent systems |
| Domain expert | L0-L5 | Apply agents to vertical problems |

## Requirements

### R1: Skills matrix

A matrix with 12 skill rows and 6 level columns (L0-L5).

Skill rows:
1. Prompting
2. Grounding / RAG
3. Tool calling
4. API / actions / plugins
5. Auth / identity
6. Orchestration
7. Evaluations
8. Observability
9. CI/CD
10. Domain modeling
11. Governance / compliance
12. Cost / performance

Each cell specifies: evidence required, lab required, reviewer required.

### R2: Role tracks (5)

1. Agent AI Engineer
2. Agent Developer
3. Agent DevOps
4. Agent Solution Architect
5. Agent Functional Consultant

### R3: Specialist schools (6)

1. Azure Agent School
2. Microsoft 365 / Copilot Agent School
3. Odoo / ERP Agent School
4. Platform Agent School
5. Delivery Agent School
6. Domain Agent School

### R4: Certification badges (6)

- IPAI Agent Operator (L1)
- IPAI Agent Builder (L2)
- IPAI Agent Platform Engineer (L3)
- IPAI Agent Architect (L4)
- IPAI ERP Agent Specialist (school)
- IPAI Copilot Agent Specialist (school)

### R5: Lab catalog (minimum 6 labs)

1. Azure OpenAI + AI Search retrieval lab
2. Slack approval agent lab
3. GitHub PR/issue agent lab
4. Odoo ask-AI lab
5. M365 Copilot/Graph sandbox lab
6. Evaluation/telemetry lab

### R6: Sandbox environments

- Azure dev subscription / resource group
- M365 developer sandbox (via Microsoft 365 Developer Program)
- Odoo dev database
- Supabase dev project
- GitHub non-prod environment

### R7: Assessment requirements (per level)

Each learner must ship:
- One bounded agent
- One integration
- One evaluation suite
- One deployment pipeline
- One incident postmortem simulation

### R8: Governance (L3+)

- Agent design review board
- Promotion standards
- Eval thresholds
- Runtime evidence pack
- Kill-switch/rollback pattern

## Success metrics

| Metric | Target |
|--------|--------|
| Skills matrix published | Phase 1 |
| Lab catalog with ≥6 labs | Phase 2 |
| Sandbox environments operational | Phase 3 |
| First L2 certification completed | Phase 4 |
| Governance board convened | Phase 5 |

## Non-goals

- External certification program (internal-first)
- Replacing Microsoft certifications (complementary, not competitive)
- Training everyone to L5 (most people operate at L0-L2)

## References

- [Microsoft Credentials Catalog](https://learn.microsoft.com/en-my/credentials/browse/?products=azure)
- [Microsoft 365 Developer Program](https://developer.microsoft.com/en-us/microsoft-365/dev-program)
- [Microsoft 365 Copilot APIs](https://devblogs.microsoft.com/microsoft365dev/microsoft-365-copilot-apis/)
- [Microsoft 365 Agents Toolkit](https://devblogs.microsoft.com/microsoft365dev/introducing-the-microsoft-365-agents-toolkit/)
