# App Icons – OCA & IPAI Modules

Goal: Replace generic Odoo/OCA placeholders with a consistent InsightPulseAI visual language.

---

## 1. Design Guidelines

- Format: **SVG**
- Style: Simple, flat, minimal outlines
- Stroke: 1.5–2 px equivalent
- Color:
  - Primary: `#ffb300` (Accent)
  - Dark: `#1a1a1a`
  - Neutral: `#f5f5f5` background
- Size: 256x256 viewBox, scalable

---

## 2. Target Modules

- `ipai_equipment` – Equipment icon (rack / devices)
- `ipai_expense` – Receipt + card icon
- `ipai_finance_ppm` – Gantt / milestones
- `ipai_finance_monthly_closing` – calendar + checkmark
- `ipai_docs` / `ipai_docs_project` – documents / binder
- `ipai_ocr_expense` – camera + receipt
- `ipai_ce_cleaner` – shield + broom
- `tbwa_spectra_integration` – bridge / arrows between ledgers
- OCA:
  - `mis_builder`
  - `account_financial_report`
  - `auditlog`
  - `purchase_request`

---

## 3. File Locations

- Icons folder (recommended):

`addons/<module_name>/static/description/icon.svg`

Example:

- `addons/ipai_equipment/static/description/icon.svg`
- `addons/ipai_expense/static/description/icon.svg`

Ensure `__manifest__.py` has:

```python
"images": ["static/description/icon.svg"],
```

---

## 4. AI Prompt Template (SVG Generator)

Use this prompt with your SVG generator:

> Design a 256x256 SVG app icon for Odoo, using a minimal flat style with a #ffb300 accent, #1a1a1a stroke, and light-neutral background.
> The icon should represent: **{MODULE_DESCRIPTION}**.
> Keep shapes simple, no gradients, and ensure it looks crisp at 64x64.

Replace `{MODULE_DESCRIPTION}`, e.g.:

* `"Cheqroom-style equipment management (cameras, lights, gear rack)"`
* `"SAP Concur-style travel and expense management (receipt and card)"`

---

## 5. Batch Update Script (optional)

Once icons are generated, run:

```bash
git add addons/*/static/description/icon.svg
git commit -m "style: add custom SVG icons for IPAI and OCA modules"
