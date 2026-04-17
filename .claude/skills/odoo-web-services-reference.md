---
source: https://www.odoo.com/documentation/18.0/developer/howtos/web_services.html
version: odoo-18-ce
enhanced: 2026-04-12T00:00:00Z
index_target: product-help-index
ipai_reviewed: false
---

> IPAI context: Odoo **18 CE** (not EE, not 19). ACA deployment.
> Connector lives in `agent-platform/` — calls Odoo via JSON-RPC only. No direct DB access from external connectors.
> Auth: session-based token or API key stored in Azure Key Vault. Never in code or environment variables.

# Web Services — Odoo 18 CE (IPAI annotated)

## Overview

The web-service module exposes a common interface for all web services:
- **XML-RPC** — legacy, avoid for new code
- **JSON-RPC** — preferred for all IPAI connector work

> OCA-first: `connector` and `connector-base` (OCA) provide a structured framework for external system
> connectors with retry, logging, and checkpoint support. Evaluate before writing a custom JSON-RPC wrapper.

Business objects are accessible via the distributed object mechanism. They can be modified via the
client interface with contextual views.

---

## Connection

### Endpoint

```
https://<odoo-host>/web/dataset/call_kw       # method calls
https://<odoo-host>/web/dataset/call_kw_multi  # batch calls
https://<odoo-host>/web/session/authenticate   # session auth
```

> Azure ACA: IPAI Odoo host is bound to `erp.insightpulseai.com` via direct ACA custom-domain.
> Internal connector calls from `agent-platform` use the ACA internal FQDN — not the public domain.
> PG Flex: `pg-ipai-odoo.postgres.database.azure.com` — never called directly from `agent-platform`.

### Authentication — API key (preferred for service accounts)

```python
import xmlrpc.client  # avoid for new code — use JSON-RPC

# JSON-RPC with API key (Odoo 16+, confirmed Odoo 18 CE)
import requests

url = "https://erp.insightpulseai.com"
api_key = get_secret("odoo-api-key")  # Azure Key Vault

# Authenticate
session = requests.Session()
auth = session.post(f"{url}/web/session/authenticate", json={
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": "odoo",
        "login": "service_account@insightpulseai.com",
        "password": api_key,
    }
})
```

> ⚠️ REVIEW NEEDED: Confirm whether Odoo 18 CE supports bearer token auth without the Enterprise
> `auth_api_key` module. OCA alternative: `auth_api_key` from OCA/server-auth.

### Authentication — XML-RPC (legacy reference only)

```python
# DO NOT USE for new IPAI connector code — reference only
import xmlrpc.client
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
```

> IPAI rule: XML-RPC is legacy. All new connector code in `agent-platform` uses JSON-RPC.
> If you see XML-RPC in existing `ipai_*` modules, flag for migration.

---

## Calling methods

### Read records

```python
def odoo_call(session, url, db, uid, model, method, args, kwargs=None):
    return session.post(f"{url}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": method,
            "args": args,
            "kwargs": kwargs or {},
        }
    }).json()["result"]

# Search and read invoices
invoices = odoo_call(
    session, url, db, uid,
    model="account.move",
    method="search_read",
    args=[[["move_type", "=", "out_invoice"], ["state", "=", "posted"]]],
    kwargs={"fields": ["name", "partner_id", "amount_total", "invoice_date"], "limit": 100}
)
```

> IPAI sync rule: Odoo-owned domains (invoices, journal entries, payments) are never written from
> `agent-platform`. Read-only via JSON-RPC. Writes go back through the Odoo UI or a controlled
> Odoo addon — never from external connectors.
> See: `pulser-run-trace` for logging connector calls as run events.

### Write records

```python
# Create a record (only for models Pulser owns — not finance/accounting)
new_id = odoo_call(
    session, url, db, uid,
    model="project.task",
    method="create",
    args=[{"name": "New task", "project_id": 1}]
)

# Update a record
odoo_call(
    session, url, db, uid,
    model="project.task",
    method="write",
    args=[[new_id], {"stage_id": 3}]
)
```

> ⚠️ Odoo 18 CE breaking change: `write()` on posted `account.move` raises `UserError`.
> You cannot modify a posted journal entry — only draft entries can be written.
> Migration: use `button_draft()` to reset to draft before writing, then `action_post()` to re-post.
> IPAI rule: `agent-platform` must never call `button_draft()` on posted finance records.

---

## Odoo 18 CE API changes affecting connectors

> Odoo 18 CE breaking change: `_cr`, `_context`, `_uid` deprecated on model instances.
> Use `self.env.cr`, `self.env.context`, `self.env.uid` instead.
> Affects any custom `ipai_*` modules that call `self._cr.execute()` directly.

> Odoo 18 CE breaking change: `fields.Datetime.now()` returns a timezone-aware datetime.
> Ensure all datetime comparisons in domain filters use `fields.Datetime.now()` — not `datetime.now()`.

> Odoo 18 CE change: `search_count()` domain parameter is now required (no default empty domain).
> Replace `model.search_count()` with `model.search_count([])` explicitly.

---

## Batch operations

```python
# search_read with pagination — use for large datasets
BATCH_SIZE = 500
offset = 0
all_records = []

while True:
    batch = odoo_call(
        session, url, db, uid,
        model="account.analytic.line",
        method="search_read",
        args=[[["date", ">=", "2026-01-01"]]],
        kwargs={"fields": ["date", "amount", "account_id"], "limit": BATCH_SIZE, "offset": offset}
    )
    if not batch:
        break
    all_records.extend(batch)
    offset += BATCH_SIZE
```

> IPAI sync pattern: use `write_date` for incremental sync, not full re-read.
> Checkpoint last `write_date` in `ops.sync_checkpoints` (platform/Supabase SSOT).
> On failure, replay from last checkpoint — do not re-read full dataset.

---

## Error handling

```python
response = session.post(f"{url}/web/dataset/call_kw", json={...})
data = response.json()

if "error" in data:
    error = data["error"]
    # error["data"]["name"] = exception class name
    # error["data"]["message"] = human-readable message
    # error["data"]["debug"] = full traceback (dev mode only)
    raise OdooConnectorError(
        code=error["code"],
        name=error["data"]["name"],
        message=error["data"]["message"],
    )
```

> IPAI failure handling: map Odoo connector errors to the `pulser-self-heal` failure taxonomy:
> - `AccessError` → `F-POL` (policy violation) — hard stop, do not retry
> - `UserError` → `F-TOOL` — retry once, then escalate
> - `ValidationError` → `F-VAL` — retry with corrected payload, then escalate
> - Network timeout → `F-INF` — retry with backoff
> Emit failure class as part of run event (see `pulser-run-trace`).

---

## OCA modules relevant to Odoo connectors

| Module | OCA repo | Purpose |
|---|---|---|
| `connector` | `OCA/connector` | Base connector framework with retry and checkpoint |
| `connector_base_product` | `OCA/connector` | Product sync helpers |
| `auth_api_key` | `OCA/server-auth` | API key auth for external callers |
| `base_import_async` | `OCA/server-tools` | Async import for large datasets |
| `queue_job` | `OCA/queue` | Job queue for async Odoo operations |

> IPAI rule: evaluate `OCA/connector` before writing a custom JSON-RPC wrapper.
> `queue_job` from OCA is the standard pattern for async Odoo operations triggered from `agent-platform`.

---

## IPAI connector pattern summary

```
agent-platform (Azure ACA)
  → JSON-RPC over HTTPS → erp.insightpulseai.com (ACA direct ingress)
  → Odoo 18 CE
  → Odoo DB (pg-ipai-odoo — PG Flex, SEA)

Rules:
- Read-only for finance/accounting domain
- Write allowed for project, expense (draft only), and custom ipai_* models
- All connector calls emit run events (pulser-run-trace)
- Failures map to pulser-self-heal taxonomy
- Sync cursors stored in ops.sync_checkpoints (platform/Supabase)
- API key in Azure Key Vault — DefaultAzureCredential auth
```
