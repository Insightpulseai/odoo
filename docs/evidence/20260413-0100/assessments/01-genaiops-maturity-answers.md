# GenAIOps Maturity Model Assessment — IPAI Answer Sheet

**URL:** https://learn.microsoft.com/en-us/assessments/e14e1e9f-d339-4d7e-b2bb-24f056cf08b6/
**Time:** 10 min (10 questions)
**Expected score:** 13-15 / 28 (Level 2: Defined, near L3 threshold)

---

## Pre-filled answers based on IPAI actual state

### Q1: LLM/Foundation Model Usage
**Answer:** We use foundation models in production applications
**Evidence:** `ipai-copilot-resource` runs Claude claude-sonnet-4-6 + GPT-4.1 via Azure AI Foundry. `foundry_service.py` (37K) handles model calls. Keyless MI auth deployed.

### Q2: Prompt Engineering Practices
**Answer:** We have structured prompt templates with role-based adaptation
**Evidence:** `SYSTEM_PROMPT` in `foundry_service.py` with 4 role levels (controller/approver/finance_ops/employee). 12 skill-to-tool mappings. Skill router classifies intent → picks skill → agent uses tools.

### Q3: Evaluation & Testing
**Answer:** We have evaluation frameworks and some automated eval runs
**Evidence:** 6 judge passports with rubric schemas. AP invoice eval: 4/4 PASS. Foundry copilot eval: 1.0 score. Red-team: 4 attacks blocked. But only 2/12 agents have production evals.

### Q4: CI/CD for LLM Applications
**Answer:** We have deployment pipelines but no automated prompt/eval CI
**Evidence:** `deploy-erp-canonical.yml` deploys containers. ADO pipelines for Odoo. No automated eval-on-prompt-change pipeline yet. Manual model deployment.

### Q5: Monitoring & Observability
**Answer:** We have basic telemetry but no GenAI-specific monitoring dashboard
**Evidence:** `ipai.copilot.telemetry` tracks latency/source/tool execution. `ipai.copilot.audit` tracks every interaction. Log Analytics workspace configured. No groundedness/relevance metrics in production.

### Q6: Content Safety & Responsible AI
**Answer:** We have guardrails and approval gates but no dedicated Content Safety resource
**Evidence:** `approval_mode="always_require"` on write tools. Constitution governs agent behavior (12 sections). Red-team evidence exists. WAF DefaultRuleSet. No Azure Content Safety resource deployed.

### Q7: Model/Prompt Version Management
**Answer:** We have agent maturity model but no formal prompt versioning
**Evidence:** L0-L5 maturity model in `agent_maturity_model.yaml`. Portfolio scorecard tracks 12 agents. Feature ship-readiness gates (5 gates). No prompt version tracking or A/B testing.

### Q8: Production Stability & Reliability
**Answer:** Some agents have production soak evidence, most do not
**Evidence:** AP invoice agent: 5-cycle soak, 95 bills, stability 1.0. Bank recon agent: 175 txns, 0 exceptions. Both L5. But 10/12 agents at L0-L1 with no soak evidence.

### Q9: Knowledge & Retrieval (RAG)
**Answer:** We have retrieval infrastructure deployed but not fully populated
**Evidence:** Azure AI Search (`srch-ipai-dev`) configured. PG MCP server live (451 tables). Doc Intelligence provisioned. `ipai_knowledge_bridge` module installed. AI Search index not yet populated.

### Q10: Continuous Improvement & Feedback
**Answer:** We have the architecture spec'd but no production implementation
**Evidence:** Self-improvement architecture designed (5-level maturity ladder: instrument → evaluate → optimize → train → RL). Judge infrastructure built (55+ assets). No replay, preference optimization, or feedback loops running.

---

## Score prediction

| Question | Likely points | Reasoning |
|----------|--------------|-----------|
| Q1 Model usage | 3/3 | Production use confirmed |
| Q2 Prompts | 2/3 | Structured but no optimization loop |
| Q3 Eval | 2/3 | Framework exists, sparse coverage |
| Q4 CI/CD | 1/3 | Deployment yes, eval CI no |
| Q5 Monitoring | 1/3 | Basic telemetry only |
| Q6 RAI | 2/3 | Guardrails yes, Content Safety no |
| Q7 Versioning | 1/3 | Maturity model yes, prompt versioning no |
| Q8 Stability | 2/3 | 2 agents at L5, rest untested |
| Q9 RAG | 1/3 | Infra deployed, index empty |
| Q10 Improvement | 1/3 | Spec'd, not implemented |
| **Total** | **~16/30** | **Level 2 (Defined)** |
