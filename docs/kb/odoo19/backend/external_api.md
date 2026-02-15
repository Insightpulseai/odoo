# Odoo 19 External API (JSON-2)

## Concept

Odoo enables external systems to interact with its data and logic via a JSON-2 API (replacing the older XML-RPC/JSON-RPC). This allows reading, writing, and executing logic on Odoo models from other applications.

## Key Changes in Odoo 19

- **Protocol:** JSON-2 (method and arguments in body, model in URL).
- **Authentication:** `Authorization: Bearer <api_key>` (replacing `login`/`password + uid`).
- **Database:** Passed via `X-Odoo-Database` header (if needed).
- **Endpoint Structure:** `POST https://<domain>/json/2/<model>/<method>`

## Core Methods

- `search([domain])`: Returns list of IDs.
- `search_read([domain], [fields])`: Returns list of dictionaries.
- `create([{'field': 'value'}])`: Returns ID of created record.
- `write([ids], {'field': 'value'})`: Returns `True`.
- `unlink([ids])`: Returns `True`.
- `execute_kw(...)`: Generic method execution (for custom methods).

## Authentication Flow

1. **Generate API Key:** In Odoo, go to Preferences -> Account Security -> Developer API Keys.
2. **Use Key:** Send as Bearer token. No session login required.

## Example (Python `requests`)

```python
import requests

headers = {
    "Authorization": "Bearer <YOUR_API_KEY>",
    # "X-Odoo-Database": "odoo-db-name" # Optional if domain maps to single DB
}

payload = {
    "ids": [1, 2, 3],
    "fields": ["name", "email"],
}

response = requests.post(
    "https://my-odoo.com/json/2/res.partner/read",
    headers=headers,
    json=payload
)
print(response.json())
```

## Agent Notes

- This implementation is **stateless**. Every request must include auth headers.
- Date/Datetime fields are returned as strings (UTC) and must be parsed.
- `execute_kw` is still the bridge for calling custom methods that are not strictly CRUD.

## Source Links

- [External JSON-2 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
