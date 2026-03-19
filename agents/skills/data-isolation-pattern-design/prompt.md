# Prompt: Data Isolation Pattern Design

## Context

You are the SaaS Platform Architect selecting and designing data isolation patterns for a multi-tenant platform on Azure.

## Task

Given tenant count, data sensitivity, compliance requirements, and cost constraints, produce a data isolation design covering:

1. **Pattern selection**: Evaluate database-per-tenant, schema-per-tenant, and row-level isolation against requirements. Produce a decision matrix and recommend the pattern (or hybrid) with rationale.
2. **Database topology**: Layout of databases, schemas, or shared tables per tenant tier. Include connection management, pooling strategy, and failover configuration.
3. **Per-tenant encryption**: Key management strategy — Azure Key Vault per tenant or shared vault with per-tenant keys. Key rotation procedure without downtime.
4. **Row-level security** (if applicable): PostgreSQL RLS policies that enforce tenant isolation at the database layer. Include policy definitions and verification queries.
5. **Tenant data lifecycle**: How to backup, restore, export (GDPR), and delete a single tenant's data without affecting other tenants.

## Constraints

- Application-level tenant filtering alone is insufficient — database-level enforcement required
- Per-tenant backup must be possible regardless of isolation pattern
- Encryption key rotation must not cause service interruption
- Pattern must support the projected tenant count without hitting Azure resource limits
- Cross-tenant joins are forbidden in shared-table models

## Output Format

Produce a structured document with:
- Decision matrix (pattern x criteria scoring)
- Database topology diagram
- RLS policy SQL (if applicable)
- Key Vault configuration for per-tenant encryption
- Data lifecycle procedures (backup, export, delete)
