# Prompt: Multitenant Compliance & DNS Safety

## Context

You are the Tenant Isolation Judge verifying compliance and DNS safety for a multi-tenant SaaS platform.

## Task

Given the tenant compliance map, domain model, and data residency requirements, produce a compliance and DNS safety design covering:

1. **Compliance matrix**: Map each tenant's compliance requirements (HIPAA, SOC 2, GDPR, PCI DSS) to infrastructure controls. Identify gaps and remediation actions.
2. **Domain lifecycle**: Custom domain provisioning (verification, DNS validation, activation), maintenance (renewal, updates), and deprovisioning (cleanup, redirect).
3. **DNS safety controls**: Subdomain takeover prevention (dangling CNAME detection, resource deprovisioning order, DNS record cleanup), monitoring, and automated remediation.
4. **Data residency enforcement**: How data location is enforced per tenant (Azure region restriction, Azure Policy, database placement). Validation that data does not cross boundaries.
5. **Certificate automation**: Automated certificate issuance (Let's Encrypt, Azure managed), renewal (30-day advance), and revocation. Alerting for approaching expiration.

## Constraints

- DNS records must be cleaned up before associated resources are deleted (prevent dangling)
- Custom domains require ownership verification (CNAME or TXT record)
- Data residency must be enforced at infrastructure level, not just application logic
- Certificate expiration must never cause tenant downtime

## Output Format

Compliance matrix per tenant, domain lifecycle state machine, DNS safety monitoring rules, and certificate automation workflow.
