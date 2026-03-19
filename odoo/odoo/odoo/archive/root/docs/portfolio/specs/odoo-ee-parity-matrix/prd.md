# PRD — Odoo EE → CE/OCA Parity Matrix

## 1) Summary

A structured catalog that maps **Odoo Enterprise-only features** into **tiered capability plans** implemented with **Odoo CE + OCA** (and minimal `ipai_*` where unavoidable), modeled after Fivetran's plan matrix (core, governance, security, extensibility).

## 2) Goals

- Provide a **plan-based parity matrix**: Free / Standard / Enterprise / Business-Critical.
- Make every item **reproducible** with CLI install + verification + rollback.
- Enforce **catalog validity and quality** with CI gates.

## 3) Non-goals

- Not a full ERP implementation guide.
- Not a paid marketplace listing.
- Not copying EE source behavior; only capability parity via OSS.

## 4) Plans (concept)

| Plan | Description |
|------|-------------|
| **Free** | Core ops for small teams; essential modules and minimal governance |
| **Standard** | Automation-first operations; fuller functional coverage; stable defaults |
| **Enterprise** | Granular governance/RBAC, auditability, advanced workflows, integrations |
| **Business-Critical** | Highest security/compliance posture, DR readiness, strict controls |

## 5) Acceptance criteria

- Catalog schema validated in CI
- At least 25 high-impact EE capabilities mapped with tier membership
- Each mapping includes verification + rollback
- Maturity/risk labels present for all items

## 6) Plan Capability Groups

### Free Tier
- core-finance
- core-sales-crm
- core-project
- core-reporting

### Standard Tier
- documents-dms
- helpdesk-support
- maintenance-field
- etl-automation
- core-finance
- core-reporting

### Enterprise Tier
- governance-access
- auditability
- advanced-approvals
- documents-dms
- etl-automation

### Business-Critical Tier
- security-hardening
- compliance-controls
- dr-readiness
- governance-access
- auditability
