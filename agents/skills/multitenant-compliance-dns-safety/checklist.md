# Checklist: Multitenant Compliance & DNS Safety

## Compliance

- [ ] Per-tenant compliance requirements documented
- [ ] Compliance requirements mapped to infrastructure controls
- [ ] Gaps identified with remediation timeline
- [ ] Compliance audit schedule defined
- [ ] Compliance evidence collection automated where possible
- [ ] Tenant-facing compliance documentation available

## Domain Management

- [ ] Custom domain provisioning workflow automated
- [ ] Domain ownership verification required (CNAME or TXT)
- [ ] Domain activation only after verification succeeds
- [ ] Domain deprovisioning cleans up all associated records
- [ ] Domain transfer process documented
- [ ] Wildcard domain security reviewed

## DNS Safety

- [ ] Dangling CNAME detection scan scheduled (daily minimum)
- [ ] Resource deprovisioning order enforced (DNS last)
- [ ] Subdomain takeover monitoring active
- [ ] Automated remediation for detected dangling records
- [ ] DNS record inventory maintained and reconciled
- [ ] Incident response plan for subdomain takeover

## Data Residency

- [ ] Per-tenant data location requirements documented
- [ ] Azure Policy restricts resource creation to allowed regions
- [ ] Database placement verified per tenant
- [ ] Data replication does not cross residency boundaries
- [ ] Backup storage location matches residency requirements
- [ ] Residency compliance validated periodically

## Certificate Management

- [ ] Certificate issuance automated (managed certificates or ACME)
- [ ] Certificate renewal automated (30+ days before expiration)
- [ ] Certificate expiration alerting configured
- [ ] Certificate revocation process documented
- [ ] BYOC (bring your own certificate) process defined for enterprise tenants
- [ ] Certificate inventory maintained and monitored
