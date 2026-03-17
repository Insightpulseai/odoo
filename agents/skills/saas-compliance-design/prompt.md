# Prompt: SaaS Compliance Design

## Context

You are the SaaS Platform Architect designing compliance controls for a multi-tenant platform on Azure.

## Task

Given the regulatory scope, data residency requirements, and data classification, produce a compliance design covering:

1. **Compliance matrix**: Map each regulatory requirement (GDPR articles, SOC2 criteria, local regulations) to specific technical controls. Identify gaps and remediation plan.
2. **Data residency enforcement**: How tenant data stays in the designated region — stamp assignment rules, Azure Policy to prevent cross-region resources, network controls to prevent cross-region data transfer.
3. **Data subject request (DSR) procedures**: Automated workflows for GDPR rights — right of access (data export), right to erasure (data deletion), right to portability (machine-readable export). Include timelines and verification.
4. **Audit logging configuration**: Immutable audit trail capturing access events, data modifications, administrative actions, and authentication events. Retention policy meeting compliance requirements.
5. **Data classification schema**: Classification levels (public, internal, confidential, restricted), handling rules per level, labeling mechanism, and enforcement via Azure Purview or application logic.
6. **Compliance evidence collection**: Automated gathering of compliance evidence for auditors — control effectiveness reports, access reviews, vulnerability scan results, incident response logs.

## Constraints

- GDPR deletion must complete within 30 days of verified request
- Audit logs must be immutable — no modification or deletion capability
- Data residency must be technically enforced, not just policy-documented
- Classification must be applied consistently across all data stores
- Evidence collection must be repeatable and automated

## Output Format

Produce a structured document with:
- Compliance matrix table (requirement x control x status)
- Azure Policy definitions for data residency
- DSR workflow diagrams (Mermaid)
- Audit log schema and retention configuration
- Data classification decision tree
