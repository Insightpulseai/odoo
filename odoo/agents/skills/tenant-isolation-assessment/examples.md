# Examples: Tenant Isolation Assessment

## Example 1: Verdict — ISOLATED

**Scenario**: Mature multi-tenant platform with database-per-tenant, Entra ID, and private endpoints.

**Assessment**:
```
## Verdict: ISOLATED

### Identity Boundary: PASS
- Token validation enforces tenant_id on all 47 API endpoints
  Evidence: Automated test suite covers all endpoints, 0 bypasses found
- Token tampering rejected by signature validation
  Evidence: Pen test report section 4.2 — all tampered tokens rejected
- RBAC scoped to tenant via Entra ID app roles
  Evidence: Role assignment audit — no cross-tenant grants

### Data Isolation: PASS
- Database-per-tenant model — each tenant has dedicated PostgreSQL database
  Evidence: pg_database listing shows 30 separate databases
- Cross-database access impossible without separate credentials
  Evidence: Connection attempt from tenant A's app to tenant B's DB rejected
- Per-tenant backup verified
  Evidence: Backup restore test for tenant "acme-corp" — complete and isolated

### Network Segmentation: PASS
- All PaaS services on private endpoints
  Evidence: Port scan of public IPs — 0 open ports on PaaS services
- Front Door enforcement — direct Container App access returns 403
  Evidence: curl to Container App FQDN returns 403 (X-Azure-Ref header missing)
- Cross-stamp VNET isolation verified
  Evidence: Network flow logs show 0 cross-VNET traffic

### Encryption: PASS
- TDE enabled on all PostgreSQL servers
  Evidence: az postgres flexible-server show — encryption_status: Enabled
- Per-tenant keys in Key Vault for enterprise tier
  Evidence: Key Vault audit log shows per-tenant key usage
- TLS 1.2 enforced on all connections
  Evidence: SSL scan — minimum TLS 1.2 across all endpoints

### Recommendations (low severity)
- Consider rotating encryption keys more frequently (current: annual, recommended: quarterly)
```

---

## Example 2: Verdict — PARTIAL

**Scenario**: Platform with good identity isolation but missing network controls.

**Assessment**:
```
## Verdict: PARTIAL

### Identity Boundary: PASS
- All endpoints validate tenant_id claim
- RBAC properly scoped

### Data Isolation: PASS
- RLS policies on all shared tables
- Cross-tenant query returns 0 rows (verified)

### Network Segmentation: FAIL
- [HIGH] PostgreSQL accessible on public IP (firewall rules too broad)
  Evidence: nmap scan shows port 5432 open on pg-ipai-prod-sea-001 public IP
- [HIGH] Container Apps accessible directly (Front Door not enforced)
  Evidence: curl to *.azurecontainerapps.io returns 200

### Encryption: PASS
- TDE enabled, TLS enforced

### Remediation Plan
1. [HIGH] Disable public access on PostgreSQL, enable private endpoint — Effort: 2 hours
2. [HIGH] Configure Container Apps ingress to require Front Door header — Effort: 1 hour
```

---

## Example 3: Verdict — NOT_ISOLATED

**Scenario**: Platform with shared database, no RLS, application-level filtering only.

**Assessment**:
```
## Verdict: NOT_ISOLATED

### Identity Boundary: PARTIAL
- [MEDIUM] Token contains tenant_id but 3/47 endpoints do not validate it
  Evidence: Endpoint audit — /api/reports, /api/export, /api/search missing validation

### Data Isolation: FAIL
- [CRITICAL] Shared database with no RLS — application-level filtering only
  Evidence: Direct SQL query without tenant filter returns all tenants' data
- [CRITICAL] Backup is whole-database — cannot restore single tenant
  Evidence: pg_dump includes all tenant data

### Network Segmentation: FAIL
- [HIGH] PostgreSQL on public IP

### Encryption: PARTIAL
- [MEDIUM] No per-tenant encryption keys

### Remediation Plan
1. [CRITICAL] Implement PostgreSQL RLS on all tenant-scoped tables — Effort: 2 weeks
2. [CRITICAL] Add tenant_id validation to 3 missing API endpoints — Effort: 1 day
3. [HIGH] Migrate PostgreSQL to private endpoint — Effort: 2 hours
4. [MEDIUM] Implement per-tenant encryption keys — Effort: 1 week
```
