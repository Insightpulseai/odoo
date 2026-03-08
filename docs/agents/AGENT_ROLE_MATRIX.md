# Agent Role Matrix

> Skills x Levels x Tracks — the complete competency grid.

## Skills matrix

| Skill | L0 User | L1 Operator | L2 Builder | L3 Platform Eng | L4 Architect | L5 Fellow |
|-------|---------|-------------|------------|-----------------|--------------|-----------|
| **Prompting** | Uses templates | Adapts prompts | Designs system prompts | Prompt architecture | Prompt governance | Prompt standards |
| **Grounding / RAG** | — | Understands sources | Builds retrieval | Multi-source RAG | Cross-domain grounding | Grounding standards |
| **Tool calling** | — | Uses predefined tools | Designs tool schemas | Tool orchestration | Tool governance | Tool standards |
| **API / actions / plugins** | — | Calls existing APIs | Builds API actions | Plugin frameworks | API governance | API standards |
| **Auth / identity** | Uses SSO | Understands RBAC | Implements auth | Identity platform | Identity architecture | Identity standards |
| **Orchestration** | — | — | Single-agent flows | Multi-agent orchestration | Business process orchestration | Orchestration standards |
| **Evaluations** | Reviews outputs | Validates artifacts | Writes eval suites | Eval frameworks | Eval governance | Eval standards |
| **Observability** | — | Reads dashboards | Adds telemetry | Observability platform | Observability architecture | Observability standards |
| **CI/CD** | — | Runs pipelines | Adds agent CI | Agent CD platform | Deployment governance | CD standards |
| **Domain modeling** | Uses domain terms | Maps workflows | Models domain agents | Domain frameworks | Cross-domain architecture | Domain standards |
| **Governance / compliance** | Follows policies | Flags risks | Implements controls | Governance tooling | Governance architecture | Governance standards |
| **Cost / performance** | — | Reports costs | Optimizes agents | Cost platform | Cost architecture | Cost standards |

## Evidence requirements per level

| Level | Evidence | Lab | Reviewer |
|-------|---------|-----|----------|
| L0 | Completed agent runbook usage log | — | Self-check |
| L1 | Supervised agent execution with artifact review | 1 guided lab | L2+ reviewer |
| L2 | Shipped agent with tests + telemetry | 2 labs | L3+ reviewer |
| L3 | Shipped shared framework/SDK | 3 labs + platform contribution | L4+ reviewer |
| L4 | Architecture design doc + governance review | All labs in track | L5 reviewer or board |
| L5 | Published standards + curriculum + peer review | Cross-track labs | External review or board |

## Track x skill priority

| Skill | AI Engineer | Developer | DevOps | Architect | Functional |
|-------|------------|-----------|--------|-----------|------------|
| Prompting | **Critical** | High | Medium | High | **Critical** |
| Grounding / RAG | **Critical** | High | Low | High | Medium |
| Tool calling | **Critical** | **Critical** | Medium | High | Low |
| API / actions / plugins | High | **Critical** | Medium | High | Low |
| Auth / identity | Medium | High | **Critical** | **Critical** | Low |
| Orchestration | High | Medium | Medium | **Critical** | Medium |
| Evaluations | **Critical** | High | Medium | High | Medium |
| Observability | Medium | Medium | **Critical** | High | Low |
| CI/CD | Medium | High | **Critical** | High | Low |
| Domain modeling | Medium | Medium | Low | **Critical** | **Critical** |
| Governance / compliance | Medium | Medium | High | **Critical** | **Critical** |
| Cost / performance | Medium | Medium | **Critical** | **Critical** | Medium |

**Critical** = must demonstrate mastery at L2+ in this track.
**High** = must demonstrate competency at L2+ in this track.
**Medium** = awareness required, depth optional.
**Low** = not required for this track.

## School x track alignment

| School | Primary tracks | Secondary tracks |
|--------|---------------|-----------------|
| Azure Agent School | AI Engineer, DevOps | Architect |
| M365 / Copilot Agent School | Developer, AI Engineer | Functional |
| Odoo / ERP Agent School | Functional, Developer | Architect |
| Platform Agent School | DevOps, AI Engineer | Architect |
| Delivery Agent School | DevOps | Developer |
| Domain Agent School | Functional | Architect |
