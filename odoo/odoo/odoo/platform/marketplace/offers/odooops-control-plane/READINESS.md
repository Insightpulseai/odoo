# OdooOps Control Plane — Marketplace Readiness

**Offer slug**: `odooops-control-plane`
**Target marketplace(s)**: Internal (IPAI), GitHub Marketplace (future)
**Current level**: **0 — Scaffolded**
**Last assessed**: 2026-03-08

## Description

OdooOps Control Plane provides centralized management for Odoo CE deployments, including module lifecycle, health monitoring, backup orchestration, and CI/CD integration.

## Readiness Summary

| Section | Status | Score |
|---------|--------|-------|
| A. Identity & Metadata | Partial | 2/8 |
| B. Technical Completeness | Not started | 0/8 |
| C. Security Baseline | Not started | 0/8 |
| D. Observability & Operations | Not started | 0/8 |
| E. Documentation | Not started | 0/7 |
| F. Testing & Quality | Not started | 0/7 |
| G. Compliance & Legal | Not started | 0/6 |
| H. Marketplace-Specific | Not started | 0/6 |
| I. Support & SLA | Not started | 0/6 |
| J. Launch Readiness | Not started | 0/7 |

**Overall**: 2/71 (3%)

## Primary Blockers

1. **Core functionality not implemented** — Control plane API and UI need to be built
2. **No health check endpoint** — Required for both B and D sections
3. **No test coverage** — Unit and integration tests needed
4. **No API documentation** — OpenAPI spec needed for API surface

## Next Steps

1. Define API surface in `spec/odooops-control-plane/prd.md`
2. Implement health check endpoint
3. Add CI pipeline for automated testing
4. Create OpenAPI specification

## Changelog

- 2026-03-08: Initial scaffold, Level 0
