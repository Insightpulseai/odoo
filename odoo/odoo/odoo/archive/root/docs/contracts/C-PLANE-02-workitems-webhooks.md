# C-PLANE-02 — Plane Work Items Webhook Contract

**Contract ID**: C-PLANE-02
**Platform Index**: C-21
**SSOT**: ssot/sources/plane/work_items.yaml
**Consumer**: ops.work_items, ops-console Boards view
**Status**: Planned
**Validator**: apps/ops-console/app/api/webhooks/plane/route.ts

---

## Overview

Plane sends issue event webhooks to the platform. The receiver persists a durable delivery row, enqueues an async processing job, and immediately returns JSON. Processing normalises the payload into `ops.work_items`.

---

## Signature Verification

| Field | Value |
|-------|-------|
| Header | `X-Plane-Signature` |
| Algorithm | HMAC-SHA256 |
| Input | raw request body bytes |
| Format | lowercase hex |
| Secret | Vault key `plane_webhook_secret` |

Requests where the computed signature ≠ header value must return `403 { ok: false, error: "invalid signature" }`.

---

## Dedupe Key

`X-Plane-Delivery` header — unique UUID per event delivery.

Duplicate deliveries (same `delivery_id`) must be rejected with `200 { ok: true, duplicate: true }` (idempotent, not an error).

---

## Async Processing Contract

1. Persist row to `ops.plane_webhook_deliveries` with status `received`.
2. Insert job into `ops.work_queue` with `source=plane`, `delivery_id`.
3. Return `200 { ok: true }` before processing begins.
4. Processor claims job, normalises payload, upserts `ops.work_items`, marks delivery `processed`.
5. On failure: mark delivery `failed`, record `last_error`, increment `attempts`.

---

## Event Mapping → ops.work_items

| Plane field | ops.work_items column |
|-------------|----------------------|
| `issue.id` | `external_id` |
| `plane:{issue.id}` | `work_item_ref` (PK) |
| `"plane"` | `system` |
| `issue.name` | `title` |
| `issue.state.name` | `status` |
| `issue.assignees[0].display_name` | `assignee` (nullable) |
| `issue.url` | `url` |
| `issue.updated_at` | `updated_at` |
| `project.id` | `project_ref` |

---

## Supported Events

| Event | Action |
|-------|--------|
| `issue.created` | upsert |
| `issue.updated` | upsert |
| `issue.deleted` | soft-delete (status = deleted) |

---

## CI Gate

- Receiver must return `Content-Type: application/json` for all outcomes.
- Receiver must never return 204 or empty body.
- `ops.plane_webhook_deliveries.delivery_id` must be a PRIMARY KEY (enforces DB-level dedupe).
