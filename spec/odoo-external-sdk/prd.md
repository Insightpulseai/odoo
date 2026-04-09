# PRD: IPAI Odoo External SDK

> **Spec ID**: `odoo-external-sdk`
> **Status**: Draft
> **Created**: 2026-04-05
> **Owner**: Platform
> **Priority**: P1

---

## 1. Problem Statement

IPAI has multiple external consumers that need to interact with Odoo's data and operations: agent runtimes, copilot gateway, n8n workflows, Databricks pipelines, MCP tools, and future SaaS API surfaces. Today each consumer hand-rolls XML-RPC calls with raw `xmlrpc.client`, duplicating auth, error handling, and model knowledge.

Odoo's API surface is also migrating: Odoo 18 uses XML-RPC (`xmlrpc/2/common`, `xmlrpc/2/object`), Odoo 19 introduced the External JSON-2 API (bearer key, method-in-URL), and **Odoo 20 (fall 2026) is scheduled to remove legacy XML-RPC and JSON-RPC endpoints**. Any SDK started now must survive this transition.

## 2. Solution

Build an **external Python SDK** (`packages/odoo-sdk/`) that wraps Odoo's external API with transport abstraction, typed helpers, and retry/error normalization. Optionally, ship a **thin Odoo bridge addon** (`addons/ipai/ipai_odoo_bridge/`) only for server-side atomic methods that cannot be safely composed from client-side calls.

## 3. Design Principles

1. **External first**: The SDK is a Python package, not an Odoo addon.
2. **Transport-agnostic**: Callers use a stable surface; transport adapters handle version differences.
3. **Thin bridge only**: Odoo-side code exists only when atomicity or custom permissions require it.
4. **Version-aware**: SDK detects Odoo version at connect time and selects the correct transport.
5. **No ORM replacement**: The SDK calls Odoo's external API. It does not replicate ORM internals.
6. **custom_module_policy compliant**: Follows `ssot/odoo/custom_module_policy.yaml` boundary rules.

## 4. Architecture

```
                        +-----------------------+
                        |     Caller Code       |
                        |  (agent, pipeline,    |
                        |   MCP tool, gateway)  |
                        +-----------+-----------+
                                    |
                        +-----------v-----------+
                        |    OdooClient         |
                        |  .connect()           |
                        |  .models              |
                        |  .extract             |
                        |  .meta                |
                        +-----------+-----------+
                                    |
                   +----------------+----------------+
                   |                |                 |
          +--------v------+ +------v--------+ +------v--------+
          | RpcTransport18| | Json2Transport| | ExtractTransport|
          | xmlrpc/2/*    | | /api/v2/*     | | /api/extract/* |
          | db+uid+pwd    | | bearer key    | | bearer key     |
          +---------------+ +---------------+ +-----------------+
                   |                |                 |
                   +----------------+-----------------+
                                    |
                        +-----------v-----------+
                        |     Odoo Server       |
                        |  (18 or 19+)          |
                        +-----------------------+
                                    |
                        +-----------v-----------+
                        |  ipai_odoo_bridge     |
                        |  (thin addon, opt.)   |
                        |  custom atomic methods|
                        +-----------------------+
```

## 5. Package Structure

```
packages/odoo-sdk/
  pyproject.toml
  src/
    ipai_odoo_sdk/
      __init__.py
      client.py              # OdooClient entry point
      auth.py                # Session/auth handling
      transports/
        __init__.py
        base.py              # Transport interface (ABC)
        rpc18.py             # XML-RPC adapter (Odoo 18)
        json2.py             # JSON-2 adapter (Odoo 19+)
        extract.py           # Extract API adapter
      models/
        __init__.py
        base.py              # Generic model CRUD
        partner.py           # res.partner typed helpers
        sale_order.py        # sale.order typed helpers
        purchase_order.py    # purchase.order typed helpers
        account_move.py      # account.move typed helpers
        product.py           # product.product / product.template
      meta.py                # Model/field introspection
      errors.py              # Normalized error hierarchy
      retry.py               # Retry with backoff
      version.py             # Version detection + transport selection
  tests/
    conftest.py
    test_client.py
    test_transports.py
    test_models.py
    test_extract.py
```

## 6. Client Surface

### 6.1 Core Client

```python
from ipai_odoo_sdk import OdooClient

# Auto-detects version and selects transport
client = OdooClient.connect(
    url="https://erp.insightpulseai.com",
    db="odoo",
    # Odoo 18: username + password
    username="admin",
    password="...",
    # Odoo 19+: API key (preferred)
    api_key="...",
)

# Version info
client.version          # "18.0" or "19.0"
client.transport_name   # "rpc18" or "json2"
```

### 6.2 Model CRUD

```python
# search_read
partners = client.models.search_read(
    "res.partner",
    domain=[("is_company", "=", True)],
    fields=["name", "email", "phone"],
    limit=50,
)

# create
partner_id = client.models.create("res.partner", {
    "name": "ACME Corp",
    "email": "info@acme.com",
})

# write
client.models.write("res.partner", [partner_id], {
    "phone": "+1-555-0100",
})

# unlink
client.models.unlink("res.partner", [partner_id])

# fields_get
fields = client.models.fields_get("sale.order", attributes=["string", "type", "required"])
```

### 6.3 Typed Domain Helpers

```python
from ipai_odoo_sdk.models import Partner, SaleOrder, AccountMove

# Typed search
companies = client.partners.search(is_company=True, limit=10)
for p in companies:
    print(p.name, p.email)  # typed attributes

# Typed create
order = client.sale_orders.create(
    partner_id=42,
    lines=[
        {"product_id": 7, "product_uom_qty": 10, "price_unit": 99.00},
    ],
)

# Action methods (calls server-side method)
client.sale_orders.action_confirm(order.id)
```

### 6.4 Meta / Introspection

```python
# List accessible models
model_names = client.meta.models()

# Get fields for a model
fields = client.meta.fields("account.move")
```

### 6.5 Extract API (OCR)

```python
# Parse invoice
token = client.extract.parse_invoice(
    document=open("invoice.pdf", "rb").read(),
    webhook_url="https://n8n.insightpulseai.com/webhook/extract-result",
)

# Poll result (if no webhook)
result = client.extract.get_result(token)
```

## 7. Transport Interface

```python
# transports/base.py
from abc import ABC, abstractmethod

class OdooTransport(ABC):
    """Abstract transport for Odoo external API."""

    @abstractmethod
    def authenticate(self, db: str, **credentials) -> int:
        """Authenticate and return uid."""

    @abstractmethod
    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a model method."""

    @abstractmethod
    def execute_kw(self, model: str, method: str, args: list, kwargs: dict) -> Any:
        """Execute with keyword arguments."""
```

### 7.1 Odoo 18 RPC Adapter

- Endpoint: `{url}/xmlrpc/2/common`, `{url}/xmlrpc/2/object`
- Auth: `db + username + password` → returns `uid`
- Every call sends: `db, uid, password, model, method, args, kwargs`

### 7.2 Odoo 19+ JSON-2 Adapter

- Endpoint: `{url}/api/v2/{model}/{method}`
- Auth: Bearer API key header
- Model and method in URL path
- JSON request/response body
- Each call runs in its own SQL transaction

### 7.3 Extract API Adapter

- Endpoint: `{url}/api/extract/invoice/2/parse`, `{url}/api/extract/invoice/2/get_result`
- Auth: Bearer API key or database token
- Separate namespace from model CRUD

## 8. Thin Bridge Addon

**Package**: `addons/ipai/ipai_odoo_bridge/`
**Create only when needed for**:

| Justification | Example |
|---|---|
| Atomic multi-step operation | Confirm SO + create invoice + register payment in one transaction |
| Custom permissioned endpoint | Restricted search that filters by security rules not expressible in domain |
| Webhook receiver | Inbound webhook that creates/updates records with validation |
| Event publisher | Publishes Odoo events to external bus (Service Bus, n8n webhook) |
| JSON-2 compatibility shim | Custom method that normalizes behavior across 18 RPC and 19 JSON-2 |

### Bridge Addon Structure

```
addons/ipai/ipai_odoo_bridge/
  __manifest__.py
  models/
    bridge_mixin.py         # Shared bridge utilities
  controllers/
    api.py                  # Custom REST endpoints (FastAPI or http.route)
  security/
    ir.model.access.csv
  tests/
    test_bridge_api.py
```

### Bridge Addon Rules

1. **No SDK code inside**: The addon does not import or vendor the SDK.
2. **No orchestration**: Multi-call sequencing happens in the SDK or caller, not in the addon.
3. **Minimal surface**: Each method does one atomic thing. If it takes >50 lines, it's too fat.
4. **FastAPI preferred**: Use `OCA/rest-framework` FastAPI module for custom endpoints.
5. **Testable in isolation**: Bridge methods must have unit tests using `TransactionCase`.

## 9. Version Detection

```python
# version.py
def detect_and_connect(url, **credentials):
    """
    1. Try JSON-2 version endpoint first (Odoo 19+)
    2. Fall back to XML-RPC /xmlrpc/2/common version()
    3. Select transport based on detected version
    4. Authenticate with appropriate method
    """
```

### Version Matrix

| Odoo Version | Primary Transport | Auth Method | Extract API | Status |
|---|---|---|---|---|
| 18.0 | XML-RPC | db + uid + password | JSON-RPC2 | Supported |
| 19.0 | JSON-2 | Bearer API key | JSON-RPC2 | Supported |
| 20.0+ | JSON-2 only | Bearer API key | TBD | Planned (RPC removed) |

## 10. Error Hierarchy

```python
# errors.py
class OdooSDKError(Exception): ...
class AuthenticationError(OdooSDKError): ...
class AccessDeniedError(OdooSDKError): ...
class RecordNotFoundError(OdooSDKError): ...
class ValidationError(OdooSDKError): ...
class TransportError(OdooSDKError): ...
class VersionMismatchError(OdooSDKError): ...
class RateLimitError(OdooSDKError): ...
```

Transport-specific errors (XML-RPC `Fault`, HTTP 4xx/5xx) are caught and normalized into this hierarchy.

## 11. Retry Strategy

```python
# retry.py — configurable per-client
RetryConfig(
    max_retries=3,
    backoff_base=1.0,       # seconds
    backoff_factor=2.0,     # exponential
    retryable_errors=[TransportError, RateLimitError],
    non_retryable_errors=[AuthenticationError, AccessDeniedError, ValidationError],
)
```

## 12. Consumers

| Consumer | Usage Pattern | Transport |
|---|---|---|
| Copilot gateway (`ipai-copilot-gateway`) | Record read/search for grounding | Auto-detect |
| n8n workflows | CRUD via HTTP nodes | Auto-detect |
| Databricks pipelines | Bulk extract for lakehouse | RPC18 (current) → JSON-2 (migration) |
| MCP tools | Model CRUD as MCP tool functions | Auto-detect |
| Agent runtimes | Typed helpers for business operations | Auto-detect |
| CI/CD scripts | Health checks, module install verification | Auto-detect |

## 13. Non-Goals

- **Not an ORM replacement**: No query builder, no lazy loading, no relation traversal.
- **Not an EE parity module**: The SDK does not add Odoo business features.
- **Not a web framework**: No HTTP server, no middleware, no routing.
- **Not a migration tool**: Does not handle database schema or module upgrades.
- **No Extract API reimplementation**: Wraps Odoo's Extract API, does not replace it with Azure Document Intelligence (that's a separate bridge).

## 14. Acceptance Criteria

- [ ] `OdooClient.connect()` works against Odoo 18 (XML-RPC) and Odoo 19 (JSON-2)
- [ ] Version auto-detection selects correct transport
- [ ] All 7 CRUD methods work: `search`, `read`, `search_read`, `create`, `write`, `unlink`, `fields_get`
- [ ] `meta.models()` and `meta.fields()` return introspection data
- [ ] Extract API client can `parse_invoice` and `get_result`
- [ ] Error normalization maps XML-RPC faults and HTTP errors to SDK error hierarchy
- [ ] Retry logic works with configurable backoff
- [ ] At least 3 typed domain helpers (`Partner`, `SaleOrder`, `AccountMove`)
- [ ] Bridge addon (if created) has <100 lines of Python per method
- [ ] Test coverage >80% for SDK package
- [ ] Published as installable package (`pip install ipai-odoo-sdk` or path dependency)

## 15. Migration Path

```
Phase 1 (Now):    Build SDK with RPC18 transport against Odoo 18/19 XML-RPC
Phase 2 (Q3):     Add JSON-2 transport, test against Odoo 19 JSON-2 API
Phase 3 (Pre-20): Default to JSON-2, deprecate RPC18 adapter
Phase 4 (Odoo 20): Remove RPC18 adapter after Odoo 20 removes XML-RPC
```

## 16. Dependencies

| Dependency | Purpose | Version |
|---|---|---|
| `httpx` | HTTP client for JSON-2 and Extract API | >=0.27 |
| `xmlrpc.client` | XML-RPC client (stdlib) for Odoo 18 | stdlib |
| `pydantic` | Typed model wrappers | >=2.0 |
| `tenacity` | Retry with backoff | >=8.0 |

## 17. Security

- API keys and passwords are never logged, even at DEBUG level.
- SDK reads credentials from env vars or explicit parameters, never from files.
- Extract API document payloads are streamed, not buffered in memory for large files.
- Bridge addon endpoints require `group_system` or custom security group by default.

---

*Spec: odoo-external-sdk | Version: 1.0 | 2026-04-05*
