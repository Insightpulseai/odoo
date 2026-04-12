---
name: Pulser Stamp Deploy
description: Orchestrate Pulser for Odoo "Deployment Stamp" rollout — Canary, Early Adopter (EA), and General Availability (GA).
disable-model-invocation: true
---

# Pulser Stamp Deploy Skill

## When to use
When promoting a validated release from Canary through the promotion sequence to the GA fleet.

## Rollout Sequence

### 1. Canary Stamp (Internal-Dev)
- **Target**: `rg-ipai-dev-odoo-runtime` / `ipai-odoo-dev-web`.
- **Goal**: Initial landing and automated health/eval verification.

### 2. Early Adopter Stamp (Pilot)
- **Target**: Selected Beta tenants.
- **Goal**: Functional sign-off and first-close validation.

### 3. General Availability (GA Fleet)
- **Target**: `ipai-prod-rg` / Production fleet.
- **Goal**: Stable enterprise operations.

## Release Invariants

### 1. Traffic Splitting
- **RULE**: Use ACA Revision Labels and traffic splitting.
- **Sequence**: 5% -> 25% -> 100% with automated health-check validation at each step.

### 2. Migration Authority
- **RULE**: AR/AP/TB reconciliation signed off by the tenant Finance Director before GA activation.

### 3. Verification
- Use [fix_erp_assets.sh](file:///Users/tbwa/Documents/GitHub/Insightpulseai/scripts/restoration/fix_erp_assets.sh) post-deployment for UI stability.

## Validation Checks
1. Verify that all P1 user stories for the Scenario UA have 100% sign-off.
2. Ensure the **Stabilization Window** and **First-Close Review** are scheduled.
3. Check for successful Canary health signals before promotion.
