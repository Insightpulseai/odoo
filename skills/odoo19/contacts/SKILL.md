---
name: contacts
description: Create and manage contact records (persons, companies), addresses, merge duplicates, and link business data.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# contacts — Odoo 19.0 Skill Reference

## Overview

The Contacts application is the central repository for customer, vendor, and partner information in Odoo. Contact records store names, addresses, emails, phones, tax IDs, payment terms, and more. Contacts can be Persons (individuals) or Companies, with Persons optionally linked to a parent Company. The module supports multiple address types (invoice, delivery, other), smart buttons linking to CRM opportunities, sales orders, invoices, and other app records, as well as merging duplicate contacts. All Odoo users interact with contacts across Sales, Purchase, Accounting, Helpdesk, and other workflows.

## Key Concepts

- **Contact type**: **Person** (individual) or **Company** (business entity). A Person can be linked to a Company via the Company field.
- **Contact form**: Central record with fields for name, email, phone, address, job position, Tax ID, website, language, tags.
- **Contacts tab**: Sub-contacts and additional addresses (Contact, Invoice, Delivery, Other) associated with a Company.
- **Sales & Purchase tab**: Salesperson, payment terms, pricelist, delivery method, fiscal position, buyer, supplier currency (visible when Sales/Purchase/POS installed).
- **Accounting tab**: Bank accounts, default accounting entries, invoice follow-ups (visible when Accounting installed).
- **Partner Assignment tab**: Geolocation, partner activation/review (visible when Resellers module installed).
- **UBO tab**: Ultimate Beneficial Owner holdings info (visible when Equity app installed).
- **Smart buttons**: Quick-access links at the top of the form to Opportunities, Meetings, Sales, POS Orders, Tasks, Purchases, Helpdesk tickets, Invoices, etc.
- **Merge contacts**: Combines duplicate contact records without losing data; destination contact is selectable.
- **Deduplicate**: Automated/manual search for duplicates by Email, Name, Is Company, VAT, Parent Company.

## Core Workflows

### 1. Create a new contact

1. Open the Contacts app > click **New**.
2. Select **Person** or **Company**.
3. Enter name (mandatory), email, phone, address.
4. Add optional fields: Job Position, Tax ID, Partner Level, Website, Language, Tags.
5. Save.

### 2. Add sub-contacts / addresses

1. Open a contact form > **Contacts** tab.
2. Click **Add Contact**.
3. In the Create Contact popup, select type: Contact, Invoice, Delivery, or Other.
4. Fill in name, address, email, phone, job position, notes.
5. Click **Save & Close** (or **Save & New** for more).

### 3. Merge duplicate contacts

1. Open Contacts app > switch to list view.
2. Select two or more duplicate contacts via checkboxes.
3. Click **Actions** > **Merge**.
4. In the Merge popup, review contacts and remove any that should not be merged.
5. Select the **Destination Contact** (defaults to oldest record).
6. Click **Merge Contacts**.

### 4. Deduplicate contacts

1. After a merge, click **Deduplicate the other Contacts** in the confirmation popup.
2. Select search criteria: Email, Name, Is Company, VAT, Parent Company.
3. Optionally exclude contacts with: a user, journal items.
4. Click **Merge with Manual Check**, **Merge Automatically**, or **Merge Automatically all process**.

### 5. Archive a contact

1. Open contact form > **Action** menu > **Archive** > confirm.
2. To restore: **Action** menu > **Unarchive**.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `res.partner` | Contact records (both persons and companies) |
| `res.partner.category` | Contact tags |
| `res.partner.bank` | Bank account records linked to contacts |

### Key Fields on `res.partner`

| Field | Purpose |
|-------|---------|
| `name` | Contact name (mandatory) |
| `is_company` | Boolean: True for companies |
| `parent_id` | Parent company (for person contacts) |
| `child_ids` | Sub-contacts / addresses |
| `type` | Address type: contact, invoice, delivery, other |
| `email` | Email address |
| `phone` / `mobile` | Phone numbers |
| `vat` | Tax ID |
| `property_payment_term_id` | Customer payment terms |
| `property_supplier_payment_term_id` | Vendor payment terms |
| `user_id` | Assigned salesperson |
| `category_id` | Many2many tags |
| `company_id` | Restrict to specific company (blank = shared) |
| `lang` | Language for communications |
| `active` | Archive flag |

### Menu Paths

- `Contacts` app (main list/Kanban)
- Contact form > Contacts tab, Sales & Purchase tab, Accounting tab, Internal Notes tab

### Smart Buttons (examples)

Opportunities, Meetings, Sales, POS Orders, Subscriptions, Tasks, Purchases, Helpdesk, On-time Rate, Invoiced, Vendor Bills, Partner Ledger, Deliveries, Documents, Loyalty Cards, Direct Debits, Go to Website.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Merge is irreversible**: There is no undo for contact merging. Verify contacts before confirming.
- **Deduplication with multiple criteria**: When multiple fields are selected, only records matching **all** fields are flagged as duplicates, potentially missing partial matches.
- **Shared vs. company-specific**: By default, contacts are shared across companies. Set the Company field to restrict visibility.
- **Smart button visibility**: Smart buttons only appear when the corresponding app is installed (e.g., CRM for Opportunities).
- **Person without company**: A Person contact not linked to a Company operates as a standalone individual; linking later requires manual assignment.
