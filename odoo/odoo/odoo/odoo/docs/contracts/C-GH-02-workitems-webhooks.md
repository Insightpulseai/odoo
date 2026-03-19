# C-GH-02 — GitHub Issues Webhook Contract

**Contract ID**: C-GH-02
**Platform Index**: C-22
**SSOT**: ssot/sources/github/work_items.yaml
**Consumer**: ops.work_items, ops-console Boards view
**Status**: Planned
**Validator**: apps/ops-console/app/api/webhooks/github/route.ts

---

## Overview

GitHub sends issue event webhooks to the platform. The receiver persists a durable delivery row, enqueues an async processing job, and immediately returns JSON. Processing normalises the payload into `ops.work_items`.

---

## Signature Verification

| Field | Value |
|-------|-------|
| Header | `X-Hub-Signature-256` |
| Algorithm | HMAC-SHA256 |
| Input | raw request body bytes |
| Format | `sha256=` + lowercase hex |
| Secret | Vault key `github_webhook_secret` |

Requests where the computed signature ≠ header value must return `403 { ok: false, error: "invalid signature" }`.

---

## Dedupe Key

`X-GitHub-Delivery` header — unique UUID per event delivery.

Duplicate deliveries (same `delivery_id`) must be rejected with `200 { ok: true, duplicate: true }` (idempotent, not an error).

---

## Async Processing Contract

1. Persist row to `ops.github_webhook_deliveries` with status `received`.
2. Insert job into `ops.work_queue` with `source=github`, `delivery_id`.
3. Return `200 { ok: true }` before processing begins.
4. Processor claims job, normalises payload, upserts `ops.work_items`, marks delivery `processed`.
5. On failure: mark delivery `failed`, record `last_error`, increment `attempts`.

---

## Event Mapping → ops.work_items

| GitHub field | ops.work_items column |
|--------------|----------------------|
| `issue.number` | `external_id` |
| `github:{repository.full_name}#{issue.number}` | `work_item_ref` (PK) |
| `"github"` | `system` |
| `issue.title` | `title` |
| `issue.state` | `status` (open\|closed) |
| `issue.assignee.login` | `assignee` (nullable) |
| `issue.html_url` | `url` |
| `issue.updated_at` | `updated_at` |
| `repository.full_name` | `project_ref` |

---

## Supported Events

| X-GitHub-Event | Action |
|----------------|--------|
| `issues` action=`opened` | upsert |
| `issues` action=`edited` | upsert |
| `issues` action=`closed` | upsert (status=closed) |
| `issues` action=`reopened` | upsert (status=open) |

---

## CI Gate

- Receiver must return `Content-Type: application/json` for all outcomes.
- Receiver must never return 204 or empty body.
- `ops.github_webhook_deliveries.delivery_id` must be a PRIMARY KEY (enforces DB-level dedupe).
- `work_item_ref` format must include repo full name to prevent cross-repo collisions.
