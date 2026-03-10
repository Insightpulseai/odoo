# Enterprise Bridge Constitution

> **Version**: 1.0.0
> **Ratified**: 2026-02-20
> **Scope**: `ipai_enterprise_bridge` and all future bridge/connector splits derived from it
> **Parent**: `spec/ee-oca-parity/constitution.md` (Principle 1 — Strict Taxonomy)

---

## Non-Negotiable Rules

### Rule 1: Odoo = System of Record (SoR)

**Statement**: Odoo is the authoritative source for all business entities (expenses, invoices,
projects, employees, products). Supabase is the SSOT for operational run state, events,
artifacts, and audit logs.

**Enforcement**:
- No direct writes to `odoo.*` PostgreSQL tables from outside Odoo.
- All writes to Odoo go through `xmlrpc.client` (XML-RPC) or `requests` (JSON-RPC).
- Supabase stores immutable event records; Odoo stores mutable business records.

---

### Rule 2: Bridge Never Touches the Odoo DB Directly

**Statement**: The enterprise bridge (and any future derived services) must never use
`psycopg2` or any direct PostgreSQL connection to the Odoo database.

**Allowed**:
- `odoo.addons.*` Python models (inside Odoo process)
- XML-RPC: `xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')`
- JSON-RPC: `POST http://localhost:8069/web/dataset/call_kw`

**Forbidden**:
- `psycopg2.connect(dsn="dbname=odoo ...")`  from outside Odoo
- Direct `COPY`, `INSERT`, `UPDATE` on `odoo.*` schema

---

### Rule 3: Every Integration Capability = One Connector Addon

**Statement**: Each external-service integration must be a separate `ipai_*` Odoo addon.
No bundling of unrelated integrations into one module.

**Target decomposition** (long-term):

| Current capability | Target addon | Type |
|---|---|---|
| IAP bypass | `ipai_iap_bypass` | Thin Connector |
| HR Expense events | `ipai_expense_bridge` | Thin Connector |
| Finance task events | `ipai_finance_bridge` | Thin Connector |
| IoT / MQTT | `ipai_iot_connector` + `iot-bridge-service` | Connector + Service |
| Job outbox queue | `ipai_job_queue` | Shared infra addon |
| EE feature routing | remains in `ipai_enterprise_bridge` | EE shim |
| Close checklists | remains in `ipai_enterprise_bridge` | Business feature |
| Company policies | remains in `ipai_enterprise_bridge` | Business governance |
| Scout retail fields | `ipai_vertical_retail` | Vertical addon |
| BIR tax fields | `ipai_finance_bir` | Finance addon |

**Phasing**: The current monolithic module is accepted as Phase 0 (stability). Splits happen
in Phase 2+ per `plan.md`.

---

### Rule 4: Events Are Immutable (Append-Only)

**Statement**: Any event emitted to Supabase (expense, finance task, close, policy violation)
must be written once and never mutated.

**Enforcement**:
- Supabase tables receiving events must have `INSERT`-only RLS (no `UPDATE`/`DELETE`).
- Each event must carry an `idempotency_key` (format: `<model>-<record_id>-<event_type>-<hash>`).
- Duplicate events (same idempotency key) are silently ignored by the bridge, not errored.

---

### Rule 5: No paho-mqtt in the Core Odoo Process (Long-Term)

**Statement**: MQTT broker connections must not run inside the Odoo worker process. They
belong in a separate service container.

**Current exception (Phase 0)**: `paho-mqtt` is listed as an `external_dependencies` in
`ipai_enterprise_bridge` and runs in-process. This is accepted for initial installation
stability only.

**Target (Phase 3)**: `iot-bridge-service` is a standalone FastAPI/MQTT container.
`ipai_iot_connector` is a thin Odoo addon (<200 LOC) that sends HTTP to the service.

---

### Rule 6: Thin Connectors Are < 1000 LOC Python

**Statement**: Any `ipai_*` connector derived from this module must stay under 1,000 lines
of Python. Business logic belongs in Odoo models or the bridge service, not in the connector.

**Enforcement**: CI gate `scripts/ci/check_parity_boundaries.sh` flags violations.

---

### Rule 7: Secrets in Environment Variables Only

**Statement**: API keys, Supabase JWT tokens, webhook signing secrets, and MQTT credentials
must never be hardcoded in Python or XML. They must be read from environment variables or
Odoo system parameters (stored encrypted).

**Allowed locations**:
- `os.environ.get('SUPABASE_URL')`
- `self.env['ir.config_parameter'].sudo().get_param('ipai.supabase_url')`

**Forbidden**:
- Hardcoded strings: `url = "https://abc.supabase.co"`
- Committed `.env` files

---

## Rationale

`ipai_enterprise_bridge` was built as a monolith to accelerate initial delivery. The constitution
defines the doctrine so future engineers know:

1. What the current module _is_ (EE shim + shared infra + business features)
2. What it is _not_ (per-capability connectors, which come later)
3. Where each capability _should_ eventually live

This avoids the module growing further in scope and provides a clear refactoring roadmap.

---

## Amendment Process

Amendments require:
1. Proposal in a GitHub PR against this file
2. Review by the `@ipai/platform` team
3. Merge only on main branch with passing CI
