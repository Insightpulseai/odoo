# Platform Benchmark: Wholesale SaaS ERP on Azure

> Version: 1.0.0
> Canonical repo: `agents`
> Related Research: `docs/research/wholesale-saas-erp-azure-architecture-study.md`

## Purpose
This document catalogs the exact benchmark references and framework samples used to derive the target architecture for the Wholesale SaaS ERP platform.

## Curated Benchmark Set

| Source | Weight | Use for | Do not use for |
|--------|-------:|---------|----------------|
| **Anthropic Context Engineering Docs** | 1.0 | Claude prompt design, safety boundaries, tool use patterns | Core transactional DB schema design |
| **Azure Architecture Center: SaaS Tenancy Models** | 1.0 | Tenant isolation strategy, database scaling, compute placement | Agent telemetry storage |
| **Azure Architecture Center: Microservices on ACA** | 1.0 | Odoo container deployment, ingress routing, scale rules | Databricks Lakehouse node sizing |
| **Microsoft Foundry Hosted Agents Docs** | 1.0 | Agent runtime placement, AI platform boundary, tracing/evals | Odoo ERP module development |
| **Databricks Medallion Architecture Docs** | 1.0 | Data intelligence layer, Bronze/Silver/Gold data pipelines, Unity Catalog | Real-time transactional write latency |
| **Azure DevOps Official Guidance** | 0.9 | Enterprise release pipelines, boards, environment approvals | Local developer loop |
| **VS Code DevContainers Specification** | 1.0 | Developer workspace setup, agentic execution environment | Production app hosting |

---
*If an architectural pattern for the ERP platform is not covered here, escalate to the `chief-architect` agent lens for derivation based on Azure Well-Architected standard practices.*
