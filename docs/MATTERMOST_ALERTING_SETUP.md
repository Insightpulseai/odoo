# Mattermost Alerting Setup – Finance & CI

---

## 1. Channels

- `#finance-alerts` – BIR deadlines, PPM failures, cron issues
- `#ci-health` – GitHub Actions telemetry (test failures, flaky jobs)

---

## 2. Incoming Webhooks

### 2.1 Create Webhook – Finance Alerts

1. Mattermost menu → **Integrations → Incoming Webhooks**
2. Create:
   - Title: `n8n – Finance Alerts`
   - Channel: `#finance-alerts`
3. Copy webhook URL, store in Vault, then configure in n8n workflow `Finance PPM Alerts`.

### 2.2 Create Webhook – CI Health

1. Create:
   - Title: `n8n – CI Health`
   - Channel: `#ci-health`
2. Use this URL in `scripts/report_ci_telemetry.sh` (via `N8N_CI_WEBHOOK_URL` secret in GitHub).

---

## 3. Severity and Routing

Recommended mapping:

- `INFO` – Cron success, nightly snapshot: log only or ping `#ci-health`
- `WARNING` – Slow cron / long installs: `#finance-alerts` (no @here)
- `ERROR` – Install failure (`ipai_finance_ppm`), DB pool exhaustion:
  - n8n triggers:
    - Auto-heal script (restart containers)
    - Message in `#finance-alerts` with log link

---

## 4. Payload Convention

Example JSON from n8n:

```json
{
  "text": ":warning: *Finance PPM Install Warning*",
  "attachments": [
    {
      "color": "#ffa500",
      "fields": [
        { "title": "Module", "value": "ipai_finance_ppm", "short": true },
        { "title": "Environment", "value": "prod", "short": true },
        { "title": "Details", "value": "Install took > 300s. Check Odoo logs." }
      ]
    }
  ]
}
```

All alerts should include: module, environment, timestamp, and actionable next step.
