# AI Foundry Stage 3 Checklist — Marketplace Readiness

> Machine-readable gate checklist for Odoo Copilot Azure adoption.
> SSOT contract: `ssot/ai/foundry_stage3.yaml`

---

## Section 1: Foundation (Stage 2 → Stage 3 Prerequisites)

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1.1 | Audit model (`ipai.copilot.audit`) — 15 event types, append-only | **Done** | `copilot_audit.py` |
| 1.2 | Action dispatch — 6 per-type handlers with JSON payload parsing | **Done** | `ipai_copilot_action_queue.py` |
| 1.3 | Fail-closed write gate — `ipai.copilot.write_actions_enabled` | **Done** | Config parameter defaults to False |
| 1.4 | Rate limiting — per-user sliding window (20/60s) | **Done** | `copilot_gateway.py` |
| 1.5 | Request validation — 8000 char, context sanitization | **Done** | `copilot_gateway.py` |
| 1.6 | Company scoping — user + company access check | **Done** | `copilot_gateway.py` |
| 1.7 | Streaming disconnect — `GeneratorExit` caught, partial content persisted | **Done** | `copilot_gateway.py` |
| 1.8 | `mail.thread` on conversations — chatter audit trail | **Done** | `copilot_conversation.py` |
| 1.9 | SQL constraints — correlation_id + request_id unique | **Done** | Models |
| 1.10 | ACLs — action_queue + audit models | **Done** | `ir.model.access.csv` |
| 1.11 | Version `19.0.2.0.0` | **Done** | `__manifest__.py` |

## Section 2: Azure Wiring (Stage 3 Core)

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 2.1 | Model contract resolved — `gpt-4.1` deployed | **Done** | `oai-ipai-dev`, 10 TPM Standard |
| 2.2 | Embedding model deployed — `text-embedding-ada-002` | **Done** | `oai-ipai-dev`, 1536 dimensions |
| 2.3 | `odoo-docs-kb` index created — vector-enabled, HNSW cosine | **Done** | 26 chunks, `srch-ipai-dev` |
| 2.4 | RBAC assigned — project + endpoint identities | **Done** | Search Reader + OpenAI User |
| 2.5 | Foundry connections created — Search + OpenAI | **Done** | `proj-ipai-claude` |
| 2.6 | Foundry endpoint live — `ipai-copilot-endpoint` | **Done** | Scoring URI verified |
| 2.7 | Gateway wired — env vars → `gpt-4.1` | **Done** | `ipai-copilot-gateway` port 8088 |
| 2.8 | Retrieval smoke test — grounded results returned | **Done** | Score 7.33, 3 results |

## Section 3: Marketplace Readiness (Stage 3 Remaining)

| # | Gate | Status | Blocker |
|---|------|--------|---------|
| 3.1 | Teams/M365 app package | **Not Started** | No manifest created |
| 3.2 | Evaluation pack — formal pass/fail thresholds | **Not Started** | No quality suite |
| 3.3 | Privacy/data handling documentation | **Not Started** | No docs |
| 3.4 | Partner Center submission assets | **Not Started** | No assets prepared |
| 3.5 | SLO baseline established | **Not Started** | No metrics |
| 3.6 | Full Odoo docs corpus (26 → 7000+ chunks) | **Not Started** | Seed only |
| 3.7 | Entra identity wired — app registration + OIDC | **Not Started** | Spec exists, not started |
| 3.8 | Write actions enabled (flip config flag) | **Blocked** | Requires 3.2 + 3.5 first |

## Acceptance Criteria

Stage 3 is complete when:

1. All Section 2 gates remain green (regression check)
2. All Section 3 gates are Done
3. `ssot/ai/foundry_stage3.yaml` status = `complete`
4. `ssot/agents/diva_copilot.yaml` `ga_ready` = `true`
5. `docs/architecture/AI_RUNTIME_AUTHORITY.md` reflects GA status

---

## SSOT References

| Document | Path |
|----------|------|
| Agent SSOT | `ssot/agents/diva_copilot.yaml` |
| Stage 3 contract | `ssot/ai/foundry_stage3.yaml` |
| Model contract | `ssot/ai/models.yaml` |
| Runtime authority | `docs/architecture/AI_RUNTIME_AUTHORITY.md` |
| Spec bundle | `spec/ipai-odoo-copilot-azure/` |
| Module source | `addons/ipai/ipai_odoo_copilot/` (v19.0.2.0.0) |

---

*Last updated: 2026-03-23*
