# Pulser 8-Plane Capability Matrix

> Maps current Azure AI Foundry inventory to the 8-plane production model.
> Status: PASS / PARTIAL / MISSING per plane.
> Last updated: 2026-04-11

---

## Summary

| # | Plane | Status | Coverage |
|---|-------|--------|----------|
| 1 | Data Plane | PARTIAL | Odoo/PG live, backup active, no document lake |
| 2 | Document Pipeline | PARTIAL | DI API available, no wired pipeline |
| 3 | LLM Application Layer | PARTIAL | Models deployed, prompt/grounding contract not enforced |
| 4 | Decision / Policy Layer | PARTIAL | Rules YAML written, Foundry guardrails not configured |
| 5 | Transaction Layer | PARTIAL | Odoo adapter exists, structured workflow not wired |
| 6 | Integration Plane | PARTIAL | Odoo RPC exists, no APIM/gateway contract |
| 7 | Governance / Control Plane | PARTIAL | Entra MI active, evals/red-team/stored-completions at 0 |
| 8 | Operating / Compliance Plane | PARTIAL | Close task catalog exists, no runtime orchestrator |

**Overall: 0/8 PASS. 8/8 PARTIAL. 0/8 MISSING.**

The base assets exist across all 8 planes. No plane is fully missing.
But no plane is fully production-ready either. The gap is composition, not provisioning.

---

## Plane 1: Data Plane

**Purpose**: Where data lives and is retained.

| Asset | Status | Evidence |
|-------|--------|----------|
| Azure PostgreSQL (`pg-ipai-odoo`) | PASS | General Purpose, active, backup-retained |
| Odoo databases (`odoo`, `odoo_dev`, `odoo_staging`) | PASS | Visible in Azure portal |
| Test databases (`test_<module>`) | PASS | Disposable, per module |
| Backup retention | PASS | Automated restore points active |
| Document blob storage | MISSING | No dedicated Blob Storage / Data Lake for raw docs |
| Extracted fields persistence | MISSING | No structured extraction result store |

**Verdict: PARTIAL** -- transactional data plane is live; document data plane is not.

### Remediation
- Provision Azure Blob Storage container for raw document intake
- Define extraction result storage (Blob JSON or PG table)
- Wire backup retention awareness into close/compliance workflows

---

## Plane 2: Document Pipeline

**Purpose**: How documents are ingested, extracted, and classified.

| Asset | Status | Evidence |
|-------|--------|----------|
| Document Intelligence API | PASS | Analyze Document API available in Foundry |
| Content Understanding - Read | PASS | Deployed in Foundry project |
| Content Understanding - Layout | PASS | Deployed in Foundry project |
| Language Detection | PASS | Azure Language service deployed |
| PII Redaction | PASS | Azure Language service deployed |
| Invoice prebuilt model | AVAILABLE | DI prebuilt:invoice available via API |
| Receipt prebuilt model | AVAILABLE | DI prebuilt:receipt available via API |
| Custom extraction model | MISSING | No custom model trained for PH finance docs |
| Intake orchestrator workflow | MISSING | `pulser-doc-intake-v1` spec written, not implemented |
| Classification eval | MISSING | No classification eval dataset or runs |

**Verdict: PARTIAL** -- primitives available; pipeline not assembled.

### Remediation
- Implement `pulser-doc-intake-v1` workflow in Foundry
- Build extraction schema for invoice/bill/receipt/payment-proof
- Create classification eval dataset (min 50 samples per class)
- Wire Content Understanding Read/Layout as first-pass OCR before DI

---

## Plane 3: LLM Application Layer

**Purpose**: How the model is prompted, grounded, and constrained.

| Asset | Status | Evidence |
|-------|--------|----------|
| `gpt-4.1` deployment | PASS | Active in Foundry project |
| `gpt-4o-mini` / `w9-pulser` | PASS | Active in Foundry project |
| `claude-sonnet-4-6` | PASS | Active in Foundry project |
| `text-embedding-3-small` | PASS | Active in Foundry project |
| Active-form grounding contract | MISSING | Context packager exists in Odoo module but grounding schema not enforced |
| Structured output schemas | WRITTEN | 4 JSON schemas in `agents/schemas/workflow/pulser/` |
| Fallback state enum | WRITTEN | `not_found`, `not_yet_computable`, `needs_review`, `blocked` in rules |
| Prompt construction controls | WRITTEN | `llm_application_controls` in rules YAML |
| Low-variance inference settings | NOT CONFIGURED | Rules specify policy, Foundry deployment not configured |
| Foundry IQ / AI Search index | MISSING | 0 indexes configured |

**Verdict: PARTIAL** -- models deployed, application contract written but not enforced.

### Recommended deployment roles
```
gpt-4.1            = primary governed transactional/decision model
w9-pulser (4o-mini) = default UI copilot, lightweight form validator
claude-sonnet-4-6   = secondary evaluator, specialist reviewer
text-embedding-3-sm = vector search, attachment retrieval, policy grounding
```

### Remediation
- Configure structured output on Foundry agent definitions
- Create at least 1 Foundry IQ / AI Search index for finance policy grounding
- Enforce prompt construction controls in agent system prompts
- Set temperature/top_p for finance-critical workflows

---

## Plane 4: Decision / Policy Layer

**Purpose**: How business rules choose a safe action.

| Asset | Status | Evidence |
|-------|--------|----------|
| Rules YAML (`pulser-odoo.rules.yaml`) | PASS | 705+ lines, comprehensive |
| Automation boundaries | PASS | `auto_create_allowed_when`, `review_required_when`, `hard_block_when` |
| Idempotency policy | PASS | Key fields and reconnect policy defined |
| Foundry custom compliance policies | MISSING | 0 custom policies configured |
| Foundry default guardrails | PARTIAL | Tab exists, no custom configuration |
| Safe action enum per workflow | WRITTEN | In workflow specs and schemas |
| Duplicate detection logic | WRITTEN | In rules, not runtime-validated |
| Company-context validation | WRITTEN | In rules, not runtime-validated |

**Verdict: PARTIAL** -- rules are comprehensive on paper; Foundry enforcement is zero.

### Remediation
- Configure >= 4 custom Pulser compliance policies in Foundry (SC-PH-14)
- Implement runtime duplicate detection in transaction agent
- Implement company-context validation gate
- Wire `hard_block_when` conditions as Foundry guardrail policies

---

## Plane 5: Transaction Layer

**Purpose**: How Odoo records are created, updated, or blocked.

| Asset | Status | Evidence |
|-------|--------|----------|
| `ipai_odoo_copilot` module | PASS | Installed, running in container |
| Odoo JSON-RPC adapter | PASS | Context packager + HTTP provider |
| Audit trail (`ipai.copilot.audit`) | PASS | Model defined in module |
| Draft-only creation policy | WRITTEN | In workflow specs |
| Credit/debit note for validated changes | WRITTEN | In rules YAML |
| Workflow-driven transaction creation | MISSING | Workflows spec'd but not wired |
| Idempotent write-back | MISSING | Key defined, implementation not verified |

**Verdict: PARTIAL** -- Odoo adapter works; structured workflow-driven transactions not wired.

### Remediation
- Wire `pulser-doc-intake-v1` safe_action to Odoo ORM calls
- Implement idempotency key check before any `account.move.create()`
- Wire `pulser-form-validator-v1` to active form context packager
- Verify audit trail captures workflow_id and safe_action

---

## Plane 6: Integration Plane

**Purpose**: How Pulser is exposed to other systems and clients.

| Asset | Status | Evidence |
|-------|--------|----------|
| Odoo systray + chat panel | PASS | OWL component in `ipai_odoo_copilot` |
| Odoo HTTP controller | PASS | `/ipai/copilot/chat` endpoint |
| Foundry agent endpoint | PASS | 5 agents running in Foundry |
| Direct REST to Foundry | AVAILABLE | OpenAI v1-compatible route |
| APIM / API gateway | MISSING | No Azure APIM configured for Pulser |
| Document upload handoff | MISSING | No structured upload-to-pipeline flow |
| Structured result callback | MISSING | No webhook/callback from Foundry to Odoo |
| PostgreSQL MCP read-only | MISSING | Not connected (SC-PH-21) |

**Verdict: PARTIAL** -- point-to-point integration works; no gateway, no structured callbacks.

### Recommended integration pattern
```
Odoo UI -> Odoo Controller -> Foundry Agent Endpoint (direct REST)
Document Upload -> Azure Function ingest -> Blob -> DI -> Foundry workflow
Foundry Result -> Odoo JSON-RPC callback -> draft creation
```

### Remediation
- Decide APIM vs direct REST (direct REST acceptable for MVP)
- Implement document upload handoff via Azure Function or Logic App
- Implement structured result callback (Foundry -> Odoo draft creation)
- Connect PostgreSQL MCP read-only for grounding (SC-PH-21)

---

## Plane 7: Governance / Control Plane

**Purpose**: Identity, auth, quotas, evals, adversarial testing, observability.

| Asset | Status | Evidence |
|-------|--------|----------|
| Microsoft Entra ID managed identity | PASS | RBAC live on `ipai-copilot-resource` |
| Foundry agent monitoring | PARTIAL | Agents running, actionable alerts not configured |
| Evaluation definitions | PARTIAL | Definitions exist, most have 0 runs |
| Completed evaluation runs | MINIMAL | Only 1 eval completed |
| Red-team runs | MISSING | 0 runs |
| Stored completions | MISSING | 0 stored completions |
| Custom compliance policies | MISSING | 0 configured |
| Foundry IQ indexes | MISSING | 0 configured |
| Network/endpoint security | PASS | WAF + AFD in place |
| Key Vault integration | PASS | `kv-ipai-dev` active |
| Environment separation | PASS | dev/staging/prod DB split |

**Verdict: PARTIAL** -- identity and infra security are solid; eval/governance tooling is empty.

### Remediation
- Run release-gate evals for all 5 core agents (SC-PH-15)
- Complete >= 1 red-team run (SC-PH-17)
- Curate >= 25 stored completions (SC-PH-16)
- Configure >= 4 custom compliance policies (SC-PH-14)
- Configure >= 1 Foundry IQ index (SC-PH-18)
- Set up actionable monitoring alerts for all core agents (SC-PH-22)

---

## Plane 8: Operating / Compliance Plane

**Purpose**: Close orchestration, compliance scenarios, filing readiness, evidence packs.

| Asset | Status | Evidence |
|-------|--------|----------|
| Month-end task catalog | PASS | `ssot/finance/close/month_end_task_catalog.yaml` |
| BIR filing calendar | PASS | `ssot/finance/close/ph_bir_filing_calendar_2026.yaml` |
| Close role capacity | PASS | `ssot/finance/close/close_role_capacity.yaml` |
| People directory | PASS | `ssot/finance/close/people_directory.yaml` |
| Close orchestrator workflow | WRITTEN | `pulser-close-orchestrator-v1` spec'd |
| Compliance scenarios | WRITTEN | 4 scenarios defined in rules YAML |
| Evidence pack generation | MISSING | No runtime evidence pack generator |
| BIR filing readiness view | MISSING | No runtime readiness dashboard |
| Task dependency engine | MISSING | Blocking rules written, no runtime engine |
| Human-in-the-loop close gates | MISSING | Defined in workflow, not implemented |

**Verdict: PARTIAL** -- SSOT catalogs are comprehensive; runtime orchestration is zero.

### Remediation
- Implement `pulser-close-orchestrator-v1` in Foundry
- Build task dependency engine (or wire to Odoo project tasks)
- Implement evidence pack generation (close artifacts -> Blob -> link)
- Build BIR filing readiness view (2307, SLSP, 2550Q, SAWT/QAP)

---

## Cross-Plane Dependencies

```
Plane 2 (Document Pipeline) depends on:
  Plane 1 (Data) for blob storage
  Plane 3 (LLM) for classification/extraction models
  Plane 6 (Integration) for upload handoff

Plane 5 (Transaction) depends on:
  Plane 3 (LLM) for action selection
  Plane 4 (Decision) for safety gates
  Plane 6 (Integration) for Odoo write-back

Plane 8 (Operating) depends on:
  Plane 4 (Decision) for blocking rules
  Plane 5 (Transaction) for close task execution
  Plane 7 (Governance) for compliance evals
```

---

## Priority Build Order

### Priority 1: Wire the inner engine (Planes 2-5)
1. Implement `pulser-doc-intake-v1` workflow
2. Implement `pulser-form-validator-v1` workflow
3. Wire structured output schemas to agent definitions
4. Configure Foundry guardrail policies

### Priority 2: Stand up integration (Plane 6)
5. Document upload handoff (Azure Function -> Blob -> DI)
6. Result callback (Foundry -> Odoo draft)
7. PostgreSQL MCP read-only connection

### Priority 3: Harden governance (Plane 7)
8. Run release-gate evals for all core agents
9. Complete first red-team run
10. Curate stored completions
11. Configure Foundry IQ index

### Priority 4: Activate operations (Plane 8)
12. Implement close orchestrator workflow
13. Build evidence pack generator
14. Build BIR filing readiness view

---

## Foundry Asset Deployment Mapping

| Foundry Asset | Plane | Role |
|---------------|-------|------|
| `gpt-4.1` | 3 (LLM) | Primary governed transaction/decision model |
| `w9-pulser` (gpt-4o-mini) | 3 (LLM) | Default UI copilot, high-throughput form validator |
| `claude-sonnet-4-6` | 3 (LLM), 7 (Governance) | Secondary evaluator, specialist reviewer |
| `text-embedding-3-small` | 3 (LLM), 6 (Integration) | Vector search, attachment retrieval, policy grounding |
| Content Understanding - Read | 2 (Document) | Fast document text + region extraction |
| Content Understanding - Layout | 2 (Document) | Structure-aware parsing of pages/tables/forms |
| Document Intelligence API | 2 (Document) | Invoice/receipt/form extraction via prebuilt models |
| Azure Language - Detection | 2 (Document) | Multilingual intake normalization |
| Azure Language - PII Redaction | 7 (Governance) | Safe downstream storage/logging |
| Azure Translator | 6 (Integration) | Cross-language user/document support |
| Speech services | 6 (Integration) | Optional voice lane (not MVP-critical) |

---

*Companion files:*
- *Workflow specs: `automations/workflows/odoo/pulser-*.yaml`*
- *Output schemas: `agents/schemas/workflow/pulser/*.schema.json`*
- *Rules: `rules/pulser-odoo.rules.yaml`*
- *SSOT catalogs: `ssot/finance/close/*.yaml`*
