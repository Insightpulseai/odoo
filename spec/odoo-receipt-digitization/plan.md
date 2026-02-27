# Plan — Odoo Receipt Digitization

**Spec bundle**: `spec/odoo-receipt-digitization/`
**Implements**: `prd.md`

---

## Architecture Overview

```
Employee uploads JPEG receipt
        │
        ▼
  hr.expense form
  [Digitize Receipt] button
        │
        ▼
  action_digitize_receipt()   ← hr_expense_mixin.py
        │
        ├── 1. Find latest image attachment (ir.attachment, mimetype=image/*)
        ├── 2. Read IPAI_OCR_ENDPOINT_URL from ir.config_parameter
        ├── 3. base64-decode → image bytes
        ├── 4. POST to ocr.insightpulseai.com/ocr  ← fetch_image_text()
        ├── 5. parse_text(raw_text)  ← OCRResult(merchant, date, total, confidence)
        ├── 6. Write blank fields on hr.expense
        ├── 7. Create ipai.expense.ocr.run audit record
        └── 8. display_notification (success / low-confidence warning)

        │  (Lane B — async, no blocking)
        ▼
  Postgres WAL (wal_level=logical)
        │
        ▼
  Supabase ETL CDC worker
  (odoo_expense_pub publication)
        │
        ▼
  Iceberg destination (DO Spaces / MinIO)
  Tables: expense, expense_sheet, expense_attachment_meta, expense_ocr_run
```

---

## Lane A: Operational OCR Digitization

### Module: `ipai_expense_ocr` (extend existing)

#### New utility module: `utils/ocr_client.py`

Extracted from `scripts/ocr_extract.py` so both CLI and Odoo models can import it.

```python
# utils/ocr_client.py

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class OCRResult:
    merchant: Optional[str]
    receipt_date: Optional[str]
    total: Optional[float]
    confidence: float
    raw: Dict[str, Any]

# Regex patterns (unchanged from ocr_extract.py)
TOTAL_CURRENCY_RE = re.compile(...)
TOTAL_RE = re.compile(...)
CURRENCY_RE = re.compile(...)
DATE_RE = re.compile(...)

def normalize_amount(amount_str: str) -> float: ...

def parse_text(text: str) -> OCRResult:
    """Regex-parse receipt text → structured extraction."""
    ...

def fetch_image_text(image_bytes: bytes, endpoint_url: str) -> str:
    """POST image bytes to PaddleOCR FastAPI /ocr endpoint, return raw text."""
    import requests
    resp = requests.post(
        f"{endpoint_url.rstrip('/')}/ocr",
        files={"file": ("receipt.jpg", image_bytes, "image/jpeg")},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # ocr_service returns {"text": "...", "lines": [...], "confidence": 0.xx}
    return data.get("text") or "\n".join(
        line.get("text", "") for line in data.get("lines", [])
    )
```

#### Updated CLI: `scripts/ocr_extract.py`

```python
# After refactor: delegates to utils.ocr_client
from ..utils.ocr_client import OCRResult, parse_text  # noqa: F401

def main():
    # CLI unchanged — reads .txt, writes .json
    ...
```

#### New model mixin: `models/hr_expense_mixin.py`

```python
class HrExpenseOCR(models.Model):
    _inherit = "hr.expense"

    ocr_run_ids = fields.One2many("ipai.expense.ocr.run", "expense_id", readonly=True)
    ocr_run_count = fields.Integer(compute="_compute_ocr_run_count")
    ocr_confidence = fields.Float(compute="_compute_ocr_confidence")

    def action_digitize_receipt(self):
        # See prd.md §Error States for failure modes
        ...

    def action_open_ocr_runs(self):
        return act_window to ipai.expense.ocr.run filtered by expense
```

**Key design decisions:**
- `ocr_run_ids` One2many added to `hr.expense` via mixin (not modifying `hr_expense_ocr_run.py`)
- Confidence badge threshold: < 0.4 → warning notification, still fills fields
- `ir.config_parameter` key: `ipai.ocr.endpoint_url` (set by `scripts/odoo_config_mail_ai_ocr.py`)

#### New form view: `views/hr_expense_views.xml`

Two XPath injections into `hr_expense.hr_expense_view_form`:

1. **Header button** — visible in states `draft` and `reported`:
   ```xml
   <xpath expr="//header" position="inside">
     <button name="action_digitize_receipt" string="Digitize Receipt"
             type="object" class="oe_highlight" icon="fa-magic"
             attrs="{'invisible': [('state', 'in', ['posted', 'done'])]}" />
   </xpath>
   ```

2. **Stat button** — shows scan count, hidden if 0:
   ```xml
   <xpath expr="//div[@name='button_box']" position="inside">
     <button class="oe_stat_button" type="object"
             name="action_open_ocr_runs" icon="fa-eye"
             attrs="{'invisible': [('ocr_run_count', '=', 0)]}">
       <field name="ocr_run_count" widget="statinfo" string="OCR Scans"/>
     </button>
   </xpath>
   ```

#### Manifest changes

```python
"data": [
    "security/ir.model.access.csv",
    "views/hr_expense_views.xml",   # ADD — before menu.xml
    "views/menu.xml",
],
```

---

## Lane B: Analytics CDC via Supabase ETL

### What Supabase ETL does

Open-source Rust framework (https://supabase.github.io/etl) for Postgres CDC via logical
replication. Streams INSERT/UPDATE/DELETE events at-least-once with resume capability.
Does NOT require the hosted Supabase product.

### Prerequisites on Odoo Postgres (DO droplet, Postgres 16)

```sql
-- 1. Enable logical replication (one-time, requires postgres restart)
ALTER SYSTEM SET wal_level = 'logical';
-- Then: systemctl restart postgresql (or docker restart odoo-postgres-1)

-- 2. Verify
SHOW wal_level;  -- must return 'logical'

-- 3. Read-only replication user
CREATE ROLE odoo_cdc REPLICATION LOGIN PASSWORD '<generated>';
GRANT SELECT ON hr_expense, hr_expense_sheet, ir_attachment TO odoo_cdc;
GRANT SELECT ON ipai_expense_ocr_run TO odoo_cdc;

-- 4. Publication
CREATE PUBLICATION odoo_expense_pub FOR TABLE
  hr_expense,
  hr_expense_sheet,
  ir_attachment,
  ipai_expense_ocr_run;
```

### Config: `infra/supabase-etl/odoo-expense.toml`

```toml
[source]
type               = "postgres"
connection_string  = "${ODOO_PG_CDC_URL}"
slot_name          = "odoo_expense_etl_slot"
publication        = "odoo_expense_pub"

[destination]
type               = "iceberg"
catalog_uri        = "${ICEBERG_CATALOG_URI}"
warehouse          = "${ICEBERG_WAREHOUSE}"
namespace          = "${ICEBERG_NAMESPACE}"
s3_endpoint        = "${ICEBERG_S3_ENDPOINT}"
region             = "${ICEBERG_REGION}"
access_key_id      = "${ICEBERG_ACCESS_KEY_ID}"
secret_access_key  = "${ICEBERG_SECRET_ACCESS_KEY}"
s3_path_style      = "${ICEBERG_S3_PATH_STYLE}"

[[table]]
source      = "hr_expense"
destination = "expense"

[[table]]
source      = "hr_expense_sheet"
destination = "expense_sheet"

[[table]]
# Metadata-only — binary datas column excluded from Iceberg schema
source      = "ir_attachment"
destination = "expense_attachment_meta"

[[table]]
source      = "ipai_expense_ocr_run"
destination = "expense_ocr_run"
```

### Secrets required

| Secret | Where | Purpose |
|--------|-------|---------|
| `ODOO_PG_CDC_URL` | GitHub Actions + runtime | `postgres://odoo_cdc:<pw>@<host>:5432/odoo?sslmode=require` |
| `ICEBERG_CATALOG_URI` | GitHub Actions + runtime | REST catalog endpoint |
| `ICEBERG_WAREHOUSE` | GitHub Actions + runtime | S3 warehouse root path |
| `ICEBERG_NAMESPACE` | GitHub Actions + runtime | Target namespace (`odoo_ops`) |
| `ICEBERG_S3_ENDPOINT` | GitHub Actions + runtime | DO Spaces / MinIO endpoint |
| `ICEBERG_REGION` | GitHub Actions + runtime | S3 region (`sgp1`) |
| `ICEBERG_ACCESS_KEY_ID` | GitHub Actions + runtime | S3 access key |
| `ICEBERG_SECRET_ACCESS_KEY` | GitHub Actions + runtime | S3 secret key |
| `ICEBERG_S3_PATH_STYLE` | GitHub Actions + runtime | `true` (DO Spaces / MinIO) |

### Deployment

DO App Platform worker (1 instance, always-on). Connects to Odoo Postgres via private
network (same droplet or DO managed DB). Replication slot persists across restarts.

---

## File Summary

| File | Action | Module |
|------|--------|--------|
| `addons/ipai/ipai_expense_ocr/utils/__init__.py` | CREATE | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/utils/ocr_client.py` | CREATE | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/scripts/ocr_extract.py` | EDIT (import from utils) | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/models/hr_expense_mixin.py` | CREATE | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/models/__init__.py` | EDIT (+1 import) | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/views/hr_expense_views.xml` | CREATE | ipai_expense_ocr |
| `addons/ipai/ipai_expense_ocr/__manifest__.py` | EDIT (+1 data entry) | ipai_expense_ocr |
| `infra/supabase-etl/odoo-expense.toml` | CREATE | infra |
| `spec/odoo-receipt-digitization/prd.md` | CREATE | docs |
| `spec/odoo-receipt-digitization/plan.md` | CREATE | docs |
| `spec/odoo-receipt-digitization/tasks.md` | CREATE | docs |

No new Supabase Edge Functions. No n8n workflows changed. No schema migrations (model
uses existing `ipai.expense.ocr.run` + new mixin fields are computed-only).

---

## Supabase Feature Adoption

> Full adoption map: `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md`
> Spec: `spec/supabase-maximization/`

| Feature | This spec uses it for | SSOT location | Phase |
|---------|----------------------|---------------|-------|
| Edge Functions | OCR policy check post-digitization | `supabase/functions/expense-policy-check/` | Existing |
| Queues (PGMQ) | Future: enqueue digitize jobs (Phase 2) | `supabase/migrations/*_queues*` | Phase 2 |
| Storage | Future: receipt images → bucket (Phase 2) | `supabase/storage/receipts/` | Phase 2 |
| ETL → Iceberg | CDC from Odoo expense tables | `infra/supabase-etl/odoo-expense.toml` | Lane B |
| Realtime | Future: digitize progress events (Phase 2) | Application subscriptions | Phase 2 |

---

## Iceberg Landing Contract (Lane B)

| Property | Value |
|----------|-------|
| Namespace | `odoo_ops` |
| Table naming | snake_case, singular noun (e.g. `expense`, `expense_ocr_run`) |
| Schema evolution | Additive only (new nullable columns); breaking changes require new table version |
| Partitioning | By `date` (daily) where `date` column present; else by `_sdc_received_at` |
| Idempotency | ETL slot ensures at-least-once; downstream queries must be dedup-tolerant |
| Replay | Recreate slot + replay from oldest LSN if needed; no destructive ETL ops |
| Binary columns | Excluded from Iceberg schema (e.g. `ir_attachment.datas`) — see `expense_attachment_meta` |
| Source env vars | All as `ICEBERG_*` prefix; registered in `ssot/secrets/registry.yaml` |
