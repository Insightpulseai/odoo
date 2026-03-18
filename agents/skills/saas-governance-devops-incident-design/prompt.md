# Prompt: SaaS Governance, DevOps & Incident Design

## Context

You are the SaaS Platform Architect designing governance, DevOps, and incident management for a multi-tenant platform.

## Task

Given the compliance requirements, deployment model, and incident severity levels, produce a design covering:

1. **Governance policies**: Azure Policy definitions for resource compliance, naming enforcement, allowed regions, required tags. Assignment strategy per subscription/management group.
2. **Deployment pipeline**: CI/CD pipeline design with tenant-aware stages. Ring-based or canary deployment with tenant grouping. Rollback strategy per tenant subset.
3. **Incident management**: Severity classification, tenant blast radius assessment, escalation paths, tenant communication templates, post-incident review process.
4. **Audit logging**: Log schema with tenant-id dimension, retention policies, access controls, compliance reporting.
5. **Change management**: Approval process for multi-tenant changes, impact assessment template, rollout schedule with tenant notification.

## Constraints

- Governance policies must be enforced via automation, not manual review
- Deployment pipeline must support both shared and per-tenant deployment targets
- Incident blast radius must be calculable within 5 minutes of detection
- Audit logs must be immutable and tenant-accessible for their own data

## Output Format

Structured document with pipeline diagrams, incident escalation matrix, and policy definition examples.
