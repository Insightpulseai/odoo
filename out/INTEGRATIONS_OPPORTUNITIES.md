# Integrations & Opportunities Assessment (Automated)
## Inputs Collected
- DNS audit: 14/14 records passing
- Mailgun audit: not run
- Supabase audit: not run
- Vercel audit: not run

## Opportunity Backlog (Ranked)
### 1. [Mailgun / Deliverability] Graduate DMARC from p=none to p=quarantine (then p=reject) with staged enforcement
**Why:** p=none is monitoring-only; staged enforcement reduces spoofing and improves alignment once SPF/DKIM are stable.

**Evidence:** `"Data: v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;"`

**Next steps (CLI):**
- Generate staged DMARC records for mg subdomain (quarantine 10% → 50% → 100%, then reject).
- Validate DMARC aggregate reports already configured (rua/ruf).
- Run DNS audit after each change.

