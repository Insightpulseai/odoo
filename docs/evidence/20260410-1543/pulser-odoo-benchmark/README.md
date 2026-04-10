# Pulser for Odoo on Azure — Benchmark Recommendation

Date: 2026-04-10
Scope: Odoo 18 on Azure Container Apps + Azure Database for PostgreSQL + Microsoft Foundry / Azure OpenAI + Pulser Assistant (`ipai_odoo_copilot`)
Question: What is the correct benchmark for Odoo on Azure with Odoo Copilot (Pulser Assistant)?

## Executive conclusion

The correct benchmark is not a single number and not a generic public agent benchmark.

For Pulser on Odoo/Azure, use a **four-layer benchmark**:

1. **Product benchmark**: SAP Joule for the ERP copilot shell.
2. **Runtime benchmark**: Odoo on Azure SLOs for latency, success rate, and availability.
3. **Agent quality benchmark**: Foundry evaluation metrics plus repo safety thresholds.
4. **ERP capacity benchmark**: Odoo worker sizing and PostgreSQL concurrency on Azure.

If only one label is needed, the correct primary benchmark is:

> **SAP Joule for product behavior, plus Foundry/Azure metrics for release truth.**

That is the defensible benchmark frame for Pulser. It matches the repo doctrine and the current Microsoft platform guidance more closely than generic chatbots or public autonomous-agent leaderboards.

## Why this is the correct benchmark

### 1. Product benchmark: SAP Joule, not a generic chatbot

The repo already defines the target copilot shape as:
- informational
- navigational
- transactional, with approval-gated writes

Repo evidence:
- `docs/architecture/odoo/COPILOT_PRECURSOR.md` states that the core marketplace benchmark for Odoo Copilot is **SAP Joule**, with Notion 3.0 only as a secondary benchmark for agentic workspace behavior.
- `docs/architecture/odoo/ON_AZURE_TARGET_STATE.md` describes the Odoo Copilot benchmark model as informational, navigational, and transactional.

This is the right product benchmark because Joule is an enterprise copilot benchmark for ERP-adjacent work, not just a chat UX benchmark.

### 2. Runtime benchmark: Azure docs say judge by traced outcomes, latency, and success rate

Microsoft Foundry and Azure OpenAI documentation do not define success as a leaderboard score. They define it as:
- measured latency
- run success rate
- evaluation scores
- continuous evaluation
- production telemetry

Repo evidence:
- `docs/architecture/agents/PRODUCTION_REALITY.md` explicitly rejects generic market/blog statistics as release truth.
- `docs/architecture/agents/AGENTOPS_DOCTRINE.md` defines evaluation-gated deployment and per-surface metrics.

Microsoft evidence:
- Foundry monitoring guidance says **latency above 10 seconds** warrants investigation and **run success rate below 95%** warrants investigation.
- Azure OpenAI performance guidance says throughput must be measured in **TPM and RPM**, not only per-call latency.

### 3. ERP capacity benchmark: Odoo itself gives the baseline worker math

Odoo’s official deployment guidance provides the production worker heuristic:
- `(#CPU * 2) + 1` workers
- `1 worker ~= 6 concurrent users`
- heavy worker RAM estimate around `1 GB`
- light worker RAM estimate around `150 MB`

This means the Odoo runtime benchmark must include worker and database capacity, not just copilot model latency.

### 4. Release truth must be composite

Pulser is not only:
- an ERP web app
- an agent
- or an LLM deployment

It is all three at once. So the benchmark must cover:
- user-facing response time
- ERP throughput
- AI quality
- safety and approvals
- auditability

Anything narrower is the wrong benchmark.

## Recommended benchmark stack

## A. Product benchmark

Primary:
- **SAP Joule**

Secondary:
- **Notion 3.0** for multi-step knowledge-work patterns only

Do not use as primary benchmark:
- generic consumer chat assistants
- WebArena / GAIA / TheAgentCompany
- demo-quality copilots with no release telemetry

Reason:
- public agent benchmarks are useful as research context, but they are not the release truth for bounded ERP workflows
- repo doctrine already rejects them as production authority

## B. Runtime and SLO benchmark

### Recommended production-facing targets

These targets combine direct repo policy with current Azure platform guidance.

#### Advisory chat flows
- **Streaming time-to-first-response (p95): <= 2 seconds**
- **End-to-end answer latency (p95): <= 5 seconds**
- **Error rate: < 1%**
- **Run success rate: >= 95%**

#### Approval-gated proposal/action flows
- **End-to-end proposal latency (p95): <= 10 seconds**
- **Unauthorized write rate: 0**
- **Approval bypass rate: 0**

#### Release-stage requirements
- `internal_beta`: eval pass + manual approval
- `limited_ga`: SLO met for 7 days
- `ga`: SLO met for 30 days

Direct repo basis:
- `spec/pulser-odoo/prd.md`: finance Q&A latency `< 5 seconds p95`
- `docs/architecture/agents/AGENTOPS_DOCTRINE.md`: response latency `< 5s advisory`, `< 10s action`, error rate `< 1%`

Direct Microsoft basis:
- Foundry monitoring: latency `> 10 seconds` indicates investigation threshold
- Foundry monitoring: run success rate `< 95%` warrants investigation
- Azure OpenAI: for streaming workloads, **time to response** is the recommended responsiveness metric

### Interpretation

The repo’s `< 5s p95` advisory target is defensible and should stay.

The missing refinement is that Pulser should benchmark **streaming TTFR** separately from **full response latency**. Azure explicitly recommends this distinction.

## C. Agent quality and safety benchmark

Use Foundry evaluators plus the repo’s stricter release thresholds.

### Minimum benchmark dimensions

System evaluation:
- task completion
- task adherence
- intent resolution

Process evaluation:
- tool call accuracy
- tool selection
- tool input accuracy
- tool output utilization
- tool call success

Pulser-specific safety:
- groundedness / citation accuracy
- RBAC enforcement
- prompt injection resistance
- privilege escalation resistance
- data exfiltration resistance
- advisory-mode enforcement
- action confirmation enforcement

### Recommended thresholds

Adopt the repo thresholds as the release truth:
- task adherence `>= 0.90`
- citation coverage `>= 0.90`
- citation accuracy `>= 0.95`
- context awareness `>= 0.95`
- refusal correctness `>= 0.95`
- hallucination rate `<= 0.05`
- PII leakage `= 0`
- prompt injection resistance `= 1.00`
- privilege escalation resistance `= 1.00`
- data exfiltration resistance `= 1.00`
- RBAC enforcement `= 1.00`
- advisory-mode enforcement `= 1.00`

Source of release truth in repo:
- `agents/evals/odoo-copilot/thresholds.yaml`
- `agents/evals/odoo-copilot/rubric.md`

Important correction:
- the latest recorded Odoo Copilot evaluation uses only **30 cases**
- the rubric target for Advisory Release is **150+ cases**

So the correct benchmark is **not yet “30/30 passed”**.
The correct benchmark is:

> pass the full 150+ case advisory dataset under the thresholds above, then maintain continuous evaluation in production.

## D. Odoo and Azure infrastructure benchmark

### Odoo app tier

Official Odoo production guidance:
- workers = `(#CPU * 2) + 1`
- `1 worker ~= 6 concurrent users`
- use proxy mode and route `/websocket/` correctly for live chat / websocket worker

Implication for Pulser:
- benchmark Odoo web runtime separately from Foundry latency
- benchmark with realistic concurrent ERP usage, not only isolated copilot calls

### Azure Container Apps

For ingress-exposed production apps, Microsoft recommends:
- **at least three replicas** for availability
- minimum always-ready replicas to reduce cold starts
- health probes
- autoscaling that can still meet the SLO under high load

Implication:
- a single-replica Odoo web container is not the correct production benchmark target
- benchmark web ingress and worker paths under at least a 3-replica availability posture if Pulser is treated as a production surface

### PostgreSQL

Microsoft guidance for PostgreSQL Flexible Server says:
- Burstable is for low-cost dev / low concurrency
- General Purpose or Memory Optimized is for production high concurrency and predictable performance
- built-in **PgBouncer** is available
- zone-redundant HA provides warm standby with synchronous replication and zero data loss on failover

Implication:
- the correct production benchmark for Pulser is **not** Burstable PG
- benchmark against **General Purpose + PgBouncer + HA** if the target is production or serious internal beta

## E. Azure OpenAI / Foundry throughput benchmark

### Benchmark by TPM and RPM, not only by “requests per second”

Azure’s performance guidance is explicit:
- system throughput must be measured in **tokens per minute**
- per-call latency alone is insufficient
- quota does not directly equal achieved throughput
- large `max_tokens` and mixed workloads increase latency

### Operational benchmark rules

For Pulser:
- separate advisory chat workloads from heavier review/extraction workloads
- keep `max_tokens` as low as practical
- stream user-facing chat responses
- measure:
  - calls per minute
  - prompt TPM
  - completion TPM
  - TTFR
  - full response p95

### Standard vs PTU

Use this split:
- **Pilot / internal beta**: Standard or Global/DataZone Standard is acceptable
- **Latency-critical / sustained high-volume / finance-critical GA**: benchmark against **PTU**

Reason:
- Microsoft says Standard tiers can show materially higher latency variability under sustained or bursty usage
- PTU is the recommended choice for latency-critical and mission-critical workloads

## Practical benchmark target for Pulser

This is the recommended benchmark card for the next real release gate.

### Product
- Benchmark shell behavior primarily against **SAP Joule**
- Benchmark knowledge-work augmentation secondarily against **Notion 3.0**

### User-facing performance
- TTFR p95 `<= 2s`
- advisory full response p95 `<= 5s`
- proposal/action p95 `<= 10s`
- error rate `< 1%`
- run success `>= 95%`

### Agent quality
- task adherence `>= 0.90`
- groundedness / citation accuracy `>= 0.95`
- citation coverage `>= 0.90`
- context awareness `>= 0.95`

### Safety
- PII leaks `0`
- unauthorized writes `0`
- prompt injection success `0`
- RBAC bypass `0`
- privilege escalation success `0`

### Data and audit
- audit coverage `100%` of interactions
- trace coverage `100%` of tool-executed actions
- continuous evaluation enabled on production traffic

### Odoo runtime
- worker count sized per Odoo formula
- benchmark concurrent ERP users and copilot requests together
- 3+ web replicas for ingress-exposed production posture
- PostgreSQL Flexible Server General Purpose or Memory Optimized
- PgBouncer enabled

### OpenAI / Foundry runtime
- benchmark in TPM/RPM, not only latency
- separate deployments by workload shape
- PTU target for latency-critical GA

## What is not the correct benchmark

Not sufficient on its own:
- “30/30 eval pass”
- “it feels fast”
- WebArena / GAIA / TheAgentCompany scores
- raw Azure OpenAI latency with no Odoo load
- Odoo throughput with no agent evals
- SAP on Azure architecture compliance with no copilot safety gates

## Recommendation

The correct benchmark for **Odoo on Azure with Pulser Assistant** is:

> **SAP Joule as the product benchmark, enforced by a composite Azure release benchmark consisting of Odoo p95 latency, Foundry evaluator thresholds, zero-bypass safety gates, and Azure OpenAI TPM/RPM sizing.**

In practice, the release gate should be:

1. pass the full 150+ case Odoo Copilot eval pack
2. meet `<= 5s` advisory p95 and `<= 10s` action p95
3. maintain `>= 95%` run success and `< 1%` error rate
4. show zero unauthorized writes / PII leaks / RBAC bypasses
5. prove Odoo worker + PostgreSQL capacity under concurrent ERP load

## Sources

### Repo sources
- `spec/pulser-odoo/prd.md`
- `spec/pulser-odoo/plan.md`
- `spec/pulser-odoo-ph/prd.md`
- `agents/evals/odoo-copilot/thresholds.yaml`
- `agents/evals/odoo-copilot/rubric.md`
- `agents/evals/odoo-copilot/LATEST.md`
- `docs/architecture/agents/AGENTOPS_DOCTRINE.md`
- `docs/architecture/agents/PRODUCTION_REALITY.md`
- `docs/architecture/odoo/COPILOT_PRECURSOR.md`
- `docs/architecture/odoo/ON_AZURE_TARGET_STATE.md`
- `docs/architecture/agents/BENCHMARK_SAP_JOULE.md`

### Official external sources
- Microsoft Learn: Azure OpenAI performance and latency
  - https://learn.microsoft.com/azure/ai-foundry/openai/how-to/latency
- Microsoft Learn: Azure OpenAI quotas and limits
  - https://learn.microsoft.com/azure/foundry/openai/quotas-limits
- Microsoft Learn: Monitor agents with the Agent Monitoring Dashboard
  - https://learn.microsoft.com/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard
- Microsoft Learn: Evaluate your AI agents
  - https://learn.microsoft.com/azure/foundry/observability/how-to/evaluate-agent
- Microsoft Learn: Agent evaluators
  - https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- Microsoft Learn: Azure Container Apps architecture best practices
  - https://learn.microsoft.com/azure/well-architected/service-guides/azure-container-apps
- Microsoft Learn: Set scaling rules in Azure Container Apps
  - https://learn.microsoft.com/azure/container-apps/scale-app
- Microsoft Learn: Azure Database for PostgreSQL overview
  - https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-compare-single-server-flexible-server
- Microsoft Learn: Monitor query requests in Azure AI Search
  - https://learn.microsoft.com/azure/search/search-monitor-queries
- Odoo 18 docs: system configuration / deployment
  - https://www.odoo.com/documentation/18.0/administration/on_premise/deploy.html
- SAP official: Joule
  - https://www.sap.com/products/artificial-intelligence/ai-assistant.html

## Verification notes

- Azure and Odoo sources were checked live on 2026-04-10.
- The recommendation above distinguishes:
  - **directly sourced platform guidance**
  - **repo-defined release thresholds**
  - **inferred benchmark synthesis**
