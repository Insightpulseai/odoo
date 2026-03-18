# Capability Test Prompt — SAP Joule + Concur + Odoo on Azure

> Use this prompt with a research-capable agent (Claude, Copilot, Perplexity)
> to validate every capability claim in the spec against real product surfaces.

---

```text
You are validating an integration spec for SAP Joule + SAP Concur + Odoo CE 19
on Azure. The spec claims specific capabilities across 4 systems. Your job is to
confirm or refute each claim against current product documentation, APIs, and
known limitations.

For each capability below, return:
- CONFIRMED: cite the doc/API/changelog that proves it
- PARTIAL: capability exists but with caveats (state them)
- UNCONFIRMED: no public documentation found
- REFUTED: documentation explicitly contradicts the claim

Be precise. Do not speculate. If a capability requires a specific license tier
or preview/beta access, state that.

---

## A. SAP Joule Capabilities

A1. Joule supports conversational interaction spanning SAP and non-SAP systems.
    - Source claim: SAP documents Joule as AI assistant across SAP workflows
      with Microsoft 365 Copilot interoperability.
    - Test: Does Joule have a documented external API or plugin/extension model
      that allows non-SAP systems to participate in Joule conversations?

A2. Joule can consume external REST APIs for read/query operations.
    - Test: Is there a documented mechanism for Joule to call arbitrary external
      endpoints (e.g., an Odoo API behind Azure API Management)?

A3. Joule can trigger bounded actions in external systems.
    - Test: Can Joule invoke webhooks, HTTP actions, or custom skills that write
      to external systems? What are the documented guardrails?

A4. Joule + Microsoft 365 Copilot bidirectional interaction.
    - Source claim: SAP documents this on their Joule product page.
    - Test: What is the actual integration mechanism? Is it GA or preview?
      Does it require SAP BTP? What Microsoft licenses are needed?

A5. Joule is available for SAP Concur specifically (not just S/4HANA).
    - Test: Does Joule have documented Concur-specific capabilities, or is
      Concur integration roadmap-only?

---

## B. SAP Concur Capabilities

B1. Concur supports Microsoft Entra ID SSO (SAML/OIDC).
    - Source claim: Microsoft Learn documents Concur Travel and Expense
      integration with Entra ID.
    - Test: Confirm the tutorial exists. What protocol (SAML 2.0, OIDC)?
      Is it GA? Any Concur edition restrictions?

B2. Concur has a REST API for retrieving approved expense reports.
    - Test: What is the API endpoint? What authentication method?
      What data fields are available on an expense report?
      Is there a webhook/event model for "report approved" events?

B3. Concur supports employee and vendor master data sync.
    - Test: Is there an API for employee import/export? Vendor import/export?
      What is the documented sync pattern (push, pull, event)?

B4. Concur expense reports have a unique report ID usable as idempotency key.
    - Test: What is the field name? Is it globally unique? Immutable after creation?

B5. Concur supports cost center and project code mapping.
    - Test: Can Concur expense line items carry custom allocation fields
      (cost center, project code, analytic account) that map to an external
      ERP's chart of accounts?

B6. Concur supports tax code and currency on expense line items.
    - Test: What tax code model does Concur use? Can it carry VAT/GST codes?
      Multi-currency support?

---

## C. Odoo CE 19 Capabilities

C1. Odoo account.move supports draft state for external document creation.
    - Test: Can an external API call create an account.move in draft state
      via XML-RPC or JSON-RPC? What fields are required?

C2. Odoo supports external API authentication via token or OAuth.
    - Test: What authentication methods does Odoo 19 CE support for API access?
      Is there native OAuth2/OIDC support, or does it require a module
      (e.g., ipai_auth_oidc, OCA auth_oauth)?

C3. Odoo account.move.ref can serve as idempotency key.
    - Test: Is the ref field indexed? Is there a unique constraint?
      Can it be used to detect duplicates before creating a new record?

C4. Odoo supports analytic account mapping for cost center allocation.
    - Test: Can account.move.line carry analytic_distribution (Odoo 17+)
      or analytic_account_id for cost center mapping?

C5. Odoo supports custom API endpoints (controllers).
    - Test: Can Odoo 19 CE expose custom REST endpoints via ir.http controllers?
      What is the standard pattern for building bounded read/write APIs?

C6. Odoo supports OIDC/SAML for user authentication.
    - Test: Does Odoo 19 CE have native OIDC support, or does it require
      auth_oauth (core) + custom provider config? Can it federate with Entra ID?

---

## D. Azure Integration Plane

D1. Azure API Management can mediate between Concur API and Odoo API.
    - Test: Can APIM proxy both outbound calls to Concur and inbound calls
      to Odoo Container Apps? What auth patterns are supported?

D2. Azure Key Vault can store Concur API credentials and Odoo API tokens.
    - Test: Confirm Key Vault supports arbitrary secret storage with
      managed identity access from Container Apps.

D3. Azure Service Bus or Storage Queue can serve as dead-letter for failed syncs.
    - Test: What is the recommended pattern for dead-letter + replay in
      Azure-native architectures? Message retention limits?

D4. Application Insights can correlate requests across Concur → Azure → Odoo.
    - Test: Does App Insights support distributed tracing with custom
      correlation IDs for non-Azure endpoints?

D5. Entra ID can issue service principal tokens for system-to-system calls.
    - Test: Can a managed identity or service principal obtain tokens for
      calling both Concur APIs and Odoo APIs?

---

## E. Integration Pattern Validation

E1. Draft-first posting pattern.
    - Test: Is there a documented pattern or reference architecture for
      "external system → ERP draft document → approval → posting"?
      Any SAP, Microsoft, or Odoo reference implementations?

E2. Concur → ERP expense sync.
    - Test: Does SAP document a reference architecture for Concur → non-SAP
      ERP expense synchronization? Or is the documented path only
      Concur → S/4HANA?

E3. Joule → external system query pattern.
    - Test: Is there a documented pattern for Joule querying external
      (non-SAP) systems? Or is Joule currently SAP-ecosystem-only
      for data access?

E4. Multi-system SSO with Entra as hub.
    - Test: Is there a documented pattern for Entra ID federating SSO
      across both SAP Concur and a self-hosted Odoo instance?

---

## Output format

For each item (A1–E4), return:

| ID | Verdict | Evidence | Caveats |
|----|---------|----------|---------|
| A1 | CONFIRMED/PARTIAL/UNCONFIRMED/REFUTED | URL or doc reference | Tier/license/preview restrictions |

Then provide a summary:
- Total CONFIRMED
- Total PARTIAL (list the caveats that matter most)
- Total UNCONFIRMED (list the biggest risks)
- Total REFUTED (list the spec claims that need revision)

Finally, recommend which spec sections should be updated based on findings.
```

---

## Usage

Run this prompt against:

1. **Claude** (with web search) — good for SAP/Microsoft doc synthesis
2. **Perplexity** — good for finding specific API docs and changelogs
3. **GitHub Copilot** — good for Odoo CE codebase questions (C1–C6)
4. **Microsoft Copilot** — good for Azure/Entra-specific questions (D1–D5)

Cross-reference findings from at least 2 sources before updating the spec.
