---
id: ADR-001-zoho-mail
title: Adopt Zoho Mail SMTP for Outbound Email
date: 2026-02-12
status: accepted
portfolio_initiative: PORT-2026-004
process_id: PROC-EMAIL-001
evidence_id: EVID-20260212-003
decision_makers: [integration_team, platform_team]
---

# ADR-001: Adopt Zoho Mail SMTP for Outbound Email

## Status
**Accepted** - 2026-02-12

## Context

InsightPulse AI required a reliable outbound email solution for:
- Transactional emails (password resets, notifications)
- System alerts and monitoring
- User communications from Odoo ERP

**Previous Solution**: Mailgun (usage-based pricing)
- Cost: Variable based on email volume
- Complexity: Separate service requiring API integration
- Maintenance: Additional service to monitor and maintain

**Trigger**: Cost optimization and infrastructure simplification during email provider evaluation.

## Decision

**Adopt Zoho Mail SMTP (`smtp.zoho.com:587`) for all outbound email.**

**Implementation**:
1. Configure Odoo to use Zoho Mail SMTP
2. Create application-specific password in Zoho Mail
3. Store credentials in environment variables
4. Deprecate Mailgun integration
5. Remove `ipai_mailgun_bridge` module

**Configuration**:
```bash
# Zoho Mail SMTP Settings
SMTP_SERVER=smtp.zoho.com
SMTP_PORT=587
SMTP_USER=business@insightpulseai.com
SMTP_PASSWORD=<app-specific-password>  # From Zoho Mail
SMTP_ENCRYPTION=STARTTLS
```

## Consequences

### Positive

**Cost Reduction**:
- ✅ **Eliminated Mailgun costs**: No more usage-based pricing
- ✅ **Consolidated billing**: Email included in Zoho Workplace subscription
- ✅ **Predictable costs**: Fixed monthly cost instead of variable

**Simplified Infrastructure**:
- ✅ **Fewer moving parts**: One less external service to maintain
- ✅ **Single auth point**: Same credentials as Google Workspace migration
- ✅ **Standard SMTP**: No custom API integration required

**Operational Benefits**:
- ✅ **Familiar interface**: Same Zoho Mail for manual and automated emails
- ✅ **Unified logs**: All email (manual + automated) in same Zoho Mail account
- ✅ **Easier troubleshooting**: Centralized email delivery monitoring

### Negative

**Limitations**:
- ⚠️ **Rate limits**: Zoho Mail has stricter rate limits than Mailgun (500 emails/day for basic plan)
- ⚠️ **No advanced features**: No A/B testing, click tracking, or email validation API
- ⚠️ **SMTP-only**: No REST API for programmatic email operations

**Mitigation**:
- Monitor email volume to ensure within Zoho Mail limits
- Upgrade Zoho Mail plan if rate limits become constraint
- For bulk email campaigns (if needed in future), evaluate dedicated bulk email service

### Technical Debt

**Removed**:
- ❌ `ipai_mailgun_bridge` module (deprecated)
- ❌ Mailgun API credentials and configuration
- ❌ Mailgun webhook handlers

**No New Debt**: Standard SMTP is supported natively by Odoo.

## Alternatives Considered

### 1. Keep Mailgun
**Pros**: Advanced features, higher rate limits, proven reliability
**Cons**: Additional cost, separate service, API integration complexity
**Rejected**: Cost and complexity not justified for current email volume

### 2. SendGrid
**Pros**: Generous free tier, advanced features, good deliverability
**Cons**: Another external service, API integration required
**Rejected**: Same infrastructure complexity as Mailgun

### 3. AWS SES (Simple Email Service)
**Pros**: Very low cost, high rate limits, AWS integration
**Cons**: AWS account dependency, additional service, SMTP configuration
**Rejected**: Added AWS dependency not desired

### 4. Google Workspace SMTP
**Pros**: Already using Google Workspace, familiar, no additional cost
**Cons**: Deprecated by Google (OAuth 2.0 required for new apps), rate limits
**Rejected**: Google discourages SMTP for applications

### 5. Zoho Mail SMTP (Selected)
**Pros**: Consolidated billing, simple SMTP, familiar interface
**Cons**: Rate limits, no advanced features
**Accepted**: Best fit for current needs and cost optimization

## Implementation Evidence

**Migration Date**: 2026-02-12

**Evidence Artifacts**:
- Migration script: `scripts/migrate/mailgun-cleanup.sh`
- Evidence directory: `docs/evidence/20260212-1844/mailgun-cleanup/`
- Verification: Email delivery confirmed via Zoho Mail logs

**Verification Commands**:
```bash
# Test SMTP connection
python3 -c "import smtplib; smtplib.SMTP('smtp.zoho.com', 587).starttls(); print('✅ SMTP connection successful')"

# Send test email via Odoo
# (manual verification in Odoo settings)
```

**Rollback Plan**:
If Zoho Mail SMTP fails:
1. Revert Odoo email configuration to previous state
2. Re-enable Mailgun API credentials (if still valid)
3. Restore `ipai_mailgun_bridge` module from git history
4. Update environment variables

## Compliance and Security

**Secrets Management**:
- ✅ SMTP credentials stored in `.env` file (not committed to git)
- ✅ Application-specific password used (not account password)
- ✅ Environment variables used in Odoo configuration

**Email Security**:
- ✅ STARTTLS encryption for SMTP connection
- ✅ SPF/DKIM/DMARC configured for `insightpulseai.com`
- ✅ Email authentication via Cloudflare DNS

**Data Privacy**:
- ✅ No email content stored by third-party (SMTP relay only)
- ✅ Email logs accessible via Zoho Mail (authorized users only)

## Review and Monitoring

**Review Cycle**: Quarterly

**Metrics to Monitor**:
1. Email delivery rate (should be >95%)
2. Email volume vs Zoho Mail limits (500 emails/day)
3. Bounce rate (should be <5%)
4. SMTP connection failures

**Next Review**: 2026-05-12

**Triggers for Re-evaluation**:
- Email volume exceeds Zoho Mail limits
- Deliverability issues (high bounce rate)
- Need for advanced email features (A/B testing, analytics)
- Cost structure changes (Zoho Mail pricing increase)

## References

**Portfolio Initiative**: PORT-2026-004 (Email Infrastructure Modernization)
**Process**: PROC-EMAIL-001 (Email Service Management)
**Control**: CTRL-DOC-001 (Documentation Requirement)
**Evidence**: EVID-20260212-003

**Related Documentation**:
- `docs/TRACEABILITY_INDEX.yaml`
- `docs/evidence/index.yaml`
- `docs/integration/README.md`

**External References**:
- Zoho Mail SMTP: https://www.zoho.com/mail/help/smtp-access.html
- Odoo Email Configuration: https://www.odoo.com/documentation/19.0/applications/general/email_communication.html

---

*Decision Date: 2026-02-12*
*Decision Makers: integration_team, platform_team*
*Status: Accepted*
*Review Date: 2026-05-12*
