# EE → OCA → Bridge Matrix (SSOT)

## Rule of Thumb
1) Prefer **OCA** (native addon parity)
2) Else prefer **CE-native** (core Odoo feature already exists)
3) Else implement **thin ipai_* bridge addon** (metadata + UX glue)
4) Else implement **external service** with strict contract (API + queues) and a tiny Odoo connector addon

## Parity Levels
- L0: OCA/CE parity (install/config only)
- L1: OCA + small config glue (server actions, views)
- L2: Thin ipai_* addon (<= 1k LOC logic, mostly wiring)
- L3: External service required (Supabase / OCR / browser / AI / BI)
- L4: Not worth matching (explicitly out-of-scope)

## What "Bridge" Means (must be true)
- **No business logic duplication**: logic lives in OCA/CE or in the service; ipai_* only routes + validates.
- **Deterministic data contract**: JSON schema + versioning.
- **Auditable**: logs/events persisted; replayable runs.
- **Replaceable**: switch providers without refactoring Odoo models.

## Bridge Interfaces
- Odoo → Service: webhooks/queue_job/cron to enqueue run
- Service → Odoo: RPC/REST callback or DB write via connector
- Storage: attachments in Odoo or object storage + link
- Events: run_events table + Odoo chatter message summary
