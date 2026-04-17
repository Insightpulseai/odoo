# IPAI — Complete Boards View

> Consolidated work surface across 4 product packs, all open issues, all triggered/deferred items.
> Ready to sync to Azure DevOps Boards per CLAUDE.md §"Engineering & Delivery Authority".
> Generated 2026-04-15.
> SSOT for what's in flight, what's queued, what's done.

---

## 0. State legend

| State | Meaning |
|---|---|
| ✅ DONE | Shipped and verified |
| 🔵 ACTIVE | Currently being built |
| 🟡 QUEUED | Ready; waiting on sequence |
| ⏸ DEFERRED | Trigger-based; not actively worked |
| 🚫 BLOCKED | External dependency (billing, Microsoft timeline, etc.) |

---

## 1. EPIC — Infrastructure Substrate

| # | Item | State | Evidence |
|---|---|---|---|
| I1 | Odoo on ACA (acae-ipai-dev-sea + pg-ipai-odoo) | ✅ DONE | Live per user confirmation 2026-04-15 |
| I2 | Foundry resource (ipai-copilot-resource, EUS2) | ✅ DONE | gpt-4.1 + text-embedding-3-small + gpt-4.1-mini deployed |
| I3 | Foundry retire ipai-copilot-payg (PAYG) | ✅ DONE | Deleted 2026-04-15 |
| I4 | Unity Catalog bootstrap (ipai_dev/staging/prod × 5 schemas) | ✅ DONE | `docs/evidence/20260415-uc-bootstrap/` |
| I5 | Databricks Lakehouse Federation to pg-ipai-odoo (odoo_erp FOREIGN_CATALOG) | ✅ DONE | Pre-existing, verified 2026-04-15 |
| I6 | Redis cache (cache-ipai-dev) | ✅ DONE | Live on PAYG rg-ipai-dev-odoo-runtime |
| I7 | Service Bus (sb-ipai-dev-sea) | ✅ DONE | Live on Sponsorship |
| I8 | Azure AI Search (srch-ipai-dev-sea) | ✅ DONE | Live on Sponsorship |
| I9 | Document Intelligence (docai-ipai-dev) | ✅ DONE | Live on Sponsorship EUS2 |
| I10 | Key Vault (kv-ipai-dev-sea) | ✅ DONE | Live on Sponsorship |
| I11 | Container Registry (acripaiodoo) | ✅ DONE | Live on Sponsorship |
| I12 | 6 per-agent Managed Identities (id-ipai-agent-{ap-invoice,bank-recon,doc-intel,finance-close,pulser,tax-guru}-dev) | ✅ DONE | On PAYG rg-ipai-dev-platform |
| I13 | ipai-odoo-mcp (ACA, 13 tools) | ✅ DONE | Live on PAYG |
| I14 | ipai-odoo-connector (ACA) | ✅ DONE | Live on PAYG |
| I15 | ipai-ocr-dev (ACA) | ✅ DONE | Live on PAYG |
| I16 | Front Door (afd-ipai-dev) + WAF | ✅ DONE | Live |

---

## 2. EPIC — Data Model & Architecture (canonical docs)

| # | Item | State | Path |
|---|---|---|---|
| D1 | Full data model ERD + schema lock | ✅ DONE | `docs/architecture/data-model-erd.md` |
| D2 | D365 entity inventory | ✅ DONE | `docs/research/d365-data-model-inventory.md` |
| D3 | D365 → Odoo mapping | ✅ DONE | `docs/research/d365-to-odoo-mapping.md` |
| D4 | D365 displacement map | ✅ DONE | `docs/architecture/d365-displacement-map.md` (validated, drift flagged) |
| D5 | CDM ↔ Odoo mapping | ✅ DONE | `docs/architecture/cdm-odoo-mapping.md` |
| D6 | CDM SSOT YAML | ✅ DONE | `platform/contracts/cdm-entity-map.yaml` |
| D7 | Semantic Layer (Unity Catalog) | ✅ DONE | `docs/architecture/semantic-layer.md` |
| D8 | Foundry runtime contract SSOT | ✅ DONE | `ssot/foundry/runtime-contract.yaml` |
| D9 | Foundry connections + tools runbook | ✅ DONE | `docs/runbooks/foundry-connections-and-tools.md` |
| D10 | Claude Code + Foundry runbook | ✅ DONE | `docs/runbooks/claude-code-foundry.md` |
| D11 | Product packaging strategy (4 packs) | ✅ DONE | `docs/strategy/pulser-product-packaging.md` |
| D12 | D365 Marketplace coverage (16 surveys) | ✅ DONE | `docs/competitive/d365-marketplace-coverage.md` |

---

## 3. EPIC — Pack 1 (Finance Ops) — SHIP Q2 2026

| # | Item | State | Owner | Issue # |
|---|---|---|---|---|
| F1 | `ipai_bir_tax_compliance` Phase 1 (DAT + PDF via Foundry Code Interpreter) | 🟡 QUEUED | Finance Guild | #9 P1 |
| F2 | Naming consolidation `ipai_expense_*` | 🟡 QUEUED | Platform | #8 P0 |
| F3 | Naming consolidation `ipai_bank_recon` vs `ipai_finance_recon` | 🟡 QUEUED | Platform | #8 P0 |
| F4 | `ipai_ar_collections` scaffold | 🟡 QUEUED | Finance Guild | #12 P1 |
| F5 | Service Bus trigger: `ipai-odoo-connector` → Bank Recon agent | 🟡 QUEUED | Platform | #11 P1 |
| F6 | eBIRForms / eFPS submission via Foundry Browser Automation | ⏸ DEFERRED | Finance Guild | #16 P2 |
| F7 | `ipai_bsp_fx_rate` (BSP FX connector) | ⏸ DEFERRED | Finance Guild | #15 P2 |
| F8 | `ipai_procurement_comms` | ⏸ DEFERRED | Finance Guild | #17 P2 |

---

## 4. EPIC — Pack 4 (PH Compliance) — SHIP Q2 2026

| # | Item | State | Issue # |
|---|---|---|---|
| C1 | BIR 2307 auto-gen on CWT vendor payments | 🟡 QUEUED | #9 P1 |
| C2 | BIR 2550M/Q VAT returns DAT | 🟡 QUEUED | #9 P1 |
| C3 | BIR SAWT/QAP/SLSP DAT | 🟡 QUEUED | #9 P1 |
| C4 | BIR 1601-C/E monthly remittance | ⏸ DEFERRED | #24 P3 |
| C5 | BIR 1702 annual ITR | ⏸ DEFERRED | #24 P3 |
| C6 | BIR CAS certification (direct eFPS) | ⏸ DEFERRED | #25 P3 |

---

## 5. EPIC — Pack 3 (Document & Audit) — SHIP Q3 2026

| # | Item | State | Issue # |
|---|---|---|---|
| DA1 | Controlled attachment flow (OCA `dms` + Azure Blob backend) | 🟡 QUEUED | — |
| DA2 | Audit packet generator via Code Interpreter → `stipaidevagent` | 🟡 QUEUED | — |
| DA3 | `platform.audit_event` schema + ingest middleware | 🟡 QUEUED | — |
| DA4 | `ipai_apiscan` (Azure Document Intelligence bridge) | 🟡 QUEUED | — |

---

## 6. EPIC — Pack 2 (Project Services) — SHIP Q4 2026

| # | Item | State | Issue # |
|---|---|---|---|
| P1 | OCA `project_*` baseline install + pin | 🟡 QUEUED | — |
| P2 | `ipai_finance_ppm` KPI + Fabric PBI wiring | 🟡 QUEUED | #18 P2 |
| P3 | Revenue recognition via OCA `project_pm_revenue_recognition` | 🟡 QUEUED | — |

---

## 7. EPIC — Data Foundation & BI

| # | Item | State | Issue # |
|---|---|---|---|
| DB1 | Unity Catalog bootstrap | ✅ DONE | #28 partial |
| DB2 | CDM export pipeline (DLT → gold CDM folders) | 🟡 QUEUED | #26 P1 |
| DB3 | First metric views (DSO, DPO, filing_on_time) | 🟡 QUEUED | #28 cont |
| DB4 | Agent role assignments (`agent_reader_ipai` per MI) | 🟡 QUEUED | #28 cont |
| DB5 | Fabric capacity + `fcipaidev` workspace | 🚫 BLOCKED | #27 P1 (Fabric trial expiry ~2026-05-20) |
| DB6 | Fabric Data Agent (wraps UC metrics as MCP) | 🟡 QUEUED | #27 downstream |
| DB7 | Power BI semantic model on UC metrics | 🟡 QUEUED | #27 downstream |

---

## 8. EPIC — Agent Identity & Governance

| # | Item | State | Issue # |
|---|---|---|---|
| A1 | Entra Agent ID registration × 3 (pulser-finance, pulser-ops, pulser-research) | 🟡 QUEUED | #13 P1 (deadline 2026-05-01) |
| A2 | `spec/pulser-agent-365-registration/` manifests | 🟡 QUEUED | #13 |
| A3 | Per-agent permission reassignment post-publish | 🟡 QUEUED | #13 |
| A4 | TBWA tenant dual registration | 🟡 QUEUED | #13 |

---

## 9. EPIC — Pulser Agent Evals (Phase 1 of fine-tune roadmap)

| # | Item | State | Path |
|---|---|---|---|
| E1 | Eval harness scaffold | ✅ DONE | `spec/pulser-evals/README.md` |
| E2 | pulser-finance evals | ✅ DONE (scaffold) | `spec/pulser-evals/pulser-finance-evals.md` |
| E3 | pulser-ops evals | ✅ DONE (scaffold) | `spec/pulser-evals/pulser-ops-evals.md` |
| E4 | pulser-research evals | ✅ DONE (scaffold) | `spec/pulser-evals/pulser-research-evals.md` |
| E5 | Baseline eval run (gpt-4.1 against scaffold cases) | 🟡 QUEUED | #14 P2 |
| E6 | Phase 3 SFT corpus assembly (BIR + recon + collections) | ⏸ DEFERRED | Trigger: Phase 2 plateau |
| E7 | Phase 4 DPO from operator corrections | ⏸ DEFERRED | Trigger: post-Phase 3 |

---

## 10. EPIC — Growth Motion

| # | Item | State | Owner |
|---|---|---|---|
| G1 | Kira (CGO) persona + decision judge | ✅ DONE | `agents/personas/growth-officer-persona.md`, `agents/judges/growth-decision-judge.md` |
| G2 | MS for Startups navigator skill | ✅ DONE | `.claude/skills/ms-startups-navigator/SKILL.md` |
| G3 | MS for Startups knowledge base | ✅ DONE | `docs/research/ms-startups/knowledge-base.md` |
| G4 | Founders Hub portal enrollment verification | 🟡 QUEUED | CGO |
| G5 | `ipai_odoo_on_aca` Marketplace listing (private offer) | 🟡 QUEUED | #29 P2, CGO |
| G6 | TBWA\SMP pilot case study draft | 🟡 QUEUED | CGO |
| G7 | W9 Studio + PrismaLab case studies | 🟡 QUEUED | CGO |
| G8 | Microsoft PH PDM engagement | 🟡 QUEUED | CGO |

---

## 11. EPIC — Security & Compliance (BLOCKERS)

| # | Item | State | Issue # |
|---|---|---|---|
| S1 | BOLA in `copilot_gateway.py` | 🟡 QUEUED | #1 P0 BLOCKER |
| S2 | PgBouncer OFF on `pg-ipai-odoo` | 🟡 QUEUED | #2 P0 BLOCKER |
| S3 | Verify Foundry system MI state | 🟡 QUEUED | #4 P0 |
| S4 | Defender for AI enable | 🟡 QUEUED | #5 P0 |
| S5 | Disable Foundry API keys (disableLocalAuth=true) | 🟡 QUEUED | #3 P0 BLOCKER |
| S6 | `d365-displacement-map.md` drift fix | 🟡 QUEUED | #7 P0 |

---

## 12. EPIC — Foundry Operational Wiring

| # | Item | State | Issue # |
|---|---|---|---|
| W1 | Connection: App Insights (`appi-ipai-dev-agent-sea`) | 🟡 QUEUED | #6 P0 (portal-only action) |
| W2 | Connection: AI Search (`srch-ipai-dev-sea`) | 🟡 QUEUED | #6 P0 |
| W3 | Connection: Storage (`stipaidevagent`) | 🟡 QUEUED | #6 P0 |
| W4 | Fine-tune Phase 1 execution (baseline evals) | 🟡 QUEUED | #14 P2 |

---

## 13. EPIC — Marketplace Publishing (Issue 29)

| # | Item | State |
|---|---|---|
| M1 | Partner Center publisher ID verify (MpnId 7097325) | ✅ DONE (per memory) |
| M2 | `ipai_odoo_on_aca` Offer ID reservation | 🟡 QUEUED |
| M3 | Legal entity for publisher account | 🟡 QUEUED (Open Q5 ms-startups) |
| M4 | Private offer for TBWA\SMP | 🟡 QUEUED |
| M5 | Transactable conversion path decision | 🟡 QUEUED (Open Q7 ms-startups) |
| M6 | Co-sell Ready submission | ⏸ DEFERRED (downstream of M4) |
| M7 | Pack-specific Marketplace SKUs (Finance Ops, PH Compliance, etc.) | ⏸ DEFERRED |

---

## 14. DEFERRED / TRIGGER-BASED

| # | Item | Trigger to activate |
|---|---|---|
| T1 | Claude-on-Foundry revisit | User explicitly asks OR MS opens Enterprise-tier quota gate |
| T2 | Cosmos DB provisioning | Postgres `ops` schema insufficient for specific agent |
| T3 | Teams bot provisioning | GTM need for Teams surface (e.g., TBWA pilot requires it) |
| T4 | BIR CAS certification | Production track record of 3+ months post Phase 1+2 |
| T5 | Tax Guru Phase 3 (1601-C + 1702) | Phase 1+2 stable |
| T6 | Supabase re-introduction | **Never** — deprecated by doctrine |
| T7 | GitHub Actions deploy | **Never** — Azure Pipelines is sole CI/CD authority |
| T8 | Vercel / Cloudflare / n8n | **Never** — deprecated |

---

## 15. Summary

| Category | Count | Notes |
|---|---|---|
| ✅ DONE | 35+ | Substrate + architecture + core docs complete |
| 🔵 ACTIVE | 0 | Awaiting user execution decision |
| 🟡 QUEUED | ~35 | Ready to execute |
| ⏸ DEFERRED | ~10 | Trigger-based |
| 🚫 BLOCKED | 1 | Fabric capacity (external timeline) |
| 🚫 FORBIDDEN | 4 | Supabase / GH Actions deploy / Vercel / n8n |

**Top 5 unblocked, ship-now items** (execute in parallel):

1. **#9** `ipai_bir_tax_compliance` Phase 1 — strategic moat (PH BIR)
2. **#13** Entra Agent ID registration — deadline 2026-05-01
3. **#6** Foundry connections wiring (portal-only: App Insights → AI Search → Storage)
4. **#8** Module naming consolidation (clean up duplicates before more code lands)
5. **#26** CDM export pipeline (now unblocked — `ipai_dev.gold` schemas live)

**Top 5 P0 blockers** (must resolve before external users):

1. **#1** BOLA fix in copilot_gateway
2. **#2** PgBouncer enable on pg-ipai-odoo
3. **#3** disableLocalAuth on Foundry
4. **#4** Verify Foundry MI state
5. **#5** Enable Defender for AI

---

## 16. ADO Boards mapping

To sync to Azure DevOps Boards (`ipai-platform` project per `project_azdo_project_state` memory):

- EPICs in §1-14 above → ADO Epics
- Issues in `docs/backlog/open-issues-20260415.md` → ADO Features
- Tasks within each issue's acceptance criteria → ADO Tasks

Map applies per `project_azdo_boards_populated_20260414` normalization matrix.

---

*Compiled 2026-04-15. Refresh when a P0 or P1 item ships, or when sprint closes.*
