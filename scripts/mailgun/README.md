# Mailgun Scripts

Automation scripts for Mailgun DNS verification and webhook configuration for InsightPulse AI.

## Domain

- **Sending Domain:** mg.insightpulseai.net
- **Webhook URL:** https://n8n.insightpulseai.net/webhook/mailgun-events

## Scripts

| Script | Purpose |
|--------|---------|
| `verify_dns.sh` | Verify all required DNS records are configured |
| `test_smtp.sh` | Test SMTP connection to Mailgun |
| `setup_webhooks.sh` | Configure webhook endpoints for all events |
| `send_test_email.sh` | Send a test email to verify delivery |

## Quick Start

```bash
# Make scripts executable
chmod +x scripts/mailgun/*.sh

# 1. Verify DNS (no credentials needed)
./scripts/mailgun/verify_dns.sh

# 2. Test SMTP (no credentials needed)
./scripts/mailgun/test_smtp.sh

# 3. Setup webhooks (requires API key)
export MAILGUN_API_KEY=key-xxxxx
./scripts/mailgun/setup_webhooks.sh

# 4. Send test email (requires API key)
./scripts/mailgun/send_test_email.sh recipient@example.com
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAILGUN_API_KEY` | Yes* | - | Mailgun API key (for webhooks/email) |
| `MAILGUN_DOMAIN` | No | mg.insightpulseai.net | Mailgun sending domain |
| `WEBHOOK_URL` | No | https://n8n.insightpulseai.net/webhook/mailgun-events | Webhook endpoint URL |
| `SMTP_HOST` | No | smtp.mailgun.org | SMTP server hostname |
| `SMTP_PORT` | No | 465 | SMTP port (465=SSL, 587=STARTTLS) |

*Only required for webhook setup and test email scripts.

## Evidence Output

All scripts write evidence files to `docs/evidence/YYYYMMDD-HHMM/mailgun/`:

- `dns_verification.json` - DNS lookup results
- `dns_verification.md` - Human-readable DNS report
- `smtp_test.json` - SMTP connection test results
- `webhook_setup.json` - Webhook configuration results
- `webhook_setup.md` - Human-readable webhook report
- `test_email.json` - Test email delivery results

## DNS Records Required

| Record | Type | Name | Value |
|--------|------|------|-------|
| SPF | TXT | mg.insightpulseai.net | `v=spf1 include:mailgun.org ~all` |
| DKIM | TXT | pic._domainkey.mg.insightpulseai.net | (Mailgun-provided public key) |
| DMARC | TXT | _dmarc.mg.insightpulseai.net | `v=DMARC1; p=none; ...` |
| MX | MX | mg.insightpulseai.net | `10 mxa.mailgun.org`, `10 mxb.mailgun.org` |
| Tracking | CNAME | email.mg.insightpulseai.net | `mailgun.org` |

## Webhook Events

All events are configured to send to the same endpoint:

| Event | Description |
|-------|-------------|
| `delivered` | Email successfully delivered |
| `permanent_fail` | Hard bounce (invalid address) |
| `temporary_fail` | Soft bounce (temporary issue) |
| `complained` | Recipient marked as spam |
| `unsubscribed` | Recipient opted out |
| `opened` | Email was opened |
| `clicked` | Link was clicked |

## Troubleshooting

### DNS not resolving
- Check DNS propagation (can take up to 48 hours)
- Verify records in your DNS provider dashboard
- Use multiple DNS resolvers to confirm

### SMTP connection failed
- Check firewall allows outbound port 465/587
- Verify SMTP credentials are correct
- Try both SSL (465) and STARTTLS (587)

### Webhook not receiving events
- Verify webhook URL is publicly accessible
- Check n8n workflow is active
- Verify webhook signing key matches

### Test email not received
- Check spam folder
- Verify sender reputation in Mailgun dashboard
- Check DMARC/SPF/DKIM alignment in email headers

## Related Documentation

- [Mailgun API Documentation](https://documentation.mailgun.com/)
- [Supabase Email Events](../docs/infra/MAILGUN_SETUP.md)
- [n8n Webhook Workflows](../n8n/)
