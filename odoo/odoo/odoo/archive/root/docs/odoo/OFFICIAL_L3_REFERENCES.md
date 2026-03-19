# Official Odoo L3 References (Platform/Service Capabilities)

> **L3** = capabilities that are NOT Odoo modules but are part of the Enterprise
> value proposition (hosting, IAP services, managed infrastructure).

These are the canonical Odoo sources for platform/service capabilities outside
the module system:

## 1. Compare Editions (capability-level EE vs CE)

- **URL**: https://www.odoo.com/page/editions
- **Used for**: Classifying items like Hosting, OCR/digitization, and online
  bank sync as non-module capabilities.
- **Key indicators**: Any feature on this page that requires Odoo.sh, IAP
  credits, or a managed service is a **platform/service capability**, not an
  EE module.

## 2. Odoo 19 Release Notes (version-specific changes)

- **URL**: https://www.odoo.com/odoo-19-release-notes
- **Used for**: Detecting Odoo 19-specific UX/engine changes that are behavioral
  (not new modules) and should not be treated as EE-module gaps.

## Interpretation Rules

- **Hosting** and service-backed features (OCR/digitization, online bank sync,
  SMS credits) are treated as **integration bridges** (`bridges/`), not parity
  addons (`addons/oca/`).
- Module parity remains strictly: EE modules → OCA addons.
- These pages are **annotation sources** — they help classify gaps, but the
  authoritative EE module list comes from code inventories
  (`scripts/ee_oca_parity_proof.py`), not marketing pages.

## Examples

| Editions Page Item | Type | Our Replacement |
|--------------------|------|-----------------|
| Hosting (Odoo.sh) | Platform | `bridges/deploy/` (self-hosted DO/Docker) |
| Vendor Bill OCR | IAP Service | `bridges/ocr/` + PaddleOCR/Google Vision |
| Expense Digitalization | IAP Service | `bridges/ocr/` + `ipai_expense_ocr` |
| Online Bank Synchronization | IAP Service | OCA `bank-statement-import` (file-based) |
| SMS Marketing Credits | IAP Service | `bridges/sms/` + Twilio API |
| Push Notifications | IAP Service | Firebase Cloud Messaging / OneSignal |

---

*Referenced by: `spec/ee-oca-parity/prd.md`, `spec/ee-oca-parity/constitution.md`*
