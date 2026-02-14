# IPAI VS Code Control Plane — PRD

## 1. Overview

A SaaS-grade **developer control plane embedded in VS Code** that projects modern platform workflows (deploys, environments, upgrades, audits, AI-assisted changes) into **Odoo CE + OCA + IPAI**.

VS Code is not the product.
The **control plane** is.

---

## 2. Problem

Odoo lacks:
- deterministic deploys
- environment visibility
- upgrade safety
- auditable change history
- safe AI assistance

Existing VS Code extensions stop at snippets and scaffolding.

---

## 3. Goals

- Replicate SaaS control-plane behavior
- Treat Odoo as a managed runtime
- Make every change diffable and replayable
- Govern AI execution
- Enforce Spec Kit alignment

---

## 4. Non-Goals

- Replacing Odoo UI
- Free-form chat AI
- Local-only tooling
- Framework-agnostic IDE helpers

---

## 5. Core Features (MVP)

### 5.1 Project & Environment Projection

Tree view:
```
IPAI Projects
 └─ tbwa-finance
     ├─ dev
     ├─ stage
     └─ prod
```

Each environment shows:
- Odoo version
- installed modules
- schema hash
- pending migrations
- last deploy
- health status

---

### 5.2 Deterministic Operations

Supported:
- module install/update
- migrations
- seed application
- upgrades
- rollbacks

Each operation emits:
- SQL diff
- ORM diff
- XML diff
- evidence bundle

---

### 5.3 Preflight Validation

Before execution:
- dependency checks
- EE-only detection
- XML ID collision scan
- security rule coverage
- schema drift vs canonical DBML

Failures block execution.

---

### 5.4 Evidence Bundles

```
docs/evidence/YYYYMMDD-HHMM/
 ├─ plan.md
 ├─ diffs/
 ├─ validation.json
 └─ logs.txt
```

---

### 5.5 Governed AI Assistance

AI commands:
- Generate module patch
- Explain schema drift
- Prepare upgrade plan
- Fix security rules

No free-form mutation.

---

## 6. Success Metrics

- 0 production changes without diffs
- 100% operations with evidence
- Upgrade confidence > speed
- Auditor replay success

---

## 7. Acceptance Criteria

Commands must not execute mutations without:
1. Displaying a diff/plan
2. Generating an evidence bundle ID
3. Recording the operation in an audit log (local + remote)

---

## 8. Control Plane API Contract (v0)

All operations call a single remote API surface (HTTP) with deterministic request/response:

### Endpoints

```
POST /v1/ops/plan
POST /v1/ops/execute
GET  /v1/ops/{op_id}
GET  /v1/evidence/{bundle_id}
POST /v1/validate/run
GET  /v1/validate/status?scope=workspace|module|repo
```

### Operation Model

```typescript
interface Operation {
  op_id: string;          // uuid
  bundle_id: string;      // uuid
  status: 'queued' | 'planned' | 'running' | 'succeeded' | 'failed' | 'rolled_back';
  diffs: Array<{
    path: string;
    summary: string;
    patch: string;
  }>;
  checks: Array<{
    id: string;
    status: 'pass' | 'warn' | 'fail';
    severity: 'error' | 'warning' | 'info';
    message: string;
    file?: string;
    line?: number;
  }>;
}
```

### Request/Response Examples

**Plan Operation**:
```json
POST /v1/ops/plan
{
  "type": "install_modules",
  "environment": "dev",
  "modules": ["sale", "account"]
}

Response:
{
  "op_id": "550e8400-e29b-41d4-a716-446655440000",
  "diffs": [...],
  "checks": [...]
}
```

**Execute Operation**:
```json
POST /v1/ops/execute
{
  "op_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response:
{
  "op_id": "550e8400-e29b-41d4-a716-446655440000",
  "bundle_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "running"
}
```

---

## 9. Future

- Web control plane
- Multi-runtime support
- Agent team orchestration
