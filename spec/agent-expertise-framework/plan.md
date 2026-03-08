# Agent Expertise Framework — Plan

## Phase 1: Capability framework (Week 1-2)

### Deliverables
- `docs/agents/AGENT_EXPERTISE_FRAMEWORK.md` — master overview
- `docs/agents/AGENT_ROLE_MATRIX.md` — skills x levels x tracks
- `docs/agents/AGENT_CERTIFICATION_PATHS.md` — badge requirements

### Tasks
- Define 12-skill x 6-level matrix with evidence/lab/reviewer cells
- Map 5 role tracks to skill priorities
- Map 6 specialist schools to curriculum outlines
- Define 6 certification badge requirements
- Publish to docs/agents/

## Phase 2: Labs (Week 3-4)

### Deliverables
- Lab specifications for >=6 applied labs
- Lab templates with success criteria

### Labs
1. **Azure OpenAI + AI Search** — build retrieval-backed Q&A agent
2. **Slack approval agent** — build approval workflow with Slack integration
3. **GitHub PR/issue agent** — build PR summarizer using GitHub API
4. **Odoo ask-AI** — build Odoo expense or invoice copilot
5. **M365 Copilot/Graph sandbox** — build Copilot agent grounded in org documents
6. **Evaluation/telemetry** — deploy agent with observability and rollback

### Success criteria
- Each lab has: objective, prerequisites, steps, deliverable, evaluation rubric
- Each lab can be completed in <=4 hours

## Phase 3: Sandboxes (Week 5-6)

### Deliverables
- Sandbox environment provisioning runbooks
- Environment access controls

### Environments
- Azure dev subscription / resource group
- M365 developer sandbox (Microsoft 365 Developer Program enrollment)
- Odoo dev database (`odoo_dev`)
- Supabase dev project
- GitHub non-prod environment (environment protection rules)

### Success criteria
- Each sandbox is isolated from production/shared-live-sandbox
- Each sandbox has documented teardown procedure

## Phase 4: Assessments (Week 7-8)

### Deliverables
- Assessment rubrics for L1-L4
- First L2 certification completed

### Assessment requirements (per candidate)
- Ship one bounded agent
- Ship one integration
- Ship one evaluation suite
- Ship one deployment pipeline
- Complete one incident postmortem simulation

### Success criteria
- At least one person certified at L2
- Assessment rubric reviewed and approved

## Phase 5: Governance (Week 9-10)

### Deliverables
- Agent design review board charter
- Promotion standards document
- Runtime evidence pack template

### Governance components
- Agent design review board (convened)
- Eval thresholds (documented per agent type)
- Kill-switch/rollback pattern (standardized)
- Cost control policy (budget per agent per environment)

### Success criteria
- Review board has met at least once
- One agent has passed full governance review

## Dependencies

| Phase | Depends on |
|-------|-----------|
| Phase 2 (Labs) | Phase 1 (Framework) |
| Phase 3 (Sandboxes) | Independent |
| Phase 4 (Assessments) | Phase 1 + Phase 2 + Phase 3 |
| Phase 5 (Governance) | Phase 1 |
