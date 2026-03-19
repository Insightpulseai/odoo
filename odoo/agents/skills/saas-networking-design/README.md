# Skill: SaaS Networking Design

## Overview

Design multi-tenant networking architecture with proper isolation, private connectivity, per-tenant routing, and WAF protection.

## Owner

- **Persona**: saas-platform-architect

## Classification

- **Type**: capability_uplift
- **Family**: azure-saas-mt

## Purpose

Network architecture defines the security boundary of the platform. Improper network design leads to data exposure, cross-tenant traffic leakage, and compliance failures. This skill ensures network isolation, private connectivity, and secure routing for multi-tenant SaaS.

## Canonical Fit

The canonical stack uses Azure Front Door for ingress, Azure Container Apps for compute, and Azure PostgreSQL Flexible Server for data. This skill designs the VNET topology connecting these, private endpoints for database access, and Front Door routing rules for per-tenant subdomains.

## Key Topics

- VNET topology: per-stamp VNETs with subnet segmentation
- Private endpoints: PostgreSQL, Storage, Redis accessible only via private network
- Front Door routing: per-tenant subdomains, custom domains, backend pool assignment
- DNS management: tenant subdomain automation, custom domain verification
- NSG policies: deny-all default, explicit allow rules per subnet
- WAF: multi-tenant traffic protection, per-tenant rate limiting

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Machine-readable skill definition |
| `prompt.md` | Agent prompt template |
| `checklist.md` | Design review checklist |
| `examples.md` | Reference examples |
| `EVALS.md` | Evaluation criteria |

## Cross-references

- `agents/skills/saas-resource-organization/`
- `agents/skills/saas-deployment-stamp-design/`
- `agents/skills/noisy-neighbor-mitigation/`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agent-platform/ssot/learning/azure_saas_multitenancy_skill_map.yaml`
