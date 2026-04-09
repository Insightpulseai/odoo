# Transport Design: Odoo 18 RPC → 19 JSON-2 Abstraction

> **Parent spec**: `spec/odoo-external-sdk/prd.md`
> **Key constraint**: SDK must survive Odoo 20 removing XML-RPC (fall 2026).

---

## Transport Interface Contract

```python
from abc import ABC, abstractmethod
from typing import Any

class OdooTransport(ABC):
    """
    Abstract transport for Odoo external API.
    Implementations handle protocol differences (XML-RPC, JSON-2).
    Callers never see transport internals.
    """

    @abstractmethod
    def authenticate(self) -> None:
        """Establish authenticated session. Raises AuthenticationError on failure."""

    @abstractmethod
    def execute_method(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        """Execute a model method and return the result."""

    @abstractmethod
    def server_version(self) -> str:
        """Return Odoo server version string (e.g., '18.0', '19.0')."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Transport identifier for logging/diagnostics."""
```

---

## RpcTransport18

**Protocol**: XML-RPC
**Endpoints**: `{base_url}/xmlrpc/2/common`, `{base_url}/xmlrpc/2/object`
**Auth**: `db + username + password` → `common.authenticate()` → returns `uid`
**Call pattern**: `object.execute_kw(db, uid, password, model, method, args, kwargs)`

```python
class RpcTransport18(OdooTransport):
    name = "rpc18"

    def __init__(self, url: str, db: str, username: str, password: str):
        self._url = url
        self._db = db
        self._username = username
        self._password = password
        self._uid: int | None = None
        self._common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self._object = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def authenticate(self) -> None:
        self._uid = self._common.authenticate(
            self._db, self._username, self._password, {}
        )
        if not self._uid:
            raise AuthenticationError("XML-RPC authentication failed")

    def execute_method(self, model, method, args=None, kwargs=None):
        return self._object.execute_kw(
            self._db, self._uid, self._password,
            model, method,
            args or [], kwargs or {},
        )

    def server_version(self) -> str:
        info = self._common.version()
        return info.get("server_version", "unknown")
```

### Odoo 18 RPC specifics

- `xmlrpc/2/common` exposes: `version()`, `authenticate(db, login, password, user_agent_env)`
- `xmlrpc/2/object` exposes: `execute_kw(db, uid, password, model, method, args, kwargs)`
- `db + uid + password` sent on **every call** (no session token)
- Response is native Python types (lists, dicts, ints, strings, booleans, `False` for null)
- Faults raise `xmlrpc.client.Fault` with `faultCode` and `faultString`
- No cursor/pagination — must use `limit` + `offset` manually
- API access restricted to Custom plan on Odoo-hosted; unrestricted on self-hosted

---

## Json2Transport19

**Protocol**: HTTP JSON
**Endpoints**: `{base_url}/api/v2/{model}/{method}`
**Auth**: `Authorization: Bearer {api_key}` header
**Call pattern**: POST JSON body with positional args and keyword args

```python
class Json2Transport19(OdooTransport):
    name = "json2"

    def __init__(self, url: str, api_key: str):
        self._url = url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=30.0,
        )

    def authenticate(self) -> None:
        # JSON-2 uses bearer key — validate by calling version
        resp = self._client.get(f"{self._url}/api/v2/version")
        if resp.status_code == 401:
            raise AuthenticationError("JSON-2 bearer key rejected")
        resp.raise_for_status()

    def execute_method(self, model, method, args=None, kwargs=None):
        url = f"{self._url}/api/v2/{model}/{method}"
        payload = {}
        if args:
            payload["args"] = args
        if kwargs:
            payload["kwargs"] = kwargs
        resp = self._client.post(url, json=payload)
        if resp.status_code == 404:
            raise RecordNotFoundError(f"{model}.{method} not found")
        if resp.status_code == 403:
            raise AccessDeniedError(f"Access denied: {model}.{method}")
        resp.raise_for_status()
        return resp.json().get("result")

    def server_version(self) -> str:
        resp = self._client.get(f"{self._url}/api/v2/version")
        resp.raise_for_status()
        return resp.json().get("server_version", "unknown")
```

### Odoo 19 JSON-2 specifics

- Model and method are **in the URL path**, not in the payload
- Auth via **bearer API key** (no db/uid/password triple)
- Each call runs in its **own SQL transaction** — critical implication:
  - Multi-step operations that need atomicity MUST use a single server-side method
  - This is why the bridge addon exists: to expose atomic methods
- Response format: `{"jsonrpc": "2.0", "result": ...}`
- Error responses include structured error info
- Odoo 20 will make this the **only** external API (XML-RPC removed)

---

## ExtractTransport

**Protocol**: HTTP JSON (JSON-RPC 2.0 variant)
**Endpoints**: `{base_url}/api/extract/invoice/2/parse`, `.../get_result`
**Auth**: Same as main transport (bearer key or db token)

```python
class ExtractTransport:
    """Separate transport for Odoo Extract API (OCR/document digitization)."""

    def __init__(self, url: str, api_key: str):
        self._url = url.rstrip("/")
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,  # OCR can be slow
        )

    def parse_invoice(self, document: bytes, webhook_url: str | None = None) -> str:
        """Submit document for parsing. Returns extraction token."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "document": base64.b64encode(document).decode(),
            },
        }
        if webhook_url:
            payload["params"]["webhook_url"] = webhook_url
        resp = self._client.post(
            f"{self._url}/api/extract/invoice/2/parse",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["result"]["document_token"]

    def get_result(self, token: str) -> dict:
        """Poll for extraction result."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"document_token": token},
        }
        resp = self._client.post(
            f"{self._url}/api/extract/invoice/2/get_result",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["result"]
```

### Extract API specifics

- Odoo Extract API is **separate** from the model CRUD API
- Uses **credit-based billing** on Odoo-hosted (self-hosted: unlimited if module installed)
- Supports: invoices, expenses, bank statements
- `parse` returns a `document_token`; `get_result` polls until `status == "done"`
- Optional `webhook_url` for push notification when extraction completes
- IPAI currently uses Azure Document Intelligence for OCR — Extract API is an **alternative path** for Odoo-native document workflows

---

## Version Detection Logic

```python
def auto_select_transport(url: str, **credentials) -> OdooTransport:
    """
    1. If api_key is provided, try JSON-2 first (Odoo 19+)
    2. If JSON-2 fails or username/password provided, try RPC18
    3. Return the working transport
    4. Raise VersionMismatchError if neither works
    """
    if "api_key" in credentials:
        try:
            t = Json2Transport19(url, credentials["api_key"])
            t.authenticate()
            return t
        except (AuthenticationError, TransportError):
            pass  # Fall through to RPC

    if "username" in credentials and "password" in credentials:
        t = RpcTransport18(url, credentials["db"], credentials["username"], credentials["password"])
        t.authenticate()
        return t

    raise VersionMismatchError(
        "Could not connect: provide api_key (Odoo 19+) or username+password+db (Odoo 18)"
    )
```

---

## Transaction Boundary Rules

| Scenario | Correct Pattern | Wrong Pattern |
|---|---|---|
| Read a single record | SDK `models.read()` | -- |
| Create + confirm SO | Bridge addon `bridge.create_and_confirm_so()` | Two SDK calls (not atomic) |
| Bulk import 100 partners | SDK `models.create()` in loop (each is its own txn) | -- |
| Create invoice + register payment | Bridge addon `bridge.invoice_and_pay()` | Two SDK calls (payment may fail, leaving orphan invoice) |
| Search + read (no mutation) | SDK `models.search_read()` | -- |

**Rule**: If the caller needs two or more **write operations** to succeed or fail together, expose a **single bridge method** on the Odoo side. The SDK calls that one method. This is not a limitation — it's a feature of clean API design.

---

## Error Mapping

| Transport Error | SDK Error |
|---|---|
| XML-RPC `Fault(1, ...)` | `AuthenticationError` |
| XML-RPC `Fault(2, ...)` | `AccessDeniedError` |
| XML-RPC `Fault(*, "...ValidationError...")` | `ValidationError` |
| HTTP 401 | `AuthenticationError` |
| HTTP 403 | `AccessDeniedError` |
| HTTP 404 | `RecordNotFoundError` |
| HTTP 429 | `RateLimitError` |
| HTTP 5xx | `TransportError` |
| Connection refused / timeout | `TransportError` |

---

*Transport Design v1.0 | 2026-04-05*
