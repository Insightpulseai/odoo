---
name: Odoo External API
description: Design external integrations, XML-RPC/JSON-RPC clients, bridge services, or API contracts. Use when building systems that talk to Odoo from outside.
---

# Odoo External API

## Purpose

Build correct external integrations that read/write Odoo data via XML-RPC, JSON-RPC, or bridge controllers.

## When to use

- Building external services that read/write Odoo data
- Designing bridge modules for Pulser, MCP, or external platforms
- Implementing XML-RPC or JSON-RPC clients
- Modeling API contracts between Odoo and external systems
- Synchronizing data with Azure services or third-party platforms

## Inputs or assumptions

- Odoo 18 CE XML-RPC/JSON-RPC endpoints
- External services connect over HTTP
- Heavy logic lives outside Odoo (AI, OCR, orchestration)

## Source priority

1. Local bridge module code in `addons/`
2. Odoo 18 CE External API documentation
3. Project API contracts in `docs/contracts/`

## Workflow

1. Authenticate via XML-RPC or JSON-RPC
2. Use `execute_kw` for CRUD operations
3. For custom endpoints, create a thin bridge controller in Odoo
4. Keep heavy logic in the external service
5. Secure credentials via env vars / Key Vault

## Authentication

```python
import xmlrpc.client

url = "http://localhost:8069"
db = "odoo_dev"

# Authenticate
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, "user@example.com", "password", {})

# Get model proxy
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
```

## CRUD operations

```python
# Search
ids = models.execute_kw(db, uid, password, "res.partner", "search", [
    [("is_company", "=", True)]
], {"limit": 10})

# Read
records = models.execute_kw(db, uid, password, "res.partner", "read", [ids], {
    "fields": ["name", "email", "phone"]
})

# Search + Read (combined)
records = models.execute_kw(db, uid, password, "res.partner", "search_read", [
    [("is_company", "=", True)]
], {"fields": ["name", "email"], "limit": 10})

# Create
new_id = models.execute_kw(db, uid, password, "res.partner", "create", [{
    "name": "New Partner",
    "email": "new@example.com",
}])

# Update
models.execute_kw(db, uid, password, "res.partner", "write", [
    [new_id], {"phone": "+1234567890"}
])

# Delete
models.execute_kw(db, uid, password, "res.partner", "unlink", [[new_id]])
```

## JSON-RPC (alternative)

```python
import requests

def jsonrpc(url, method, params):
    return requests.post(url, json={
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }).json()

# Authenticate
result = jsonrpc(f"{url}/web/session/authenticate", "call", {
    "db": db, "login": "user@example.com", "password": "password"
})
session_id = result["result"]["session_id"]
```

## Bridge module design

External integrations follow this pattern:

```
External service → HTTP/JSON-RPC → Odoo controller or API → Odoo models
```

### In Odoo (thin bridge module)

```python
class ExternalBridge(http.Controller):
    @http.route("/api/v1/my_endpoint", type="json", auth="user")
    def handle_request(self, **kwargs):
        # Validate input
        # Call Odoo model methods
        # Return structured response
        return {"status": "ok", "data": result}
```

### Outside Odoo (external service)

Heavy logic (AI, OCR, orchestration) lives in external services that call Odoo's API:

```
Azure Function / ACA service → JSON-RPC → Odoo
Odoo → webhook/callback → External service
```

## Model introspection

```python
# List available fields
fields = models.execute_kw(db, uid, password, "res.partner", "fields_get", [], {
    "attributes": ["string", "type", "required"]
})
```

## Security considerations

- API credentials must come from env vars or Key Vault, never hardcoded
- Use dedicated API user accounts with minimal permissions
- Rate-limit external endpoints
- Validate all input in controller methods
- Log API access for audit trails

## Output format

Integration code with authentication, CRUD operations, and bridge controller stubs.

## Verification

- Authentication succeeds against target Odoo instance
- CRUD operations return expected data
- Bridge endpoints respond with correct JSON structure
- No credentials in source code

## Anti-patterns

- Embedding heavy business logic inside Odoo for external consumption
- Exposing internal model names or field names to public APIs without abstraction
- Using `sudo()` in API endpoints to bypass access control
- Storing external service credentials in Odoo database or `ir.config_parameter`
- Building synchronous long-running API calls (use `queue_job` for async processing)
- Hardcoding database names or URLs in integration code
