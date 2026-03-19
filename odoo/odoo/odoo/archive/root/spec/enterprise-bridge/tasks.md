# Enterprise Bridge — Task Breakdown

> **Version**: 1.0.0
> **Date**: 2026-02-20
> **Phases covered**: Phase 0 (install) + Phase 1 (spec)

---

## Phase 0 — Installation Tasks

### Task 0.1 — Verify Python Dependencies in Container

**Priority**: P0 — blocker for install
**Assignee**: DevOps / Platform
**Verification command**:
```bash
docker exec odoo-web-1 python3 -c "
import requests
import paho.mqtt.client
print('requests:', requests.__version__)
print('paho-mqtt: ok')
"
```
**Pass**: Both imports succeed
**Fail path**: Install missing packages in `requirements.txt` → rebuild container

---

### Task 0.2 — Verify OCA Module Availability

**Priority**: P1 — optional but recommended before install
**Check**:
```bash
docker exec odoo-web-1 python3 -c "
import xmlrpc.client
common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
uid = common.authenticate('odoo_dev', 'admin', 'admin', {})
obj = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
r = obj.execute_kw('odoo_dev', uid, 'admin', 'ir.module.module', 'search_read',
  [[['name','in',['account_asset_management','document_page','web_timeline']]]],
  {'fields':['name','state']})
for mod in r:
    print(mod['name'], '->', mod['state'])
"
```
**Expected states**: `installed` or `uninstalled` (not `unknown`)
**Action if missing**: Add OCA submodule or ensure `addons_path` includes OCA repos

---

### Task 0.3 — Install ipai_enterprise_bridge

**Priority**: P0
**Command**:
```bash
docker exec odoo-web-1 python3 /usr/lib/python3/dist-packages/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d odoo_dev \
  --update=ipai_enterprise_bridge \
  --stop-after-init 2>&1 | tee /tmp/enterprise_bridge_install.log
```
**Check log for**: No `ERROR` or `CRITICAL` lines
**Verify state**:
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
**Expected**: `[{'name': 'ipai_enterprise_bridge', 'state': 'installed'}]`

---

### Task 0.4 — Smoke Test Views

**Priority**: P1
**Manual check** (or automated via Playwright):
- Settings → Technical → Enterprise Bridge: page loads
- Settings → Technical → IoT Devices: page loads
- Settings → Technical → Close Checklists: page loads
- Settings → Technical → Company Policies: page loads
**Pass**: No 500/404 errors in Odoo log

---

### Task 0.5 — Verify Job Queue Cron

**Priority**: P1
**Check**:
```bash
docker exec odoo-web-1 python3 -c "
import xmlrpc.client
common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
uid = common.authenticate('odoo_dev', 'admin', 'admin', {})
obj = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
r = obj.execute_kw('odoo_dev', uid, 'admin', 'ir.cron', 'search_read',
  [[['name','ilike','ipai']]], {'fields':['name','active','interval_number','interval_type']})
for cron in r:
    print(cron)
"
```
**Expected**: At least one cron with `active=True` and `interval_number=5`, `interval_type='minutes'`

---

## Phase 1 — Spec Kit Tasks

### Task 1.1 — Create spec/enterprise-bridge/ directory

**Status**: ✅ DONE
**Evidence**: `ls spec/enterprise-bridge/`

### Task 1.2 — Write constitution.md

**Status**: ✅ DONE
**File**: `spec/enterprise-bridge/constitution.md`
**Content**: 7 non-negotiable rules covering SoR, DB access, connector decomposition,
event immutability, MQTT isolation, LOC limits, secrets policy

### Task 1.3 — Write prd.md

**Status**: ✅ DONE
**File**: `spec/enterprise-bridge/prd.md`
**Content**: 10 capabilities documented, dependencies, target architecture, acceptance criteria

### Task 1.4 — Write plan.md

**Status**: ✅ DONE
**File**: `spec/enterprise-bridge/plan.md`
**Content**: 5 phases (0-4), decision log, per-phase steps and risk assessment

### Task 1.5 — Write tasks.md

**Status**: ✅ DONE (this file)

### Task 1.6 — Commit Spec Kit

**Command**:
```bash
cd /path/to/repo
git add spec/enterprise-bridge/
git commit -m "docs(spec): add enterprise-bridge spec kit (constitution, prd, plan, tasks)"
```

---

## Phase 2 — Future Tasks (Placeholder)

### Task 2.1 — Scaffold ipai_vertical_retail

**Status**: Pending
**Prerequisite**: Task 0.3 complete
**Deliverable**: `addons/ipai/ipai_vertical_retail/__manifest__.py` with Scout retail fields

### Task 2.2 — Migrate Scout fields from enterprise_bridge

**Status**: Pending
**Prerequisite**: Task 2.1

### Task 2.3 — Update ee_parity_mapping.yml for retail entries

**Status**: Pending
**File**: `config/ee_parity/ee_parity_mapping.yml`
**Change**: `module: ipai_enterprise_bridge` → `module: ipai_vertical_retail` for retail fields

---

## Phase 3 — Future Tasks (Placeholder)

### Task 3.1 — Create iot-bridge-service

**Status**: Pending
**Deliverable**: `services/iot-bridge/` FastAPI + paho-mqtt standalone service

### Task 3.2 — Create ipai_iot_connector

**Status**: Pending
**Deliverable**: `addons/ipai/ipai_iot_connector/` (<200 LOC, HTTP client only)

### Task 3.3 — Remove paho-mqtt from ipai_enterprise_bridge

**Status**: Pending
**Prerequisite**: Tasks 3.1, 3.2 verified in dev environment

---

## Phase 4 — Future Tasks (Placeholder)

### Task 4.1 — Create ipai_expense_bridge connector

**Status**: Pending
**Target LOC**: <500

### Task 4.2 — Create ipai_finance_bridge connector

**Status**: Pending
**Target LOC**: <400

---

## Acceptance Criteria Summary

| Criterion | Phase | Check |
|---|---|---|
| `ipai_enterprise_bridge` state = `installed` | 0 | XML-RPC verify |
| No import errors in Odoo log during install | 0 | Log scan |
| Job queue cron active, 5-minute interval | 0 | XML-RPC verify |
| All 4 spec files present in spec/enterprise-bridge/ | 1 | `ls` verify |
| Spec committed to main branch | 1 | `git log` |
| Scout retail fields in ipai_vertical_retail | 2 | Module state |
| No paho-mqtt in ipai_enterprise_bridge manifest | 3 | Manifest check |
| ipai_iot_connector <200 LOC | 3 | CI LOC gate |
| ipai_expense_bridge <500 LOC | 4 | CI LOC gate |
| ipai_finance_bridge <400 LOC | 4 | CI LOC gate |
