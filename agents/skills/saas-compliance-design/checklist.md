# Checklist: SaaS Compliance Design

## Pre-flight

- [ ] Regulatory scope identified (GDPR, SOC2, PCI-DSS, local regulations)
- [ ] Data residency requirements documented per tenant/region
- [ ] Data categories inventoried (PII, financial, health, general)
- [ ] Audit retention requirements documented
- [ ] Compliance timeline and certification targets established

## Compliance Matrix

- [ ] Each regulatory requirement mapped to a technical control
- [ ] Control effectiveness assessed (effective, partial, gap)
- [ ] Gap remediation plan with timelines
- [ ] Control owner assigned for each requirement
- [ ] Matrix reviewed by legal/compliance team

## Data Residency

- [ ] Tenants assigned to stamps in their designated region
- [ ] Azure Policy prevents resource creation outside designated regions
- [ ] Cross-region data transfer blocked at network level
- [ ] Backups stored in the same region as primary data
- [ ] Residency compliance auditable via resource inventory

## Data Subject Requests (GDPR)

- [ ] Right of access: data export workflow automated
- [ ] Right to erasure: data deletion workflow with verification
- [ ] Right to portability: machine-readable export format (JSON/CSV)
- [ ] DSR intake process documented (identity verification, request logging)
- [ ] DSR completion within 30-day regulatory deadline
- [ ] DSR audit trail maintained

## Audit Logging

- [ ] Access events logged (who accessed what, when)
- [ ] Data modification events logged (create, update, delete with before/after)
- [ ] Administrative actions logged (configuration changes, user management)
- [ ] Authentication events logged (login, logout, MFA, failures)
- [ ] Logs stored in immutable storage (append-only, no delete)
- [ ] Retention period meets compliance requirements (minimum 1 year SOC2)

## Data Classification

- [ ] Classification levels defined (public, internal, confidential, restricted)
- [ ] Handling rules per level (encryption, access control, retention)
- [ ] Classification applied at data creation (not retroactive)
- [ ] Classification labels visible in data catalog
- [ ] Misclassification detection and remediation process

## Evidence Collection

- [ ] Automated control effectiveness reports
- [ ] Regular access reviews (quarterly minimum)
- [ ] Vulnerability scan results archived
- [ ] Incident response logs maintained
- [ ] Evidence package generation for auditor review

## Post-flight

- [ ] GDPR export tested — complete data package verified
- [ ] GDPR deletion tested — zero residual PII verified
- [ ] Data residency audit — all resources in correct region
- [ ] Audit log query — complete trail for sample operations
- [ ] Compliance report generated successfully
