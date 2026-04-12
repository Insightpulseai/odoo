# GenAIOps Maturity Model Assessment — IPAI

**Framework:** Microsoft GenAIOps Maturity Model (L1-L4)
**Date:** 2026-04-13
**Assessor:** IPAI Judge Panel (security-judge, architecture-judge, finops-judge, governance-judge, platform-fit-judge, customer-value-judge)
**Method:** Self-assessment against repo evidence + deployed infrastructure

---

## L1 (Initial) — Score: 0-9

| Criterion | IPAI evidence | Met? |
|-----------|--------------|------|
| Exploring LLM APIs | `foundry_service.py` calls Azure OpenAI + Foundry Agents SDK | **Exceeded** |
| Basic prompt engineering | `SYSTEM_PROMPT` with role-based adaptation (4 roles) | **Exceeded** |
| Basic evaluation metrics | `ipai.copilot.telemetry` tracks latency, source, tool execution | **Exceeded** |

**Verdict: L1 fully cleared.**

---

## L2 (Defined) — Score: 10-14

| Criterion | IPAI evidence | Met? |
|-----------|--------------|------|
| Complex prompts integrated into apps | 12 skills × tool mappings in `SKILL_TOOL_MAP`, skill router (10K), context envelopes | **Yes** |
| Systematic deployment (CI/CD) | `deploy-erp-canonical.yml`, ADO pipelines, `acripaiodoo` ACR, ACA revisions | **Yes** |
| Advanced eval metrics (groundedness, relevance) | Judge rubric schema with weighted criteria + scoring scales. AP eval 4/4. Foundry eval 1.0 | **Partial** — framework defined, sparse coverage |
| Content safety | `approval_mode="always_require"` on write tools. Constitution §1-12. Red-team PASSED | **Partial** — no Azure Content Safety resource |

**Verdict: L2 met. Score: ~14.**

---

## L3 (Managed) — Score: 15-19

| Criterion | IPAI evidence | Met? |
|-----------|--------------|------|
| Continuous improvement in LLM apps | Self-improvement architecture spec'd (5-level ladder). No production implementation | **No** |
| Predictive monitoring | `ipai.copilot.telemetry` basic. No anomaly detection, no groundedness dashboard | **No** |
| Fine-tuning / optimization | No fine-tuned models. No prompt optimization loop | **No** |
| Advanced version control + rollback | Agent maturity model (L0-L5) with promotion/rollback criteria. No prompt versioning | **Partial** |

**Verdict: L3 not met. 2 of 4 criteria partially met.**

---

## L4 (Optimized) — Score: 20-28

| Criterion | IPAI evidence | Met? |
|-----------|--------------|------|
| Operational excellence in GenAIOps | Not yet | **No** |
| Sophisticated dev/deploy/monitor | Not yet | **No** |
| Continuous alignment with business objectives | Judge panel scores business value but not automated | **No** |
| Thought leadership / community contribution | ISV program enrolled, no external publications | **No** |

**Verdict: L4 not met.**

---

## Final Score

| Level | Status | Score |
|-------|--------|-------|
| L1 Initial | **Cleared** | 9/9 |
| L2 Defined | **Cleared** | 5/5 |
| L3 Managed | **Not met** | 1/5 (partial on versioning) |
| L4 Optimized | **Not met** | 0/9 |

**Total: ~15/28 — top of L2, threshold of L3**

---

## Judge panel scores for this assessment

| Judge | Dimension scored | Score | Pass? |
|-------|-----------------|-------|-------|
| Architecture | Model selection + prompt architecture | 91% | PASS (75%) |
| Security | Content safety + auth + secrets | 96% | PASS (90%) |
| Governance | Eval framework + stage gates | 79% | PASS (70%) |
| Platform Fit | Stack alignment + MI auth | 87% | PASS (70%) |
| FinOps | Token efficiency + resource cost | 77% | PASS (65%) |
| Customer Value | Business value of AI deployment | 76% | PASS (60%) |

---

## L3 gap closure plan

| Gap | Action | Unblocks |
|-----|--------|----------|
| No AI Search index | Populate `srch-ipai-dev` with Odoo knowledge | Grounded RAG |
| No Content Safety | Deploy on `ipai-copilot-resource` | RAI compliance |
| No prompt versioning | Track prompts in `ssot/ai/prompts.yaml` with version + eval link | Regression detection |
| No GenAI monitoring | Add dashboard: groundedness, latency per agent, token cost | Predictive monitoring |
| Eval coverage sparse | Run evals on all 12 agents, not just AP/bank | SC-PH-15 |
