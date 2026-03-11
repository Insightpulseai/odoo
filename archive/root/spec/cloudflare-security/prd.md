# Cloudflare Security Hardening - Product Requirements Document

**Status**: Draft
**Priority**: P0 (Critical Security Fix)
**Target**: Production deployment within 48 hours
**Owner**: Infrastructure Team
**Date**: 2026-02-13

---

## Executive Summary

Implement Cloudflare WAF (Web Application Firewall) rules to protect MCP agent ingress, n8n automation, and Superset BI endpoints from direct attacks. Current DNS-only configuration exposes critical services to WAF bypass, credential stuffing, and DDoS attacks.

**Impact**: HIGH - Prevents unauthorized MCP tool execution, automation takeover, and BI data exfiltration

---

## Problem Statement

### Current State (VULNERABLE)

Three critical services are exposed via DNS-only records, bypassing Cloudflare protection:

| Endpoint | Service | Risk Level | Attack Vectors |
|----------|---------|------------|----------------|
| `mcp.insightpulseai.com` | Agent ingress (11 MCP servers) | **HIGH** | Unauthenticated tool calls, enumeration, credential stuffing |
| `n8n.insightpulseai.com` | Workflow automation | **CRITICAL** | Automation takeover, workflow manipulation |
| `superset.insightpulseai.com` | BI + SQL interface | **MEDIUM** | SQL injection, data exfiltration, unauthorized analytics access |

**Attack Surface**:
- Direct IP exposure (`178.128.112.214`)
- No WAF protection (OWASP Core, Managed Rules disabled)
- No rate limiting (unlimited requests per IP)
- No bot mitigation (crawler/scraper access)
- No geo-restrictions or IP allowlists

### Target State (HARDENED)

All services proxied through Cloudflare with defense-in-depth:

```
Client → Cloudflare WAF → Origin (178.128.112.214)
           ↓
    - Authentication enforcement
    - Rate limiting (per IP, per user)
    - Bot mitigation
    - SQL injection blocking
    - Geo-restrictions (optional)
    - OWASP Core Ruleset
```

---

## Requirements

### Functional Requirements

#### F1: MCP Endpoint Protection
- **FR1.1**: Block all unauthenticated requests to `mcp.insightpulseai.com` (must have `Authorization: Bearer` header)
- **FR1.2**: Rate limit to 100 requests/minute per IP (challenge on exceed)
- **FR1.3**: (Optional) Allowlist known IP ranges (Figma Make, GitHub MCP)
- **FR1.4**: Allow `/healthz` endpoint without authentication (monitoring)

#### F2: n8n Automation Protection
- **FR2.1**: Block known bots and crawlers (prevent indexing)
- **FR2.2**: (Optional) Challenge requests from unknown ASNs (non-cloud providers)
- **FR2.3**: (Optional) Require n8n session cookie for non-health-check requests
- **FR2.4**: Rate limit to 60 requests/minute per IP (block on exceed)

#### F3: Superset BI Protection
- **FR3.1**: Block SQL injection patterns (`' OR 1=1`, `UNION SELECT`, `DROP TABLE`)
- **FR3.2**: (Optional) Geo-restrict to allowed countries (US, PH, SG)
- **FR3.3**: Rate limit to 300 requests/5 minutes per authenticated user
- **FR3.4**: Enable OWASP Core Ruleset (medium sensitivity)

#### F4: Staging Environment Isolation
- **FR4.1**: (Optional) Block public access to `stage-*` subdomains (office/VPN IPs only)
- **FR4.2**: Apply same security rules to staging subdomains

#### F5: Global Security Controls
- **FR5.1**: Block common exploit patterns (path traversal, XSS, Log4Shell)
- **FR5.2**: Global rate limit: 1000 requests/minute per IP (challenge on exceed)
- **FR5.3**: Enable Cloudflare Managed Ruleset (known CVEs, bot attacks)

### Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: Firewall rule evaluation latency < 5ms (p95)
- **NFR1.2**: No impact on legitimate user experience (< 0.1% false positive rate)
- **NFR1.3**: Health check endpoints always reachable (99.9% uptime)

#### NFR2: Observability
- **NFR2.1**: All blocked requests logged to Cloudflare Analytics
- **NFR2.2**: Alerting on rule triggers exceeding threshold (>100/hour)
- **NFR2.3**: Weekly security report with top blocked IPs and attack patterns

#### NFR3: Maintainability
- **NFR3.1**: All rules defined in declarative Terraform configuration
- **NFR3.2**: Rule priority documented with rationale and false positive risk
- **NFR3.3**: Quarterly rule review and IP allowlist updates

---

## Architecture

### Cloudflare WAF Rule Pipeline

```
Incoming Request
    ↓
1. Health Check Bypass (Priority 11)
    ↓ (if not /healthz)
2. IP Allowlist (Priority 3) - Optional
    ↓ (if not whitelisted)
3. Authentication Check (Priority 1, 5)
    ↓ (if authenticated)
4. Rate Limiting (Priority 2, 6, 10)
    ↓ (if within limits)
5. Exploit Pattern Blocking (Priority 8, 12)
    ↓ (if clean)
6. Bot Mitigation (Priority 4)
    ↓ (if human/allowed bot)
7. Geo-Restriction (Priority 7) - Optional
    ↓ (if allowed country)
8. OWASP Core Ruleset (Managed)
    ↓ (if passes)
9. Cloudflare Managed Ruleset (Managed)
    ↓
Allow Request → Origin
```

### Trust Boundary

```
┌──────────────────────────────────────────────────────────┐
│ Cloudflare WAF (Defense-in-Depth)                       │
├──────────────────────────────────────────────────────────┤
│ - Authentication enforcement                             │
│ - Rate limiting (per IP, per user, global)              │
│ - Bot mitigation (cf.client.bot)                        │
│ - SQL injection blocking (pattern matching)             │
│ - OWASP Core Ruleset (SQLi, XSS, RCE, LFI/RFI)         │
│ - Cloudflare Managed Rules (CVEs, DDoS, bot attacks)   │
│ - Geo-restrictions (optional)                           │
│ - IP allowlist (optional)                               │
└──────────────────────────────────────────────────────────┘
                       ↓ HTTPS (TLS 1.3)
┌──────────────────────────────────────────────────────────┐
│ Origin Server (178.128.112.214)                         │
├──────────────────────────────────────────────────────────┤
│ - MCP Gateway (pulse-hub-web-an645.ondigitalocean.app)  │
│ - n8n Automation (port 5678)                            │
│ - Superset BI (port 8088)                               │
│ - Odoo ERP (port 8069)                                  │
│ - OCR Service (port 8080)                               │
│ - Auth Service (port 3000)                              │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: DNS Proxying (COMPLETE ✅)
- [x] Update `infra/dns/subdomain-registry.yaml` (SSOT)
- [x] Set `cloudflare_proxied: true` for mcp, n8n, superset (prod + staging)
- [x] Regenerate Terraform artifacts via `scripts/generate-dns-artifacts.sh`
- [x] Commit changes to `feat/infra-dns-ssot` branch
- [x] Push to remote repository

**Evidence**: Commit b2b74b22 - "security(dns): harden Cloudflare proxying for MCP, n8n, Superset"

### Phase 2: Terraform Apply (NEXT)
**Task**: Apply DNS changes to Cloudflare production zone

```bash
cd infra/cloudflare/envs/prod
terraform plan  # Review changes
terraform apply # Apply proxying changes
```

**Expected Changes**:
- 6 DNS records updated (`proxied: false → true`)
- mcp.insightpulseai.com → Cloudflare IP (was: 178.128.112.214 direct)
- superset.insightpulseai.com → Cloudflare IP
- stage-mcp/n8n/superset → Cloudflare IPs

**Validation**:
```bash
# Should return Cloudflare IPs, not origin
dig mcp.insightpulseai.com +short
dig n8n.insightpulseai.com +short
dig superset.insightpulseai.com +short
```

### Phase 3: Firewall Rules Implementation
**Task**: Deploy Cloudflare WAF rules from `spec/cloudflare-security/firewall-rules.json`

**Approach**: Incremental deployment with testing

1. **Create Terraform module** (`infra/cloudflare/modules/firewall-rules/`)
   - Convert JSON spec to `cloudflare_firewall_rule` resources
   - Support dynamic rule enablement via variables

2. **Test in log-only mode** (first 7 days)
   ```hcl
   action = "log"  # Override all rules to log-only
   ```
   - Monitor Cloudflare Analytics for false positives
   - Adjust expressions and thresholds based on real traffic

3. **Enable blocking incrementally**
   - Week 1: Health check bypass (Priority 11)
   - Week 2: Exploit pattern blocking (Priority 8, 12)
   - Week 3: Rate limiting (Priority 2, 6, 10)
   - Week 4: Authentication enforcement (Priority 1, 5)
   - Week 5: Optional rules (geo, IP allowlist, ASN)

4. **Enable managed rulesets**
   - OWASP Core Ruleset (medium sensitivity)
   - Cloudflare Managed Ruleset (low sensitivity)

### Phase 4: Monitoring & Alerting
**Task**: Configure observability for firewall rules

1. **Cloudflare Analytics Dashboard**
   - Top blocked IPs (by rule)
   - False positive rate tracking
   - Attack pattern visualization

2. **Alerting Rules** (via Cloudflare Workers or webhook)
   - Trigger: >100 blocked requests/hour for any single rule
   - Trigger: False positive rate >1% (low threat score blocks)
   - Action: Send alert to Slack/email

3. **Weekly Security Report**
   - Blocked request summary (by rule, by IP, by country)
   - Top attack vectors identified
   - Recommendations for rule adjustments

---

## Success Criteria

### Security Metrics
- ✅ 0 unauthenticated MCP tool executions in production
- ✅ 0 SQL injection attempts reaching Superset backend
- ✅ 95% reduction in bot traffic to n8n automation UI
- ✅ <0.1% false positive rate (legitimate requests blocked)

### Performance Metrics
- ✅ Firewall rule evaluation latency < 5ms (p95)
- ✅ Health check endpoint availability 99.9%+
- ✅ No user-reported authentication issues (except attackers)

### Operational Metrics
- ✅ All firewall rules deployed via Terraform (Infrastructure as Code)
- ✅ Quarterly rule review completed on schedule
- ✅ Alerting configured and tested for critical rules

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **False positives block legitimate users** | HIGH | MEDIUM | Start with log-only mode, monitor for 7 days, adjust thresholds |
| **Rate limiting too aggressive** | MEDIUM | MEDIUM | Set conservative limits initially, increase based on traffic analysis |
| **IP allowlist blocks new integrations** | MEDIUM | LOW | Document allowlist update process, monitor for authentication failures |
| **Terraform apply breaks DNS resolution** | CRITICAL | LOW | Test in staging first, have rollback plan, monitor DNS resolution |
| **MCP authentication breaks existing clients** | HIGH | MEDIUM | Verify all MCP clients send Bearer token, provide migration guide |

---

## Open Questions

1. **Q**: What are the actual Figma Make webhook IP ranges for MCP allowlist?
   **A**: TBD - Research Figma documentation or contact support

2. **Q**: What is the exact n8n session cookie name for authentication rule?
   **A**: TBD - Inspect n8n HTTP headers or check n8n configuration

3. **Q**: Should we enable geo-restriction for Superset, or allow global access?
   **A**: TBD - Confirm with business stakeholders if BI access should be global

4. **Q**: What office/VPN IP ranges should be allowlisted for staging access?
   **A**: TBD - Collect IP ranges from IT/DevOps team

5. **Q**: Should MCP allowlist be enabled immediately, or wait for IP range confirmation?
   **A**: TBD - Recommend waiting to avoid blocking legitimate traffic

---

## Dependencies

- ✅ DNS proxying enabled (Phase 1 complete)
- ⏳ Cloudflare API token with Firewall Rules write permission
- ⏳ Terraform Cloudflare provider configured (`~/.terraformrc`)
- ⏳ Figma and GitHub IP ranges confirmed (for MCP allowlist)
- ⏳ n8n session cookie name confirmed (for authentication rule)
- ⏳ Office/VPN IP ranges confirmed (for staging restriction)

---

## Acceptance Criteria

### DNS Proxying (Phase 2)
- [ ] `terraform apply` completes successfully with 0 errors
- [ ] `dig mcp.insightpulseai.com` returns Cloudflare IP ranges
- [ ] `dig superset.insightpulseai.com` returns Cloudflare IP ranges
- [ ] All staging subdomains resolve to Cloudflare IPs
- [ ] Health checks pass for all proxied services (200 OK)

### Firewall Rules (Phase 3)
- [ ] All 12 firewall rules deployed via Terraform
- [ ] Log-only mode validated for 7 days (no critical false positives)
- [ ] Rules enabled incrementally per deployment plan
- [ ] MCP authentication enforcement active (blocks unauthenticated requests)
- [ ] SQL injection pattern blocking active (blocks malicious queries)
- [ ] OWASP Core and Managed Rulesets enabled

### Monitoring (Phase 4)
- [ ] Cloudflare Analytics dashboard configured with firewall metrics
- [ ] Alerting rules configured for >100 blocks/hour threshold
- [ ] Weekly security report generated and sent to stakeholders
- [ ] False positive rate < 0.1% (monitored daily)

---

## Timeline

| Phase | Duration | Start Date | End Date | Status |
|-------|----------|------------|----------|--------|
| Phase 1: DNS Proxying | 1 day | 2026-02-13 | 2026-02-13 | ✅ Complete |
| Phase 2: Terraform Apply | 1 day | 2026-02-14 | 2026-02-14 | ⏳ Next |
| Phase 3: Firewall Rules | 35 days (5 weeks) | 2026-02-15 | 2026-03-22 | 🔜 Planned |
| Phase 4: Monitoring | 7 days | 2026-03-23 | 2026-03-30 | 🔜 Planned |

**Total Duration**: 44 days (~6 weeks)

---

## References

- **DNS SSOT**: `infra/dns/subdomain-registry.yaml`
- **Firewall Rules Spec**: `spec/cloudflare-security/firewall-rules.json`
- **Terraform Module**: `infra/cloudflare/modules/firewall-rules/` (to be created)
- **Cloudflare Docs**: https://developers.cloudflare.com/firewall/
- **GitHub IP Ranges**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses

---

**Document Version**: 1.0
**Last Updated**: 2026-02-13
**Next Review**: 2026-03-13 (30 days)
