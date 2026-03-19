# Plane Production: Auth, Email, and Integrations

---

## Overview

Production is **not considered ready** until auth, email, and all three canonical integrations are configured and verified. This document defines the setup requirements and acceptance criteria for each.

---

## 1. Authentication on Production

### Auth Mode Options

| Mode | When to Use | Plane Config |
|------|-------------|-------------|
| **Local auth** | Small team, no SSO infrastructure | Default -- no additional config |
| **OIDC / OAuth 2.0** | Keycloak, Google Workspace, or other OIDC provider | Configure OIDC env vars |
| **SAML** | Enterprise SSO requirement | Configure SAML provider in Plane admin |

### Recommended: OIDC via Keycloak

Keycloak is already self-hosted in our stack. Use it as the OIDC provider for Plane.

**Required environment variables** (set in Plane's runtime env, never committed):

```
OIDC_CLIENT_ID=<from-keycloak>
OIDC_CLIENT_SECRET=<from-keycloak>
OIDC_ISSUER_URL=https://auth.insightpulseai.com/realms/insightpulseai
OIDC_TOKEN_URL=https://auth.insightpulseai.com/realms/insightpulseai/protocol/openid-connect/token
OIDC_USERINFO_URL=https://auth.insightpulseai.com/realms/insightpulseai/protocol/openid-connect/userinfo
OIDC_AUTHORIZATION_URL=https://auth.insightpulseai.com/realms/insightpulseai/protocol/openid-connect/auth
```

### Acceptance Criteria

| Criterion | Pass Condition |
|-----------|---------------|
| Login works | User can authenticate through chosen auth mode |
| Logout works | Session is destroyed on logout |
| New user invite works | Invited user receives email and can complete registration |
| Role assignment works | Admin can assign workspace roles (Admin, Member, Guest) |
| Session persistence | User stays logged in across browser restarts (within session TTL) |

### Verification Command

```bash
# After auth is configured, verify by:
# 1. Attempting login via the configured auth provider
# 2. Checking Plane admin panel for active sessions
# 3. Sending a test invite and completing registration flow
```

---

## 2. Email on Production

### SMTP Configuration

| Field | Value |
|-------|-------|
| **Provider** | Zoho Mail (or configured SMTP relay) |
| **Sender identity** | `plane@insightpulseai.com` or `noreply@insightpulseai.com` |
| **Protocol** | SMTP over TLS (port 587) |

### Required Environment Variables

Set in Plane's runtime environment (never committed):

```
EMAIL_HOST=smtp.zoho.com
EMAIL_PORT=587
EMAIL_HOST_USER=<from-env>
EMAIL_HOST_PASSWORD=<from-env>
EMAIL_USE_TLS=1
DEFAULT_FROM_EMAIL=plane@insightpulseai.com
```

### Notification Policy

| Event | Email Sent | Slack Sent |
|-------|-----------|-----------|
| Work item assigned | Yes | Yes |
| Comment on work item | Yes | Yes |
| Cycle started | No | Yes |
| Cycle ended | Yes | Yes |
| Workspace invite | Yes | No |
| Password reset | Yes | No |
| Approval requested | Yes | Yes |

### Acceptance Criteria

| Criterion | Pass Condition |
|-----------|---------------|
| Invite emails deliver | New user receives invite email within 5 minutes |
| Comment notifications deliver | Assignee receives email on new comment |
| Reset/auth flows work | Password reset email arrives and link works |
| No spam folder routing | Emails land in inbox (SPF/DKIM/DMARC configured) |
| Sender identity correct | From address matches configured identity |

### Verification

```bash
# Verify SMTP connectivity from Plane container
# Check Plane admin for email delivery logs
# Send test invite and confirm receipt
# Verify SPF/DKIM/DMARC with:
dig TXT insightpulseai.com +short | grep spf
dig TXT mail._domainkey.insightpulseai.com +short
dig TXT _dmarc.insightpulseai.com +short
```

---

## 3. Integration Setup on Production

### 3.1 Slack Integration

| Field | Value |
|-------|-------|
| **Slack workspace** | InsightPulseAI workspace |
| **Integration type** | Plane native Slack integration |
| **Reference** | https://docs.plane.so/integrations/slack |

**Setup requirements:**

- Plane workspace admin connects Slack workspace via OAuth
- Map Plane projects to Slack channels
- Configure notification preferences per project

**Acceptance criteria:**

| Criterion | Pass Condition |
|-----------|---------------|
| Connection established | Slack workspace linked in Plane admin |
| Notifications flow | Work item updates appear in mapped Slack channel |
| Thread sync works | Slack thread creates/updates work item |
| Test notification sent | At least one test notification verified end-to-end |

**Credential boundary:**

- OAuth tokens managed by Plane internally
- No tokens stored in repo or env files
- Rotation owner: Workspace admin

---

### 3.2 Draw.io Integration

| Field | Value |
|-------|-------|
| **Integration type** | Plane native Draw.io integration |
| **Reference** | https://docs.plane.so/integrations/draw-io |

**Setup requirements:**

- Enable Draw.io integration in Plane workspace settings
- Verify diagram creation works inside Pages and Wiki

**Acceptance criteria:**

| Criterion | Pass Condition |
|-----------|---------------|
| Integration enabled | Draw.io option visible in Page editor |
| Diagram creation works | New diagram created and saved inside a Page |
| Diagram editing works | Existing diagram opens in Draw.io editor and saves back |
| Diagram renders | Diagram displays inline in Page view mode |

**Credential boundary:**

- Draw.io is client-side; no server credentials required
- No external service tokens

---

### 3.3 GitHub Integration

| Field | Value |
|-------|-------|
| **GitHub org** | Insightpulseai (or jgtolentino) |
| **Integration type** | Plane native GitHub integration |
| **Reference** | https://docs.plane.so/integrations/github |

**Setup requirements:**

- Plane workspace admin connects GitHub org via OAuth/App
- Link GitHub repos to Plane projects
- Configure PR/commit linkage

**Acceptance criteria:**

| Criterion | Pass Condition |
|-----------|---------------|
| Connection established | GitHub org linked in Plane admin |
| Repo linkage works | At least one repo linked to a Plane project |
| PR tracking works | PR created in linked repo appears in Plane work item |
| Commit tracking works | Commits referencing work item ID appear in work item activity |

**Credential boundary:**

- GitHub App or OAuth token managed by Plane internally
- Installation token scoped to linked org/repos only
- Rotation owner: Workspace admin

---

## 4. Production Readiness Checklist

This checklist must be completed before production is declared ready. Each item produces evidence in `docs/evidence/<YYYYMMDD-HHMM>/plane/`.

```markdown
## Production Readiness: Plane Commercial Self-Hosted

### Auth
- [ ] Auth mode selected and documented
- [ ] Login flow verified (at least 2 test users)
- [ ] Logout flow verified
- [ ] Invite flow verified (email received, registration completed)
- [ ] Role assignment verified (Admin, Member, Guest)

### Email
- [ ] SMTP configured and env vars set
- [ ] Invite email delivery verified
- [ ] Comment notification delivery verified
- [ ] Password reset flow verified
- [ ] SPF/DKIM/DMARC records verified
- [ ] Sender identity correct in delivered emails

### Slack
- [ ] Workspace connected
- [ ] Project-channel mapping configured
- [ ] Test notification delivered to Slack
- [ ] Thread-to-work-item sync verified

### Draw.io
- [ ] Integration enabled
- [ ] Test diagram created in a Page
- [ ] Diagram edit + save verified
- [ ] Diagram inline rendering verified

### GitHub
- [ ] Org connected
- [ ] At least one repo linked to a project
- [ ] PR linkage verified
- [ ] Commit linkage verified

### Seed Data
- [ ] Workspace created (InsightPulseAI)
- [ ] All 6 projects created
- [ ] Work item types configured
- [ ] Cycles created (current month + current quarter)
- [ ] Standard views created
- [ ] Wiki pages seeded
- [ ] Project pages seeded

### Backup / Update
- [ ] Backup procedure documented and tested
- [ ] Upgrade path documented
- [ ] Rollback procedure documented
```

---

## 5. Rollback and Credential Rotation

| Integration | Rollback Procedure | Rotation Owner |
|-------------|-------------------|----------------|
| **Auth (OIDC)** | Revert to local auth by removing OIDC env vars | Infra lead |
| **Email (SMTP)** | Swap SMTP credentials in env; restart Plane | Infra lead |
| **Slack** | Disconnect in Plane admin; reconnect with new OAuth | Workspace admin |
| **Draw.io** | Disable/re-enable in workspace settings | Workspace admin |
| **GitHub** | Disconnect in Plane admin; reconnect with new OAuth/App | Workspace admin |

All credential changes follow the secrets policy in CLAUDE.md: secrets live in runtime env vars or secret stores, never in committed files.
