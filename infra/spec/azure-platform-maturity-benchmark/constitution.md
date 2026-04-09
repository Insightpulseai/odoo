# Azure Platform Maturity Benchmark — Constitution

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11
**Owner**: InsightPulse AI Platform Team

---

## Purpose

This spec defines the **scoring rubric and non-negotiable rules** for benchmarking Azure platform maturity across identity, networking, compute, monitoring, backup, and deployment domains. It is inspired by SAP-on-Azure landing zone patterns but adapted for Odoo 18 CE workloads on Azure Container Apps (ACA) + Cloudflare + GitHub Actions.

### What This Is

- A **platform maturity assessment framework** for Azure-hosted workloads
- A **scoring rubric** with weighted domains and clear pass/fail thresholds
- An **operational readiness gate** consumed by CI and pre-cutover checklists

### What This Is Not

- Not an ERP/Odoo-specific benchmark (that lives in `odoo/`)
- Not a vendor certification or compliance framework
- Not a cloning of SAP-on-Azure architecture (inspiration only)

---

## Non-Negotiables

### 1. Platform-First, Not ERP-First

This benchmark evaluates the Azure operating model. Odoo-specific runtime checks (health endpoints, module installation, database restore) belong in `odoo/` spec bundles, not here.

### 2. Scored Domains Are Fixed

The six benchmark domains cannot be removed or merged:

| # | Domain | Weight |
|---|--------|--------|
| 1 | Identity & Governance | 20% |
| 2 | Networking | 15% |
| 3 | Compute & Runtime | 20% |
| 4 | Monitoring & Observability | 15% |
| 5 | Backup & Disaster Recovery | 15% |
| 6 | Deployment & Promotion Discipline | 15% |

### 3. Pass Threshold

- **Minimum passing score**: 70% weighted aggregate
- **No domain may score below 50%** individually (a single domain failure blocks overall pass)
- **Production cutover gate**: 85% weighted aggregate

### 4. Evidence-Based Scoring Only

Every score must reference verifiable evidence:
- CLI output (`az` / `gh` / `terraform`)
- CI workflow run artifacts
- ARM/Bicep template analysis
- Runtime probe results

Claims without evidence score 0.

### 5. Azure-Native + Cloudflare + GitHub Actions Stack

This benchmark assumes:
- **Identity**: Entra ID (Azure AD) with managed identities
- **Networking**: Azure VNet + Cloudflare DNS/WAF/CDN
- **Compute**: Azure Container Apps (ACA) or Azure App Service
- **CI/CD**: GitHub Actions (not Azure DevOps)
- **Secrets**: Azure Key Vault (not Supabase Vault for Azure-scoped secrets)
- **Monitoring**: Azure Monitor + Application Insights

### 6. No Console-Only Evidence

Per SSOT Rule 10: all Azure configuration must have a corresponding IaC commit. Dashboard screenshots are supplementary, never primary evidence.

---

## Governance

- This spec is owned by `infra/` and consumed by `odoo/` for derived runtime checks.
- Changes require a PR with at least one domain-expert review.
- The scoring rubric is append-only (new criteria may be added; existing criteria may not be weakened).
