# Constitution — InsightPulse Inbox for Odoo

## 1. Document Control

- Spec Slug: `gmail-inbox-addon`
- Product Name: `InsightPulse Inbox for Odoo`
- Status: Draft / Proposed
- Owner: Platform + Odoo Integrations
- Product Type: Google Workspace Marketplace app implemented as a Gmail add-on
- Primary Host Surface: Gmail
- Primary System of Action: Odoo
- Initial Distribution Model: Private Google Workspace Marketplace deployment
- Canonical Repo Path:
  - `spec/gmail-inbox-addon/constitution.md`
  - `spec/gmail-inbox-addon/prd.md`
  - `spec/gmail-inbox-addon/plan.md`
  - `spec/gmail-inbox-addon/tasks.md`

## 2. Purpose

InsightPulse Inbox for Odoo exists to let users triage, classify, create, and link operational work from Gmail without losing traceability in Odoo.

The product must reduce context switching between inbox work and business systems while preserving tenant safety, admin governability, explicit user intent, and auditability.

## 3. Product Thesis

Inbox activity is often the first place where customer requests, sales opportunities, support issues, and execution follow-ups appear. Gmail is the intake surface; Odoo is the operational system where those interactions should become structured work.

This add-on creates a Gmail-native action layer that:

- identifies relevant Odoo contacts and records,
- enables record creation from email,
- links conversations to existing Odoo entities,
- stores selected metadata and attachments in Odoo chatter,
- and opens the user directly into the corresponding Odoo workflow.

## 4. Constitutional Principles

### 4.1 Gmail-native first

The product must feel native to Gmail's side-panel and compose experience. Workflows must be card-based, concise, and action-oriented. The add-on must not depend on users leaving Gmail for routine lookup and record-creation tasks unless the user explicitly chooses to open Odoo.

### 4.2 Odoo is the operational source of action

The add-on is a bridge, not a replacement UI for CRM, Helpdesk, Projects, or Contacts. All durable operational records must resolve into Odoo entities or controlled integration-layer records.

### 4.3 Explicit user intent over silent automation

No email, attachment, or metadata should be logged into Odoo without a user action or an explicitly enabled policy. The product must make it clear what will be sent to Odoo and to which record.

### 4.4 Identity and tenant boundaries are mandatory

The product must distinguish three separate concepts:

1. **Workspace user/session** — The Gmail add-on runs in a Google Workspace context and authenticates the acting user in Gmail.

2. **Application tenant** — The Odoo customer/workspace that receives records, links, and chatter writes.

3. **Identity tenant / authority** — The Microsoft Entra tenant or authority, when used, that governs admin onboarding, access policy, application registrations, workload identity, or federation.

These concepts must never be conflated in code, config, or documentation.

The product must support a fail-closed tenant registry model:

- approved Odoo tenant base URLs,
- tenant metadata,
- allowed identity authority / issuer metadata where applicable,
- feature flags and module capabilities by tenant.

A simple hostname allowlist is acceptable only as a bootstrap control, not as the long-term tenancy model.

### 4.10 Azure-native infrastructure boundary

The product assumes an Azure-native infrastructure baseline for public ingress, DNS, certificates, identity, and runtime integration. Mailbox-host, Odoo auth-provider, and Marketplace distribution decisions must align to Azure-native platform ownership and must not assume Cloudflare or any other third-party edge/DNS dependency. The canonical public Odoo base URL must be provided by the Azure-native ingress layer for the target tenant/environment.

### 4.11 Brand-to-mailbox mapping

The product respects two distinct mailbox tenants:

- **W9 Studio** (`w9studio.net`) — Google Workspace tenant for collaboration, creative, and client work
- **InsightPulseAI** (`insightpulseai.com`) — Zoho Mail tenant for role inboxes, operational aliases, and business mail

This makes the Gmail add-on lane real for W9/Google users and the Zoho Mail extension lane real for InsightPulseAI users. Personal Gmail remains separate from both.

### 4.12 Zoho capability separation

When Zoho is introduced, the product must distinguish between:

- Zoho Mail as a mailbox host surface
- Zoho OAuth/OIDC as a Zoho identity/service-access mechanism
- Zoho Sigma / Flow / Catalyst / APIs as implementation tooling
- Odoo auth providers as the target-system login model

These concerns must not be conflated in product architecture or tenant metadata.

### 4.11 Mail host abstraction

The product must separate:

- **Mailbox host surface** — Gmail Google Workspace add-on (v1), future Zoho Mail eWidget extension
- **Operational target** — Odoo
- **Identity/auth provider model** — Odoo-local or tenant-configured OAuth providers

The mailbox host surface must be replaceable without redefining the Odoo operational model.

### 4.11 Odoo auth providers are separate from mailbox plugins

The product must treat mailbox plugins and Odoo authentication providers as distinct integration lanes.

- Mailbox plugins: Gmail Plugin, Outlook Plugin
- Odoo authentication providers: Google OAuth, Microsoft Entra OAuth, local Odoo fallback

The architecture must not assume that Gmail plugin installation is equivalent to Google sign-in for Odoo, or that Outlook usage is equivalent to Microsoft Entra sign-in.

### 4.X Fabric mirroring is the canonical analytics ingress

For Azure-native deployments, the canonical analytics ingress for the Odoo PostgreSQL operational database is Microsoft Fabric database mirroring.

The source operational database remains PostgreSQL (`odoo`), while analytics consumption is performed from the Fabric mirrored database, OneLake-backed Delta tables, and the autogenerated SQL analytics endpoint.

This product must treat Fabric mirroring as:

- the default analytics replication path,
- the preferred read-only analytical access surface,
- and the default bridge from Odoo operational data into Microsoft-native BI, data engineering, and AI workloads.

Invariants:

- do not treat the Fabric mirrored database as the operational system of record.
- do not write application mutations through the SQL analytics endpoint, which is analytical and read-only.
- do not introduce custom ETL as the default path when Fabric mirroring is available and approved for the tenant.

### 4.Y Microsoft-native plane separation

The platform must distinguish operational, analytics, data-engineering, and AI planes.

- Operational system of record:
  - Odoo on Azure
  - Azure Database for PostgreSQL

- Analytics ingress and BI-facing mirrored data:
  - Microsoft Fabric

- Advanced data engineering, lakehouse processing, and ML workloads:
  - Azure Databricks

- AI application, agent, governance, and scaling plane:
  - Foundry

These planes are complementary and must not be collapsed into a single-tool assumption.

Invariants:

- do not treat Fabric as a replacement for the operational PostgreSQL source of record.
- do not treat Fabric mirroring as a replacement for Databricks data-engineering or ML workloads.
- do not treat Foundry as the operational database, analytics mirror, or lakehouse runtime.

### 4.Z Wix headless is an experience/business-solution lane

Wix Headless, when used, is an experience-layer and business-solution integration lane rather than an operational system-of-record, identity authority, or platform-control-plane replacement.

Supported Wix business-solution use cases may include: bookings, events, contacts, eCommerce/stores, pricing plans, blog, groups, inbox, loyalty, and marketing tags.

Wix adoption must not replace the Azure-native/Odoo operational baseline unless explicitly approved by architecture change.

### 4.5 Private-first distribution

The initial deployment target is a private Marketplace listing or private domain deployment. Public publication is a later decision, with a separate readiness bar for legal, security, review, and support obligations.

### 4.6 Thin integration layer

The add-on must remain a thin, branded interaction layer. Business logic should live in Odoo endpoints or a small integration service when necessary. Avoid embedding complex policy logic or irreversible business rules in Apps Script.

### 4.7 Auditability and operator trust

Every record-creation or link action must be reconstructible through Odoo-side evidence, deterministic payload contracts, and minimal structured logs. Failure states must be understandable and non-destructive.

### 4.8 Automation-first delivery

The project must be reproducible from source control, scriptable for deployment, and testable without manual repo drift. Generated manifests, branding assets, and deployment metadata must have a clear source of truth.

### 4.9 Marketplace stakeholder model

The product must be designed for three distinct Marketplace stakeholders:

1. **End users** — install and use the add-on inside Gmail.

2. **Developers/operators** — build, version, deploy, and maintain the add-on and its tenant configuration.

3. **Administrators** — evaluate security/privacy, control installation, and govern org-wide usage.

The product must not optimize only for end-user flows while ignoring admin review, app-governance, and deployment-operability requirements.

## 5. Scope Boundaries

### In scope

- Gmail homepage
- Gmail message-context UI
- Gmail compose UI
- Odoo authentication / tenant connection
- Search for contacts / companies / candidate records
- Create contacts
- Create leads / opportunities
- Create helpdesk tickets
- Create project tasks
- Link message thread to existing Odoo records
- Log selected email metadata and optional attachments to chatter
- Open linked Odoo record in browser
- Configurable tenant registry / allowlist
- Private deployment docs and release workflow
- Admin-facing governance and installation documentation

### Out of scope for v1

- Full inbox sync
- Two-way mailbox mirroring
- Automatic background classification of all mail
- Complex admin analytics console
- Public multi-tenant self-serve signup
- Deep non-Gmail Workspace surface support

## 6. Product Invariants

The product must not:

- create hidden Odoo records without user action,
- bypass tenant resolution or tenant-domain validation,
- write to arbitrary non-approved URLs,
- store plaintext secrets in source control,
- require users to understand Odoo internals to complete core actions,
- couple Marketplace branding to Odoo SA assets or naming,
- assume that a Microsoft Entra tenant and an application/customer tenant are the same object,
- make identity authority decisions from email-domain matching alone,
- treat administrator approval, app listing metadata, and deployment governance as release afterthoughts,
- conflate Gmail/Outlook mailbox integration with Odoo SSO provider configuration,
- treat Zoho Mail host integration as equivalent to an Odoo authentication provider,
- model Zoho OAuth/OIDC as an Odoo auth provider unless a tenant explicitly uses Zoho as the identity authority for Odoo,
- couple the product to Cloudflare-era assumptions or third-party DNS/edge services when the platform baseline is Azure-native,
- or model Wix Headless as an Odoo auth provider, operational SoR, or Azure platform substitute.

## 7. Success Conditions

The project is considered launchable for private release when:

1. a user can authenticate to an approved Odoo tenant,
2. a user can open a Gmail message and create or link an Odoo record,
3. selected email content can be written to chatter with clear user confirmation,
4. opening the linked record in Odoo works reliably,
5. tenant registry / allowlist enforcement is verified,
6. add-on deployment is reproducible from repo artifacts,
7. support, privacy, admin-governance, and release docs exist,
8. pilot users can complete at least one CRM, one support, and one project flow end-to-end.

## 8. Change Control

Any future change that expands:

- audience from private to public,
- supported hosts beyond Gmail,
- or data movement beyond explicit user action,

must update this constitution first, then cascade changes into the PRD, plan, and tasks.
