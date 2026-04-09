# Odoo on Azure + Databricks Genie + Foundry + Document Intelligence
## Go-Live Checklist

> Version: 1.0.0
> Last updated: 2026-03-23
> Launch tier: Internal beta / trusted users / read-only advisory
> Companion: `docs/delivery/ODOO_AZURE_GENIE_GO_LIVE_CHECKLIST.md` (detailed file targets)
> SSOT: `ssot/ai/go_live_posture.yaml`

---

## 1. Purpose

This deployment has four distinct work surfaces:

### 1.1 Odoo Copilot (Foundry-backed)

Purpose:
- provide guided, context-aware assistance inside Odoo
- answer process and record-aware questions
- explain finance, CRM, project, procurement, and compliance workflows
- propose actions safely before any write path is enabled

This is the transactional/process assistant surface.

### 1.2 Databricks Genie

Purpose:
- answer natural-language analytics questions over curated governed data
- support finance, operations, delivery, and executive KPI exploration
- complement dashboards with conversational analytics

This is the analytics assistant surface.

### 1.3 Document Intelligence Agentic Assistant

Purpose:
- ingest invoices, receipts, statements, forms, and other business documents
- extract text, tables, fields, and structure
- route low-confidence outputs to review queues
- reduce manual encoding into downstream systems

This is the document extraction and review-assist surface.

### 1.4 Azure AI Foundry

Purpose:
- provide governed agent runtime, tools, orchestration, evaluation, and endpoint management
- connect Odoo Copilot to retrieval, model inference, and downstream tools

This is the agent runtime/orchestration surface.

---

## 2. Launch posture

### 2.1 Allowed launch posture

Current allowed posture:
- internal beta
- trusted users only
- read-only advisory by default
- monitored rollout
- human-in-the-loop for document review
- no unrestricted write execution

### 2.2 Not allowed to claim yet

Do not label this release as:
- GA
- unrestricted production copilot
- autonomous transaction execution
- multi-tenant enterprise release
- fully grounded production assistant
- autonomous accounting/document posting

---

## 3. Architecture outcomes

### 3.1 What this architecture should accomplish

#### Odoo Copilot
- reduce manual ERP lookup and support friction
- improve answer quality inside Odoo workflows
- provide safer guided next steps for operators
- centralize process knowledge across Odoo modules

#### Databricks Genie
- let users ask business questions without writing SQL
- accelerate insight discovery over curated data
- reduce dashboard dependency for ad hoc questions
- improve KPI accessibility for non-technical stakeholders

#### Document Intelligence assistant
- convert unstructured documents into structured reviewable data
- reduce encoding effort for finance/admin teams
- improve intake speed for invoices, receipts, and forms
- preserve evidence links between extracted fields and source files

#### Foundry runtime
- enforce model/runtime control, evaluation, and observability
- connect retrieval, inference, and tools through a governed serving path

---

## 4. Identity and access

### 4.1 Odoo SSO
- [ ] Entra app is single-tenant
- [ ] redirect URI is `https://erp.insightpulseai.com/auth_oauth/signin`
- [ ] Graph delegated `User.Read` is configured
- [ ] Odoo OAuth provider fields are wired
- [ ] break-glass admin access is documented

### 4.2 Foundry / Azure runtime identity
- [ ] Foundry project identity has Azure AI Search access
- [ ] Foundry project identity has Azure OpenAI/model inference access
- [ ] gateway identity ownership is documented
- [ ] runtime secrets are stored in the approved secret store
- [ ] no production dependency relies on ad hoc portal-only values

### 4.3 Azure DevOps automation identity
- [ ] service principal is present in Azure DevOps org
- [ ] access level/license is assigned
- [ ] project membership is least-privilege
- [ ] automation path is PAT-free where possible

---

## 5. Odoo Copilot readiness

### 5.1 Runtime hardening
- [ ] `action_execute()` is safely implemented or explicitly disabled
- [ ] audit model exists and persists events
- [ ] rate limiting is enforced
- [ ] request validation is enforced
- [ ] company scoping is enforced
- [ ] session/stream protections are enforced
- [ ] unsupported capabilities fail closed

### 5.2 Retrieval contract
- [ ] retrieval order is defined as:
  1. Odoo runtime context
  2. curated Odoo docs knowledge base
  3. bounded approved-domain public retrieval
- [ ] assistant does not falsely claim capabilities
- [ ] UI exposes grounded vs non-grounded behavior
- [ ] source indicators/citations are visible where applicable

---

## 6. Foundry Stage 3 wiring

### 6.1 Retrieval/indexing
- [ ] `odoo-docs` is indexed
- [ ] retrieval index/schema is finalized
- [ ] vector-search decision is explicit
- [ ] chunking and metadata strategy are documented
- [ ] indexed document/chunk counts are recorded as evidence

### 6.2 Foundry connections
- [ ] Foundry Search connection exists
- [ ] Foundry OpenAI connection exists
- [ ] at least one online endpoint is deployed
- [ ] deployed model is recorded in SSOT
- [ ] spec/runtime model drift is resolved

### 6.3 Gateway wiring
- [ ] gateway is wired to the Foundry endpoint
- [ ] endpoint URL/name is recorded
- [ ] retrieval is invoked on Odoo-docs questions
- [ ] smoke tests prove grounded response flow end to end

---

## 7. Databricks Genie readiness

### 7.1 Data governance
- [ ] exposed datasets are curated and approved
- [ ] Unity Catalog ownership/permissions are correct
- [ ] warehouse backing Genie is defined and cost-owned
- [ ] KPI/business definitions are documented
- [ ] sample questions are documented

### 7.2 Functional acceptance
- [ ] Genie answers top finance/ops questions correctly
- [ ] answers trace to approved data sources
- [ ] no ERP writeback is implied
- [ ] Genie positioning is separate from Odoo transactional assistance

### 7.3 Top question pack
- [ ] cash position
- [ ] AR aging trend
- [ ] spend by vendor
- [ ] project margin
- [ ] close readiness
- [ ] collections risk
- [ ] utilization trend
- [ ] delivery variance

---

## 8. Document Intelligence readiness

### 8.1 Ingestion
- [ ] supported ingress paths are documented
- [ ] supported document classes are enumerated
- [ ] storage/retention policy is defined
- [ ] duplicate detection rules are defined

### 8.2 Extraction + review
- [ ] extracted fields map to canonical business objects
- [ ] confidence thresholds are defined
- [ ] human review queue exists
- [ ] malformed/low-confidence documents are routed safely
- [ ] evidence links to source documents are preserved

### 8.3 Posting safety
- [ ] no autonomous posting to accounting without review
- [ ] exception approval path exists
- [ ] irreversible operations are blocked by default

---

## 9. Observability and rollback

### 9.1 Observability
- [ ] structured logs exist for gateway, Foundry, retrieval, and OCR
- [ ] latency/token/query metrics are captured
- [ ] trace IDs exist across the serving path
- [ ] error dashboards are live

### 9.2 Rollback
- [ ] feature flags exist for Copilot visibility
- [ ] feature flags exist for retrieval on/off
- [ ] feature flags exist for endpoint switchback
- [ ] feature flags exist for document automation on/off
- [ ] rollback owner is named
- [ ] rollback path is tested

### 9.3 Support
- [ ] known issues document exists
- [ ] support/escalation owner is named
- [ ] evidence pack path is documented

---

## 10. FinOps and value proof

### 10.1 Cost tracking
- [ ] cost per copilot session
- [ ] cost per grounded answer
- [ ] cost per document processed
- [ ] Genie warehouse/query cost
- [ ] retrieval/query volume
- [ ] model usage by surface

### 10.2 Value tracking
- [ ] reduction in manual document lookup time
- [ ] reduction in manual encoding effort
- [ ] improvement in answer quality
- [ ] improved support/onboarding speed
- [ ] improved analytics turnaround time
- [ ] user adoption by team

### 10.3 Pricing/model review
- [ ] current deployed model is explicitly accepted for launch
- [ ] upgrade criteria are documented
- [ ] provisioned/commitment pricing trigger is documented

---

## 11. Go-live decision matrix

### 11.1 May launch as internal beta

Launch is allowed only if:
- [ ] Odoo Copilot is read-only advisory
- [ ] trusted user scope is enforced
- [ ] write paths are disabled or safely fail-closed
- [ ] retrieval is either working or transparently marked unavailable
- [ ] Genie is limited to curated analytics
- [ ] Document Intelligence remains human-in-the-loop
- [ ] rollback path is available

### 11.2 Must not launch as GA if any of these remain open
- [ ] no audit model
- [ ] no rate limiting
- [ ] no company scoping
- [ ] no `odoo-docs` indexing
- [ ] no Foundry Search/OpenAI connections
- [ ] no online endpoint
- [ ] no gateway wiring
- [ ] unresolved model contract drift
- [ ] no observability/rollback proof

---

## 12. Recommended launch order

### Phase 1

Odoo Copilot internal beta:
- Odoo SSO
- read-only advisory
- grounded Odoo-docs retrieval
- monitored rollout

### Phase 2

Document Intelligence assisted intake:
- extraction
- review queues
- no autonomous posting

### Phase 3

Databricks Genie analytics rollout:
- curated finance/ops questions
- dashboard-adjacent NLQ
- no ERP execution claims

### Phase 4

Controlled write actions:
- only after audit, rate limiting, company scoping, approvals, retrieval maturity, and rollback proof

---

## 13. Definition of Done for broader production readiness

Broader production readiness is achieved only when:
- Odoo Copilot is grounded and observable
- Foundry endpoint is in the live serving path
- Genie is governed and business-accepted
- Document Intelligence is review-safe
- cost/value metrics are live
- rollback has been tested
- docs and SSOT match runtime reality

---

*Last updated: 2026-03-23*
