---
name: odoo19-external-api
description: Odoo 19 External JSON-2 API reference for HTTP integration with models, methods, authentication, and migration from XML-RPC/JSON-RPC
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/external_api.rst"
  extracted: "2026-02-17"
---

# Odoo 19 External JSON-2 API

New in Odoo 19. The JSON-2 API replaces the deprecated XML-RPC and JSON-RPC APIs (scheduled for removal in Odoo 20). It provides a clean, stateless HTTP interface for calling ORM model methods externally.

---

## 1. Overview

The JSON-2 API exposes part of the ORM Model API over HTTP via `POST /json/2/<model>/<method>`. All operations run in their own SQL transaction.

Key characteristics:
- RESTful-style endpoint (`POST` only)
- Bearer token authentication via API keys
- JSON request/response bodies
- One transaction per request (committed on success, rolled back on error)
- Standard Odoo security model (access rights, record rules, field access)

---

## 2. Request Format

### HTTP Method and URL

```
POST /json/2/<model>/<method>
```

| URL Component | Description |
|---|---|
| `model` | Technical model name (e.g., `res.partner`, `sale.order`) |
| `method` | Method to call (e.g., `search`, `read`, `search_read`, `create`, `write`, `unlink`) |

### Required Headers

| Header | Value | Notes |
|---|---|---|
| `Host` | Server hostname | Required by HTTP/1.1 |
| `Authorization` | `bearer <API_KEY>` | API key from user preferences |
| `Content-Type` | `application/json` | Charset recommended: `application/json; charset=utf-8` |

### Optional Headers

| Header | Value | Notes |
|---|---|---|
| `X-Odoo-Database` | Database name | Required when server hosts multiple DBs without dbfilter |
| `User-Agent` | Software identifier | Recommended for identification |

### Request Body (JSON Object)

| Field | Type | Description |
|---|---|---|
| `ids` | `array` of integers | Record IDs to operate on. Empty/omitted for `@api.model` methods |
| `context` | `object` | Optional context values, e.g., `{"lang": "en_US"}` |
| `*params` | any | Method-specific keyword arguments |

All arguments are **named** (keyword arguments). There is no positional argument support in JSON-2.

### Example: Raw HTTP Request

```http
POST /json/2/res.partner/search_read HTTP/1.1
Host: mycompany.example.com
X-Odoo-Database: mycompany
Authorization: bearer 6578616d706c65206a736f6e20617069206b6579
Content-Type: application/json; charset=utf-8
User-Agent: mysoftware python-requests/2.25.1

{
    "context": {
        "lang": "en_US"
    },
    "domain": [
        ["name", "ilike", "%deco%"],
        ["is_company", "=", true]
    ],
    "fields": ["name"]
}
```

---

## 3. Response Format

### Success Response (200)

Returns the JSON-serialized return value of the called method.

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

[
   {"id": 25, "name": "Deco Addict"}
]
```

### Error Response (4xx / 5xx)

Returns a JSON error object with the following fields:

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Fully qualified Python exception name |
| `message` | `string` | Exception message |
| `arguments` | `array` | Exception constructor arguments |
| `context` | `object` | Request context |
| `debug` | `string` | Full traceback for debugging |

#### Example: 401 Unauthorized

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json; charset=utf-8

{
  "name": "werkzeug.exceptions.Unauthorized",
  "message": "Invalid apikey",
  "arguments": ["Invalid apikey", 401],
  "context": {},
  "debug": "Traceback (most recent call last):\n  ..."
}
```

#### Common HTTP Error Codes

| Code | Meaning |
|---|---|
| `400` | Bad request (malformed JSON, missing parameters) |
| `401` | Unauthorized (invalid/missing API key) |
| `403` | Forbidden (access rights violation) |
| `404` | Not found (invalid model or method) |
| `500` | Internal server error |

---

## 4. API Key Configuration

### Creating an API Key

1. Log into Odoo
2. Go to **Preferences** > **Account Security** > **New API Key**
3. Provide a **description** and **duration** (max 3 months)
4. Click **Generate Key**
5. **Copy immediately** -- the key is shown only once

### Security Best Practices

- Set short durations for interactive use (typically 1 day)
- Maximum key lifetime: 3 months (must be rotated)
- Store keys securely; delete compromised keys immediately
- Use dedicated bot users for automated integrations
- Set empty passwords on bot users to disable login/password auth

---

## 5. Access Rights

The JSON-2 API uses standard Odoo security:
- Access rights (ir.model.access)
- Record rules (ir.rule)
- Field access control

**Interactive usage**: Use a personal account for discovery/one-time scripts.

**Automated integrations**: Create **dedicated bot users** with:
- Minimum required permissions
- Empty password (disables password login)
- Proper audit trail via log access fields

---

## 6. Database Header

| Scenario | `Host` Header | `X-Odoo-Database` |
|---|---|---|
| Single DB, no reverse proxy | Required (HTTP/1.1) | Not needed |
| Single DB, reverse proxy | Required for routing | Not needed if dbfilter configured |
| Multi-DB server | Required | Required if dbfilter doesn't resolve from Host |

Most HTTP libraries set the `Host` header automatically from the URL.

---

## 7. Transaction Handling

Each JSON-2 API call runs in its own SQL transaction:
- **Success**: transaction is committed
- **Error**: transaction is rolled back

**You cannot chain multiple calls in a single transaction.**

### Concurrency Risks

When making consecutive calls, other transactions may modify data between your calls. This is dangerous for:
- Reservations
- Payments
- Stock operations

### Solution: Single-Method Operations

Always prefer calling a single method that performs all related operations atomically:

```python
# BAD: Two separate transactions -- concurrent modification risk
ids = requests.post(".../sale.order/search", json={"domain": [...]}).json()
requests.post(".../sale.order/action_confirm", json={"ids": ids})

# GOOD: Single method, single transaction
# Use action_* methods that handle validation + confirmation atomically
requests.post(".../sale.order/action_confirm", json={"ids": [order_id]})
```

The `search_read` method is a built-in example: it performs `search` then `read` in a single transaction, avoiding missing-record errors from concurrent deletes.

---

## 8. Code Examples

### Python (requests library)

```python
import requests

BASE_URL = "https://mycompany.example.com/json/2"
API_KEY = "..."  # get from secure location
headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": "mycompany",
    "User-Agent": "mysoftware " + requests.utils.default_user_agent(),
}

# --- Search for companies matching "deco" ---
res_search = requests.post(
    f"{BASE_URL}/res.partner/search",
    headers=headers,
    json={
        "context": {"lang": "en_US"},
        "domain": [
            ("name", "ilike", "%deco%"),
            ("is_company", "=", True),
        ],
    },
)
res_search.raise_for_status()
ids = res_search.json()

# --- Read names for found records ---
res_read = requests.post(
    f"{BASE_URL}/res.partner/read",
    headers=headers,
    json={
        "ids": ids,
        "context": {"lang": "en_US"},
        "fields": ["name"],
    },
)
res_read.raise_for_status()
names = res_read.json()
print(names)
# Output: [{"id": 25, "name": "Deco Addict"}]
```

### Python -- Combined search_read (Preferred)

```python
import requests

BASE_URL = "https://mycompany.example.com/json/2"
API_KEY = "..."
headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": "mycompany",
}

# Single call -- search + read in one transaction
res = requests.post(
    f"{BASE_URL}/res.partner/search_read",
    headers=headers,
    json={
        "context": {"lang": "en_US"},
        "domain": [
            ("name", "ilike", "%deco%"),
            ("is_company", "=", True),
        ],
        "fields": ["name"],
    },
)
res.raise_for_status()
print(res.json())
```

### Python -- Create Records

```python
res = requests.post(
    f"{BASE_URL}/res.partner/create",
    headers=headers,
    json={
        "vals_list": [
            {"name": "New Partner", "email": "new@example.com", "is_company": True},
        ],
    },
)
res.raise_for_status()
new_ids = res.json()
print(f"Created partner IDs: {new_ids}")
```

### Python -- Write (Update) Records

```python
res = requests.post(
    f"{BASE_URL}/res.partner/write",
    headers=headers,
    json={
        "ids": [25],
        "vals": {"phone": "+1-555-0100"},
    },
)
res.raise_for_status()
```

### Python -- Delete Records

```python
res = requests.post(
    f"{BASE_URL}/res.partner/unlink",
    headers=headers,
    json={
        "ids": [25],
    },
)
res.raise_for_status()
```

### Python -- Get Current User Info

```python
# Retrieve the current user's context (including user ID)
res = requests.post(
    f"{BASE_URL}/res.users/context_get",
    headers=headers,
    json={},
)
res.raise_for_status()
user_context = res.json()
print(user_context)
```

### JavaScript (fetch API)

```javascript
(async () => {
    const BASE_URL = "https://mycompany.example.com/json/2";
    const API_KEY = "...";  // get from secure location
    const DATABASE = "mycompany";
    const headers = {
        "Content-Type": "application/json",
        "Authorization": "bearer " + API_KEY,
        "X-Odoo-Database": DATABASE,
    };

    // Search
    const reqSearch = {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
            context: { lang: "en_US" },
            domain: [
                ["name", "ilike", "%deco%"],
                ["is_company", "=", true],
            ],
        }),
    };
    const resSearch = await fetch(BASE_URL + "/res.partner/search", reqSearch);
    if (!resSearch.ok) throw new Error(await resSearch.json());
    const ids = await resSearch.json();

    // Read
    const reqRead = {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
            ids: ids,
            context: { lang: "en_US" },
            fields: ["name"],
        }),
    };
    const resRead = await fetch(BASE_URL + "/res.partner/read", reqRead);
    if (!resRead.ok) throw new Error(await resRead.json());
    const names = await resRead.json();
    console.log(names);
})();
```

### curl (Bash)

```bash
set -eu

DATABASE=mycompany
BASE_URL=https://$DATABASE.example.com/json/2
API_KEY="6578616d706c65206a736f6e20617069206b6579"

# Search
ids=$(curl $BASE_URL/res.partner/search \
    -X POST \
    --oauth2-bearer $API_KEY \
    -H "X-Odoo-Database: $DATABASE" \
    -H "Content-Type: application/json" \
    -d '{"context": {"lang": "en_US"}, "domain": [["name", "ilike", "%deco%"], ["is_company", "=", true]]}' \
    --silent \
    --fail
)

# Read
curl $BASE_URL/res.partner/read \
    -X POST \
    --oauth2-bearer $API_KEY \
    -H "X-Odoo-Database: $DATABASE" \
    -H "Content-Type: application/json" \
    -d "{\"ids\": $ids, \"context\": {\"lang\": \"en_US\"}, \"fields\": [\"name\"]}" \
    --silent \
    --fail-with-body
```

### curl -- search_read (Single Call)

```bash
curl https://mycompany.example.com/json/2/res.partner/search_read \
    -X POST \
    --oauth2-bearer "$API_KEY" \
    -H "X-Odoo-Database: mycompany" \
    -H "Content-Type: application/json" \
    -d '{
        "context": {"lang": "en_US"},
        "domain": [["is_company", "=", true]],
        "fields": ["name", "email"],
        "limit": 10
    }' \
    --silent \
    --fail-with-body | python3 -m json.tool
```

### curl -- Create

```bash
curl https://mycompany.example.com/json/2/res.partner/create \
    -X POST \
    --oauth2-bearer "$API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "vals_list": [
            {"name": "Test Partner", "email": "test@example.com"}
        ]
    }' \
    --silent \
    --fail-with-body
```

---

## 9. ORM Equivalents

The JSON-2 API calls are equivalent to internal ORM calls:

| JSON-2 Request | ORM Equivalent |
|---|---|
| `POST /json/2/res.partner/search {"domain": [...]}` | `env["res.partner"].search([...])` |
| `POST /json/2/res.partner/read {"ids": [1,2], "fields": ["name"]}` | `env["res.partner"].browse([1,2]).read(["name"])` |
| `POST /json/2/res.partner/search_read {"domain": [...], "fields": ["name"]}` | `env["res.partner"].search_read([...], ["name"])` |
| `POST /json/2/res.partner/create {"vals_list": [{...}]}` | `env["res.partner"].create([{...}])` |
| `POST /json/2/res.partner/write {"ids": [1], "vals": {...}}` | `env["res.partner"].browse([1]).write({...})` |
| `POST /json/2/res.partner/unlink {"ids": [1]}` | `env["res.partner"].browse([1]).unlink()` |
| `POST /json/2/sale.order/action_confirm {"ids": [1]}` | `env["sale.order"].browse([1]).action_confirm()` |
| `POST /json/2/res.users/context_get {}` | `env["res.users"].context_get()` |

Context is applied via `with_context`:

```python
# JSON-2 with context {"lang": "en_US"}
# is equivalent to:
env["res.partner"].with_context(lang="en_US").search([...])
```

---

## 10. Server Version Endpoint

```http
GET /web/version HTTP/1.1
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"version_info": [19, 0, 0, "final", 0, ""], "version": "19.0"}
```

---

## 11. Migrating from XML-RPC / JSON-RPC

Both XML-RPC (`/xmlrpc`, `/xmlrpc/2`) and JSON-RPC (`/jsonrpc`) are **deprecated** and scheduled for removal in **Odoo 20** (fall 2026).

### Key Differences

| Aspect | XML-RPC / JSON-RPC | JSON-2 |
|---|---|---|
| Auth | `uid` + password per call | Bearer API key |
| Database | Required parameter per call | `X-Odoo-Database` header (optional) |
| Endpoint | `/xmlrpc/2/object` | `/json/2/<model>/<method>` |
| Arguments | Positional (`args`) + keyword (`kw`) | Named keyword arguments only |
| IDs | First element of `args` | `ids` field in JSON body |
| Context | Keyword argument | `context` field in JSON body |

### Migration: Common Service

| Old Function | New Equivalent |
|---|---|
| `version()` | `GET /web/version` |
| `login(db, login, password)` | Not needed; use API key |
| `authenticate(db, login, password, ...)` | Not needed; use `res.users/context_get` |

### Migration: Database Service

| Old Function | New Equivalent |
|---|---|
| `create_database(...)` | `POST /web/database/create` |
| `duplicate_database(...)` | `POST /web/database/duplicate` |
| `drop(...)` | `POST /web/database/drop` |
| `dump(...)` | `POST /web/database/backup` |
| `restore(...)` | `POST /web/database/restore` (multipart) |
| `change_admin_password(...)` | `POST /web/database/change_password` |
| `list()` | `POST /web/database/list` (JSON-RPC) |
| `server_version()` | `GET /web/version` |
| `list_lang()` | `POST /json/2/res.lang/<method>` |
| `list_countries(...)` | `POST /json/2/res.country/<method>` |

### Migration: Object Service

Old pattern:

```python
from xmlrpc.client import ServerProxy
object_proxy = ServerProxy("https://example.com/xmlrpc/2/object")
result = object_proxy.execute_kw(
    "mydb", 2, "admin",
    "res.partner", "read",
    [[1, 2, 3], ["name"]],
    {"context": {"lang": "en_US"}, "load": None},
)
```

New JSON-2 pattern:

```python
import requests

result = requests.post(
    "https://example.com/json/2/res.partner/read",
    headers={
        "Authorization": "bearer <API_KEY>",
        # "X-Odoo-Database": "mydb",  # only when needed
    },
    json={
        "ids": [1, 2, 3],
        "context": {"lang": "en_US"},
        "fields": ["name"],
        "load": None,
    },
).json()
```

---

## 12. Dynamic Documentation

Each Odoo database exposes its available models, fields, and methods at `/doc`. For a database hosted at `https://mycompany.example.com`, the documentation is at:

```
https://mycompany.example.com/doc
```

---

## 13. Common Patterns

### Pagination with search_read

```python
res = requests.post(
    f"{BASE_URL}/res.partner/search_read",
    headers=headers,
    json={
        "domain": [("is_company", "=", True)],
        "fields": ["name", "email"],
        "limit": 20,
        "offset": 0,
        "order": "name ASC",
    },
)
```

### Counting Records

```python
res = requests.post(
    f"{BASE_URL}/res.partner/search_count",
    headers=headers,
    json={
        "domain": [("is_company", "=", True)],
    },
)
count = res.json()
```

### Calling Action Methods

```python
# Confirm a sale order
res = requests.post(
    f"{BASE_URL}/sale.order/action_confirm",
    headers=headers,
    json={
        "ids": [42],
    },
)
res.raise_for_status()
```

### Error Handling Pattern

```python
import requests

def call_odoo(model, method, **kwargs):
    res = requests.post(
        f"{BASE_URL}/{model}/{method}",
        headers=headers,
        json=kwargs,
    )
    if not res.ok:
        error = res.json()
        raise Exception(
            f"Odoo API error: {error['name']}: {error['message']}"
        )
    return res.json()

# Usage
partners = call_odoo(
    "res.partner", "search_read",
    domain=[("is_company", "=", True)],
    fields=["name"],
    limit=10,
)
```
