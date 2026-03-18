# Checklist: SaaS Governance, DevOps & Incident Design

## Governance

- [ ] Azure Policy definitions created for resource compliance
- [ ] Policy assignments scoped to appropriate management groups/subscriptions
- [ ] Naming convention enforcement policy active
- [ ] Required tags enforcement policy active
- [ ] Allowed regions policy configured for data residency
- [ ] Compliance dashboard configured in Azure portal

## Deployment Pipeline

- [ ] CI/CD pipeline supports tenant-aware deployment stages
- [ ] Ring-based or canary deployment configured with tenant groupings
- [ ] Rollback procedure documented and tested per tenant subset
- [ ] Feature flags integrated for per-tenant feature gating
- [ ] Deployment approval gates configured for production rings
- [ ] Deployment health checks include per-tenant validation

## Incident Management

- [ ] Severity levels defined (P1-P4) with response time SLAs
- [ ] Tenant blast radius assessment procedure documented
- [ ] Escalation matrix defined with on-call rotation
- [ ] Tenant communication templates prepared for each severity
- [ ] Post-incident review process includes tenant impact analysis
- [ ] Incident tracking integrates with tenant metadata

## Audit Logging

- [ ] Log schema includes tenant-id as required dimension
- [ ] Audit logs stored in immutable storage (append-only)
- [ ] Retention policy meets compliance requirements
- [ ] Tenant self-service access to their own audit data
- [ ] Log access is RBAC-controlled and audited itself
- [ ] Compliance reporting automated from audit logs

## Change Management

- [ ] Change approval process documented for multi-tenant changes
- [ ] Impact assessment template includes tenant enumeration
- [ ] Tenant notification process for planned changes defined
- [ ] Emergency change process defined with retrospective requirement
- [ ] Change calendar maintained and accessible to stakeholders
