# Web Shell Threat Model

**Version:** 1.0.0
**Date:** 2026-01-29
**Odoo.sh Parity:** GAP 4 - Browser Web Shell

---

## 1. Overview

This document provides a security threat model for the browser-based web shell feature, implementing Odoo.sh-style terminal access for self-hosted environments.

### 1.1 Component Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Web Shell Architecture                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   User Browser                                                           │
│       │                                                                  │
│       ▼ HTTPS (TLS 1.3)                                                  │
│   ┌─────────────────┐                                                    │
│   │  Caddy Proxy    │  - SSL termination                                │
│   │  (Port 8443)    │  - Basic Auth / OAuth                              │
│   │                 │  - Rate limiting                                   │
│   │                 │  - Security headers                                │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼ HTTP (Internal)                                             │
│   ┌─────────────────┐                                                    │
│   │     Wetty       │  - WebSocket terminal                              │
│   │   (Port 3000)   │  - Session management                              │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼ SSH (Port 22)                                               │
│   ┌─────────────────┐                                                    │
│   │  SSH Bastion    │  - Limited shell                                   │
│   │                 │  - Audit logging                                   │
│   │                 │  - No sudo by default                              │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼ Volume mounts (read-only)                                   │
│   ┌─────────────────┐                                                    │
│   │  Odoo Container │  - Data directory                                  │
│   │                 │  - Addons                                          │
│   │                 │  - Scripts                                         │
│   └─────────────────┘                                                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Trust Boundaries

### 2.1 Boundary Definitions

| Boundary | Description | Trust Level |
|----------|-------------|-------------|
| **Internet ↔ Caddy** | External network to reverse proxy | Untrusted |
| **Caddy ↔ Wetty** | Authenticated HTTPS to internal HTTP | Partially trusted |
| **Wetty ↔ SSH Bastion** | WebSocket to SSH | Trusted |
| **SSH Bastion ↔ Odoo** | Shell to application data | Highly trusted |

### 2.2 Trust Assumptions

1. TLS certificates are valid and properly configured
2. Users must authenticate before accessing shell
3. SSH bastion has no internet access
4. Volume mounts are read-only by default
5. Audit logging is always enabled

---

## 3. Threat Analysis

### 3.1 STRIDE Classification

#### 3.1.1 Spoofing (S)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| S1 | Attacker impersonates legitimate user | Medium | High | MFA, session tokens, IP allowlist |
| S2 | Man-in-the-middle attack | Low | Critical | TLS 1.3, HSTS, certificate pinning |
| S3 | Session hijacking | Medium | High | Secure cookies, short TTL, binding to IP |

**Controls:**
- [x] HTTPS with TLS 1.3
- [x] HSTS with preload
- [x] Basic Auth (upgrade to OAuth/SAML for production)
- [ ] IP allowlisting (optional)
- [ ] MFA integration (future)

#### 3.1.2 Tampering (T)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| T1 | Command injection via WebSocket | Medium | Critical | Input validation, CSP |
| T2 | Configuration tampering | Low | High | Read-only mounts, integrity checks |
| T3 | Log tampering | Low | Medium | Append-only logs, remote logging |

**Controls:**
- [x] Input sanitization in Wetty
- [x] Read-only volume mounts
- [x] Centralized logging (Fluentd)
- [ ] Integrity monitoring (future)

#### 3.1.3 Repudiation (R)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| R1 | User denies executing commands | Medium | Medium | Comprehensive audit logging |
| R2 | Missing access logs | Low | Low | Multiple logging sinks |

**Controls:**
- [x] Shell session recording
- [x] Audit log with timestamps
- [x] User identification in logs
- [x] Log forwarding to Supabase/S3

#### 3.1.4 Information Disclosure (I)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| I1 | Sensitive data in terminal output | Medium | High | Data masking, warning banners |
| I2 | Credential exposure in logs | Low | Critical | Log sanitization |
| I3 | Memory disclosure | Low | Medium | Container isolation |

**Controls:**
- [x] Warning banners on login
- [x] Log sanitization (passwords, tokens)
- [x] Container resource limits
- [ ] Screen recording restrictions (future)

#### 3.1.5 Denial of Service (D)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| D1 | Resource exhaustion via shell | Medium | Medium | CPU/memory limits |
| D2 | WebSocket flooding | Medium | Medium | Rate limiting |
| D3 | Fork bomb | Medium | High | Process limits, nproc |

**Controls:**
- [x] Rate limiting (30 req/min)
- [x] Container resource limits (0.5 CPU, 256MB)
- [x] Session timeout (30 min idle)
- [ ] ulimit restrictions (future)

#### 3.1.6 Elevation of Privilege (E)

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| E1 | Container escape | Low | Critical | Non-root, minimal capabilities |
| E2 | Sudo abuse | Medium | High | No sudo by default |
| E3 | SSH key theft | Low | High | Key rotation, no persistent keys |

**Controls:**
- [x] Non-root container
- [x] Dropped capabilities (CAP_DROP: ALL)
- [x] No sudo access
- [x] Read-only filesystem where possible
- [ ] seccomp profiles (future)

---

## 4. Security Controls Matrix

### 4.1 Authentication & Authorization

| Control | Status | Implementation |
|---------|--------|----------------|
| Basic Auth | ✅ | Caddy basicauth |
| OAuth 2.0 | ⏳ | Caddy forward_auth (future) |
| SAML SSO | ⏳ | Keycloak integration (future) |
| MFA | ⏳ | TOTP via Keycloak (future) |
| IP Allowlist | ⚙️ | Optional in Caddyfile |
| Role-Based Access | ⏳ | Different shell profiles |

### 4.2 Network Security

| Control | Status | Implementation |
|---------|--------|----------------|
| TLS 1.3 | ✅ | Caddy auto-TLS |
| HSTS | ✅ | Caddy headers |
| Rate Limiting | ✅ | Caddy rate_limit |
| Firewall Rules | ⚙️ | iptables/ufw |
| Network Isolation | ✅ | Docker networks |

### 4.3 Container Security

| Control | Status | Implementation |
|---------|--------|----------------|
| Non-root User | ✅ | USER directive |
| Read-only FS | ✅ | ro volume mounts |
| Resource Limits | ✅ | deploy.resources |
| Capability Drop | ✅ | cap_drop: ALL |
| Seccomp | ⏳ | Profile needed |

### 4.4 Audit & Monitoring

| Control | Status | Implementation |
|---------|--------|----------------|
| Access Logs | ✅ | Caddy JSON logs |
| Shell History | ✅ | Bash history |
| Session Recording | ✅ | Wetty logs |
| Alert on Anomaly | ⏳ | n8n workflow |
| SIEM Integration | ⏳ | Fluentd → Supabase |

---

## 5. Risk Assessment

### 5.1 Risk Matrix

| Risk | Likelihood | Impact | Score | Status |
|------|------------|--------|-------|--------|
| Unauthorized access | Medium | High | **6** | Mitigated |
| Data exfiltration | Low | High | **4** | Mitigated |
| Privilege escalation | Low | Critical | **5** | Mitigated |
| DoS attack | Medium | Medium | **4** | Mitigated |
| Container escape | Very Low | Critical | **3** | Mitigated |

**Risk Score Legend:**
- 1-3: Low (acceptable)
- 4-6: Medium (monitor)
- 7-9: High (action required)

### 5.2 Residual Risks

1. **Social Engineering**: Users may be tricked into running malicious commands
   - Mitigation: Security awareness training, command allowlisting

2. **Zero-Day Vulnerabilities**: Unpatched vulnerabilities in Wetty/SSH
   - Mitigation: Regular updates, security scanning

3. **Insider Threat**: Authorized users abusing access
   - Mitigation: Audit logging, anomaly detection

---

## 6. Compliance Requirements

### 6.1 Relevant Standards

| Standard | Requirement | Status |
|----------|-------------|--------|
| SOC 2 Type II | Access logging | ✅ |
| ISO 27001 | Access control | ✅ |
| PCI DSS | Session management | ⚙️ |
| GDPR | Data protection | ✅ |

### 6.2 Audit Trail Requirements

All shell sessions must log:
- [ ] User identity (username, IP, user-agent)
- [ ] Session start/end times
- [ ] Commands executed
- [ ] Files accessed
- [ ] Errors and warnings

---

## 7. Incident Response

### 7.1 Detection Triggers

1. Failed login attempts > 5 in 5 minutes
2. Unusual command patterns (regex detection)
3. Large data transfers (> 10MB)
4. Access outside business hours
5. Commands matching known attack patterns

### 7.2 Response Actions

| Severity | Response | Timeline |
|----------|----------|----------|
| Low | Log, notify | Next business day |
| Medium | Investigate, alert | Within 4 hours |
| High | Block, investigate | Within 1 hour |
| Critical | Disable, escalate | Immediate |

### 7.3 Kill Switch

Emergency disable procedure:

```bash
# Immediate shutdown
docker compose -f docker-compose.shell.yml down

# Or block at firewall
ufw deny 8443/tcp

# Preserve evidence
docker logs odoo-web-shell > /var/log/shell-incident-$(date +%Y%m%d).log
```

---

## 8. Recommendations

### 8.1 Immediate (P0)

- [x] Enable TLS with HSTS
- [x] Implement basic authentication
- [x] Configure rate limiting
- [x] Set up audit logging

### 8.2 Short-term (P1)

- [ ] Upgrade to OAuth/SAML SSO
- [ ] Implement MFA
- [ ] Add IP allowlisting
- [ ] Configure alerting

### 8.3 Long-term (P2)

- [ ] Session recording with replay
- [ ] Command allowlisting
- [ ] Anomaly detection ML
- [ ] Zero-trust network access

---

## 9. References

- [Odoo.sh Security](https://www.odoo.sh/security)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Document Control:**
- Created: 2026-01-29
- Author: Claude Code (Gap Closure)
- Review Date: Quarterly
- Classification: Internal
