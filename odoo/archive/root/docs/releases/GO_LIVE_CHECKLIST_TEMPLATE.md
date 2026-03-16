# Go-Live Checklist Template

**Purpose**: Comprehensive pre-launch checklist for InsightPulse AI Platform
**Stack**: Odoo CE + Supabase + Vercel + DigitalOcean + n8n
**Version**: 1.0 (2026-01-24)

---

## Usage

1. Copy this template to `GO_LIVE_CHECKLIST_<release-tag>.md`
2. Complete each section before go-live
3. All blockers must pass before deployment
4. Obtain sign-offs from required roles

---

## Summary

| Platform | Status | Owner | Sign-off Date |
|----------|--------|-------|---------------|
| DigitalOcean | ⬜ Pending | | |
| Supabase | ⬜ Pending | | |
| Vercel | ⬜ Pending | | |
| Odoo CE | ⬜ Pending | | |
| n8n | ⬜ Pending | | |
| GitHub CI/CD | ⬜ Pending | | |

---

## 🚫 Blockers (Must Pass)

These items **MUST** pass before go-live. Any failure blocks the release.

| ID | Blocker | Status | Evidence | Verified By |
|----|---------|--------|----------|-------------|
| B-01 | No secrets in version control | ⬜ | | |
| B-02 | RLS enabled on all tenant tables | ⬜ | | |
| B-03 | Backup restore verified (<90 days) | ⬜ | | |
| B-04 | Production access audit logging | ⬜ | | |
| B-05 | Main branch protection enabled | ⬜ | | |
| B-06 | Rollback procedure tested | ⬜ | | |

---

## 1. DigitalOcean Infrastructure

### 1.1 Domain & DNS

| Check | Status | Command/Evidence | Notes |
|-------|--------|------------------|-------|
| DNS A record → Droplet IP | ⬜ | `dig +short domain.com` | |
| DNS propagation complete | ⬜ | `nslookup domain.com` | |
| Subdomains configured | ⬜ | api, app, n8n, etc. | |
| TTL appropriate (300-3600) | ⬜ | | |

### 1.2 SSL/TLS

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Let's Encrypt cert valid | ⬜ | `curl -I https://domain` | |
| Auto-renewal configured | ⬜ | certbot timer/cron | |
| HTTPS redirect enforced | ⬜ | HTTP → HTTPS | |
| TLS 1.2+ only | ⬜ | No SSLv3/TLS1.0/1.1 | |
| HSTS header present | ⬜ | Strict-Transport-Security | |

### 1.3 Backups & Snapshots

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Managed DB backup enabled | ⬜ | `doctl db backups list` | |
| Droplet snapshots scheduled | ⬜ | Weekly minimum | |
| Backup retention ≥30 days | ⬜ | | |
| Restore drill completed | ⬜ | Date: _________ | |

### 1.4 Monitoring & Alerts

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Droplet metrics enabled | ⬜ | CPU/mem/disk/net | |
| Database metrics enabled | ⬜ | Connections/queries | |
| CPU alert >80% | ⬜ | | |
| Memory alert >85% | ⬜ | | |
| Disk alert >90% | ⬜ | | |
| Response time alert >2s | ⬜ | | |
| Alert recipients tested | ⬜ | | |

### 1.5 Security

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Cloud Firewall enabled | ⬜ | `doctl firewall list` | |
| Only required ports open | ⬜ | 22, 80, 443, 8069 | |
| SSH key-only auth | ⬜ | No password auth | |
| Root login disabled | ⬜ | | |
| Fail2ban installed | ⬜ | | |

---

## 2. Supabase Backend

### 2.1 Database Security

| Check | Status | Command/Evidence | Notes |
|-------|--------|------------------|-------|
| RLS enabled all tables | ⬜ | `SELECT * FROM pg_policies` | |
| RLS policies tested | ⬜ | Per user role | |
| Service role key secured | ⬜ | Not client-exposed | |
| Anon key minimized | ⬜ | | |
| Strong DB password | ⬜ | Rotated recently | |

### 2.2 Authentication

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Auth providers configured | ⬜ | Email, OAuth | |
| Email templates customized | ⬜ | | |
| Password policy enforced | ⬜ | | |
| MFA for admins | ⬜ | | |
| Session timeouts set | ⬜ | | |

### 2.3 Edge Functions

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| All functions deployed | ⬜ | `supabase functions list` | |
| Env vars set (not hardcoded) | ⬜ | | |
| Error handling implemented | ⬜ | | |
| Rate limiting configured | ⬜ | | |
| CORS policies correct | ⬜ | | |

### 2.4 Performance

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Connection pooling | ⬜ | PgBouncer | |
| Indexes on query columns | ⬜ | | |
| Slow queries reviewed | ⬜ | pg_stat_statements | |
| Connection limits | ⬜ | | |

---

## 3. Vercel Frontend

### 3.1 Domain & SSL

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Production domain added | ⬜ | | |
| SSL certificate active | ⬜ | | |
| www redirect configured | ⬜ | | |

### 3.2 Environment & Build

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Prod env vars set | ⬜ | | |
| No secrets in client code | ⬜ | | |
| Production build succeeds | ⬜ | `next build` | |
| Bundle size optimized | ⬜ | | |
| Core Web Vitals passing | ⬜ | LCP, FID, CLS | |

### 3.3 Security

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Security headers set | ⬜ | CSP, X-Frame-Options | |
| API routes protected | ⬜ | | |
| No source maps exposed | ⬜ | | |

---

## 4. Odoo CE (ERP)

### 4.1 Configuration

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| `proxy_mode = True` | ⬜ | odoo.conf | |
| Workers configured | ⬜ | 2-4 for production | |
| Log level = info | ⬜ | Not debug | |
| Session timeout set | ⬜ | | |

### 4.2 Database

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Production DB created | ⬜ | | |
| dbfilter configured | ⬜ | | |
| Master password secured | ⬜ | | |
| Demo data NOT installed | ⬜ | | |

### 4.3 Modules

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| All required modules installed | ⬜ | | |
| IPAI modules verified | ⬜ | | |
| OCA modules pinned | ⬜ | Specific versions | |
| Module auto-install disabled | ⬜ | | |

### 4.4 Security

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Admin password changed | ⬜ | Not default | |
| API keys generated | ⬜ | Not shared | |
| File upload limits set | ⬜ | | |

---

## 5. n8n Automation

### 5.1 Configuration

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Production credentials | ⬜ | | |
| Webhook URLs production | ⬜ | | |
| Timezone correct | ⬜ | | |

### 5.2 Workflows

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Workflows exported to Git | ⬜ | | |
| Error triggers configured | ⬜ | | |
| Retry logic implemented | ⬜ | | |
| Idempotency verified | ⬜ | | |

---

## 6. GitHub CI/CD

### 6.1 Branch Protection

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Main branch protected | ⬜ | | |
| Required status checks | ⬜ | | |
| Required reviews | ⬜ | | |
| Force push disabled | ⬜ | | |

### 6.2 Security

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Secrets in GitHub Secrets | ⬜ | | |
| Dependabot alerts enabled | ⬜ | | |
| Code scanning enabled | ⬜ | | |
| Secret scanning enabled | ⬜ | | |

---

## 7. Performance Testing

| Check | Status | Evidence | Notes |
|-------|--------|----------|-------|
| Load test at expected traffic | ⬜ | | |
| Stress test at 2x traffic | ⬜ | | |
| p95 response time <500ms | ⬜ | | |
| Error rate <0.1% | ⬜ | | |

---

## 8. Go-Live Execution

### T-24h (Pre-Go-Live)

- [ ] All checklist items complete
- [ ] Stakeholder sign-off obtained
- [ ] User communication sent
- [ ] Support team briefed

### T-0 (Go-Live)

- [ ] DNS cutover executed
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Monitoring confirmed

### T+1h (Post-Go-Live)

- [ ] No critical errors
- [ ] Performance within targets
- [ ] User feedback positive

### T+24h (Stabilization)

- [ ] Backup verified
- [ ] Metrics baseline captured
- [ ] Evidence pack committed

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Platform Lead | | | |
| Security Lead | | | |
| Operations Lead | | | |
| Product Owner | | | |

---

## References

- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Vercel Production Checklist](https://vercel.com/docs/production-checklist)
- [Supabase Production Guide](https://supabase.com/docs/guides/platform/going-into-prod)
- [Odoo Deployment](https://www.odoo.com/documentation/18.0/administration/on_premise/deploy.html)
