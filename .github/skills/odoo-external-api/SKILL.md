---
name: Odoo External API
description: Use when designing external integrations, XML-RPC/JSON-RPC clients, bridge services, or API contracts.
---

# Odoo External API

## When to use

- Building external services that read/write Odoo data
- Designing bridge modules for Pulser, MCP, or external platforms
- Implementing XML-RPC or JSON-RPC clients
- Modeling API contracts between Odoo and external systems
- Synchronizing data with Azure services or third-party platforms

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
import json

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

External integrations should follow this pattern:

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

## Do not

- Embed heavy business logic inside Odoo for external consumption
- Expose internal model names or field names to public APIs without abstraction
- Use `sudo()` in API endpoints to bypass access control
- Store external service credentials in Odoo database or `ir.config_parameter`
- Build synchronous long-running API calls (use queue_job for async processing)
