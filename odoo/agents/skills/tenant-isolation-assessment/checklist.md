# Checklist: Tenant Isolation Assessment

## Identity Boundary

- [ ] Token validation enforces tenant_id claim on every API endpoint
- [ ] Token without tenant_id rejected (tested)
- [ ] Token with tampered tenant_id rejected (tested)
- [ ] RBAC assignments scoped to tenant — no cross-tenant roles
- [ ] Managed identities scoped to correct tenant resources
- [ ] No shared service accounts with cross-tenant access
- [ ] Session management prevents tenant context switching

## Data Access Paths

- [ ] Database isolation model documented (per-tenant DB, schema, RLS)
- [ ] Cross-tenant query attempted and blocked (tested)
- [ ] RLS policies active on all tenant-scoped tables (if shared)
- [ ] RLS bypass not possible via application code (no SUPERUSER)
- [ ] Backup/restore scoped to individual tenant
- [ ] Data export contains only requesting tenant's data
- [ ] No cross-tenant foreign keys or joins

## Network Segmentation

- [ ] PaaS services accessible only via private endpoints
- [ ] No public IP on PostgreSQL, Redis, Storage, Key Vault
- [ ] NSG deny-all default on all subnets
- [ ] Front Door is sole ingress — direct Container App access blocked
- [ ] Cross-stamp network path does not exist
- [ ] VNET flow logs enabled for audit

## Encryption

- [ ] TDE enabled on all databases
- [ ] Per-tenant encryption keys (for confidential/restricted tiers)
- [ ] Key rotation schedule defined and tested
- [ ] Data encrypted in transit (TLS 1.2+ on all connections)
- [ ] Encryption at rest for storage accounts and blobs
- [ ] Key Vault access restricted to authorized services only

## Verdict Assignment

- [ ] All four domains assessed with evidence
- [ ] Each finding classified by severity (critical, high, medium, low)
- [ ] Verdict assigned based on highest severity finding
- [ ] Remediation plan produced for all high and critical findings
- [ ] Assessment report signed off by security team
