# Agent Production Reality

## Canonical position

Do not use generic market/blog statistics as the source of truth for agent performance.

Use:

- Microsoft Foundry official observability and evaluator guidance
- Primary public benchmarks (WebArena, GAIA, TheAgentCompany)
- Production evaluation lessons from major operators (Amazon)

---

## What current evidence says

Realistic long-horizon agents remain materially below human performance on public benchmarks:

| Benchmark | Agent | Human | Gap |
|-----------|-------|-------|-----|
| WebArena | 14.41% | 78.24% | 5.4x |
| GAIA | 15% | 92% | 6.1x |
| TheAgentCompany | ~30% | — | Top agent, consequential workplace tasks |

**Sources:**

- [WebArena (arXiv:2307.13854)](https://arxiv.gg/abs/2307.13854)
- [GAIA (arXiv:2311.12983)](https://www.sciencestack.ai/paper/2311.12983v1)
- [TheAgentCompany (arXiv:2412.14161)](https://arxiv.gg/abs/2412.14161)

**Implication:**

- Agents are useful assistants
- Agents are not broadly reliable autonomous workers
- Bounded workflows outperform open-ended autonomy
- "Mostly right" is not acceptable for compliance-bearing work

---

## Foundry production doctrine

Use **Discover → Protect → Govern**:

- **Discover** with pre-production evaluations and adversarial testing (AI red teaming via PyRIT)
- **Protect** with guardrails on input, tool call, tool response, and output (4 intervention points)
- **Govern** with tracing, monitoring, continuous evaluation, and alerts

**Source:** [Responsible AI for Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/responsible-use-of-ai-overview)

---

## Production metrics that matter

From [Foundry Agent Evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators):

- task completion
- task adherence
- intent resolution
- tool call accuracy
- tool selection
- tool input accuracy
- tool output utilization
- task navigation efficiency

From [Foundry Agent Monitoring Dashboard](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard):

- token usage
- latency
- run success rate
- evaluation scores on sampled traffic
- red teaming results

From [Amazon production eval lessons](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/):

- tool selection accuracy
- parameter accuracy
- multi-turn function-calling accuracy
- memory/context retrieval quality
- reasoning quality
- failure recovery
- human-in-the-loop review

---

## Operational interpretation

| Signal | Action |
|--------|--------|
| Run success rate < 95% | Investigate failed runs |
| Sustained latency > 10s | Investigate throttling, tool complexity, or network |
| Any critical compliance failure | Block release, escalate |
| Groundedness score < 0.90 | Do not deploy to production |
| Benchmark wins without production telemetry | Insufficient — not a release gate |

---

## TaxPulse-specific release stance

### v0.1 — Assisted review (first production target)

The agent should:

- Flag tax/compliance anomalies
- Explain the likely issue
- Cite the rule source or rule-pack logic
- Propose the next human action

The agent should **not**:

- Autonomously file, post, or finalize compliance decisions
- Generate tax rates from training data (must use grounded rule pack)
- Act without human confirmation on any consequence-bearing operation

### v0.2 — Suggested corrections

- Agent proposes correction with explanation
- Human explicitly approves before write
- Requires evaluation pass on tax accuracy (>= 0.90) and zero critical failures

### v0.3 — Bounded automation

- Agent corrects simple, well-defined cases (e.g., missing withholding on known vendor type)
- Full audit trail logged
- Requires benchmark pass + monitoring + human reviewer sign-off

### v1.0 — Filing support

- Agent prepares complete filing package
- Human files
- Requires full AvaTax benchmark pass + zero critical failures + continuous production monitoring

---

## Release gates

| Gate | Threshold |
|------|-----------|
| Task adherence | >= 0.85 |
| Groundedness | >= 0.90 |
| Custom tax accuracy | >= 0.90 |
| Critical safety/compliance failures | 0 |
| Production run success rate | >= 0.95 |
| Latency investigation trigger | > 10s sustained |

---

## What NOT to trust

- Blended "industry stats" like "average task completion is 75.3%"
- Generic blog claims about enterprise adoption percentages
- Cross-vendor benchmark tables without reproducible workload details
- Demo quality as proxy for production quality

These can be useful as color, but not as architecture or release-truth.

---

## Key principle

> **In production, agents should be judged by traced task outcomes on bounded workflows, not by demo quality or generic market success-rate claims.**

---

*Created: 2026-03-18*
*Sources: Microsoft Foundry docs, WebArena, GAIA, TheAgentCompany, Amazon ML blog*
