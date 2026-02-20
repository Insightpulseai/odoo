# Enterprise Bridge — Product Requirements Document

> **Version**: 1.0.0
> **Date**: 2026-02-20
> **Module**: `addons/ipai/ipai_enterprise_bridge/`
> **Status**: Installed (Phase 0)

---

## 1. Problem Statement

Odoo CE 19.0 lacks several capabilities that Odoo Enterprise ships by default (Document
management, Studio, Planning, Sign, IAP services). InsightPulseAI's target is ≥80% EE
feature parity using CE + OCA + custom connectors without paying for EE licenses.

`ipai_enterprise_bridge` is the central adapter that:
1. Routes EE feature requests to CE/OCA alternatives
2. Emits business events to Supabase for operational observability
3. Provides shared infrastructure (job queue, IoT registry) for other connectors
4. Adds domain-specific extensions (BIR tax fields, Scout retail fields)

---

## 2. Current Capabilities (Phase 0 — as built)

### 2.1 EE Feature Bridge Routing

**Model**: `EnterpriseBridgeConfig` (`models/enterprise_bridge.py`)

Maps EE feature slugs to CE/OCA alternatives:

| EE Feature | CE/OCA Replacement | Status |
|---|---|---|
| Studio | `web_studio_community` | Routed |
| Planning | `project_timeline` | Routed |
| Documents | DMS (`document_page`) | Routed |
| Sign | Disabled | Disabled |
| IoT | `ipai_iot_connector` (planned) | Partial |
| Helpdesk | `helpdesk_mgmt` (OCA) | Routed |
| Field Service | `fieldservice` (OCA) | Routed |

**Config stored in**: `ir.config_parameter` under `enterprise_bridge.*` keys
**Admin UI**: Settings → Technical → Enterprise Bridge

---

### 2.2 IAP Bypass Mixin

**Class**: `IAPBridgeMixin` (`models/iap_bridge.py`)

Intercepts Odoo IAP service calls and redirects them to direct alternatives:

| IAP Service | Bypass Target |
|---|---|
| `iap.account` (SMS) | Zoho SMS / direct gateway |
| `iap.account` (mail) | Zoho Mail SMTP |
| `iap.account` (ocr) | PaddleOCR-VL (local OCR service) |
| `iap.account` (enrich) | Disabled (no commercial enrichment) |

**Billing bypass**: No requests go to `iap.odoo.com`

---

### 2.3 Job Outbox Queue

**Model**: `IpaiJob` (`models/ipai_job.py`)

Async outbox for deferred processing:

| Field | Type | Description |
|---|---|---|
| `job_type` | char | `ai_analysis`, `sync_event`, `webhook_callback`, `data_export` |
| `state` | selection | `pending → processing → completed/failed` |
| `payload` | text (JSON) | Job input data |
| `result` | text (JSON) | Job output / error |
| `idempotency_key` | char | Deduplication key |
| `retry_count` | int | Max 3 retries |

**Cron**: Runs every 5 minutes (`data/scheduled_actions.xml`)

---

### 2.4 HR Expense Events

**Model mixin on** `hr.expense` and `hr.expense.sheet`

Events emitted to Supabase webhook on state changes:

| Event | Trigger |
|---|---|
| `expense.submitted` | Sheet state → `submit` |
| `expense.approved` | Sheet state → `approve` |
| `expense.rejected` | Sheet state → `refuse` |
| `expense.paid` | Sheet state → `post` |

**Idempotency**: `expense-{sheet_id}-{event_type}-{date_hash}`
**Cron**: Daily reconciliation cron to catch missed events

---

### 2.5 Project / Finance Task Events

**Model mixin on** `project.task`

Events emitted on stage change:

| Event | Trigger |
|---|---|
| `finance_task.created` | Task created in finance project |
| `finance_task.in_progress` | Stage: In Progress |
| `finance_task.submitted` | Stage: Review |
| `finance_task.approved` | Stage: Approved |
| `finance_task.filed` | Stage: Filed/Closed |
| `finance_task.overdue` | Deadline passed, still open |

---

### 2.6 IoT Device Registry + MQTT Bridge

**Model**: `IotDevice` (`models/iot_device.py`)

| Field | Description |
|---|---|
| `device_type` | `printer`, `scale`, `scanner`, `payment_terminal` |
| `ip_address` | Device IP on LAN |
| `mqtt_topic` | MQTT subscription topic |
| `last_ping` | Last successful ping timestamp |
| `state` | `online`, `offline`, `unknown` |

**MQTT**: Uses `paho-mqtt` in-process (Phase 0 exception — see constitution Rule 5)
**Views**: IoT Devices menu under Settings

---

### 2.7 Month-End Close Checklists

**Model**: `IpaiCloseChecklist` (`models/close_checklist.py`)

Period-based close workflows:

| Field | Description |
|---|---|
| `period` | Accounting period (month/year) |
| `items` | One2many: checklist items with `done`/`blocked` toggle |
| `state` | `draft → in_progress → completed / blocked` |
| `responsible_user_id` | Accountant assigned |

---

### 2.8 Company Approval Policies

**Model**: `IpaiPolicy` (`models/ipai_policy.py`)

Configurable governance rules:

| Policy | Description |
|---|---|
| `bill_approval_threshold` | Float: amount above which CFO approval required |
| `attachment_required` | Boolean: receipts mandatory for expense |
| `dms_linking` | Boolean: enforce DMS attachment before bill approval |

---

### 2.9 Scout Retail Product Fields

**Model mixin on** `product.template`

Added fields for Scout retail operations:

| Field | Description |
|---|---|
| `is_grocery` | Boolean: grocery item flag |
| `shelf_code` | Char: shelf/aisle code |
| `expiry_required` | Boolean: needs expiry tracking |
| `substitution_group` | Char: substitution group for stockouts |

---

### 2.10 BIR Tax Form Fields

**Model mixin on** `account.move` (invoices/bills)

| Field | Values |
|---|---|
| `bir_form_type` | `2307`, `2316`, `1601-C`, `2550M`, `2550Q` |

Used by BIR compliance automation (separate `ipai_finance_bir` module planned).

---

## 3. Dependencies

### 3.1 Odoo Modules (must be installed first)

| Module | Source | Required for |
|---|---|---|
| `base` | Odoo core | Always |
| `mail` | Odoo core | Event emitter |
| `auth_oauth` | Odoo core | OAuth provider config |
| `fetchmail` | Odoo core | Mail server config |
| `hr_expense` | Odoo core | Expense events |
| `maintenance` | Odoo core | IoT device model |
| `project` | Odoo core | Finance task events |
| `web` | Odoo core | Views |

### 3.2 Python Dependencies

| Package | Version | Used for |
|---|---|---|
| `requests` | ≥2.28 | Supabase webhook HTTP calls |
| `paho-mqtt` | ≥1.6 | IoT MQTT bridge (Phase 0) |

### 3.3 OCA Modules (optional, enhances routing)

| Module | OCA Repo | Enhances |
|---|---|---|
| `account_asset_management` | `account-financial-tools` | Asset bridge routing |
| `document_page` | `server-tools` | DMS bridge routing |
| `web_timeline` | `web` | Planning bridge routing |

---

## 4. Target Architecture (Phase 2+)

Per the Integration Bridge doctrine (`spec/ee-oca-parity/constitution.md`, Principle 1),
the long-term target decomposes the monolith:

```
ipai_enterprise_bridge (retained — EE shim + shared infra + business features)
├── Feature routing (stays)
├── IAP bypass (stays as mixin, or extracts to ipai_iap_bypass)
├── Job queue (stays — shared infra)
├── Close checklists (stays — business feature)
└── Policies (stays — business governance)

ipai_expense_bridge        ← extracted from expense event emitter
ipai_finance_bridge        ← extracted from finance task event emitter
ipai_iot_connector         ← extracted; calls iot-bridge-service (external)
iot-bridge-service         ← new standalone service (FastAPI + paho-mqtt)
ipai_vertical_retail       ← extracted; Scout retail product fields
ipai_finance_bir           ← BIR fields (already planned separately)
```

---

## 5. Acceptance Criteria

### Phase 0 (current) — Installation

- [ ] Module installs without errors: `state = installed` in `ir.module.module`
- [ ] All 10 views load in Odoo UI without 500 errors
- [ ] `requests` and `paho-mqtt` available in Odoo Python environment
- [ ] Job queue cron enabled; runs every 5 minutes
- [ ] No direct DB writes outside Odoo ORM

### Phase 1 (spec) — Spec Kit

- [x] `spec/enterprise-bridge/constitution.md` created
- [x] `spec/enterprise-bridge/prd.md` created
- [x] `spec/enterprise-bridge/plan.md` created
- [x] `spec/enterprise-bridge/tasks.md` created

### Phase 2+ (future) — Decomposition

- [ ] Scout retail fields moved to `ipai_vertical_retail`
- [ ] IoT MQTT moved to `iot-bridge-service`
- [ ] Each connector ≤1000 LOC Python
