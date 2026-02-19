# IPAI BIR Notifications

**Version**: 19.0.1.0.0
**Author**: InsightPulseAI
**License**: AGPL-3

## Purpose

Email notification system for BIR tax filing deadlines with two alert types:

1. **Daily Digest** (08:00 PH time): Summary of upcoming, overdue, and today's deadlines
2. **Urgent Alerts** (every 4h check): Critical alerts for deadlines <24h

## Features

- **Notification Pattern**: Digest + escalation (prevents spam)
- **Deliverability**: Zoho Mail SMTP → TBWA Outlook/365
- **Idempotency**: 4-hour cooldown on urgent alerts
- **Tracking**: Complete alert history with status (sent/failed)
- **Configuration**: System parameters for recipient lists
- **Plain Text**: Reliable delivery with minimal HTML

## Installation

1. Ensure `ipai_bir_tax_compliance` module is installed
2. Configure Zoho Mail SMTP in Odoo:
   - Go to: Settings → Technical → Email → Outgoing Mail Servers
   - Create server:
     - SMTP Server: `smtp.zoho.com`
     - SMTP Port: `587`
     - Connection Security: `TLS (STARTTLS)`
     - Username: Your Zoho Mail email (e.g., `alerts@insightpulseai.com`)
     - Password: Your Zoho Mail password or app password
3. Install this module: `odoo-bin -u ipai_bir_notifications`

## Configuration

### Recipient Lists

Configure via System Parameters (Settings → Technical → Parameters → System Parameters):

**Daily Digest Recipients**:
- Key: `ipai_bir_notifications.digest_recipients`
- Value: `email1@company.com,email2@company.com,email3@company.com`

**Urgent Alert Recipients**:
- Key: `ipai_bir_notifications.urgent_recipients`
- Value: `urgent@company.com,manager@company.com`
- Default: Falls back to digest recipients if not set

### Cron Jobs

Two scheduled actions are created automatically:

**1. Daily Digest** (`ir_cron_bir_daily_digest`):
- Schedule: Daily at 08:00 PH (00:00 UTC)
- Method: `bir.alert.send_daily_digest()`
- Active: Yes

**2. Urgent Check** (`ir_cron_bir_urgent_check`):
- Schedule: Every 4 hours
- Method: `bir.alert.check_urgent_deadlines()`
- Active: Yes

To modify schedules: Settings → Technical → Automation → Scheduled Actions

## Usage

### Automatic Operation

Once configured, alerts are sent automatically:

**Daily Digest (08:00 PH)**:
- Lists overdue filings
- Lists today's deadlines
- Lists upcoming deadlines (next 7 days)
- Skipped if no deadlines to report

**Urgent Alerts (every 4h)**:
- Checks for deadlines <24h
- Sends alert per deadline
- 4-hour cooldown prevents spam
- Continues until deadline passes or status changes

### Manual Testing

**Send Daily Digest Now**:
```python
# In Odoo shell (odoo-bin shell -d odoo)
env['bir.alert'].send_daily_digest()
```

**Send Urgent Alert for Specific Deadline**:
```python
# In Odoo shell
env['bir.alert'].send_urgent_alert(deadline_id=123)
```

### Alert History

View sent alerts: Accounting → BIR Tax Compliance → Alert History

Filters available:
- Alert Type (Digest / Urgent)
- Status (Sent / Failed)
- Date ranges (Last 7 Days / Last 30 Days)
- Group by recipient, type, status

## Email Format

### Daily Digest Example

```
======================================================================
BIR TAX FILING DIGEST
Date: Monday, February 12, 2026
======================================================================

📅 DUE TODAY:
----------------------------------------------------------------------
  • 1601-C - Withholding Tax Return
    Period: 2026-01-01 to 2026-01-31
    Status: IN_PROGRESS

⚠️  OVERDUE FILINGS:
----------------------------------------------------------------------
  • 2550M - Monthly VAT Declaration - 2 days late
    Deadline: 2026-02-10
    Period: 2026-01-01 to 2026-01-31
    Status: PENDING

📋 UPCOMING (Next 7 Days):
----------------------------------------------------------------------
  • 2550Q - Quarterly VAT Declaration - 5 days remaining
    Deadline: 2026-02-17 (Monday)
    Period: 2025-10-01 to 2025-12-31
    Status: PENDING

======================================================================
This is an automated daily digest from InsightPulseAI Odoo ERP.
To update recipients, contact your system administrator.
======================================================================
```

### Urgent Alert Example

```
======================================================================
🚨 URGENT: BIR TAX FILING DEADLINE ALERT
======================================================================

Form Type: 1601-C
Description: Withholding Tax Return
Filing Period: 2026-01-01 to 2026-01-31
Deadline: 2026-02-13 (Tuesday)

TIME REMAINING: 18 hours

Current Status: IN_PROGRESS

======================================================================
ACTION REQUIRED:
  1. Review filing status in Odoo ERP
  2. Complete and submit form before deadline
  3. Update status in system once filed
======================================================================

This is an automated urgent alert from InsightPulseAI Odoo ERP.
You will not receive another alert for this deadline for 4 hours.
======================================================================
```

## Deliverability Best Practices

**SPF/DKIM/DMARC**:
- Ensure `insightpulseai.com` has proper SPF record including Zoho Mail
- Example SPF: `v=spf1 include:zoho.com ~all`
- Configure DKIM signing in Zoho Mail admin panel
- Set DMARC policy to `p=quarantine` or `p=reject`

**From Address**:
- Use consistent From address (e.g., `alerts@insightpulseai.com`)
- Verify domain in Zoho Mail
- Avoid frequent changes to From address

**Content**:
- Plain text body (HTML in `<pre>` tags for formatting)
- Minimal styling (better deliverability)
- Clear subject lines (no spammy keywords)
- Unsubscribe not needed (internal alerts only)

## Integration with Supabase Edge Function

For advanced use cases, a Supabase Edge Function is available:

**Function**: `bir-urgent-alert`
**Location**: `supabase/functions/bir-urgent-alert/index.ts`

**Usage**:
```bash
# Via Supabase CLI
supabase functions invoke bir-urgent-alert \
  --body '{"deadline_data": {...}, "force": false}'
```

**Environment Variables** (Supabase Vault):
- `BIR_URGENT_RECIPIENTS`: Comma-separated email list
- `SMTP_HOST`: `smtp.zoho.com`
- `SMTP_PORT`: `587`
- `SMTP_USER`: Zoho Mail username
- `SMTP_PASS`: Zoho Mail password

## Troubleshooting

**No emails received**:
1. Check Zoho Mail SMTP configuration in Odoo
2. Verify system parameters have recipient emails
3. Check cron jobs are active (Settings → Technical → Scheduled Actions)
4. Review alert history for errors (Alert History → Failed filter)
5. Check Odoo server logs for SMTP errors

**Duplicate alerts**:
- Ensure only one cron job instance is running
- Check 4-hour cooldown is working (review Alert History)
- Verify deadline status is updating correctly after filing

**Wrong timezone**:
- Daily digest cron is set to 00:00 UTC (08:00 Manila)
- Adjust `nextcall` field in cron if needed for different timezone

## Security Considerations

- SMTP credentials stored in Odoo mail server settings (not in code)
- Alert history accessible only to account managers (`account.group_account_manager`)
- Recipients configured via system parameters (admin access required)
- No sensitive tax data included in emails (only deadlines)

## Support

For issues or questions:
- GitHub: https://github.com/Insightpulseai/odoo
- Email: business@insightpulseai.com

## License

AGPL-3 - See LICENSE file for details
