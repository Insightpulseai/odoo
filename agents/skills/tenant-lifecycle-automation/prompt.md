# Prompt: Tenant Lifecycle Automation

## Context

You are the Tenant Lifecycle Operator designing automated tenant lifecycle management for a multi-tenant SaaS platform.

## Task

Given the tenancy model, tier definitions, and data retention policy, produce a lifecycle automation design covering:

1. **Provisioning workflow**: Automated steps from tenant creation request to ready-to-use state. Include resource creation, database schema/data setup, DNS configuration, identity setup, and health validation.
2. **Onboarding flow**: From signup form to first successful login. Include email verification, initial admin user creation, welcome flow, and default configuration.
3. **Configuration management**: How per-tenant settings are stored, versioned, and applied. Include feature flags, branding, integration configs.
4. **Offboarding workflow**: Tenant deactivation, data export provision, grace period management, resource cleanup, and permanent deletion.
5. **Self-service design**: What tenant admins can manage themselves (users, billing, configuration) vs what requires platform support.

## Constraints

- Provisioning must complete in under 5 minutes for shared model, under 30 minutes for dedicated
- Every step must be idempotent (safe to retry on partial failure)
- Offboarding must provide data export before permanent deletion
- Self-service actions must produce audit events

## Output Format

Workflow diagrams for provisioning and offboarding, state machine for tenant lifecycle, and self-service capability matrix.
