# Email Infrastructure Strategy - insightpulseai.com

**Purpose**: Define email infrastructure strategy for `@insightpulseai.com` workspace email

**Current State**: Mailgun configured for sending only
**Decision Point**: Choose between self-hosted mailboxes vs. managed provider

**Date**: 2026-01-28

---

## Current DNS Configuration (Verified)

### ✅ What's Working Now

**Mailgun Subdomain (`mg.insightpulseai.com`)**:
- MX → `10 mxa.mailgun.org`, `10 mxb.mailgun.org` ✅
- SPF → `v=spf1 include:mailgun.org ~all` ✅
- DKIM → Configured ✅
- DMARC → Configured with reporting ✅

**Root Domain (`insightpulseai.com`)**:
- SPF → `v=spf1 include:mailgun.org ~all` ✅
- DMARC → `v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org` ✅
- MX → ❌ **NOT CONFIGURED**

### Current Capabilities

| Feature | Status | Details |
|---------|--------|---------|
| **Send from** `*@mg.insightpulseai.com` | ✅ Works | Mailgun SMTP/API |
| **Send from** `*@insightpulseai.com` | ✅ Works | Mailgun SMTP/API (SPF authorized) |
| **Receive at** `*@mg.insightpulseai.com` | ✅ Works | Mailgun routes/webhooks |
| **Receive at** `*@insightpulseai.com` | ❌ Not configured | No MX records |

---

## Critical Understanding: Mailgun Limitations

**Mailgun is NOT a mailbox provider**:
- ❌ No IMAP/POP3 access
- ❌ No web mail interface
- ❌ No mailbox storage
- ✅ Only: SMTP relay (sending) + inbound webhooks (receiving)

**Source**: [Mailgun IMAP Glossary](https://www.mailgun.com/glossary/imap/)

**What this means**:
- You **can** send email from `@insightpulseai.com` via Mailgun
- You **cannot** have a "real mailbox" (like Gmail/Outlook) for `jake@insightpulseai.com` using only Mailgun
- You **can** receive email via Mailgun routes and forward to webhooks (n8n, Odoo, Azure Boards)

---

## Decision Matrix: Email Infrastructure Options

### Option 1: Mailgun Only (Current State - Transactional Only)

**What You Get**:
- ✅ Send from `*@insightpulseai.com` via Mailgun SMTP/API
- ✅ Receive at automation addresses → webhooks (boards@, odoo@)
- ❌ No workspace inboxes (jake@, devops@, etc.)

**Use Case**: Pure automation/transactional email, no human mailboxes needed

**Cost**: $0/month (Mailgun free tier: 5,000 emails/month)

**Required DNS Changes**: None (already configured)

**Pros**:
- ✅ Zero additional infrastructure
- ✅ High deliverability (Mailgun reputation)
- ✅ Already working

**Cons**:
- ❌ No workspace email for team
- ❌ No IMAP/POP3 for email clients
- ❌ No calendar/contacts integration

---

### Option 2: Self-Hosted Mailserver (Docker Mailserver)

**What You Get**:
- ✅ Real workspace inboxes: `jake@insightpulseai.com`, `devops@insightpulseai.com`
- ✅ IMAP/POP3 access (Thunderbird, Apple Mail, etc.)
- ✅ Automation addresses → pipe to scripts (Azure Boards, Odoo)
- ✅ Full control and ownership

**Infrastructure**:
- Docker Mailserver on DigitalOcean droplet (178.128.112.214)
- Postfix (SMTP) + Dovecot (IMAP) + Rspamd (anti-spam) + DKIM

**Cost**: $0/month (using existing droplet capacity)

**Complexity**: Moderate (requires maintenance, monitoring, spam management)

**Required DNS Changes**:
```dns
# Add MX records for root domain
MX    @                        10 mail.insightpulseai.com
A     mail.insightpulseai.com  →  178.128.112.214

# Update SPF to include your mail server
TXT   @  v=spf1 ip4:178.128.112.214 include:mailgun.org ~all

# PTR/Reverse DNS (via DigitalOcean dashboard)
PTR   178.128.112.214  →  mail.insightpulseai.com
```

**Pros**:
- ✅ Real workspace email for team
- ✅ Full control over data
- ✅ No per-user fees
- ✅ Custom automation pipelines

**Cons**:
- ❌ Requires ongoing maintenance
- ❌ Spam/blacklist management
- ❌ Deliverability depends on server reputation
- ❌ Backup/disaster recovery responsibility

**Recommended For**: Teams comfortable with self-hosting, want full control, technical capability available

---

### Option 3: Google Workspace / Microsoft 365 (Managed Provider)

**What You Get**:
- ✅ Enterprise-grade workspace inboxes
- ✅ Calendar, contacts, drive integration
- ✅ Mobile apps, web interface
- ✅ Guaranteed deliverability
- ✅ No server maintenance

**Cost**:
- **Google Workspace**: $6/user/month (Business Starter)
- **Microsoft 365**: $6/user/month (Business Basic)

**Required DNS Changes**:
```dns
# Google Workspace example
MX    @  1  aspmx.l.google.com
MX    @  5  alt1.aspmx.l.google.com
MX    @  5  alt2.aspmx.l.google.com
# ... etc (provider-specific)

# Update SPF
TXT   @  v=spf1 include:_spf.google.com include:mailgun.org ~all
```

**Pros**:
- ✅ Zero maintenance
- ✅ 99.9% uptime SLA
- ✅ Professional email experience
- ✅ Enterprise support

**Cons**:
- ❌ Monthly cost ($6/user)
- ❌ Less control over data
- ❌ Vendor lock-in

**Recommended For**: Teams prioritizing reliability over cost, want enterprise features

---

### Option 4: Hybrid (Mailgun + Managed Provider)

**What You Get**:
- ✅ Workspace inboxes via Google/Microsoft
- ✅ Transactional email via Mailgun (better deliverability)
- ✅ Automation addresses → either provider

**Setup**:
- Root MX → Google/Microsoft (workspace email)
- Mailgun subdomain (`mg.insightpulseai.com`) → automation/transactional

**Cost**: $6/user/month + $0 Mailgun free tier

**Required DNS Changes**:
```dns
# Root MX → managed provider
MX    @  ... (provider-specific)

# Keep mg subdomain for Mailgun automation
MX    mg  10 mxa.mailgun.org
# ... (no change)

# SPF includes both
TXT   @  v=spf1 include:_spf.google.com include:mailgun.org ~all
```

**Pros**:
- ✅ Best of both worlds
- ✅ High deliverability for transactional (Mailgun)
- ✅ Enterprise workspace experience
- ✅ Clear separation: humans vs. automation

**Cons**:
- ❌ Monthly cost
- ❌ Two systems to manage

**Recommended For**: Most production scenarios, best balance of reliability and functionality

---

## Recommended Strategy for InsightPulse AI

### Phase 1: Current State (Immediate - No Changes)

**Status**: Mailgun for transactional/automation only

**Capabilities**:
- ✅ Send transactional email from `*@insightpulseai.com`
- ✅ Automation webhooks: `boards@mg.insightpulseai.com` → n8n → Azure Boards
- ✅ Odoo notifications: `odoo@mg.insightpulseai.com` → n8n → Odoo tasks

**No workspace email** - team uses personal emails or other provider

**Action Required**: None

---

### Phase 2: Add Workspace Email (When Needed)

**Trigger**: When team needs professional `@insightpulseai.com` email addresses

**Recommended Approach**: **Option 4 - Hybrid (Mailgun + Google Workspace)**

**Why**:
- ✅ Professional workspace experience (Google Workspace)
- ✅ Reliable transactional delivery (Mailgun)
- ✅ Clear separation (humans on root, automation on mg subdomain)
- ✅ No self-hosting maintenance burden
- ✅ Cost-effective for small team (start with 1-3 users)

**Implementation**:
1. Sign up for Google Workspace (Business Starter - $6/user/month)
2. Add DNS MX records for root domain → Google
3. Update SPF to include both Google and Mailgun
4. Keep Mailgun `mg` subdomain for automation
5. Configure automation addresses (`boards@`, `odoo@`) in Google Workspace → forward to n8n webhooks

**Cost**: ~$18-36/month (3-6 users)

---

### Phase 3: Self-Hosted Option (Future - If Requirements Change)

**Trigger**: If cost becomes prohibitive OR full control required

**Implementation**: Deploy Docker Mailserver (see detailed spec below)

**When to Consider**:
- Team grows beyond 10 users ($60+/month on managed)
- Regulatory/compliance requires data sovereignty
- Advanced automation pipelines need direct server access

---

## Implementation Spec: Docker Mailserver (Self-Hosted Option)

### Prerequisites

- DigitalOcean droplet: 178.128.112.214
- Docker and Docker Compose installed
- PTR/Reverse DNS configured (via DO dashboard)

### DNS Configuration

```bash
#!/usr/bin/env bash
# Add these records to DigitalOcean DNS panel

# MX record for root domain
doctl compute domain records create insightpulseai.com \
  --record-type MX \
  --record-name @ \
  --record-data "mail.insightpulseai.com" \
  --record-priority 10

# A record for mail server
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name mail \
  --record-data 178.128.112.214

# Update SPF (replace existing)
doctl compute domain records update insightpulseai.com <RECORD_ID> \
  --record-data "v=spf1 ip4:178.128.112.214 include:mailgun.org ~all"
```

### Docker Mailserver Deployment

```bash
#!/usr/bin/env bash
set -euo pipefail

# Create directory structure
ssh root@178.128.112.214 "mkdir -p /opt/mailserver/{data,config}"

# Create docker-compose.yml
cat > /tmp/mailserver-compose.yml <<'YAML'
services:
  mailserver:
    image: docker.io/mailserver/docker-mailserver:latest
    container_name: mailserver
    hostname: mail
    domainname: insightpulseai.com
    env_file: .env
    ports:
      - "25:25"     # SMTP
      - "465:465"   # SMTPS
      - "587:587"   # Submission
      - "143:143"   # IMAP
      - "993:993"   # IMAPS
    volumes:
      - ./data/mail:/var/mail
      - ./data/state:/var/mail-state
      - ./data/log:/var/log/mail
      - ./config/:/tmp/docker-mailserver/
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    cap_add:
      - NET_ADMIN
    healthcheck:
      test: "ss -lntp | grep -E ':25|:465|:587|:993' || exit 1"
      timeout: 3s
      retries: 0
YAML

# Create .env file
cat > /tmp/mailserver.env <<'ENV'
# Core settings
ENABLE_RSPAMD=1
ENABLE_CLAMAV=0
ENABLE_FAIL2BAN=1

# TLS
SSL_TYPE=letsencrypt

# DKIM
ENABLE_OPENDKIM=1

# Relay outbound through Mailgun (recommended for deliverability)
RELAY_HOST=smtp.mailgun.org
RELAY_PORT=587
RELAY_USER=postmaster@mg.insightpulseai.com
RELAY_PASSWORD=__MAILGUN_SMTP_PASSWORD__

# Postmaster
POSTMASTER_ADDRESS=postmaster@insightpulseai.com

# Spam settings
ENABLE_SPAMASSASSIN=1
SPAMASSASSIN_SPAM_TO_INBOX=0
ENV

# Copy files to server
scp /tmp/mailserver-compose.yml root@178.128.112.214:/opt/mailserver/docker-compose.yml
scp /tmp/mailserver.env root@178.128.112.214:/opt/mailserver/.env

# Deploy
ssh root@178.128.112.214 "cd /opt/mailserver && docker compose up -d"
```

### Create Mailboxes (Non-Interactive)

```bash
#!/usr/bin/env bash
# Create workspace email accounts

ssh root@178.128.112.214 <<'REMOTE'
cd /opt/mailserver

# Create accounts
docker exec mailserver setup email add jake@insightpulseai.com 'STRONG_PASSWORD'
docker exec mailserver setup email add devops@insightpulseai.com 'STRONG_PASSWORD'
docker exec mailserver setup email add business@insightpulseai.com 'STRONG_PASSWORD'

# List accounts
docker exec mailserver setup email list
REMOTE
```

### Automation Pipelines (Azure Boards + Odoo)

```bash
#!/usr/bin/env bash
# Configure Postfix aliases for automation addresses

ssh root@178.128.112.214 <<'REMOTE'
cd /opt/mailserver/config

# Create pipe script for Azure Boards
cat > /opt/mailserver/data/scripts/boards-pipe.sh <<'SCRIPT'
#!/usr/bin/env bash
# Read email from stdin and create Azure DevOps work item

EMAIL_CONTENT=$(cat)

# Extract subject and body
SUBJECT=$(echo "$EMAIL_CONTENT" | grep -i "^Subject:" | sed 's/^Subject: //')
BODY=$(echo "$EMAIL_CONTENT" | sed -n '/^$/,$ p' | tail -n +2)

# Create Azure DevOps work item via API
curl -X POST "https://dev.azure.com/${ADO_ORG}/${ADO_PROJECT}/_apis/wit/workitems/\$Task?api-version=7.1" \
  -H "Authorization: Basic $(echo -n :${ADO_PAT} | base64)" \
  -H "Content-Type: application/json-patch+json" \
  -d "[
    {\"op\": \"add\", \"path\": \"/fields/System.Title\", \"value\": \"$SUBJECT\"},
    {\"op\": \"add\", \"path\": \"/fields/System.Description\", \"value\": \"$BODY\"}
  ]"
SCRIPT

chmod +x /opt/mailserver/data/scripts/boards-pipe.sh

# Configure Postfix virtual aliases
cat > /opt/mailserver/config/postfix-virtual.cf <<'ALIASES'
boards@insightpulseai.com    boards_pipe
odoo@insightpulseai.com      odoo_pipe
ALIASES

# Configure transport for pipes
cat > /opt/mailserver/config/postfix-master.cf <<'TRANSPORT'
boards_pipe  unix  -       n       n       -       -       pipe
  flags=F user=vmail argv=/opt/mailserver/data/scripts/boards-pipe.sh

odoo_pipe    unix  -       n       n       -       -       pipe
  flags=F user=vmail argv=/opt/mailserver/data/scripts/odoo-pipe.sh
TRANSPORT

# Restart mailserver
docker restart mailserver
REMOTE
```

---

## Verification Commands

### DNS Verification

```bash
# Check MX records
dig +short MX insightpulseai.com

# Check SPF
dig +short TXT insightpulseai.com | grep spf

# Check PTR/Reverse DNS
dig -x 178.128.112.214 +short
```

### SMTP/IMAP Connectivity

```bash
# SMTP (port 25, 587)
nc -vz mail.insightpulseai.com 25
nc -vz mail.insightpulseai.com 587

# IMAP (port 993)
nc -vz mail.insightpulseai.com 993
```

### Send Test Email

```bash
# Via Mailgun API (current - already works)
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/mg.insightpulseai.com/messages \
  -F from='Test <test@insightpulseai.com>' \
  -F to='recipient@example.com' \
  -F subject='Test from insightpulseai.com' \
  -F text='Testing Mailgun sending'

# Via self-hosted mailserver (after Option 2 implementation)
echo "Test body" | mail -s "Test subject" -a "From: jake@insightpulseai.com" recipient@example.com
```

---

## Decision Summary

| Scenario | Recommended Option | Cost | Complexity |
|----------|-------------------|------|------------|
| **Automation/transactional only** | Keep current (Mailgun only) | $0 | Low |
| **Small team workspace (<10 users)** | Hybrid (Mailgun + Google Workspace) | ~$36/mo | Low |
| **Large team (>10 users)** | Self-hosted mailserver | $0 | Moderate |
| **Enterprise requirements** | Hybrid (Mailgun + Microsoft 365) | ~$60/mo | Low |

---

## Next Steps

**Immediate** (No action required):
- Current setup works for transactional/automation email
- Continue using Mailgun for sending from `@insightpulseai.com`

**When workspace email needed**:
1. Choose option (recommended: Hybrid with Google Workspace)
2. Follow implementation spec above
3. Update DNS records
4. Configure automation forwarding

**Documentation**:
- This document serves as decision guide
- Implementation specs ready for execution when needed

---

**Last Updated**: 2026-01-28
**Author**: InsightPulse AI Engineering
**Status**: Decision guide ready, awaiting workspace email requirement
