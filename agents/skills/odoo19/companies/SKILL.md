---
name: companies
description: Configure companies, branches, multi-company environments, inter-company transactions, and document layouts.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# companies — Odoo 19.0 Skill Reference

## Overview

The Companies module manages business entities within an Odoo database. Each company has its own legal identity, financial records, and operational settings. The module supports multi-company configurations (sharing data between entities), hierarchical branches (subdivisions under a parent company), inter-company transactions, digest emails, and email templates. Administrators and finance teams use this to set up organizational structures, control record visibility, and automate cross-company document generation.

## Key Concepts

- **Company**: An independent business entity with its own name, address, Tax ID, LEI, currency, and logo.
- **Branch**: A subdivision of a parent company (regional office, department) that inherits some settings but can have its own address, logo, and configurations.
- **Multi-company**: Feature enabling multiple companies in one database with shared or company-specific data.
- **Company selector**: Top-right header control to switch between or select multiple active companies.
- **Shared records**: Products, contacts, etc. that are accessible across all companies (Company field left blank). Setting the Company field restricts a record to one entity.
- **Company-specific records**: Quotations, invoices, vendor bills — tied to the active company at creation.
- **Inter-company transactions**: Auto-generation of counterpart documents (bills, SOs, POs) when one company transacts with another in the same database.
- **Digest emails**: Periodic KPI summary emails sent to users.
- **Email templates**: Reusable email templates for automated communications.

## Core Workflows

### 1. Create a company

1. Settings > Companies section > Manage Companies > New.
2. Fill in: Company Name, Address, Tax ID, LEI, Company ID, Currency, Phone, Mobile, Email, Website, Email Domain, Color.
3. Upload logo and Save.

### 2. Create a branch

1. Settings > Companies > Manage Companies > open parent company.
2. In the Branches tab, click **Add a line**.
3. Fill in General Information in the Create Branches window.
4. For multi-level hierarchy, open the new branch and add sub-branches in its Branches tab.

### 3. Configure multi-company environment

1. Create additional companies.
2. On each user profile > Access Rights tab > set Allowed Companies and Default Company.
3. Use the company selector to switch contexts.

### 4. Enable inter-company transactions

1. Select the relevant company in the company selector.
2. Settings > Companies section > enable **Inter-Company Transactions** > Save.
3. Configure: Generate Bills and Refunds, Generate Sales Orders, Generate Purchase Orders.
4. Optionally select **Create and validate** for auto-validation.

### 5. Configure document layout

1. Open company form.
2. Set default layout for all company documents via Settings > Document Layout or Studio PDF report defaults.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `res.company` | Company records |
| `res.partner` | Company contact (linked) |
| `mail.template` | Email templates |
| `digest.digest` | Digest email configuration |

### Key Fields on `res.company`

| Field | Purpose |
|-------|---------|
| `name` | Company name |
| `partner_id` | Related partner record |
| `parent_id` | Parent company (for branches) |
| `child_ids` | Branch companies |
| `currency_id` | Main currency |
| `vat` | Tax ID |

### Menu Paths

- `Settings > Companies > Manage Companies`
- `Settings > Users & Companies > Companies`
- `Settings > Companies > Inter-Company Transactions`
- Developer mode: social media accounts and email system parameters on company form

### Inter-Company Options

| Option | Effect |
|--------|--------|
| Generate Bills and Refunds | Bill/refund created when invoice/credit note confirmed for the counterpart company |
| Generate Sales Orders | Quotation created when SO confirmed for the counterpart |
| Generate Purchase Orders | RFQ created when PO confirmed for the counterpart |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Parent cannot become branch**: A company defined as a parent cannot later be converted to a branch — this causes access rights issues. Always create the parent first.
- **Multi-company plan upsell**: Enabling multi-company on a Standard plan triggers automatic upsell to Custom plan. Yearly contracts get a 30-day upsell order; monthly contracts switch immediately.
- **Branch adds multi-company**: Adding a branch to any company automatically enables multi-company functions database-wide.
- **Accounting inheritance**: Branch accounting settings are inherited from the parent company. All other configurations must be set per-branch individually.
- **Inter-company product sharing**: Products involved in inter-company transactions must be shared (Company field left blank) across the involved companies.
