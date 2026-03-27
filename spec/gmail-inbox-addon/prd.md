# PRD — InsightPulse Inbox for Odoo

## 1. Executive Summary

InsightPulse Inbox for Odoo is a Google Workspace Marketplace app implemented as a Gmail add-on. It converts inbox work into structured Odoo actions by enabling users to search Odoo records, create new operational records, link emails to existing records, and write selected email context into Odoo chatter without leaving Gmail.

The initial release is private-first and targets teams already operating Odoo as a system of action.

## 2. Problem Statement

Email remains a primary intake surface for customer requests, sales conversations, approvals, and follow-ups. Users often receive an email in Gmail, then manually re-enter data into Odoo, copy-paste context into chatter, or postpone record creation entirely. This creates:

- data loss,
- delayed record creation,
- fragmented customer history,
- inconsistent audit trails,
- and admin/governance ambiguity if the integration is not packaged correctly.

The current legacy Odoo inbox integration pattern is functionally useful but insufficient for our product strategy because we need:

- our own brand and operating model,
- private-first deployment control,
- explicit Marketplace/admin readiness,
- structured tenant registration,
- and room for AI-assisted workflows later.

## 3. Goals

### Primary goals

1. Reduce time from "email received" to "structured Odoo action."
2. Preserve traceability between Gmail conversations and Odoo records.
3. Support the most common operational actions directly inside Gmail.
4. Support tenant-safe private deployment for Odoo customer workspaces.
5. Establish a foundation for later AI-assisted summarization and recommendations.

### Secondary goals

1. Standardize inbox-to-Odoo workflows across CRM, Helpdesk, and Projects.
2. Provide a brand-clean alternative to the legacy Odoo listing.
3. Enable repeatable repo-first deployment and maintenance.
4. Treat admin approval and Marketplace packaging as first-class product requirements.

## 4. Identity and tenancy model

The product uses a layered tenancy model:

- **Google Workspace runtime context** — where the Gmail add-on executes and the acting user session exists.
- **Application tenant** — the target Odoo environment/customer workspace.
- **Identity authority** — optional Microsoft Entra-backed authority for onboarding, admin consent, policy, and workload/app identity.

### Initial v1 requirement

The add-on must work without Entra as a hard dependency for basic private deployment.

### Target-state requirement

The control plane must be able to register tenants with structured metadata:

- tenant slug
- immutable application tenant ID
- Odoo base URL
- allowed redirect/callback origins
- enabled capabilities (`crm`, `helpdesk`, `project`, `mail`)
- identity mode (`native_odoo`, `entra_federated`, `entra_admin_governed`)
- issuer / authority metadata where applicable

## Infrastructure baseline

The baseline deployment target is Azure-native. Public Odoo access is exposed through Azure-native ingress, tenant-facing canonical URLs are resolved from Azure-native infrastructure, identity/governance aligns to Microsoft Entra, and mailbox-host decisions remain separate from infrastructure ownership.

The add-on must not hardcode assumptions about non-Azure DNS, proxy, or edge providers. Each application tenant must declare one canonical public Odoo base URL derived from the Azure-native ingress layer and used for user navigation, OAuth redirect registration, Odoo record deep links, and tenant validation.

## Brand-to-mailbox mapping

Two distinct mailbox tenants drive the host-channel strategy:

- **W9 Studio** (`w9studio.net`) — Google Workspace. Gmail add-on is the primary mailbox host surface.
- **InsightPulseAI** (`insightpulseai.com`) — Zoho Mail. Zoho Mail extension is the planned second mailbox host surface.

Website hosting, DNS, and app runtime remain decoupled from mail provider choice. Both brands share Odoo as the operational backend.

## Odoo authentication model

For self-hosted Azure deployments, Odoo authentication is modeled separately from mailbox integrations.

### Supported Odoo auth providers

- `local_odoo` — break-glass/admin fallback
- `google_oauth` — Google Sign-In Authentication
- `microsoft_entra_oauth` — Microsoft Azure sign-in authentication

### Canonical redirect model

For OAuth-backed providers, the tenant record must store one canonical public Odoo base URL, and provider redirect registration must use:

`https://<odoo-base-url>/auth_oauth/signin`

### Baseline identity posture

For Azure-native deployments, `microsoft_entra_oauth` is the default workforce identity lane unless tenant policy explicitly enables additional providers.

### Provider-specific setup constraints

- Google requires Odoo `OAuth Authentication` and `Google Authentication` to be enabled, with the Google Client ID configured.
- Microsoft Entra requires the Odoo system parameter `auth_oauth.authorization_header = 1`.
- Microsoft Entra internal-user deployments default to single-tenant app registration.

### First-login linking behavior

The add-on and related docs must account for Odoo's provider-linking behavior:

- existing users may need to reach the Odoo Reset Password flow first,
- new users may need to use their invitation flow rather than a standard first-time password path.

### Product requirement

Users may encounter the product in Gmail, but the Odoo tenant they act against may authenticate using Google, Microsoft Entra, or native Odoo credentials, depending on tenant policy.

### Implementation note

The Gmail add-on must not assume that the active Gmail identity is automatically the same identity authority used to authenticate into Odoo.

### FR-2D Auth provider metadata

Each application tenant must declare supported Odoo auth providers: `local_odoo`, `google_oauth`, and `microsoft_entra_oauth`.

### FR-2E Canonical redirect URI model

Each OAuth-enabled tenant must declare a canonical public Odoo base URL used for provider redirect registration at `/auth_oauth/signin`.

### FR-2F Provider-specific setup flags

The tenant/provider model must support provider-specific setup requirements, including Microsoft's `auth_oauth.authorization_header = 1`.

### FR-2G First-login linking guidance

If a user must authenticate to Odoo, the system and docs must account for Odoo's password-reset/invitation-based first-link behavior for existing and new users.

### Risk: first-login linking confusion

A user may be signed into Gmail already but still fail Odoo access because Odoo account linking for Google or Microsoft requires the Reset Password or invitation flow first.

## Analytics ingress model

The baseline analytics ingress for Azure-native Odoo deployments is Microsoft Fabric mirrored databases from Azure Database for PostgreSQL.

### Source of truth
- Operational source database: Azure Database for PostgreSQL
- Canonical source database name: `odoo`

### Mirrored analytics target
- Fabric mirrored database for `odoo`
- OneLake-backed Delta representation of mirrored tables
- autogenerated SQL analytics endpoint for analytical querying

### Product requirement
The product must assume that operational data needed for analytics, BI, semantic modeling, or downstream Microsoft-native analytical workloads is accessed through the Fabric mirrored database path rather than through ad hoc direct reads from the production PostgreSQL system wherever mirrored data is sufficient.

### Consumption surfaces
The mirrored PostgreSQL data must be considered valid default input for:
- Fabric SQL analytics endpoint
- Power BI
- notebooks / Spark / data engineering
- cross-database analytical queries inside Fabric

### FR-16 Fabric mirroring baseline
Each Azure-native application tenant must be able to declare whether Fabric mirroring is enabled for its operational PostgreSQL source.

### FR-17 Mirrored database metadata
Tenant metadata must support: source server name, source database name, mirrored database item name, mirror status/readiness, workspace/capacity association, whether mirror-all-data or selected tables are used.

### FR-18 Read-only analytics posture
Analytical reads should default to the Fabric mirrored database and SQL analytics endpoint, not direct mutation-capable operational connections, unless an explicit exception is documented.

### Risk: source prerequisites not fully configured
Fabric mirroring for Azure Database for PostgreSQL requires source-side prerequisites such as logical WAL, Azure CDC configuration, and adequate worker-process settings.

### Risk: operational impact during snapshot or long transactions
Initial snapshotting and long-running source transactions can increase source resource usage and WAL growth.

### Risk: capacity or tenant-setting misconfiguration
Fabric mirroring depends on active Fabric capacity and required tenant settings being enabled.

### Risk: plane confusion
Without an explicit platform-plane model, teams may overload Fabric, Databricks, or Foundry into roles they are not intended to own.

## Microsoft-native platform plane model

The baseline platform model is split into four complementary planes:

### 1. Operational plane

- Odoo
- Azure Database for PostgreSQL (`odoo`)

### 2. Analytics plane

- Microsoft Fabric mirrored database / BI-facing analytical access

### 3. Data-intelligence plane

- Azure Databricks for advanced data engineering, lakehouse transformation, feature engineering, and ML-oriented workloads

### 4. AI plane

- Foundry for AI application development, agent workflows, governance, and scaling

### Product requirement

The product must assume:

- Fabric is the default mirrored analytical ingress for read-oriented reporting and Microsoft-native analytics consumption
- Databricks remains the heavier data-engineering / lakehouse / ML lane
- Foundry remains the AI runtime / orchestration / governance lane

### FR-19 Plane-aware data policy

The architecture must distinguish: operational writes, analytical reads, data-engineering transformations, and AI/agent execution.

### FR-20 Databricks workload posture

Data engineering, model-oriented transformations, feature pipelines, and advanced lakehouse workloads should be modeled as Databricks-eligible workloads.

### FR-21 Foundry AI posture

Agent/application AI workflows, governed AI deployment patterns, and AI scaling concerns should be modeled in the Foundry lane rather than in the Odoo or mailbox-host layers.

## 5. Non-goals

- Replace the Odoo web UI
- Build a generic email client
- Mirror all mailboxes into Odoo
- Implement autonomous classification and filing of all messages in v1
- Support arbitrary third-party backends beyond Odoo in v1
- Solve full org-wide SaaS admin governance beyond what is needed for private deployment
- Shipping Gmail and Zoho Mail hosts simultaneously in v1
- Forcing Fabric, Databricks, and Foundry into one interchangeable runtime role
- Replatforming the Azure-native Odoo operational stack onto Wix

## Wix headless integration lane

Wix Headless is a future or optional experience/business-solution lane for projects that need Wix-managed commercial or engagement capabilities exposed through custom frontend experiences.

### Supported solution classes

Wix Headless business APIs can support: Bookings, Events, Contacts, eCommerce/Stores, Pricing Plans, Blog, Groups, Inbox, Loyalty, and Marketing Tags.

### Preferred development path

For the current Azure-native architecture, the default Wix mode is `self_managed_headless` so hosting, deployment, auth integration, and runtime ownership remain under the existing platform model.

### Alternate mode

`wix_managed_headless` may be used only when the project intentionally accepts Wix-managed hosting, Wix CLI/Vibe scaffolding, and Wix-handled auth/runtime conveniences.

### FR-22 Wix lane classification

If Wix is introduced, the tenant/project metadata must classify it as `self_managed_headless` or `wix_managed_headless`.

### FR-23 Wix capability declaration

The system must record which Wix business capabilities are in use, such as bookings, events, stores, pricing plans, blog, groups, inbox, or loyalty.

### FR-24 Azure-native preservation

Introducing Wix must not change the default Azure-native/Odoo/Fabric/Databricks/Foundry role split unless explicitly documented as an exception.

## 6. Personas

### 6.1 Sales operator

Needs to convert inbound conversations into leads or opportunities quickly, while checking if the sender already exists as a contact or company.

### 6.2 Support coordinator

Needs to create helpdesk tickets from customer emails, attach relevant context, and avoid duplicated tickets.

### 6.3 Project / delivery operator

Needs to turn email threads into follow-up tasks linked to a project or customer.

### 6.4 Executive / founder

Needs a fast way to preserve business context from the inbox into Odoo without admin-heavy workflows.

## 7. Marketplace actors

### End users

Need fast Gmail-native actions:

- search Odoo
- create or link records
- log selected email context
- open the resulting Odoo record

### Administrators

Need confidence that:

- installation scope is controlled
- privacy and permissions are documented
- tenant and identity boundaries are explicit
- deployment visibility is appropriate for the organization

### Developers/operators

Need a release model that supports:

- versioned deployments
- a publishable Google Cloud project
- Marketplace listing metadata
- reproducible private rollout

## Mail host channels

### Primary v1 host

Gmail Google Workspace add-on.

### Future host channel

Zoho Mail eWidget extension. Zoho Mail supports custom extensions in the mailbox via eWidget, Marketplace-based distribution, widget placements including preview right panel (`zoho.mail.preview.rightpanel`) and pinned right panel (`zoho.mail.pinnedview.rightpanel`), and developer APIs for mail details, compose/reply, attachments, contacts, relation data, and widget actions.

### Product requirement

The core record actions must be host-agnostic: search Odoo, create contact/lead/ticket/task, link message to record, log selected message context to chatter. These actions should be implementable on Gmail first, then mapped to Zoho Mail later.

## Zoho implementation lanes

If Zoho is introduced as a future host or integration lane, it must be decomposed into the following roles:

### Zoho Mail host lane

Zoho Mail supports mailbox extensions via Developer Space / widgets, with placements including `zoho.mail.preview.rightpanel`, `zoho.mail.pinnedview.rightpanel`, `zoho.mail.preview.moreoption`, and `zoho.mail.emailaddress.moreaction`.

### Zoho integration/tooling lane

Zoho provides multiple developer tools, each with a different role: Sigma for extensions, Flow for workflow integrations, Creator/Catalyst for application development, and Zoho APIs for direct service integration.

### Zoho identity lane

Zoho supports OAuth 2.0 for delegated API access and OIDC for "Sign in using Zoho."

### Product requirement

Zoho must be treated as a future mailbox-host and integration ecosystem, not collapsed into the Odoo auth-provider model by default. Selecting the full Zoho implementation stack for v1 is a non-goal.

## 8. Jobs to Be Done

### When reading an email

- I want to see whether the sender already exists in Odoo.
- I want to search likely matching records.
- I want to create a contact, lead, ticket, or task from the email.
- I want to attach selected email context to an Odoo record.
- I want to jump into the resulting Odoo record immediately.

### When composing or replying

- I want quick access to related Odoo context.
- I want to use compose-side actions for structured follow-up workflows.
- I want to preserve linkage between the draft/reply and the target Odoo record when appropriate.

### When opening the add-on with no message selected

- I want a useful homepage with recent entities, quick actions, tenant/account status, and help.

## 9. User Stories

1. As a user reading a customer email, I can search existing Odoo contacts by sender so I know whether the conversation is already known.
2. As a sales user, I can create a lead or opportunity from the current message.
3. As a support user, I can create a helpdesk ticket from the current message.
4. As a delivery user, I can create a project task from the current message.
5. As a user, I can link the message to an existing Odoo record instead of creating a new one.
6. As a user, I can choose whether to log the email body, metadata, and attachments to chatter.
7. As a user, I can open the Odoo record that was created or linked.
8. As an operator, I can connect only through a resolved, approved application tenant.
9. As an administrator, I can evaluate installation, permissions, and support/governance posture before rollout.

## 10. Functional Requirements

### FR-1 Homepage

The add-on must provide a Gmail homepage card that shows connection status, current tenant, quick-create actions, recent/pinned record shortcuts where supported, and help/settings entry points.

### FR-2 Tenant connection

The add-on must support login to an approved Odoo tenant. The user must be prevented from connecting to non-approved domains. The product must store only the minimum state required for session continuity.

### FR-2A Tenant registry

The system must resolve the target application tenant from a registry, not from free-form user input alone.

### FR-2B Identity mode support

The system must support per-tenant identity modes: native Odoo auth, Entra-governed admin onboarding/policy, and future federated extensions.

### FR-2C Admin-governed onboarding

For Entra-enabled tenants, onboarding must capture tenant admin metadata, authority identifiers, and policy state separately from Gmail-user session state.

### FR-2D Auth provider metadata

Each application tenant must declare supported Odoo auth providers: `local_odoo`, `google_oauth`, `microsoft_entra_oauth`.

### FR-2E Canonical redirect URI model

Each OAuth-enabled tenant must declare a canonical public Odoo base URL used for provider redirect registration at `/auth_oauth/signin`.

### FR-2F Provider-specific setup flags

The tenant/provider model must support provider-specific setup requirements, including Microsoft's `auth_oauth.authorization_header = 1`.

### FR-2G First-login linking guidance

If a user must authenticate to Odoo, the system and docs must account for Odoo's password-reset/invitation-based first-link behavior for existing and new users.

### FR-3 Message-context panel

When a user opens a Gmail message, the add-on must display a contextual card with sender identity summary, candidate Odoo matches, actions to create contact/lead/ticket/task, action to link to an existing record, and action to preview what will be logged.

### FR-4 Odoo search

The add-on must search Odoo for contacts, companies, and relevant open entities as configured.

### FR-5 Record creation

The add-on must support creation of contact, lead/opportunity, helpdesk ticket, and project task.

### FR-6 Record linking

The add-on must allow the current message/thread to be linked to an existing Odoo record.

### FR-7 Chatter logging

The add-on must allow the user to selectively log message subject, sender/recipient metadata, selected message body content, attachment references and/or attachments, and execution note indicating add-on action performed.

### FR-8 Open in Odoo

Every created or linked record must present an action that opens the canonical Odoo URL in the browser.

### FR-9 Compose support

The add-on must support Gmail compose UI for at least one high-value action in v1: draft-side lookup and linking, or creation of a structured reply helper tied to an Odoo record.

### FR-10 Errors and recovery

The add-on must surface recoverable errors clearly: auth expired, tenant not allowed, Odoo unavailable, required module not enabled, validation failure, attachment too large/unsupported.

### FR-11 Marketplace/admin readiness

The product must include admin-facing documentation for supported deployment model, required scopes/permissions, privacy summary, support path, and installation/governance assumptions.

### FR-12 Google Cloud publishability

The product must be deployable from a standard Google Cloud project suitable for Marketplace publication. The default Apps Script project cannot be used for publication.

### FR-14 Host channel abstraction

The product architecture must isolate mailbox-host-specific UI/runtime code from Odoo record-action logic.

### FR-15 Zoho host readiness

The system design must allow a future Zoho Mail extension host that can access current email context, compose/reply actions, attachments, and relation/link metadata, without redesigning the Odoo adapter.

### FR-13 Listing completeness

The product must have complete Marketplace assets and metadata: app name, short description, full overview, graphics (icon, banner, hero), privacy policy, and support URL/content.

## 11. Non-functional Requirements

### NFR-1 Security

Tenant registry/allowlist required. No plaintext secrets in repo. Minimal scopes. Bounded external calls only.

### NFR-2 Reliability

Safe retries on transient Odoo/API failures. Idempotent create/link behavior where practical. No duplicate chatter logging on user-visible retries unless confirmed.

### NFR-3 Performance

Homepage should feel immediate. Contextual actions should return within acceptable Gmail add-on latency. Heavy processing should be deferred to Odoo-side or service-side logic.

### NFR-4 Maintainability

Manifest and domain/tenant policy must be easy to audit. Branded fork/customization boundaries must be explicit. Repo layout must cleanly separate UI shell, auth, registry/config, and Odoo adapter logic.

### NFR-5 Observability

Structured logs for create/link attempts. Clear correlation from Gmail-side action to Odoo-side result. Evidence artifacts for pilot validation.

## 12. Dependencies

- Google Workspace add-on / Gmail runtime
- standard Google Cloud project linked for publish/deploy
- approved Odoo tenant(s)
- Odoo mail/plugin capability and corresponding app modules
- integration endpoints in Odoo or a minimal bridge service
- optional tenant registry/control-plane backend

## 13. Risks

### Risk: tenant/authority conflation

Confusing Microsoft Entra tenants with Odoo customer tenants can produce bad onboarding, misrouted auth, and broken multi-customer isolation.

### Risk: domain/tenant misconfiguration

Could block authentication or create security gaps.

### Risk: Odoo module variance

Some tenants may lack Helpdesk, Projects, or mail plugin settings.

### Risk: Marketplace/publication complexity

Mitigated by private-first release.

### Risk: attachment handling complexity

Needs clear bounds in v1.

### Risk: mailbox identity vs Odoo identity mismatch

A user may operate in Gmail with a Google account while the target Odoo tenant requires Microsoft Entra or native Odoo auth. This mismatch must be handled explicitly in UX and configuration.

### Risk: first-login linking confusion

A user may be signed into Gmail already but still fail Odoo access because Odoo account linking for Google or Microsoft requires the Reset Password or invitation flow first.

### Risk: too much logic in Apps Script

Mitigated by keeping the add-on thin and pushing complex logic out.

## 14. Success Metrics

### Adoption

- % of pilot users who complete auth
- weekly active users
- messages opened with add-on panel active

### Workflow conversion

- leads created from Gmail
- tickets created from Gmail
- tasks created from Gmail
- link actions completed

### Efficiency

- median time from email open to Odoo record creation/link
- reduction in manual copy-paste steps

### Quality

- duplicate creation rate
- failed auth rate
- failed tenant validation rate
- failed chatter log rate

## 15. Launch Strategy

### Phase 1

Private pilot with one controlled tenant/workspace and a small user group.

### Phase 2

Broaden within the same workspace/domain after UX and logging stabilize.

### Phase 3

Evaluate whether public publication is justified, with separate legal/security/support readiness.

Private pilot remains the default launch path because:

- private apps can be limited to a domain,
- private apps are immediately available within the organization,
- public publication introduces Google review and broader support obligations,
- and the visibility selection is treated as a durable release decision.

## 16. Acceptance Criteria

The PRD is satisfied for v1 when:

- a pilot user can install and authorize the add-on,
- connect to a resolved approved tenant,
- create or link at least one supported Odoo record from a Gmail message,
- log selected message context to chatter,
- and open the resulting Odoo record successfully.

---

## Gmail Mail Plugin (merged)

> Merged from `spec/gmail-mail-plugin/prd.md` on 2026-03-28. The original spec described an earlier iteration of the Gmail-to-Odoo bridge using `ipai_mail_plugin_bridge`. Content below is preserved for historical reference and architectural context.

### Original Bridge Architecture

```
Gmail UI (Card Service)
    |
    | HTTPS / JSON-RPC
    v
erp.insightpulseai.com/ipai/mail_plugin/*
    |
    | ORM
    v
Odoo CE 19 (res.partner, crm.lead, project.task, mail.thread)
```

### V1 Endpoint Scope (Original)

| Feature | Endpoint |
|---------|----------|
| Auth via API key | `POST /ipai/mail_plugin/session` |
| Contact lookup by sender email | `POST /ipai/mail_plugin/context` |
| View related leads | included in context response |
| View related tasks/tickets | included in context response |
| Create CRM lead | `POST /ipai/mail_plugin/actions/create_lead` |
| Create ticket (project.task) | `POST /ipai/mail_plugin/actions/create_ticket` |
| Log note to chatter | `POST /ipai/mail_plugin/actions/log_note` |
| Open record in Odoo | client-side OpenLink |

### Security (Original)

- Tokens stored as SHA-256 hashes server-side; raw tokens stay client-side.
- API key authentication; no session cookies exposed to the add-on.
- Credentials stored in `PropertiesService.getUserProperties()` (per-user, encrypted by Google).
- All traffic over TLS via Azure Front Door.
