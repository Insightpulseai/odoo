# Bridge Addon Spec: ipai_odoo_bridge

> **Parent spec**: `spec/odoo-external-sdk/prd.md`
> **Addon path**: `addons/ipai/ipai_odoo_bridge/`
> **Create only when**: atomicity, custom permissions, webhooks, or event publishing require server-side code.

---

## When to Add a Bridge Method

| Trigger | Example | Method |
|---|---|---|
| Two+ writes must be atomic | Confirm SO + create invoice | `bridge.confirm_and_invoice(order_id)` |
| Security filter not expressible in domain | "My team's open invoices" with RLS | `bridge.my_team_invoices()` |
| Inbound webhook | n8n sends payment notification | `POST /api/bridge/payment_webhook` |
| Outbound event | Publish "invoice_posted" to Service Bus | `bridge._publish_event(event_type, payload)` |
| JSON-2 compat shim | Normalize behavior across 18/19 | `bridge.compat_method(...)` |

## When NOT to Add a Bridge Method

- Single model CRUD → use SDK directly
- Read-only search/read → use SDK directly
- Client-side retry/pagination → SDK handles this
- Orchestrating multiple external services → belongs in agent runtime, not Odoo

---

## Manifest

```python
# addons/ipai/ipai_odoo_bridge/__manifest__.py
{
    "name": "IPAI Odoo Bridge",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "Thin server-side bridge for external SDK atomic operations",
    "author": "InsightPulse AI",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
}
```

## Security

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_bridge_system,bridge.system,model_ipai_bridge_mixin,base.group_system,1,1,1,0
```

- Bridge methods default to `group_system` (admin only).
- Specific methods may be opened to `group_user` with explicit ACL rows.
- No public (unauthenticated) endpoints unless explicitly justified and documented.

## Controller Pattern (FastAPI preferred)

```python
# controllers/api.py
from odoo.addons.fastapi.dependencies import odoo_env
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/bridge", tags=["bridge"])

@router.post("/confirm_and_invoice")
async def confirm_and_invoice(
    order_id: int,
    env=Depends(odoo_env),
):
    """Atomic: confirm SO + create invoice in one transaction."""
    order = env["sale.order"].browse(order_id)
    order.ensure_one()
    order.action_confirm()
    invoice = order._create_invoices()
    return {"invoice_id": invoice.id, "state": invoice.state}
```

If `OCA/rest-framework` FastAPI is not available, fall back to `http.route`:

```python
# controllers/api.py (fallback)
from odoo import http
from odoo.http import request
import json

class BridgeController(http.Controller):
    @http.route("/api/bridge/confirm_and_invoice", type="json", auth="user", methods=["POST"])
    def confirm_and_invoice(self, order_id):
        order = request.env["sale.order"].browse(order_id)
        order.ensure_one()
        order.action_confirm()
        invoice = order._create_invoices()
        return {"invoice_id": invoice.id, "state": invoice.state}
```

## Method Size Rule

Each bridge method: **<50 lines of Python**. If longer, either:
1. The method is doing too much → split into smaller atomic units
2. The logic belongs in a dedicated `ipai_*` module, not the bridge

## Test Pattern

```python
# tests/test_bridge_api.py
from odoo.tests import TransactionCase

class TestBridge(TransactionCase):
    def test_confirm_and_invoice(self):
        order = self.env["sale.order"].create({...})
        # Call bridge method directly (not via HTTP in unit test)
        result = self.env["ipai.bridge.mixin"].confirm_and_invoice(order.id)
        self.assertTrue(result["invoice_id"])
        self.assertEqual(order.state, "sale")
```

## Event Publishing Pattern

```python
# models/bridge_mixin.py
class BridgeMixin(models.AbstractModel):
    _name = "ipai.bridge.mixin"
    _description = "Bridge utilities for external SDK"

    def _publish_event(self, event_type, payload):
        """
        Publish event to external bus.
        Current: webhook to n8n.
        Future: Azure Service Bus when integration_messaging bridge is deployed.
        """
        webhook_url = self.env["ir.config_parameter"].sudo().get_param(
            "ipai_bridge.event_webhook_url"
        )
        if webhook_url:
            import requests
            requests.post(webhook_url, json={
                "event_type": event_type,
                "payload": payload,
                "timestamp": fields.Datetime.now().isoformat(),
            }, timeout=5)
```

---

## Planned Bridge Methods (Initial)

| Method | Justification | Atomicity Required |
|---|---|---|
| `confirm_and_invoice(order_id)` | Two writes must succeed together | Yes |
| `register_payment(invoice_id, amount, journal_id)` | Payment + reconciliation atomic | Yes |
| `my_team_open_invoices(user_id)` | Custom security filter | No (read-only) |
| `bulk_partner_upsert(partners)` | Batch create/update with dedup | Yes |
| `health_check()` | SDK connectivity verification | No |

---

*Bridge Addon Spec v1.0 | 2026-04-05*
