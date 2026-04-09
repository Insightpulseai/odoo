# Blocker 1: Alert Routing Verification

> Evidence: test notification fired and confirmed delivered

## Date

2026-04-05T00:47:42Z

## Action Group

- Name: `ag-ipai-platform`
- Resource Group: `rg-ipai-dev-odoo-runtime`
- Recipient: `business@insightpulseai.com` (platform-admin)
- Status: Enabled

## Alert Rules Routing to `ag-ipai-platform`

| Alert | Metric | Severity | Enabled |
|---|---|---|---|
| `alert-aca-restarts` | RestartCount > 3 in 5min | Sev 1 | Yes |
| `alert-http-5xx` | HTTP 5xx > 10 in 5min | Sev 2 | Yes |
| `alert-aca-no-replicas` | (configured) | Sev 0 | Yes |
| `alert-aca-high-cpu` | (configured) | Sev 2 | Yes |

## Test Notification Result

```json
{
  "actionDetails": [
    {
      "MechanismType": "Email",
      "Name": "platform-admin",
      "SendTime": "2026-04-05T00:47:42.026755+00:00",
      "Status": "Succeeded"
    }
  ],
  "state": "Complete",
  "completedTime": "2026-04-05T00:51:12.8364514+00:00"
}
```

## Verdict

**PASS** — Alert routing reaches a human. Blocker 1 closed.

## Remaining Gap

- `Application Insights Smart Detection` action group has no email receivers (only ARM role receivers). Consider adding `business@insightpulseai.com` to this group as well.

## Impact on Assessment

- Reliability: +0.3 (alert routing unverified → verified)
- OpEx: +0.2 (alert routing unverified → verified)
