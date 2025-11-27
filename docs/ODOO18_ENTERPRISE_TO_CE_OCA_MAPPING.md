# Odoo 18 Enterprise → CE + OCA Mapping (Smart Delta)

**System:** InsightPulse ERP (`erp.insightpulseai.net`)  
**Target Stack:** Odoo 18 CE + OCA 18.0 + ipai_* delta modules  
**Policy:** No Enterprise, no IAP. Always prefer **Config → OCA → Delta → New**.

This document is the canonical map of:

- What Odoo 18 offers in **Community Edition (CE)**  
- Which **OCA 18.0** modules cover Enterprise features  
- Where we accept **custom ipai_*** delta modules  
- Which Enterprise features we **explicitly do not rebuild**

---

## 1. Smart Delta Rules (Mandatory)

Every feature request must pass these gates, in order:

```text
Feature Request
    │
    ▼
1. CE_CONFIG      – Can CE settings/config solve it?
    │ NO
    ▼
2. OCA_EQUIVALENT – Is there an OCA 18.0 module?
    │ NO
    ▼
3. GAP_DELTA      – Small `_inherit` delta on existing models?
    │ NO
    ▼
4. GAP_NEW_MODULE – New module (last resort, must be justified)
```

**Definitions:**

* `CE_NATIVE`        – Already in CE core
* `CE_CONFIG`        – Achievable via configuration only (no code)
* `OCA_EQUIVALENT`   – Covered by OCA 18.0 modules
* `GAP_DELTA`        – Small `_inherit` delta module (`ipai_*`)
* `GAP_NEW_MODULE`   – New domain; avoid unless explicitly whitelisted here

No PR, AI plan, or human spec should propose a new module without referencing this document.

---

## 2. CE Native – Available Out-of-the-Box

These are **shipped in Odoo 18 CE** and should be used before anything else.

### 2.1 Core Business Apps

* Sales
* CRM
* Invoicing
* Accounting (basic)
* Purchase
* Inventory
* Manufacturing
* Point of Sale
* Project
* Timesheets (basic)
* Expenses (basic)
* Website (basic)
* eCommerce (basic)
* Contacts
* Calendar
* Discuss

**Tag:** `CE_NATIVE`

---

### 2.2 HR & Operations

* Employees
* Recruitment
* Time Off (basic)
* Fleet
* Maintenance
* Repairs
* Attendances
* Lunch

**Tag:** `CE_NATIVE`

---

### 2.3 Utilities

* Surveys
* Events
* To-Do

**Tag:** `CE_NATIVE`

---

## 3. OCA Alternatives – Community Coverage

These are **Enterprise-style features** that can be covered by **OCA 18.0** modules and must be solved this way before writing custom code.

> Note: repo names and module names are indicative; use 18.0 branches.

### 3.1 Marketing & Sales

* **Email Marketing / Automation**

  * CE: `mass_mailing`
  * OCA: `OCA/marketing-automation` (`marketing_automation`, `mass_mailing_*`)
  * Tag: `OCA_EQUIVALENT`

* **Social Marketing**

  * CE: basic website + share buttons
  * OCA: `OCA/website` (`website_social`, related modules)
  * Tag: `OCA_EQUIVALENT` (lightweight)

* **SMS Marketing**

  * CE: `sms` / `sms_*` basics
  * OCA: `OCA/sms` (`sms_*`)
  * Tag: `OCA_EQUIVALENT`

---

### 3.2 Service & Support

* **Helpdesk**

  * CE: basic ticketing via `project`
  * OCA: `OCA/helpdesk` (`helpdesk`, `helpdesk_mgmt`)
  * Tag: `OCA_EQUIVALENT`

* **Field Service**

  * CE: `project` + timesheets
  * OCA: `OCA/field-service` (`fieldservice`, `fieldservice_project`, etc.)
  * Tag: `OCA_EQUIVALENT`

* **Appointments / Scheduling**

  * CE: `calendar`
  * OCA:

    * `OCA/website` (`website_calendar`)
    * `OCA/calendar` (`calendar_appointment`)
  * Tag: `OCA_EQUIVALENT`

---

### 3.3 Advanced Operations

* **Quality Management**

  * CE: manufacturing basics
  * OCA: `OCA/quality` (`quality_control`, `quality_*`)
  * Tag: `OCA_EQUIVALENT`

* **Planning / Resource Scheduling**

  * CE: `project`, `resource`
  * OCA:

    * `OCA/project` (`project_resource_calendar`)
    * `OCA/hr` (`hr_holidays_planning`)
  * Tag: `OCA_EQUIVALENT`

* **MRP II / Work Orders**

  * CE: `mrp` basics
  * OCA: `OCA/manufacture` (`mrp_*`)
  * Tag: `OCA_EQUIVALENT`

* **PLM (Product Lifecycle Management)**

  * CE: documents + mrp
  * OCA: `OCA/plm` (`plm`, `plm_*`)
  * Tag: `OCA_EQUIVALENT`

---

### 3.4 HR

* **Appraisal / Performance Reviews**

  * OCA: `OCA/hr` (`hr_appraisal`, `hr_evaluation`)
  * Tag: `OCA_EQUIVALENT`

* **Skills Management**

  * OCA: `OCA/hr` (`hr_skills`, `hr_employee_skill`)
  * Tag: `OCA_EQUIVALENT`

---

## 4. Enterprise-Only Features – Strategy & Stance

These are **highly Enterprise-centric** or low-value for our use case.
We **do not rebuild** them unless explicitly allowed below.

### 4.1 Critical "Gap" Features

* **Studio (Visual App Builder)**

  * Enterprise: `web_studio`
  * Strategy: **Do NOT clone fully.**
  * Use:

    * `ipai_dev_studio_base` (limited helper tools)
    * Proper module development (Python/XML/JS)
  * Tag: `GAP_DELTA` (limited subset only), no full `GAP_NEW_MODULE`.

* **Sign (Digital Signatures)**

  * Enterprise: `sign`
  * Strategy:

    * Use external e-signature (e.g. DocuSign, local PH e-sign tools)
    * Optionally basic OCA EDI if strictly needed
  * Tag: `GAP_NEW_MODULE` **but discouraged** – prefer external tools.

* **Knowledge (Internal KB)**

  * Enterprise: `knowledge`
  * Strategy:

    * Use **Notion** + API integration (already in your stack)
    * Odoo -> Notion sync for documentation
  * Tag: `EXTERNAL_TOOL` (Notion-first).

---

### 4.2 Service Tools

* **Live Chat**

  * Enterprise has more polished integration.
  * Strategy:

    * CE Discuss for internal
    * Mattermost / external chat for support
    * OCA connectors for telephony/VoIP as needed
  * Tag: `OCA_EQUIVALENT` or `EXTERNAL_TOOL`

* **VoIP**

  * Strategy:

    * Use `OCA/connector-telephony` (Asterisk, etc.)
    * Treat tight Enterprise VoIP as non-goal
  * Tag: `OCA_EQUIVALENT`

* **Data Recycle / Cleanup**

  * Strategy:

    * Admin scripts + scheduled actions
    * No attempt to 1:1 match Enterprise "Recycle" app
  * Tag: `CE_CONFIG` / admin tooling.

---

### 4.3 Enhanced / Nice-To-Have Features

* **Subscriptions (MRR / Churn dashboards)**

  * Enterprise: subscription analytics
  * Strategy:

    * Use CE recurring + **OCA/contract** (`contract`, `contract_sale`)
    * MRR / churn graphs in Superset/BI instead of Odoo Studio dashboards
  * Tag: `OCA_EQUIVALENT` (+ external BI)

* **Barcode (advanced mobile UX)**

  * Strategy:

    * CE + `OCA/stock-logistics-barcode`
    * PWA/mobile web app frontend (React) if needed
  * Tag: `OCA_EQUIVALENT`

* **Android / iPhone Apps**

  * Strategy:

    * Use stock Odoo mobile apps with CE
    * Optional custom mobile UIs for key flows (not part of ERP core)
  * Tag: `EXTERNAL_CLIENT`

* **Marketing Card / Social Sharing**

  * Strategy:

    * Out of scope for core ERP
    * Use external tools (Buffer, Hootsuite, platform-native UIs)
  * Tag: `GAP_NEW_MODULE` (but **"do not build"**)

* **Online Jobs Portal Enhancements**

  * Strategy:

    * CE `website_hr_recruitment` is enough
    * Any fancy job portal UX handled in custom website / Notion forms, not new backend logic
  * Tag: `CE_NATIVE` + custom frontend.

---

## 5. Custom InsightPulse Modules (ipai_*)

These are the only approved custom module families for the **target image**.

* `ipai_workspace_core`

  * Notion-style workspaces (clients, brands, portfolios)
  * Base model: `ipai.workspace`

* `ipai_industry_accounting_firm`

  * Workspace deltas for accounting firms
  * Binds workspaces to accounting engagements, closing cycles, BIR calendar

* `ipai_industry_marketing_agency`

  * Workspace deltas for marketing/creative agencies
  * Binds workspaces to brands, campaigns, budgets

* `ipai_industry_ppm`

  * Clarity PPM / MS Project WBS-style deltas
  * PPM metadata on workspaces + WBS on `project.task`

* `ipai_ce_branding`

  * CE/OCA branding + hide Enterprise upsells

* `ipai_dev_studio_base`

  * Limited "mini-Studio" helpers (field scaffolding, safe inheritance patterns)

> Any new ipai_* module must be justified as `GAP_DELTA` in this document or added here explicitly.

---

## 6. Coverage Summary

| Category        | Approx. Count | Notes                                             |
| --------------- | ------------: | ------------------------------------------------- |
| CE Native       |      ~25 apps | Core ERP + HR + Utilities                         |
| OCA Available   | ~15 app areas | Helpdesk, FSM, MRP II, PLM, QMS, HR extensions    |
| Enterprise-Only |  ~12 features | Studio, Sign, Knowledge biggest "visible" gaps    |
| Custom ipai_*   |   5–6 modules | Workspaces, industries, PPM, branding, dev studio |

Estimated **Enterprise parity**:

* CE Native: ~40%
* OCA Equivalents: ~35%
* GAP_DELTA (ipai_* modules): ~20%
* GAP_NEW_MODULE (intentionally avoided): ~5%

Result: **≈95% Enterprise functional coverage** for our use cases, without using Enterprise/IAP.

---

## 7. Governance – How Agents & Devs Must Use This

Any time you (human or AI) consider building something in Odoo:

1. **Check if it's in CE.**

   * If yes → configure it. No code.

2. **If not, check this doc for an OCA module.**

   * If `OCA_EQUIVALENT` exists → vendor that module (18.0), no custom code.

3. **If neither CE nor OCA cover it, look for a tagged `GAP_DELTA`.**

   * If covered → extend via `_inherit` in the appropriate `ipai_*` family.

4. **Only if the feature is explicitly tagged `GAP_NEW_MODULE` and not marked "do not build",**

   * Propose a new module, and update this document with:

     * Module name, models, and justification.

5. **If a feature falls under "do not build / external tool":**

   * Use Notion, Superset, external SaaS, or mobile UIs instead of ERP changes.

This document is the **source of truth** for all Odoo 18 CE/OCA design decisions in InsightPulse ERP.
