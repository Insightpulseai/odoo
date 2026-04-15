# OData Bridge for Odoo CE 18 + OCA

> **Locked:** 2026-04-15
> **Renamed from "OData ↔ Odoo Mapping Position" — narrower scope, clearer expectations**
> **Authority:** this file (IPAI position on exposing Odoo data via OData)
> **Wire contracts:** [`platform/contracts/odata/v1/`](../../platform/contracts/odata/v1/) (separate layer)
> **Companion:** [`docs/architecture/cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md), [`docs/research/d365-data-model-inventory.md`](../research/d365-data-model-inventory.md)
> **Doctrine:** No-custom-default. Use OCA `fastapi` for any external API surface; build OData adapter only when a real OData consumer exists.

---

## Anti-goals (read these first)

```
- not full OData v4 protocol parity
- not a generic ORM exposure layer
- not a Dataverse clone
- not a write API in v1
- not a substitute for native Odoo JSON-RPC / XML-RPC
```

This is a **bridge**, not an OData server.

---

## TL;DR

```
Odoo CE 18      = JSON-RPC + XML-RPC native. NO native OData.
OCA fastapi     = Canonical external API surface (REST + Pydantic).
OData Bridge    = Read-only, tenant-scoped, narrow v1 conformance surface.
                  Built only when a NAMED consumer exists with explicit OData need.

When OData becomes needed:
  1) OCA fastapi route that emits OData-shaped JSON   (Path A — preferred)
  2) PG mirror to Fabric → Fabric SQL endpoint        (Path B — heavy)
  3) Third-party odoo-odata module                    (Path C — last resort, not OCA-blessed)
```

## v1 conformance surface (LOCKED)

```
SUPPORTED in v1:
  $metadata
  EntitySet listing
  $select
  $filter
  $top
  $skip
  $orderby
  $count

EXPLICITLY EXCLUDED from v1:
  $batch
  $delta
  $expand
  actions/functions
  writes (POST/PATCH/DELETE)
  generic model reflection
```

This is the line between a **shippable bridge** and an endless protocol project.

## v1 entity sets (LOCKED — first 3)

```
Projects      → project.project           (D365 PO equivalent: msdyn_project)
ProjectTasks  → project.task              (D365 PO equivalent: msdyn_projecttask)
TimeEntries   → account.analytic.line     (D365 PO equivalent: msdyn_timeentry)
```

Why these 3:
- Core PPM
- Map cleanly to D365 Project Operations concepts
- High-value for downstream consumers (Power BI, Customer Insights, etc.)
- Avoid the uglier finance writeback problem in v1
- Minimal surface for first contract test cycle

Wire contracts at [`platform/contracts/odata/v1/`](../../platform/contracts/odata/v1/).

## Build trigger (LOCKED)

Stay deferred unless ALL four are true:

```
[ ] Named consumer exists (specific Power BI / app / partner integration)
[ ] Consumer requires OData specifically (not just REST/JSON)
[ ] First 3 entity sets are sufficient for their use case
[ ] Owner and target milestone are assigned
```

If any are missing → stay deferred. Do not pre-build "in case."

---

## 1. Why this matters

Multiple Microsoft surfaces (Power BI, Power Platform, Excel, CDM tooling, Fabric Lakehouse, Dataverse virtual tables) consume **OData v4** as their preferred read protocol. If we want any of them to read Odoo data **without a custom connector per tool**, we expose OData.

We do **not** have an OData consumer today. But the doctrine alignment matters for:

- D365 displacement scenarios (Power BI dashboards previously fed by Dataverse OData)
- Marketplace listings that promise "BI-friendly access"
- Multitenant SaaS path (per `docs/architecture/multitenant-saas-target-state.md`) where customers expect OData
- CDM-aligned reporting (per `docs/architecture/cdm-and-analytics-bridge.md`)

---

## 2. What Odoo CE 18 offers natively

| Surface | Use | OData-compatible? |
|---|---|---|
| `/web/dataset/call_kw` (JSON-RPC) | Internal Odoo client + custom integrations | No |
| `/xmlrpc/2/object` (XML-RPC) | Legacy integrations | No |
| `/web/session/authenticate` | Session-based auth | No |
| Custom controllers (`http.route`) | Hand-rolled REST endpoints | Possible — manually emit OData JSON |
| ORM Python API | Server-side only | N/A |

**No native OData server** ships with Odoo CE 18. There's no flag, module, or config to "enable OData."

---

## 3. What OCA offers

| OCA repo / module | Purpose | OData fit |
|---|---|---|
| **`OCA/rest-framework`** → `fastapi` | FastAPI inside Odoo runtime; Pydantic schemas; declarative routes | ✅ Best base layer for an OData adapter |
| **`OCA/rest-framework`** → `base_rest` | Older REST framework, still maintained | OK; less ergonomic than fastapi |
| **`OCA/web-api`** | (relocated) | n/a 18.0 |
| **`OCA/connector`** | Outbound integration framework | Not OData; for ETL-style sync |
| **OCA `odoo_odata`** | Does not exist as official OCA module | — |

OCA's official position: use **`fastapi`** for new external APIs. Per CLAUDE.md doctrine §"Doctrine sentence" and per OCA governance.

---

## 4. Schema-level mapping (Odoo ↔ OData)

| OData v4 concept | Odoo equivalent | Notes |
|---|---|---|
| `EntitySet` | Odoo `model._name` (e.g. `res.partner`, `account.move`) | Each model = one EntitySet |
| `Entity` | individual record | Identified by `id` |
| `Property` | `fields.X` declaration on the model | Type mapping below |
| `Navigation property` | `Many2one`, `One2many`, `Many2many` | OData supports both directions |
| `Key property` | `id` (`fields.Integer` PK) | Use as `Edm.Int64` |
| `$filter` | Odoo domain (`[('field', '=', value)]`) | Translate operators ($eq → '=', $gt → '>', etc.) |
| `$select` | `read([...])` field list | Direct mapping |
| `$orderby` | `_order` class attr or `search_read(order=...)` | Direct |
| `$top`, `$skip` | `limit`, `offset` | Direct |
| `$expand` | nested `read()` of relational field | Manual unfolding |
| `$count` | `search_count(domain)` | Direct |
| `$metadata` | Generated from model registry | Hand-build or auto-generate from `_fields` dict |
| Annotations | `_description`, `help`, `Selection.label` | Map to `Description`, `LongDescription` annotations |

### Field-type mapping

| Odoo field | OData EDM type |
|---|---|
| `fields.Char` | `Edm.String` |
| `fields.Text` | `Edm.String` |
| `fields.Html` | `Edm.String` (annotation: `IsHtml`) |
| `fields.Integer` | `Edm.Int32` |
| `fields.Float` | `Edm.Decimal(precision, scale)` |
| `fields.Monetary` | `Edm.Decimal(16, 2)` |
| `fields.Boolean` | `Edm.Boolean` |
| `fields.Date` | `Edm.Date` |
| `fields.Datetime` | `Edm.DateTimeOffset` (UTC) |
| `fields.Binary` | `Edm.Stream` (separate URL) |
| `fields.Selection` | `Edm.String` + EnumType definition |
| `fields.Many2one` | Navigation property → target EntitySet |
| `fields.One2many` | Collection navigation property |
| `fields.Many2many` | Collection navigation with junction |

### Domain operator mapping

| OData `$filter` | Odoo domain operator |
|---|---|
| `eq` | `=` |
| `ne` | `!=` |
| `gt` | `>` |
| `ge` | `>=` |
| `lt` | `<` |
| `le` | `<=` |
| `contains(field, 'x')` | `('field', 'ilike', 'x')` |
| `startswith(field, 'x')` | `('field', '=ilike', 'x%')` |
| `field in (...)` | `('field', 'in', [...])` |
| `not field` | `('!', '|')` constructs |
| `and` / `or` | implicit AND in Odoo domains; explicit `'\|'` for OR |

---

## 5. Three implementation paths

### Path A — OCA `fastapi` adapter (PREFERRED)

Build a thin FastAPI router that:
- Reads a registry of Odoo models exposed as OData EntitySets
- Translates `$filter`, `$select`, `$orderby`, `$top`, `$skip`, `$expand` to Odoo `search_read` calls
- Emits OData v4 JSON responses with `@odata.context`, `@odata.nextLink`, `value` array
- Generates `$metadata` document from model registry
- Auths via Entra OIDC (per IPAI no-custom auth doctrine)

**Doctrine:** thinnest viable, pure Python, runs in Odoo worker, OCA-blessed base.

**Skeleton (illustrative):**

```python
# addons/ipai/ipai_odata_bridge/routers/odata.py
from fastapi import APIRouter, Request, Query
from odoo.addons.fastapi.dependencies import odoo_env

router = APIRouter(prefix="/odata/v4")

EXPOSED_MODELS = {
    "Partners": "res.partner",
    "Invoices": "account.move",
    "Products": "product.product",
}

@router.get("/{entityset}")
async def get_entityset(
    entityset: str,
    request: Request,
    env=Depends(odoo_env),
    filter_: str | None = Query(None, alias="$filter"),
    select: str | None = Query(None, alias="$select"),
    orderby: str | None = Query(None, alias="$orderby"),
    top: int = Query(50, alias="$top", le=1000),
    skip: int = Query(0, alias="$skip"),
    expand: str | None = Query(None, alias="$expand"),
):
    model_name = EXPOSED_MODELS.get(entityset)
    if not model_name:
        raise HTTPException(404, f"EntitySet {entityset} not found")

    domain = parse_odata_filter(filter_) if filter_ else []
    fields = select.split(",") if select else None
    order = parse_odata_orderby(orderby) if orderby else None

    records = env[model_name].search_read(
        domain=domain, fields=fields, order=order, limit=top, offset=skip
    )

    if expand:
        records = expand_relations(env, model_name, records, expand)

    return {
        "@odata.context": f"{request.base_url}odata/v4/$metadata#{entityset}",
        "@odata.count": env[model_name].search_count(domain),
        "value": records,
    }

@router.get("/$metadata")
async def get_metadata(env=Depends(odoo_env)):
    return Response(
        content=generate_csdl_xml(env, EXPOSED_MODELS),
        media_type="application/xml",
    )
```

**Pros:**
- ✅ OCA-native (no foreign module)
- ✅ Pure Python; testable; type-safe
- ✅ Per-tenant via FastAPI dependency injection
- ✅ Auth via Entra OIDC (FastAPI security)
- ✅ Doctrine-aligned (CE → OCA → thinnest `ipai_*` adapter)

**Cons:**
- ❌ You write the OData parser
- ❌ `$expand` semantics are non-trivial (recursive includes)
- ❌ `$metadata` CSDL XML must be generated correctly or Power BI fails

**Effort:** 2–3 weeks of focused work for Partners + Invoices + Products. Add models incrementally.

### Path B — PG mirror to Fabric, expose Fabric SQL endpoint

Per memory `feedback_fabric_mirroring_cli.md`: Fabric mirroring of `pg-ipai-odoo` already exists.

```
Odoo writes → pg-ipai-odoo → Fabric mirror (ACTIVE) → Fabric SQL endpoint
                                              ↓
                                       Power BI / Excel / Fabric notebooks
                                              ↓
                                       Reads via SQL (not OData directly)
```

Power BI's Fabric connector is OData-equivalent for our purposes. **Tier 2 reporting per `docs/ops/azure-boards-reporting.md` already uses this**.

**Pros:**
- ✅ Already partially in place
- ✅ Read-only by design (no risk of writeback)
- ✅ Fabric handles auth + access control
- ✅ Cross-system queries (joins with ADO Analytics, FinOps, etc.)

**Cons:**
- ❌ Latency (mirror lag, typically minutes)
- ❌ Snapshot view, not transactional
- ❌ Not true OData — Power BI sees it as Fabric SQL
- ❌ External tools that strictly require OData v4 endpoint (some legacy Microsoft Office connectors, third-party CDM consumers) won't work

**Effort:** ~zero new dev. Just configure Fabric report consumers.

### Path C — Third-party `odoo-odata` module (LAST RESORT)

Some community Odoo modules exist (search "odoo odata" on GitHub). Examples:
- `odoo/odoo-odata` (stale, 17.0 abandoned)
- Various single-author modules

**IPAI position: do not adopt** unless a customer contract forces it. Per OCA governance memory `feedback_oca_first_default.md`:
- Foreign modules require per-module verification
- Stale modules (>30 days no-commit) are forbidden
- Non-OCA modules add maintenance debt
- We can build the same in OCA `fastapi` with better quality

---

## 6. IPAI canonical position

```
Today:         No OData adapter built. No consumer needs it.
                Tier 2 reporting via Fabric mirror (Path B fragment) covers Power BI.

If a real OData consumer appears (e.g. a Power BI customer demands native OData feed,
or a Marketplace partner contract specifies OData):
                Build Path A — OCA fastapi router emitting OData JSON.
                Start with 3 entities: Partners, Invoices, Products.
                Add entities incrementally.

Never:         Adopt third-party odoo-odata modules without OCA review.
                Build a custom non-FastAPI HTTP layer for this.
                Build an OData WRITE surface (use Odoo JSON-RPC for writes; OData read-only).
```

---

## 7. CDM alignment (when we ship)

Per [`docs/architecture/cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md), if we want Odoo data to *appear as* CDM entities:

### 7.1 Finance / Sales / Procurement core

| Odoo model | CDM target entity | Naming hygiene to apply now |
|---|---|---|
| `res.partner` | `Account` / `Contact` | Use `account_name`, `parent_account_id` style aliases in OData adapter output |
| `account.move` | `Invoice` / `JournalLine` | Map `name` → `invoiceNumber`, `state` → `statusCode` |
| `product.product` | `Product` | `name` → `productName`, `default_code` → `productNumber` |
| `sale.order` | `SalesOrder` | `name` → `salesOrderNumber` |
| `purchase.order` | `PurchaseOrder` | `name` → `purchaseOrderNumber` |
| `account.account` | `MainAccount` | `code` → `mainAccountId`, `name` → `mainAccountDescription` |
| `res.company` | `Company` / `LegalEntity` | `name` → `companyName` |
| `res.currency` | `Currency` | `name` → `currencyCode` |

### 7.2 Project / PPM (D365 Project Operations parity)

Per `feedback_d365_project_operations_services_erp.md` doctrine: D365 PO = services/project-based delivery ERP. Parity = CE + OCA + thin bridge. PPM entities mapped:

| D365 / CDM target entity | Odoo CE 18 model | OCA module | Naming hygiene |
|---|---|---|---|
| `Project` (`msdyn_project`) | `project.project` | core CE | `name` → `projectName`, `partner_id` → `customerAccountId` |
| `ProjectTask` (`msdyn_projecttask`) | `project.task` | core CE | `name` → `subject`, `date_deadline` → `dueDate` |
| `ProjectTeamMember` (`msdyn_projectteam`) | `project.task.user` (assignment side) | core CE + `OCA/project` | `user_id` → `resourceId` |
| `BookableResource` (`bookableresource`) | `hr.employee` + `resource.resource` | core CE | `name` → `resourceName` |
| `BookableResourceBooking` (`bookableresourcebooking`) | `account.analytic.line` (timesheet) | `hr_timesheet` (CE) | `unit_amount` → `effort`, `date` → `bookingDate` |
| `TimeEntry` (`msdyn_timeentry`) | `account.analytic.line` (timesheet) | `hr_timesheet` (CE) | `unit_amount` → `duration` |
| `ProjectContract` (`msdyn_contract`) | `sale.order` (project-linked) | `OCA/project` `sale_project_link` | `name` → `contractNumber` |
| `ProjectContractLineItem` (`msdyn_contractlineitem`) | `sale.order.line` | core CE | `name` → `description`, `price_unit` → `unitPrice` |
| `Quote` (`quote`) for project | `sale.order` (state=draft) | core CE | `state='draft'` → `quoteStatus` |
| `JournalLine` (project actuals) (`msdyn_actual`) | `account.analytic.line` + `account.move.line` | core CE | Aggregate per project |
| `EstimateLine` (`msdyn_estimateline`) | `ipai_finance_ppm.estimate_line` (custom thin bridge) | `ipai_finance_ppm` | Per memory `project_finance_ppm` |
| `Forecast` / `BudgetVersion` | `ipai_finance_ppm.forecast_version` | `ipai_finance_ppm` | Per memory #4509 |
| `ResourceAvailability` | computed from `resource.calendar` + `hr.leave` | core CE | Computed view |
| `WorkBreakdownStructure` | `project.task` parent/child | core CE | Hierarchical via `parent_id` |
| `ProjectStage` (`msdyn_projectstage`) | `project.task.type` (stage) | core CE | `name` → `stageName` |
| `Skill` / `Resource Role` | `hr.skill` + `hr.job` | core CE + `OCA/hr` | `name` → `skillName` / `roleName` |
| `Expense` (`msdyn_expense`) | `hr.expense` | core CE | `name` → `expenseDescription`, `total_amount` → `amount` |

### 7.3 Three D365 PO shapes (per doctrine memory)

| D365 PO shape | IPAI implementation | OData EntitySet exposure |
|---|---|---|
| **Core** (lite project) | core CE `project` + `hr_timesheet` | `Projects`, `ProjectTasks`, `TimeEntries` |
| **Integrated with ERP** (primary IPAI benchmark) | core CE + OCA `project-reporting` + OCA `account-analytic` + `ipai_finance_ppm` | All Core entities + `ProjectContracts`, `EstimateLines`, `ForecastVersions`, `Actuals`, `Invoices` (project-linked) |
| **Manufacturing** (PO+Manufacturing) | Defer; not yet in scope | n/a |

### 7.4 Adjacent OCA modules (must verify before adopt per `oca-governance.md`)

| OCA repo | Module | Purpose for PPM |
|---|---|---|
| `OCA/project` | `project_timeline` | Gantt / timeline view |
| `OCA/project` | `project_status` | Custom project state machine |
| `OCA/project` | `project_template` | Template-based project creation |
| `OCA/project` | `project_task_material` | Materials linked to tasks |
| `OCA/project` | `project_milestone` | Absorbed into core 18 — verify before installing |
| `OCA/project` | `project_key` | Key field for cross-module reference |
| `OCA/project` | `project_role` | Resource role assignments |
| `OCA/project-reporting` | (multiple) | KPIs, burn-down, profitability |
| `OCA/account-analytic` | `account_analytic_*` | Project actuals + budgets |
| `OCA/hr-timesheet` | (multiple) | Timesheet enhancements |
| `OCA/contract` | `contract` | Recurring contracts (post-engagement) |

### 7.5 PPM EntitySet wiring (extends `EXPOSED_MODELS` in §5)

```python
EXPOSED_MODELS = {
    # Finance/Sales/Procurement
    "Partners": "res.partner",
    "Invoices": "account.move",
    "Products": "product.product",
    "SalesOrders": "sale.order",
    "PurchaseOrders": "purchase.order",
    "MainAccounts": "account.account",
    "Companies": "res.company",
    "Currencies": "res.currency",

    # Project / PPM (D365 Project Operations parity)
    "Projects": "project.project",
    "ProjectTasks": "project.task",
    "ProjectStages": "project.task.type",
    "TimeEntries": "account.analytic.line",
    "Resources": "resource.resource",
    "Employees": "hr.employee",
    "Expenses": "hr.expense",
    "ProjectContracts": "sale.order",          # filter contract_type=project
    "EstimateLines": "ipai_finance_ppm.estimate_line",
    "ForecastVersions": "ipai_finance_ppm.forecast_version",

    # CDM-friendly aliases (same model, different EntitySet name for CDM consumers)
    "BookableResources": "resource.resource",
    "BookableResourceBookings": "account.analytic.line",
}
```

### 7.6 Pulser PPM displacement angle

When IPAI displaces D365 Project Operations (per `feedback_d365_displacement_not_development.md`), the ship sequence is:

1. **R2 (2026-07-14)** — Core PPM EntitySets live (Projects, Tasks, TimeEntries, Expenses) via OCA fastapi
2. **R3 (2026-10-14)** — Integrated-with-ERP shape: ProjectContracts, EstimateLines, ForecastVersions exposed; first customer cuts over from D365 PO
3. **R4 (2026-12-15)** — Resource scheduling (BookableResource + Availability) live; partner-shippable

Per `project_acceleration_plan_20260414.md`. PPM EntitySet exposure is part of the R2 Recon-Agent-v0 + Finance slice scope.

This is **schema hygiene only** — applied in the FastAPI response shape, not in Odoo storage. Costs nothing today, simplifies CDM consumer mapping later.

---

## 8. Auth and tenancy

OData adapter inherits the multitenant pattern from [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md):

```
Request hits  /odata/v4/Partners
  ↓
Front Door injects tenant header (per multitenant routing)
  ↓
FastAPI dependency reads tenant context
  ↓
FastAPI dependency authenticates Entra OIDC token
  ↓
Odoo env switched to tenant's res.company context
  ↓
search_read filters by tenant_id where applicable
  ↓
OData JSON returned, scoped to tenant
```

Enforcement points:
- Auth must be Entra OIDC bearer token (no API keys after initial pilot)
- Tenant context never trusted from URL — always from validated token claims
- Read-only — POST/PUT/DELETE return 405 Method Not Allowed

---

## 9. Performance notes

| Concern | Mitigation |
|---|---|
| Large `$top` requests | Cap at 1000; default 50 |
| Heavy `$expand` chains | Limit depth to 2; reject `$expand=$expand=$expand` patterns |
| Repeated `$count` queries | Cache for 60s per tenant + filter combo |
| `$metadata` document generation | Cache aggressively; only invalidate on module upgrade |
| OData JSON serialization overhead | FastAPI uses `orjson` by default; sufficient |
| Worker exhaustion | Throttle per-tenant via FastAPI middleware |

---

## 10. Anti-pattern guard

- Don't expose every Odoo model — pick a curated set, expand on demand
- Don't let OData write — Odoo JSON-RPC handles writes, OData stays read-only
- Don't skip $metadata — Power BI and Excel require it for navigation
- Don't hand-roll without OCA `fastapi` — that's the doctrine path
- Don't adopt third-party odoo-odata without OCA verification
- Don't expose Odoo internal models (`ir.*`, `base.*`) — only business models

---

## References

- [OData v4 specification](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html)
- [OCA rest-framework](https://github.com/OCA/rest-framework)
- [OCA fastapi module](https://github.com/OCA/rest-framework/tree/18.0/fastapi)
- [Odoo 18 ORM API](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html)
- [`docs/architecture/cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md) — CDM consumer triggers
- [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md) — auth/tenancy pattern
- [`docs/research/d365-data-model-inventory.md`](../research/d365-data-model-inventory.md) — D365/CDM entity catalog

---

*Last updated: 2026-04-15*
