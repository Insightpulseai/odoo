# Runbook: Odoo Mail Smoke Tests

> Script: `scripts/odoo/smoke_mail.py`
> Cleanup: `scripts/odoo/cleanup_smoke_mail.py`
> Dev sink: Mailpit at `http://localhost:8025` (see §Sink Setup)

## Purpose

Deterministic, no-UI tests for:
1. Outgoing SMTP pipeline — `mail.mail` created → queued → optional send
2. User invite/reset template — `res.users.action_reset_password()` queues mail
3. Digest generation — `digest.digest` (skipped gracefully if not installed)

All artifacts are tagged with a timestamped marker so they can be purged precisely.

## Preconditions

- `ir.mail_server` configured for target env (`apply_mail_settings.py` already handles this)
- `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD` set
- For `--send` mode: SMTP reachable (or Mailpit running in dev)
- No secrets in logs (script enforces this — only host/port/user printed)

## Inputs

| Flag | Default | Description |
|------|---------|-------------|
| `--recipient` | required | Email address to receive smoke mails |
| `--send` | off | Attempt SMTP send; omit for queue-only (CI-safe) |
| `--env` | `dev` | Informational label only |

## Outputs / Evidence

| Field | Description |
|-------|-------------|
| `marker` | Unique `smoke-mail-<ISO8601>` tag in all subjects |
| `outgoing.mail_id` | `mail.mail` ID created |
| `outgoing.state` | `outgoing`, `sent`, or `exception` |
| `invite.user_id` | `res.users` ID created |
| `invite.invite_mail_count` | Count of reset/invite mails found |
| `digest.skipped` | `true` if digest not installed |
| `OVERALL` | `PASS` or `FAIL` |

## Verification Checklist

- [ ] `mail.mail` row created with marker in subject
- [ ] Queue-only mode: state is `outgoing` (no SMTP attempted)
- [ ] Send mode: state is `sent` (Mailpit/real) or `exception` with readable reason
- [ ] Invite/reset mail found for recipient (count ≥ 1)
- [ ] Digest test skipped cleanly when module not installed
- [ ] No passwords / tokens appear in stdout

## Rollback / Cleanup

```bash
python3 scripts/odoo/cleanup_smoke_mail.py \
  --marker "smoke-mail-20260221T123456Z" \
  [--dry-run]
```

Deletes: `mail.mail` rows matching marker + `res.users` with matching smoke login.

## CI Usage (queue-only, safe)

```bash
ODOO_URL=https://erp.insightpulseai.com \
ODOO_DB=odoo_prod \
ODOO_USER=admin \
ODOO_PASSWORD=$ODOO_ADMIN_PASSWORD \
python3 scripts/odoo/smoke_mail.py \
  --recipient smoke-sink@insightpulseai.com \
  --env prod
```

## §Sink Setup — Mailpit (dev only)

For repeatable CI that validates actual SMTP delivery without hitting Zoho:

```yaml
# docker-compose.override.yml (dev only, git-ignored)
services:
  mailpit:
    image: axllent/mailpit:latest
    ports:
      - "8025:8025"   # Web UI
      - "1025:1025"   # SMTP
```

Point Odoo SMTP at Mailpit in dev:

```bash
ODOO_URL=http://localhost:8069 \
ODOO_DB=odoo_dev \
ODOO_USER=admin \
ODOO_PASSWORD=admin \
python3 scripts/odoo/apply_mail_settings.py --env dev
# Then override host/port for Mailpit via env or a local mail_settings.yaml override
```

Captured mails visible at `http://localhost:8025`. No real email sent.

**Decision: use Mailpit for dev CI; use `--env prod --no-send` (queue-only) for prod smoke.**
