---
name: odoo_api_integration
description: Odoo 19 external API integration — JSON-RPC, controllers, FastAPI patterns
category: integration
priority: high
version: "1.0"
---

# API Integration

## JSON-RPC (Primary External API)
Endpoint: /jsonrpc
```python
import json, urllib.request
def rpc(url, service, method, *args):
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "call", "id": 1,
        "params": {"service": service, "method": method, "args": list(args)}
    }).encode()
    req = urllib.request.Request(url, payload, {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["result"]
```

## Authentication
```python
uid = rpc(url, "common", "authenticate", db, user, password, {})
```

## CRUD via execute_kw
```python
rpc(url, "object", "execute_kw", db, uid, pwd, model, method, args, kwargs)
# Methods: search, search_read, read, create, write, unlink, search_count
```

## HTTP Controllers
```python
from odoo import http
class MyController(http.Controller):
    @http.route('/my/endpoint', type='json', auth='user', methods=['POST'])
    def my_endpoint(self, **kw):
        return {'status': 'ok'}
```
- Controller file: name after module (my_module.py), NOT main.py
- type='json' for JSON-RPC, type='http' for standard HTTP
- auth='user' (logged in), 'public' (anyone), 'none' (no session)

## OCA FastAPI (Recommended for Agent APIs)
- Module: fastapi from OCA/rest-framework
- Pydantic type safety, OpenAPI auto-docs
- Native Odoo ORM access in routes
- Preferred over custom controllers for AI agent communication

## Context Flags (Suppress Side Effects)
```python
context = {
    'no_reset_password': True,      # No email invite
    'mail_create_nosubscribe': True, # No follower subscription
    'mail_notrack': True,           # No tracking messages
    'tracking_disable': True,       # No field tracking
}
```

## Odoo 19 API Notes
- Field: group_ids (not groups_id) on res.users
- Portal/Internal User are exclusive groups — cannot assign both
- Command tuples for relational writes: (4, id) add, (3, id) remove, (6, 0, [ids]) replace
