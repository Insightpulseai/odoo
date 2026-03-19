# Checklist: Data Isolation Pattern Design

## Pre-flight

- [ ] Tenant count (current and projected 12-month) documented
- [ ] Data sensitivity classification per data category established
- [ ] Compliance requirements mapped (GDPR, SOC2, data residency)
- [ ] Cost budget per tenant for data infrastructure defined
- [ ] Performance SLA per tenant documented (latency, throughput)

## Pattern Selection

- [ ] Decision matrix created scoring each pattern against requirements
- [ ] Selected pattern documented with rationale
- [ ] Hybrid approach documented if different tiers use different patterns
- [ ] Azure resource limits validated against selected pattern and tenant count
- [ ] Migration path defined for moving tenants between isolation levels

## Database Topology

- [ ] Database/schema/table layout documented per tenant tier
- [ ] Connection pooling strategy defined (PgBouncer, connection limits)
- [ ] Failover and high availability configured per isolation level
- [ ] Read replica strategy defined for read-heavy tenants
- [ ] Database naming convention includes tenant identifier

## Encryption

- [ ] Per-tenant encryption keys created in Azure Key Vault
- [ ] Key rotation procedure documented and tested
- [ ] Transparent Data Encryption (TDE) enabled at server level
- [ ] Column-level encryption for highly sensitive fields (if required)
- [ ] Key access policies follow least-privilege (only tenant's services)

## Row-Level Security (if applicable)

- [ ] RLS policies created for every shared table
- [ ] RLS enforced via `SET app.current_tenant` or equivalent session variable
- [ ] RLS policies tested — cross-tenant query returns zero rows
- [ ] RLS bypass prevented — no SUPERUSER queries in application code
- [ ] Performance impact of RLS measured and acceptable

## Tenant Data Lifecycle

- [ ] Per-tenant backup procedure documented and tested
- [ ] Per-tenant restore tested to new environment
- [ ] GDPR data export covers all tenant data across all tables
- [ ] Tenant deletion removes all data with verification query
- [ ] Data retention policy documented (how long after deletion)

## Post-flight

- [ ] Cross-tenant access test: query as tenant A, verify zero tenant B data
- [ ] Backup/restore test: single tenant backup, restore to clean database
- [ ] Encryption test: key rotation without service interruption
- [ ] Performance test: isolation pattern meets latency SLA under load
- [ ] Compliance review: isolation pattern approved by security team
