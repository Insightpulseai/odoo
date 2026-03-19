# n8n ↔ Odoo RPC Contract

**Last Updated:** 2026-02-20
**Scope:** Odoo JSON-RPC integration from n8n workflows
**Escape Hatch:** Raw HTTP/RPC when n8n Odoo node has edge-case bugs

---

## RPC Contract

### Allowed Methods (Allowlist)

| **Model** | **Method** | **Purpose** | **Idempotency** |
|-----------|----------|-------------|----------------|
| `res.partner` | `search`, `read` | Customer lookup | ✅ Safe |
| `account.move` | `search`, `read` | Invoice queries | ✅ Safe |
| `account.move` | `create` | Invoice creation | ⚠️ Use `external_id` |
| `hr.expense` | `create` | Expense creation | ⚠️ Use `external_id` |

**Forbidden Methods:**
- ❌ `write` on posted documents (violates SOR integrity)
- ❌ `unlink` (deletion) on any accounting records
- ❌ Direct SQL via `execute_kw`

### Idempotency Key Strategy

**Use `external_id` (ref) for create operations:**
```xml
<record id="invoice_ext_123" model="account.move">
  <field name="partner_id" ref="base.res_partner_1"/>
  <field name="move_type">out_invoice</field>
</record>
```

**n8n Pattern:**
```json
{
  "model": "account.move",
  "method": "create",
  "args": [{
    "move_type": "out_invoice",
    "partner_id": 123,
    "ref": "n8n-invoice-{{ $json.unique_id }}"  // External ID for dedup
  }]
}
```

**Deduplication Query Before Create:**
```json
{
  "model": "account.move",
  "method": "search",
  "args": [[["ref", "=", "n8n-invoice-{{ $json.unique_id }}"]]],
  "kwargs": {"limit": 1}
}
```

---

## Retry & Backoff Strategy

### Error Classification

| **HTTP Status** | **Error Type** | **Retry** | **Backoff** |
|----------------|---------------|-----------|-------------|
| 200 (success) | N/A | ❌ No | N/A |
| 400 (bad request) | Data error | ❌ No | Fix data |
| 401 (unauthorized) | Auth error | ❌ No | Refresh creds |
| 500 (server error) | Transient | ✅ Yes | Exponential (1s, 2s, 4s) |
| 503 (unavailable) | Transient | ✅ Yes | Exponential (1s, 2s, 4s) |

### n8n Retry Configuration

```json
{
  "retries": 3,
  "retryOnFail": true,
  "retryInterval": 1000,
  "maxRetryInterval": 5000
}
```

---

## Audit Trail

**Every Odoo RPC call MUST emit:**
```sql
INSERT INTO ops.run_events (run_id, event_type, event_data)
VALUES (
  <run_id>,
  'odoo_rpc_call',
  jsonb_build_object(
    'model', 'account.move',
    'method', 'create',
    'args', '[{...}]',
    'response_status', 200,
    'record_id', 456
  )
);
```

---

## HTTP Escape Hatch

**When n8n Odoo node fails, use raw HTTP:**
```json
{
  "name": "Odoo RPC via HTTP",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "https://erp.insightpulseai.com/jsonrpc",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "jsonrpc": "2.0",
      "method": "call",
      "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
          "{{ $env.ODOO_DB }}",
          "{{ $credentials.uid }}",
          "{{ $credentials.password }}",
          "account.move",
          "search_read",
          [[["ref", "=", "n8n-invoice-123"]]],
          {"fields": ["id", "name", "state"]}
        ]
      },
      "id": 1
    }
  }
}
```

---

## Cross-References

- **n8n Runbook:** `automations/n8n/docs/RUNBOOK.md`
- **Audit Trail:** `docs/architecture/AUTOMATION_AUDIT_TRAIL.md`
- **SSOT Policy:** `spec/odoo-ee-parity-seed/constitution.md`
