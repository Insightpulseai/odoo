# RAG Architecture Implementation Plan
## Master Control: Docs KB + Parity Mapper + Module Factory

**Status:** Draft
**Created:** 2025-12-20
**Branch:** `claude/rag-architecture-comparison-2kCli`

---

## Executive Summary

This document provides a comprehensive implementation plan for building a **Master Control** platform—a single control plane that manages two factories:

1. **Knowledge Factory** → Docs → RAG/KG → Context Packs → SOPs
2. **Module Factory** → Feature → Spec → Scaffold → CI → PR → Deploy

### Architecture Pattern: Databricks Lakeflow (Self-Hosted)

We replicate the Databricks Pipeline Editor pattern using **Continue + Supabase + n8n**:

| Databricks Component | Our Equivalent |
|---------------------|----------------|
| Asset Browser (left) | Sources, Pipelines, Context Packs, Capability Maps |
| Multi-file Editor (center) | `pipeline.yaml`, `contracts/*.yaml`, `prompts/*.md` |
| DAG Visualization | crawl → normalize → chunk → embed → KG → publish |
| Data Preview (right) | Chunk preview, KG nodes, Module diff preview |
| Issues Panel (bottom) | Parse failures, SLA breaches, CI failures → auto-create work_items |
| Run Inspector | Pipeline runs, metrics, logs, "run this command" button |

### No External Dependencies

| Instead of... | We Use... |
|--------------|-----------|
| Jira/Atlassian | `runtime.work_items` in Supabase |
| ServiceNow | `run.work_items` + `run.escalations` |
| Databricks | Continue + Supabase + n8n |
| SAP (live) | SAP docs as **reference only** → map to Odoo CE/OCA |

### Stack Roles

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONTINUE (IDE Layer)                       │
│  Slash commands • Context providers • Workflow runners         │
│  → User-facing surface, agent executor, review interface        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      N8N (Orchestration)                        │
│  Scheduled crawls • Webhook triggers • Multi-step workflows    │
│  → Glue between Continue, Supabase, Odoo, external APIs        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE (Backend)                         │
│  Pipeline defs • Work items • Runs • Evidence • Audit trail    │
│  → Single source of truth, multi-tenant, RLS-safe              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ODOO 18 CE/OCA (ERP)                       │
│  Transactions • Employees • Expenses • Projects • Inventory    │
│  → System of record, no custom core modifications              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Current State Analysis

### 1.1 Existing Infrastructure

| Component | Status | Location |
|-----------|--------|----------|
| RAG Schema (basic) | ✅ Exists | `supabase/migrations/20251220085409_kapa_docs_copilot_hybrid_search.sql` |
| Hybrid Search RPC | ✅ Exists | `rag.search_hybrid()` function |
| Docs Assistant API | ✅ Exists | `docs-assistant/api/answer_engine.py` |
| Docker Compose | ✅ Exists | `deploy/docker-compose.yml` |
| IPAI Addons | ✅ 27 modules | `addons/ipai/` |
| CE/OCA Mapping | ✅ Documented | `docs/ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md` |

### 1.2 Gap Analysis - What's Missing

| Component | Gap Level | Required For |
|-----------|-----------|--------------|
| `rag.document_versions` | CRITICAL | Immutable version history + citations |
| `rag.pages` | HIGH | HTTP metadata + crawl tracking |
| `rag.page_links` | HIGH | Link graph + broken link detection |
| `authz.document_acl` | CRITICAL | Multi-tenant access control |
| `gold.capability_map` | CRITICAL | SAP → Odoo/OCA mapping contracts |
| `gold.parity_packs` | MEDIUM | Filtered document + capability sets |
| `runtime.pipeline_defs` | CRITICAL | Declarative pipeline specs |
| `runtime.pipeline_runs` | HIGH | Execution history + debugging |
| `runtime.pipeline_run_steps` | HIGH | DAG step tracking |
| `runtime.error_codes` | HIGH | Error taxonomy + remediation |
| `dev.feature_requests` | MEDIUM | Module factory intake |
| `dev.module_runs` | MEDIUM | Scaffolding stage tracking |

---

## 2. Odoo 18 CE Documentation Catalog

### 2.1 Structure (Recursive Scan)

```
📚 Odoo 18.0 Documentation (https://www.odoo.com/documentation/18.0/)
├── User Docs (Applications)
│   ├── Odoo Essentials
│   │   ├── Stages, Activities, Reporting, Search/Filter/Group
│   │   ├── Rich-text Editor, Contacts, Import/Export
│   │   └── IAP, Keyboard Shortcuts, Property Fields
│   ├── Finance (5 modules)
│   │   ├── Accounting & Invoicing
│   │   ├── Expenses
│   │   ├── Online Payments
│   │   └── Fiscal Localizations (17+ countries)
│   ├── Sales (6 modules)
│   │   ├── CRM, Sales, Point of Sale
│   │   ├── Subscriptions, Rental, Members
│   ├── Websites (6 modules)
│   │   ├── Website, eCommerce, eLearning
│   │   ├── Forum, Blog, Live Chat
│   ├── Supply Chain (8 modules)
│   │   ├── Inventory, Manufacturing, Purchase
│   │   ├── Barcode, Quality, Maintenance
│   │   ├── Product Lifecycle, Repairs
│   ├── Human Resources (9 modules)
│   │   ├── Attendances, Employees, Appraisals
│   │   ├── Frontdesk, Fleet, Payroll
│   │   ├── Time Off, Recruitment, Referrals, Lunch
│   ├── Marketing (6 modules)
│   │   ├── Email Marketing, Marketing Automation
│   │   ├── SMS, Events, Surveys, Social
│   ├── Services (5 modules)
│   │   ├── Project, Timesheets, Planning
│   │   ├── Field Service, Helpdesk
│   └── Productivity (10+ modules)
│       ├── Documents, Sign, Spreadsheet
│       ├── Dashboards, Knowledge, Calendar
│       ├── Appointments, Discuss, Data Cleaning
│       ├── WhatsApp, VoIP
├── Administration (Install & Maintain)
│   ├── Hosting (On-Premise, Odoo Online, Odoo.sh)
│   ├── Deployment & Installation
│   ├── Upgrades & Updates
│   ├── Database Management
│   ├── Neutralized Databases
│   ├── Mobile Apps
│   └── Odoo.com Accounts
├── Developer
│   ├── Tutorials (Getting Started, Modules, Views)
│   ├── How-to Guides (Authentication, ORM)
│   ├── API Reference
│   ├── External API
│   ├── Framework Reference
│   └── Module Index (Python + RNG)
└── Contributing
    ├── Coding Guidelines
    ├── Documentation Standards
    └── Content Guidelines
```

### 2.2 Key Metrics

| Metric | Value |
|--------|-------|
| Primary Applications | 50+ (across 10 business domains) |
| Supported Languages | 16 (DE, ES, FR, ID, IT, JA, KR, NL, PT, RO, SV, TH, VI, ZH variants) |
| Versions Tracked | Master, 19.0, 18.0, 17.0 |
| Estimated Pages | ~2,000+ |
| Estimated Content | ~10 MB markdown after normalization |

---

## 3. SAP vs Odoo Comparison

### 3.1 Documentation Feature Gap

| Feature | SAP Help Portal | Odoo 18 Docs | Gap Level |
|---------|-----------------|--------------|-----------|
| Semantic Search | ✅ Hybrid (keyword + meaning) | ❌ Keyword only | CRITICAL |
| Learning Journeys | ✅ Structured paths | ❌ Linear list | HIGH |
| Glossary | ✅ Indexed terminology | ⚠️ Inline only | MEDIUM |
| Version Management | ✅ Explicit per product | ✅ Per release | LOW |
| API Surface | ⚠️ Limited REST | ✅ Full JSON-RPC | LOW (Odoo wins) |
| Mobile Experience | ⚠️ Web-only | ✅ Native apps | LOW (Odoo wins) |
| Real-time Collaboration | ❌ No | ✅ Discuss module | LOW (Odoo wins) |

### 3.2 SAP Concur Expense Capability Map

```
SAP Concur Expense
├── User Guides
│   ├── Employee Expense Reporting
│   │   ├── Receipt Capture (OCR + ML) → hr_expense + external OCR
│   │   ├── Expense Entry & Submission → hr_expense
│   │   ├── Approval Workflows (2-tier) → hr_expense_tier_validation (OCA)
│   │   └── Reimbursement Methods → hr_expense + account
│   └── Expense Policy Management
│       ├── Policy Definition (rule engine) → GAP_DELTA: ipai_expense_policy
│       ├── Approval Rules (condition-based) → hr_expense_tier_validation (OCA)
│       └── Audit & Compliance → ipai_bir_compliance
├── Admin Guides
│   ├── User Provisioning → base + mail
│   ├── Integration (GL, Tax, Bank) → account + l10n_ph_*
│   └── Reporting & Export → account_financial_report (OCA)
└── APIs
    ├── Employee Expense API → /web/dataset/call_kw (JSON-RPC)
    ├── Approvals API → GAP_DELTA needed
    └── Webhooks → ipai_custom_routes
```

---

## 4. Implementation Phases

### Phase 1: Schema Extension (Week 1)

**Deliverable:** Supabase migration with all missing tables

| Schema | Tables | Priority |
|--------|--------|----------|
| `rag` | document_versions, pages, page_links | P0 |
| `authz` | document_acl | P0 |
| `gold` | capability_map, parity_packs | P0 |
| `runtime` | pipeline_defs, pipeline_runs, pipeline_run_steps, error_codes, audit_log | P1 |
| `dev` | feature_requests, module_runs | P2 |

### Phase 2: Pipeline Engine (Week 2)

**Deliverable:** n8n workflows for document crawling

| Pipeline | Sources | Schedule |
|----------|---------|----------|
| `odoo_docs_18` | https://www.odoo.com/documentation/18.0/ | Daily 2 AM |
| `oca_repos_sync` | GitHub OCA orgs (webhook-triggered) | On push |
| `sap_concur_ref` | https://help.sap.com/docs/concur/ | Weekly |
| `internal_sops` | Internal wiki/Notion | On update |

### Phase 3: API Extensions (Week 3)

**Deliverable:** FastAPI endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/capabilities` | GET | Fetch capability maps |
| `/v1/capabilities/map` | POST | Create/update mapping |
| `/v1/error-codes/lookup` | GET | Error taxonomy lookup |
| `/v1/scaffold/feature` | POST | Module factory |
| `/v1/pipelines/run` | POST | Trigger pipeline |
| `/v1/pipelines/runs/{id}` | GET | Pipeline status |

### Phase 4: Continue IDE Integration (Week 4)

**Deliverable:** VS Code/JetBrains plugin configuration

| Command | Function |
|---------|----------|
| `/docs <query>` | Hybrid search with citations |
| `/capability <feature>` | SAP → Odoo/OCA mapping |
| `/error-code <code>` | Failure modes + remediation |
| `/scaffold <feature>` | Auto-generate addon |
| `/spec-kit <feature>` | Generate Spec Kit markdown |

---

## 5. Schema Design

### 5.1 Core Tables (New)

```sql
-- rag.document_versions: Immutable snapshots
CREATE TABLE rag.document_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL REFERENCES rag.documents(id),
    version_at timestamptz NOT NULL DEFAULT now(),
    content_md text NOT NULL,
    content_hash text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    UNIQUE (tenant_id, document_id, content_hash)
);

-- gold.capability_map: SAP → Odoo/OCA contracts
CREATE TABLE gold.capability_map (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    source_framework text NOT NULL,  -- sap_concur, sap_srm
    capability_key text NOT NULL,     -- expense.capture.receipts
    title text NOT NULL,
    target_modules jsonb NOT NULL,    -- [{odoo_module, oca_repo, gap_severity}]
    config_notes text,
    docs_refs jsonb DEFAULT '[]'::jsonb,
    status text DEFAULT 'draft',
    UNIQUE (tenant_id, source_framework, capability_key)
);

-- runtime.pipeline_defs: Declarative specs
CREATE TABLE runtime.pipeline_defs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    key text NOT NULL,
    name text NOT NULL,
    enabled boolean DEFAULT true,
    spec_yaml text NOT NULL,
    schedule_cron text,
    UNIQUE (tenant_id, key)
);

-- runtime.error_codes: Error taxonomy
CREATE TABLE runtime.error_codes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE,
    title text NOT NULL,
    description text,
    remediation jsonb NOT NULL,
    edge_cases jsonb DEFAULT '[]'::jsonb
);
```

### 5.2 Capability Map JSON Schema

```json
{
  "source_framework": "sap_concur",
  "capability_key": "expense.capture.receipts",
  "title": "Expense Capture + Receipt Processing",
  "target_modules": [
    {
      "odoo_module": "hr_expense",
      "oca_repo": "OCA/hr-expense",
      "oca_module": "hr_expense_receipt_ocr",
      "gap_severity": "critical",
      "config": {
        "ocr_provider": "external_api"
      },
      "workaround": "Third-party OCR integration"
    }
  ],
  "config_notes": "OCR processing happens outside Odoo",
  "docs_refs": [
    {
      "document_id": "uuid",
      "version_at": "2025-12-20T00:00:00Z",
      "url": "https://help.sap.com/...",
      "evidence": "H2 Receipt Capture"
    }
  ],
  "status": "mapped"
}
```

---

## 6. Error Codes Taxonomy

### 6.1 Initial Error Codes

| Code | Title | Auto-Retry | Remediation |
|------|-------|------------|-------------|
| `CRAWL_TIMEOUT` | Crawler timeout on URL | Yes (3x) | Increase timeout, check URL |
| `PARSE_FAILURE` | HTML/MD parsing failed | No | Review HTML structure |
| `RATE_LIMIT` | Rate limit exceeded (429) | Yes (5s backoff) | Decrease rate_limit_rps |
| `CHUNK_TOKENIZE_FAILURE` | Token counting failed | No | Use fallback tokenizer |
| `EMBED_API_FAILURE` | OpenAI embedding error | Yes (1s backoff) | Check API key, retry |
| `KG_EXTRACTION_EMPTY` | No entities extracted | No | Review chunk quality |

---

## 7. Declarative Pipeline Spec

```yaml
# Example: sap_concur_parity_pack.yaml
version: "1.0"
metadata:
  owner: "platform-team"
  tags: ["sap", "concur", "parity"]
  slack_channel: "#odoo-parity"

sources:
  - key: sap_help_concur
    type: web
    seed_urls:
      - "https://help.sap.com/docs/expense/"
    crawl:
      max_depth: 4
      rate_limit_rps: 2
      timeout_sec: 30

transforms:
  normalize:
    html_to_md: true
    strip_boilerplate: true
  chunk:
    strategy: heading_semantic
    max_tokens: 700
    overlap_tokens: 120
  embed:
    model: "text-embedding-3-large"
    dims: 3072

publish:
  outputs:
    - type: capability_candidates
      key: sap_concur_capability_candidates
    - type: parity_pack
      key: sap_concur_parity_pack

governance:
  acl_default: tenant
  citations_required: true
  provenance:
    include_url: true
    include_version_at: true
    include_chunk_id: true
```

---

## 8. Verification Checklist

### 8.1 Schema Verification

```sql
-- Run after migration
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'rag' ORDER BY table_name;
-- Expected: answers, answer_votes, chunks, document_versions,
--           documents, eval_sets, pages, page_links, questions

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'gold' ORDER BY table_name;
-- Expected: capability_map, parity_packs

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'runtime' ORDER BY table_name;
-- Expected: audit_log, error_codes, pipeline_defs,
--           pipeline_runs, pipeline_run_steps
```

### 8.2 API Verification

```bash
# Health check
curl https://erp.insightpulseai.net/api/v1/health

# Capability lookup
curl "https://erp.insightpulseai.net/api/v1/capabilities?framework=sap_concur"

# Error code lookup
curl "https://erp.insightpulseai.net/api/v1/error-codes/lookup?pattern=CRAWL"

# Hybrid search
curl -X POST "https://erp.insightpulseai.net/api/v1/answer" \
  -H "Content-Type: application/json" \
  -d '{"query": "expense approval workflow"}'
```

---

## 9. Next Steps

1. **Immediate:** Apply migration `20251220_agentbrain_delta.sql`
2. **Week 1:** Deploy n8n pipelines for Odoo 18 docs crawl
3. **Week 2:** Seed `gold.capability_map` with SAP Concur mappings
4. **Week 3:** Extend `docs-assistant/api/answer_engine.py` with new endpoints
5. **Week 4:** Configure Continue IDE plugin

---

## 10. QMS-Lite Layer (MasterControl-Style Document Control)

### 10.1 Platform Positioning

This platform is **"GitHub + Notion + Kapa + Runbooks + Auto-remediation"**, NOT a full regulated QMS like MasterControl. However, for SOPs and policies, we add a **QMS-lite layer** to provide:

| Feature | MasterControl | Our Platform | Status |
|---------|---------------|--------------|--------|
| Controlled documents | ✅ Full | ✅ Implemented | `qms.controlled_docs` |
| Immutable versions | ✅ Full | ✅ Implemented | `qms.doc_versions` |
| Approval workflows | ✅ Multi-step | ✅ Multi-step | `qms.approval_routes` + `qms.approvals` |
| Audit trail | ✅ Part 11 | ✅ Append-only | `qms.audit_events` |
| Read/ack tracking | ✅ Training mgmt | ✅ Basic | `qms.read_receipts` |
| Evidence packs | ✅ Validation | ✅ Basic | `qms.evidence_packs` |
| Training & competency | ✅ Full | ❌ Not built | External/future |
| CAPA / deviations | ✅ Full | ⚠️ Optional | `qms.change_controls` |
| e-signatures (Part 11) | ✅ Validated | ⚠️ Placeholder | Signature hash only |

### 10.2 QMS Schema (8 Tables)

```sql
-- Core document control
qms.controlled_docs      -- SOP|POLICY|WI|FORM|SPEC|RECORD
qms.doc_versions         -- Immutable snapshots with effective_at/superseded_at
qms.approval_routes      -- Workflow templates (steps, roles, escalation)
qms.approvals            -- Actual approval records with decisions
qms.read_receipts        -- "I have read and understood" acknowledgments

-- Audit & compliance
qms.audit_events         -- Append-only audit log (no UPDATE/DELETE)
qms.change_controls      -- Optional: change control records
qms.evidence_packs       -- Snapshots + citations for audits
```

### 10.3 Key Integration Points

**RAG Integration:**
- View `qms.v_effective_docs_for_rag` feeds only **effective versions** to RAG indexers
- Agents can draft SOPs but **cannot mark them effective** without approval workflow completion

**Workflow:**
```
Agent drafts SOP → qms.doc_versions (status='draft')
                 ↓
Submit for approval → qms.approvals created (step 1, 2, ...)
                 ↓
All approvers complete → status='approved'
                 ↓
Admin marks effective → status='effective', effective_at set
                 ↓
RAG indexes effective version only
```

### 10.4 Sample Approval Route

```json
{
  "name": "Standard SOP Approval",
  "applies_to_types": ["SOP", "WI"],
  "steps": [
    {"step": 1, "role": "department_manager", "action": "review", "required": true},
    {"step": 2, "role": "quality_assurance", "action": "approve", "required": true}
  ],
  "sequential": true,
  "escalation_hours": 72
}
```

### 10.5 What We Intentionally Don't Build

| Feature | Reason |
|---------|--------|
| Training assignments & quizzes | Use external LMS (Notion, Moodle, etc.) |
| Full CAPA workflow | Out of scope; use `qms.change_controls` for basics |
| Part 11 validated e-signatures | Requires identity binding; placeholder only |
| Validation package generation | Use `qms.evidence_packs` manually |

### 10.6 Migration File

```
supabase/migrations/20251220_qms_lite_document_control.sql
```

---

## 11. N8N Role: End-to-End Workflow Orchestration

### 11.1 What n8n Does (vs Continue vs Supabase)

| Component | Role | Examples |
|-----------|------|----------|
| **n8n** | Workflow orchestration + triggers | Scheduled crawls, webhook handlers, multi-step automations |
| **Continue** | IDE interface + agent executor | `/docs`, `/scaffold`, code review, chat |
| **Supabase** | Data store + API + RLS | Work items, pipeline runs, evidence, audit trail |

### 11.2 n8n Workflows for Master Control

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `docs_ingest_odoo18` | Cron (daily 2 AM) | Crawl → Normalize → Chunk → Embed → Publish |
| `docs_ingest_sap_help` | Cron (weekly) | Crawl SAP Help → Map to Odoo/OCA capabilities |
| `oca_repo_sync` | GitHub webhook | On push → re-index module docs |
| `bpmn_to_sop` | Manual/API | Parse BPMN → Generate SOP draft → Submit for approval |
| `module_factory` | Work item created | Spec → Scaffold → Lint → Test → PR |
| `sla_monitor` | Cron (every 5 min) | Check timers → Create escalations → Notify |
| `onboard_offboard` | Odoo webhook | Create run.instances → Generate work items |

### 11.3 n8n ↔ Supabase ↔ Odoo Flow

```
[Trigger: GitHub push to OCA/hr-expense]
         ↓
    n8n Workflow
         ↓
┌────────────────────────────────────────────────┐
│ Step 1: Fetch module manifest                  │
│ Step 2: Extract README + doc/*                 │
│ Step 3: POST /v1/ingest/normalize              │
│ Step 4: POST /v1/ingest/chunk                  │
│ Step 5: POST /v1/ingest/embed                  │
│ Step 6: Upsert to Supabase rag.documents       │
│ Step 7: If error → Create runtime.work_items   │
│ Step 8: Notify Mattermost #docs-sync           │
└────────────────────────────────────────────────┘
```

### 11.4 Why n8n (Not Just Continue)

| Scenario | n8n | Continue |
|----------|-----|----------|
| Scheduled crawl at 2 AM | ✅ Cron trigger | ❌ Needs user in IDE |
| Retry with backoff | ✅ Built-in | ❌ Manual |
| Multi-system coordination | ✅ 400+ integrations | ⚠️ Limited |
| Visual workflow editor | ✅ Drag-and-drop | ❌ Code only |
| Agent execution | ⚠️ Via webhook | ✅ Native |
| IDE integration | ❌ | ✅ Native |

**Bottom line:** n8n handles **scheduled/triggered automation**, Continue handles **interactive/IDE work**.

---

## 12. Comprehensive Error Codes (Agent-Ready)

### 12.1 Error Code Taxonomy

Every error code includes:
- **Root cause** (why it failed)
- **Auto-fix command** (what to run)
- **Rollback command** (how to undo)
- **Verification command** (how to confirm)

### 12.2 Ingest Errors (`INGEST_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `INGEST_FETCH_BLOCKED` | Fetch blocked by robots.txt | `n8n execute --workflow=crawl --flag=ignore_robots --url={url}` |
| `INGEST_AUTH_REQUIRED` | Source requires authentication | `vault read secret/crawlers/{source} && n8n execute --workflow=crawl --with-auth` |
| `INGEST_RATE_LIMITED` | 429 Too Many Requests | `sleep 60 && n8n execute --workflow=crawl --rate-limit=0.5` |
| `INGEST_TIMEOUT` | Connection timeout | `n8n execute --workflow=crawl --timeout=60s --url={url}` |

### 12.3 Parse Errors (`PARSE_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `PARSE_HTML_MALFORMED` | Invalid HTML structure | `curl {url} \| tidy -q -o /tmp/clean.html && n8n execute --input=/tmp/clean.html` |
| `PARSE_ENCODING_ERROR` | Non-UTF8 encoding | `iconv -f ISO-8859-1 -t UTF-8 {file} -o {file}.utf8` |
| `PARSE_BOILERPLATE_FAIL` | Boilerplate stripping failed | `n8n execute --workflow=normalize --strip-mode=lenient` |
| `PARSE_HEADING_TREE_INVALID` | Heading hierarchy broken | `n8n execute --workflow=chunk --heading-aware=false` |

### 12.4 Embed Errors (`EMBED_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `EMBED_API_QUOTA` | OpenAI quota exceeded | `sleep 3600 && n8n execute --workflow=embed --batch-id={id}` |
| `EMBED_MODEL_UNAVAILABLE` | Model not available | `n8n execute --workflow=embed --model=text-embedding-3-small` |
| `EMBED_INPUT_TOO_LONG` | Token limit exceeded | `n8n execute --workflow=chunk --max-tokens=500 && n8n execute --workflow=embed` |

### 12.5 Module Factory Errors (`MOD_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `MOD_MANIFEST_MISSING` | `__manifest__.py` not found | `copier copy gh:OCA/oca-addons-repo-template {path}` |
| `MOD_DEPENDENCY_MISSING` | Required module not installed | `pip install odoo-addon-{module} && odoo -u {module}` |
| `MOD_LINT_FAIL` | pylint-odoo errors | `pre-commit run --all-files --hook-stage=commit` |
| `MOD_TEST_FAIL` | Unit tests failed | `odoo --test-enable -u {module} --stop-after-init` |

### 12.6 Odoo Errors (`ODOO_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `ODOO_REGISTRY_INIT` | Registry initialization failed | `odoo --stop-after-init -d {db} && odoo -d {db}` |
| `ODOO_MODULE_INSTALL` | Module installation error | `odoo -u {module} --stop-after-init 2>&1 \| tee /tmp/install.log` |
| `ODOO_XMLRPC_AUTH` | Authentication failed | `curl -X POST -d '{"jsonrpc":"2.0","method":"authenticate"}' {url}` |

### 12.7 Process Runtime Errors (`RUN_*`)

| Code | Title | Auto-Fix |
|------|-------|----------|
| `RUN_SLA_BREACH` | SLA timer exceeded | `SELECT run.check_sla_timers(); -- Creates escalation` |
| `RUN_WORK_ITEM_BLOCKED` | Work item dependencies unmet | `UPDATE run.work_items SET status='blocked' WHERE id={id}` |
| `RUN_EVIDENCE_MISSING` | Required artifact not uploaded | `SELECT * FROM run.evidence WHERE instance_id={id}` |

---

## 13. Architecture Summary

### Four-Layer Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 4: QMS-LITE                            │
│  Controlled docs • Approvals • Audit trail • Evidence packs    │
│  → Only effective versions feed into RAG                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 3: PROCESS RUNTIME                     │
│  Hire-to-Retire • Work items • SLAs • Escalations • Ticketing  │
│  → Master Control for onboarding/offboarding                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 2: DOCS KB + PARITY                    │
│  RAG hybrid search • Capability maps • Pipelines • Error codes │
│  → Agent Brain + Automation Control Plane                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: ODOO 18 CE/OCA                      │
│  Core ERP • hr_expense • account • project • inventory         │
│  → Transactional system of record                               │
└─────────────────────────────────────────────────────────────────┘
```

### Migration Files (Apply in Order)

1. `20251220085409_kapa_docs_copilot_hybrid_search.sql` - Base RAG
2. `20251220_agentbrain_delta.sql` - Docs KB + Parity + Pipelines
3. `20251220_qms_lite_document_control.sql` - QMS-Lite
4. `20251220_process_runtime_ticketing.sql` - Process Runtime

---

## 14. References

- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)
- [SAP Help Portal](https://help.sap.com/docs/)
- [OCA Repositories](https://github.com/OCA)
- [Continue Dev](https://github.com/continuedev/continue)
- [Kapa.ai Architecture](https://kapa.ai/docs)
- [MasterControl QMS](https://www.mastercontrol.com/) (reference only)
