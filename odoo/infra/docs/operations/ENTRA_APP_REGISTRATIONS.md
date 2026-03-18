# Entra App Registrations Inventory

> Version: 1.0.0
> Last updated: 2026-03-14
> Canonical repo: `infra`
> Parent: `docs/architecture/IDENTITY_TARGET_STATE.md`

## Purpose

Track all Azure Entra app registrations and their purpose, redirect URIs, and secrets.

## Current Inventory

The Entra tenant has 3 app registrations. Details pending inventory.

| # | App Name | Client ID | Purpose | Redirect URIs | Secret Expiry |
|---|----------|-----------|---------|---------------|---------------|
| 1 | TBD | TBD | TBD | TBD | TBD |
| 2 | TBD | TBD | TBD | TBD | TBD |
| 3 | TBD | TBD | TBD | TBD | TBD |

## Service Principals

| Name | Type | Role | Scope | Confirmed |
|------|------|------|-------|-----------|
| `sp-ipai-azdevops` | Service principal | Contributor | Subscription (inherited) | Yes (2026-03-14) |

## Required Actions

- [ ] Complete app registration inventory from Entra portal
- [ ] Document redirect URIs for each app
- [ ] Document secret expiry dates
- [ ] Establish secret rotation schedule
- [ ] Remove unused app registrations

## Rotation Policy

- App secrets: rotate every 90 days
- Service principal credentials: rotate every 180 days
- Managed identity: no rotation needed (Azure-managed)

## Audit

| Date | Action | By |
|------|--------|----|
| 2026-03-14 | Initial inventory created (pending completion) | System |
