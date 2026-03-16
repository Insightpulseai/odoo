# Enterprise Bridge — Implementation Plan

> **Version**: 1.0.0
> **Date**: 2026-02-20
> **Approach**: Phased — install first, decompose later

---

## Phase Overview

| Phase | Name | Goal | Status |
|---|---|---|---|
| Phase 0 | Install as-is | Module installed and stable | **Current** |
| Phase 1 | Spec Kit | Document current state + target architecture | **Current** |
| Phase 2 | Extract verticals | Move Scout retail fields to own addon | Planned |
| Phase 3 | Extract IoT | Move MQTT to standalone service | Planned |
| Phase 4 | Extract event connectors | ipai_expense_bridge, ipai_finance_bridge | Planned |

---

## Phase 0 — Install As-Is

**Goal**: Prove `ipai_enterprise_bridge` installs cleanly in the current environment
without breaking existing modules.

**Pre-conditions**:

1. **OCA deps check**: The following OCA modules should be installed or at minimum
   available (not required by manifest but enhance routing):
   - `account_asset_management` (account-financial-tools)
   - `document_page` (server-tools)
   - `web_timeline` (web)

2. **Python deps check**: Confirm `requests` and `paho-mqtt` present in container:
   ```bash
   docker exec odoo-web-1 python3 -c "import requests, paho.mqtt.client; print('deps ok')"
   ```

3. **Database**: Target database is `odoo_dev`

**Install command**:
```bash
docker exec odoo-web-1 python3 /usr/lib/python3/dist-packages/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --update=ipai_enterprise_bridge \
  --stop-after-init
```

**Verification**:
```bash
docker exec odoo-web-1 python3 -c "
import xmlrpc.client
common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
uid = common.authenticate('odoo_dev', 'admin', 'admin', {})
obj = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
r = obj.execute_kw('odoo_dev', uid, 'admin', 'ir.module.module', 'search_read',
  [[['name','=','ipai_enterprise_bridge']]], {'fields':['name','state']})
print(r)
"
```

Expected: `[{'name': 'ipai_enterprise_bridge', 'state': 'installed'}]`

---

## Phase 1 — Spec Kit (This Phase)

**Goal**: Create the spec bundle so future engineers understand the module's
purpose, constraints, and decomposition roadmap.

**Deliverables**:

| File | Status |
|---|---|
| `spec/enterprise-bridge/constitution.md` | ✅ Created |
| `spec/enterprise-bridge/prd.md` | ✅ Created |
| `spec/enterprise-bridge/plan.md` | ✅ This file |
| `spec/enterprise-bridge/tasks.md` | ✅ Created |

**Commit**:
```
docs(spec): add enterprise-bridge spec kit (constitution, prd, plan, tasks)
```

---

## Phase 2 — Extract Scout Retail Fields

**Goal**: Move `is_grocery`, `shelf_code`, `expiry_required`, `substitution_group`
from `ipai_enterprise_bridge` to a new `ipai_vertical_retail` module.

**Why now**: Scout retail fields have no architectural relation to EE bridging.
They belong in a vertical addon.

**Steps**:
1. Scaffold `addons/ipai/ipai_vertical_retail/__manifest__.py`
2. Move mixin from `ipai_enterprise_bridge/models/product_mixin.py`
3. Add `ipai_vertical_retail` to `ipai_enterprise_bridge` depends (migration shim)
4. Write Odoo migration script to move `ir.model.fields` if already installed
5. Update `config/ee_parity/ee_parity_mapping.yml` — retail entries reference new module
6. CI: module LOC check passes (bridge shrinks)

**Risk**: Low — fields are additive; no existing logic depends on them being in bridge.

---

## Phase 3 — Extract IoT / MQTT

**Goal**: Move MQTT broker connection out of Odoo process into `iot-bridge-service`.

**Architecture**:
```
Odoo (ipai_iot_connector)
  └─ HTTP POST → iot-bridge-service (FastAPI)
                    └─ MQTT → paho-mqtt → broker
```

**Steps**:
1. Create `services/iot-bridge/` — FastAPI app with paho-mqtt
2. Add Docker Compose service: `iot-bridge`
3. Scaffold `addons/ipai/ipai_iot_connector` — HTTP client only
4. Remove paho-mqtt from `ipai_enterprise_bridge` external_dependencies
5. Move `IotDevice` model to `ipai_iot_connector`
6. Write migration: no data migration needed (IoT device records carry over)
7. Update `.devcontainer/docker-compose.devcontainer.yml` to include `iot-bridge` service

**Risk**: Medium — depends on DevContainer Docker Compose changes (tested in dev only).

---

## Phase 4 — Extract Event Connectors

**Goal**: Move expense and finance task event emitters into dedicated connectors.

**Deliverables**:

| Connector | Extracted from | LOC target |
|---|---|---|
| `ipai_expense_bridge` | `hr.expense` mixin | <500 LOC |
| `ipai_finance_bridge` | `project.task` mixin | <400 LOC |

**Steps per connector**:
1. Scaffold new addon with manifest depends: `[hr_expense]` or `[project]`
2. Move event emitter mixin
3. Add connector to `ipai_enterprise_bridge` depends (ensures install order)
4. Update Supabase Edge Function routing if webhook endpoint changes
5. Verify idempotency keys still function after migration

**Risk**: Low-Medium — event emission is side-effect only; no UI dependency.

---

## Decision Log

| Decision | Rationale |
|---|---|
| Keep close checklists in ipai_enterprise_bridge | Business governance feature, not an integration. Extracting adds complexity with no benefit. |
| Keep company policies in ipai_enterprise_bridge | Same — governance, not an external integration. |
| Keep IAP bypass mixin in ipai_enterprise_bridge | Core EE shim functionality; small surface area. May extract to `ipai_iap_bypass` in Phase 4+. |
| paho-mqtt allowed in Phase 0 | Stability first. IoT bridge extraction is Phase 3, after core business events are proven. |
| BIR fields stay in `ipai_finance_bir` | Already planned as separate module. Not in scope here. |
