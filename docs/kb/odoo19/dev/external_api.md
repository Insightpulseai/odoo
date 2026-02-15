# External API: JSON-RPC / XML-RPC

## What it is

Odoo exposes its ORM via XML-RPC and JSON-RPC, allowing external applications to authenticate, query, and modify data.

## Key concepts

- **Endpoints:**
  - `common`: Authentication (login)
  - `object`: CRUD operations (execute_kw)
- **Protocol:** XML-RPC is the standard for external integrations. JSON-RPC is used primarily by the web client.

## Implementation patterns

### Python XML-RPC Client

```python
import xmlrpc.client

url = "https://my-odoo-instance.com"
db = "my_database"
username = "admin"
password = "my_api_key"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])
records = models.execute_kw(db, uid, password, 'res.partner', 'read', [ids], {'fields': ['name', 'country_id']})
```

## Gotchas

- **Datetimes:** XML-RPC handles dates differently than JSON. Ensure correct type conversion.
- **Many2one:** Read returns `[id, name]` tuple. Write expects `id` integer.
- **One2many/Many2many:** Write uses special command syntax (`(0, 0, val)`, `(4, id)`, etc.).

## References

- [Odoo External API Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/external_api.html)
