---
title: Authority model
description: Which system owns which data, and the hard rules that protect data integrity.
---

# Authority model

Every datum in the platform has exactly one authoritative system. This page defines those assignments and the invariants that protect them.

## Canonical statement

> **Odoo is the system of record (SoR) for transactional and regulated business data. Supabase is the single source of truth (SSOT) for the platform control plane, integrations, evidence/audit, analytics serving layer, and AI indexes. ADLS is the analytical lake -- consumer-only, never a source of authority.**

## System authority table

| # | System | Role | Owns | Does not own |
|---|--------|------|------|--------------|
| 1 | **Entra ID** | Identity provider | SSO federation, conditional access policies | ERP user records, application permissions |
| 2 | **SAP Concur** | Expense SaaS | Expense reports, receipts, travel bookings | Accounting entries (these post in Odoo) |
| 3 | **SAP Joule** | AI agent | Conversational context for SAP queries | Business data, decisions |
| 4 | **Slack** | Communication | Messages, channels, presence | Task state, audit records |
| 5 | **Odoo CE 19** | System of record | Accounting entries, invoices, payments, HR records, inventory, CRM, purchases, sales | Auth identity, platform events, AI indexes |
| 6 | **n8n** | Automation | Workflow definitions, execution logs | Business data (passes through, does not own) |
| 7 | **Relay** | Webhook gateway | Inbound event buffering | Business data, state |
| 8 | **Supabase** | SSOT / control plane | Auth, platform events, AI/RAG indexes, analytics serving layer, integration state | Transactional ERP data |
| 9 | **ADLS Gen2** | Analytical lake | Bronze/silver/gold data copies | Nothing -- consumer-only |
| 10 | **Azure AI Foundry** | AI compute | Model weights, inference results | Business data, decisions |
| 11 | **Tableau** | BI / reporting | Dashboard definitions, calculated fields | Source data (reads from ADLS gold layer) |
| 12 | **Azure Front Door** | Edge / WAF | TLS certificates, WAF rules, routing config | Application data |

## Hard rules

These invariants must never be violated:

!!! danger "Non-negotiable constraints"

    1. **ADLS is consumer-only.** The analytical lake never writes back to Odoo or Supabase. Data flows one direction: source systems into ADLS.

    2. **Supabase SSOT tables are not overwritable by reverse ETL.** Tables in the `ops.*` schema are append-only. No external process may update or delete rows.

    3. **Posted accounting entries are immutable.** Once an `account.move` is posted in Odoo, it cannot be modified by any external system. Corrections use reversal entries.

    4. **Draft-first for external writes.** Any system that creates records in Odoo (SAP Concur expenses, n8n-triggered tasks) must create them in `draft` state. Only Odoo users or approved automation rules may post/confirm.

    5. **Every cross-system flow needs an SSOT YAML entry.** Before implementing a new data flow between systems, add it to `infra/ssot/azure/service-matrix.yaml`.

## Mirroring policy

### Odoo to Supabase (one-way)

Odoo data is mirrored into Supabase for read-optimized access by analytics, AI, and product surfaces.

| Constraint | Detail |
|------------|--------|
| Append-only events | Mirrors use CDC (change data capture) or event-based sync |
| Read-only by policy | Supabase tables mirroring Odoo enforce RLS read-only |
| No dual-write | No Supabase edit may override Odoo transactional truth |
| Deterministic keys | All mirrored entities use stable identifiers (external_id, UUID, natural keys) |

### Odoo to ADLS (one-way)

Odoo data flows through Supabase into ADLS bronze, then transforms through silver and gold layers. ADLS never writes back.

### Examples

| Entity | Authoritative system | Replica / consumer | Flow |
|--------|---------------------|--------------------|------|
| Invoice record | Odoo (SoR) | Supabase read replica | Odoo to Supabase (one-way) |
| Platform event metadata | Supabase (SSOT) | ADLS bronze | Supabase to ADLS (one-way) |
| Employee master | Odoo (SoR) | Supabase analytics view | Odoo to Supabase (materialized) |
| RAG embeddings | Supabase (SSOT) | None | Supabase only |
| Payment transaction | Odoo (SoR) | Tableau dashboard | Odoo to Supabase to ADLS gold to Tableau |
| Expense report | SAP Concur (SaaS) | Odoo (draft entry) | Concur to n8n to Odoo (draft-first) |
