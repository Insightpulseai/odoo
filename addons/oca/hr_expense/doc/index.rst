========================
Expense Management (OCA)
========================

Enterprise-parity expense management module.

Overview
========

This module provides comprehensive expense management capabilities as part
of the CE + OCA + ipai_* = Enterprise Parity strategy.

Features
========

* Employee expense submission workflow
* Multi-level approval process
* OCR pipeline integration support
* Receipt attachment and validation
* Expense categories and policies
* Journal entry generation
* Analytics integration
* Mobile-friendly interface

EE Parity
=========

This module replaces Odoo Enterprise ``hr_expense`` features with the
following coverage:

+---------------------------+--------+
| Feature                   | Status |
+===========================+========+
| Basic expense recording   | ✓      |
+---------------------------+--------+
| Expense reports           | ✓      |
+---------------------------+--------+
| Multi-level approval      | ✓      |
+---------------------------+--------+
| Journal entry creation    | ✓      |
+---------------------------+--------+
| Analytic distribution     | ✓      |
+---------------------------+--------+
| OCR extraction            | ✓ *    |
+---------------------------+--------+

* OCR requires ``ipai_expense_ocr`` connector module.

BIR Compliance
==============

For Philippines-based companies, the module supports:

* OR/SI number tracking
* Vendor TIN capture
* VAT input tracking on expenses

Configuration
=============

1. Navigate to Expenses > Configuration > Expense Categories
2. Define expense products with proper accounts
3. Configure employee expense access groups
4. Set up approval workflows as needed

Usage
=====

Creating Expenses
-----------------

1. Go to Expenses > My Expenses > Expenses to Submit
2. Click "Create"
3. Fill in expense details
4. Attach receipt
5. Click "Submit to Manager"

Approving Expenses
------------------

1. Go to Expenses > Expense Reports > Reports to Approve
2. Review expense details
3. Click "Approve" or "Refuse"

Posting Journal Entries
-----------------------

1. Go to approved expense report
2. Click "Post Journal Entries"
3. Verify accounting entries

Integration
===========

n8n Workflows
-------------

Use n8n to automate:

* Expense approval notifications
* OCR processing triggers
* Report generation

Supabase
--------

Store receipt images in Supabase Storage for scalable document management.
