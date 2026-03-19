---
name: sign
description: Electronic signature app for preparing, sending, signing, and managing document signature requests
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# sign -- Odoo 19.0 Skill Reference

## Overview

Odoo Sign enables users to sign, send, and approve documents online using electronic signatures. It supports one-off documents, reusable templates, document envelopes (multiple documents in one request), auto-complete fields linked to Odoo models, signing order enforcement, and multiple authentication methods (SMS, Aadhaar eSign, itsme). Signatures generated are legally valid simple electronic signatures under eIDAS (EU) and ESIGN/UETA (USA).

## Key Concepts

- **Signature Request**: A request sent to one or more signers to complete and sign a document or envelope.
- **Template**: A reusable document (or envelope) prepared for signing with pre-configured fields, signers, tags, and settings.
- **Document Envelope**: Multiple PDF documents bundled into a single signature request.
- **Signers**: Parties required to sign. Each assigned a unique color. Support for signing order, delegation, and fixed assignment.
- **Field Types**: Signature, Initial, Text, Multiline Text, Checkbox, Radio, Selection, Strikethrough, Stamp.
- **Auto-complete Fields**: Fields linked to Odoo model data (e.g., Contact > Email) that auto-populate during signing.
- **Certificate of Completion**: Automatically generated proof document sent to all parties upon full signing.
- **Signing Order**: Sequential order in which signers receive the request.
- **Authentication Methods**: SMS verification, Aadhaar eSign (India), itsme (EU/UK/Norway/Iceland).
- **Tags**: Categorization labels for templates and documents.
- **Validity / Expiry**: Configurable `Valid Until` date on signature requests, with optional auto-reminders.
- **Redirect Link**: URL to redirect signers after completing signing.
- **Cryptographic Signature**: Optional digital signature using a `.p12`/`.pfx` certificate uploaded in settings.

## Core Workflows

1. **Send a One-Off Document for Signing (from Sign app)**
   1. Go to Sign > Documents > My Documents, click Upload PDF, select file(s).
   2. Add fields to the document by dragging from the left panel.
   3. Add/configure signers as needed.
   4. Click Send.
   5. Configure New Signature Request: select signers, set Valid Until, Reminders, CC, message.
   6. Click Sign Now (if self-signing) or Send.

2. **Create and Use a Template**
   1. Go to Sign > Templates, click Upload PDF.
   2. Add fields, configure signers and signer settings.
   3. Optionally configure via gear icon > Configuration (Tags, Model, Redirect Link, Validity, etc.).
   4. To send: from Templates view click Send on the template, fill signer contacts, click Send.
   5. To share link (single-signer only): click Share, copy link.

3. **Sign a Document Received via Odoo Sign**
   1. Open the document from email or Sign app.
   2. Click "Click to start" arrow or click fields directly.
   3. Complete all mandatory fields (colored background).
   4. Define initials/signature when prompted (Auto, Draw, or Load image).
   5. Click "Validate & Send Completed Document."

4. **Request Signature from an Odoo Record**
   1. On any record, click Actions (gear) > Request Signature.
   2. Upload PDF or select template.
   3. Add fields, click Send.
   4. Customer from the record is auto-added as signer.

5. **Create a Document Envelope**
   1. During Upload PDF, select multiple files.
   2. Or after opening a document, click Add in the Documents section.
   3. Reorder with Move Up/Down; remove with Delete.
   4. Each document can have its own fields.

## Technical Reference

- **Key Models**: `sign.request`, `sign.template`, `sign.request.item`, `sign.item.value`, `sign.type` (field types)
- **Settings**: Sign > Configuration > Settings
  - Default Terms & Conditions (email or web page)
  - Manage Template Access (restrict by user groups)
  - Authentication: Aadhaar eSign, itsme, SMS credits
  - Cryptographic signature: upload `.p12`/`.pfx` certificate
- **Fields Configuration**: Sign > Configuration > Fields. Each field has: Field Name, Type, Placeholder, Tip, Field Size (Text only), Linked to (model + field for auto-complete).
- **Tags**: Sign > Configuration > Tags. Fields: Tag Name, Color Index.
- **Template Configuration Fields**: Name, Tags, Model (restricts to specific record types), Redirect Link, Documents folder, Documents tags, Authorized Users, Authorized Groups, Valid for (days), Communication tab (default email text), Responsible user.
- **Document Status**: To Sign, Signed, Cancelled, Expired.
- **Sign Action in Documents App**: Enable per-folder via Actions > Actions on Select > Sign.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Document envelopes: send multiple documents in a single signature request.
- Strikethrough field type for rejecting specific phrases.
- Stamp field type for company stamps.
- Signing order configurable at request time (not just template time).
- Templates can be linked to Odoo models to restrict availability by record type.

## Common Pitfalls

- A template that has been used to send a signature request cannot be edited directly; editing creates a copy.
- Each template must have the Phone Field set to the Phone or Mobile model to avoid errors when changing the Applies to field.
- Forgetting to add Authorized Group to a canned response means only the creator can use it.
- Auto-complete fields default to editable; set Read-only on the field instance in the document to prevent signer changes.
- Validity dates: if not set, signature requests never expire; ensure Valid Until is configured for time-sensitive documents.
