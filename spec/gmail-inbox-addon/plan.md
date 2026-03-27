# Plan — InsightPulse Inbox for Odoo

## 1. Delivery Strategy

Build a Gmail Google Workspace add-on with Apps Script as the UI/runtime shell and a thin Odoo integration layer behind it.

Use a private-first release model:

- private deployment and pilot first,
- public Marketplace listing only after deliberate readiness review.

## 2. Architecture Overview

### 2.1 Major components

1. Gmail Add-on Shell
   - homepage trigger
   - contextual message trigger
   - compose trigger
   - card navigation
   - action callbacks

2. Auth / Session Layer
   - user authorization flow
   - session continuity
   - logout / re-auth flows

3. Odoo Adapter
   - contact/company lookup
   - create contact
   - create lead/opportunity
   - create helpdesk ticket
   - create project task
   - link message to existing record
   - chatter logging
   - open-in-Odoo URL generation

4. Tenant Registry / Policy Layer
   - tenant registry with immutable tenant IDs
   - Odoo base URL and capability metadata
   - identity mode per tenant
   - Entra authority metadata where applicable
   - environment separation (dev / pilot / prod)
   - fail-closed tenant resolution

5. Azure-native Platform Layer
   - canonical public ingress (Azure Front Door)
   - DNS and certificate ownership
   - Microsoft Entra governance
   - environment routing for dev / pilot / prod

6. Evidence / Support Layer
   - structured logs
   - pilot evidence records
   - support docs
   - privacy and release metadata

## 3. Target Repo Layout

```text
apps/gmail-inbox-addon/
  appsscript.json
  package.json
  README.md
  src/
    main.ts
    auth.ts
    config.ts
    registry.ts
    odoo.ts
    types.ts
    cards/
      home.ts
      message.ts
      compose.ts
      common.ts
    actions/
      login.ts
      search.ts
      create_contact.ts
      create_lead.ts
      create_ticket.ts
      create_task.ts
      link_record.ts
      log_chatter.ts
  assets/
    icon.svg
    marketplace/
  docs/
    privacy.md
    support.md
    marketplace-listing.md
    admin-install-governance.md
    architecture/
      multitenancy-identity.md
  tests/
    fixtures/
    unit/

spec/gmail-inbox-addon/
  constitution.md
  prd.md
  plan.md
  tasks.md
```

## 4. Key Technical Decisions

### 4.1 Add-on runtime

Use Apps Script first because it matches Gmail add-on triggers and card UI well and is the fastest path to an internal/private release.

### 4.2 Thin shell, externalized business logic

Keep the add-on logic focused on rendering cards, collecting user intent, validating resolved tenant context, and invoking Odoo-side operations. Avoid complex business policy and document-processing logic inside the add-on.

### 4.3 Odoo integration contract

Preferred backend contract options, in order:

1. Odoo HTTP/JSON-RPC against approved server endpoints
2. Small custom Odoo controller endpoints for the add-on
3. Minimal bridge service only if required for auth or response shaping

### 4.4 Tenant validation

Introduce a registry-driven fail-closed model:

- immutable application tenant ID
- approved Odoo base URL
- allowed capabilities and feature flags
- environment-specific configuration
- optional authority/issuer metadata

No arbitrary-domain login.

### 4.5 Branding

Ship under InsightPulse branding with original icon assets and copy. Do not reuse Odoo SA branding in the product name, listing, or app icon.

### 4.6 Licensing

If upstream Odoo mail extension code is reused, record the fork basis, preserve notices, and isolate local modifications clearly.

### 4.7 Identity architecture

Recommended target-state architecture:

- **Gmail Add-on** — user-facing action surface in Google Workspace. Never acts as the source of truth for tenant registration.

- **Tenant Registry / Control Plane** — canonical store for application tenants. Stores Odoo URL, capabilities, branding, feature flags, and identity mode. May be governed by an Entra-backed admin portal.

- **Identity Plane** — optional Microsoft Entra integration for tenant admin onboarding, organization-level access policy, workload identity for backend services, and future federation patterns.

- **Odoo Adapter** — operational record search/create/link/log actions. Receives a resolved tenant context, not raw arbitrary domains.

## 5. User Flows

### Flow A — First open / homepage

1. User opens add-on in Gmail side panel.
2. Homepage trigger runs.
3. If not authenticated, show connect flow.
4. If authenticated, show quick actions and current tenant status.

### Flow B — Create lead from message

1. User opens Gmail message.
2. Contextual trigger runs.
3. Add-on resolves sender metadata and candidate Odoo matches.
4. User chooses Create Lead.
5. Form is prefilled with sender + subject context.
6. User confirms optional chatter logging.
7. Odoo adapter creates record.
8. Result card shows success and Open in Odoo action.

### Flow C — Link message to existing ticket

1. User opens Gmail message.
2. User searches existing Odoo entities.
3. User selects ticket.
4. User chooses what to log.
5. Add-on writes chatter message and linkage note.
6. Result card confirms link.

### Flow D — Compose-side action

1. User opens compose window.
2. Compose trigger loads card.
3. Add-on offers draft-side lookup / link / helper action.
4. User inserts structured response or records linkage metadata.

## 6. Marketplace and release architecture

### Product type

This product is a Google Workspace Marketplace app implemented as a Gmail add-on.

Required Gmail surfaces:

- homepage trigger
- contextual message trigger
- compose trigger

### Publication architecture

The project must support:

- Apps Script-based add-on implementation for lightweight Gmail workflows
- linked standard Google Cloud project for publishing
- versioned deployment IDs for release tracking
- private-first Marketplace rollout

### Governance artifacts

The release package must include:

- Marketplace listing copy
- privacy documentation
- support documentation
- admin-facing installation/governance note
- deployment/version record

### Private-first rationale

Private pilot remains the default launch path because:

- private apps can be limited to a domain
- private apps are immediately available within the organization
- public publication introduces Google review and broader support obligations
- the visibility selection cannot be changed later

## Azure-native deployment topology

### Canonical model

Each tenant/environment exposes one canonical public HTTPS Odoo base URL from the Azure-native ingress layer. That canonical URL is the source of truth for `/auth_oauth/signin` redirect registration, record deep links, add-on tenant resolution, and provider-aware login guidance.

### Platform assumptions

- DNS is Azure-native
- Ingress / edge is Azure-native (Azure Front Door)
- Certificates / TLS are Azure-native
- Identity governance is Microsoft Entra-native
- Do not assume Cloudflare, registrar-managed DNS, or other third-party edge products unless explicitly documented as an exception in repo SSOT

### Odoo auth providers

Register the canonical URL with each provider using `https://<odoo-base-url>/auth_oauth/signin`.

### Google lane

- Google OAuth client configured with Odoo redirect URI
- Odoo `OAuth Authentication` enabled
- Odoo `Google Authentication` enabled
- Google Client ID configured in Odoo

### Microsoft Entra lane

- Entra app registration configured with `Web` redirect URI to `/auth_oauth/signin`
- Default internal-user mode: single-tenant
- Odoo system parameter `auth_oauth.authorization_header = 1`
- Provider-linked first login routed through Reset Password / invitation flow as documented by Odoo

### Operational policy

Support multiple auth providers per tenant, but retain one local Odoo admin/break-glass path where policy allows.

## Future Zoho Mail host lane

### Host model

Zoho Mail provides a mailbox extension model through eWidget / Developer Space and supports custom extension development and Marketplace distribution.

### Relevant extension placements

- `zoho.mail.preview.rightpanel`
- `zoho.mail.pinnedview.rightpanel`
- optional secondary placements such as preview more-actions and email-address actions

### Zoho host capabilities

Zoho's developer platform exposes: current email details, compose/reply/forward actions, attachments, contact lookup, relation data, app/config parameters, event hooks (mail preview, compose open, draft save, app visibility, mail close), and widget open/invoke flows.

### Architecture decision

Do not expand the current project into a multi-host v1. Instead: keep Gmail as the launch host, isolate Odoo action logic behind a host-neutral adapter boundary, and add Zoho Mail as a second host lane after Gmail pilot stabilization.

### Zoho implementation surface selection

For a future Zoho lane, choose the implementation surface intentionally:

- **Sigma** — if the goal is a Zoho-native extension experience
- **Flow** — if the goal is workflow/event integration between Zoho and Odoo
- **Zoho APIs** — if the goal is direct programmatic data exchange
- **Catalyst / Creator** — if auxiliary Zoho-hosted application logic is needed
- **Zoho OAuth/OIDC** — only if Zoho-side delegated access or sign-in is required for Zoho services

Do not pick Zoho tooling by brand affinity alone. Select based on the actual product role: mailbox host, workflow orchestration, backend integration, app runtime, or identity/sign-in.

## Azure PostgreSQL → Fabric analytics topology

### Canonical data flow

1. Odoo writes operational data to Azure Database for PostgreSQL (`odoo`).
2. Microsoft Fabric mirrors the PostgreSQL database into OneLake.
3. Fabric exposes:
   - mirrored Delta-backed tables
   - autogenerated SQL analytics endpoint
4. Analytics and BI workloads consume mirrored data from Fabric.

### Platform assumptions

- Source database: Azure Database for PostgreSQL Flexible Server
- Mirroring type: database mirroring
- Replication mode: near real-time
- Analytical endpoint: SQL analytics endpoint
- Downstream Microsoft-native consumption: Power BI, Fabric SQL, notebooks / Spark, cross-database query patterns

### Source-side prerequisites

The plan must account for PostgreSQL mirroring prerequisites, including:

- system-assigned managed identity enabled
- WAL level set to logical
- `azure_cdc` allowlisted and preloaded
- `max_worker_processes` increased appropriately
- mirror-capable database user/ownership model

## Fabric mirroring readiness and operating model

### Readiness checks

- Fabric capacity is active
- required Fabric tenant settings are enabled
- source server is ready for mirroring
- selected source database is approved (`odoo`)
- public/VNet/private-endpoint connectivity path is valid
- replication status reaches Running after initialization

### Operational guidance

- mirror all data unless a scoped-table exception is intentionally chosen
- treat the SQL analytics endpoint as the default read surface for lightweight analyst/SQL access
- use Fabric-native downstream tooling for BI and semantic layers

## Microsoft-native target-state topology

### Canonical split

1. Odoo writes to Azure Database for PostgreSQL (`odoo`)
2. Fabric mirrors PostgreSQL for analytics-facing access
3. Databricks consumes governed operational/analytical data for engineering, transformation, and ML-oriented workloads
4. Foundry consumes approved data/context/services for AI application, agent, and governance workflows

### Responsibilities by plane

#### Operational plane

- Odoo transactional workflows
- source-of-record PostgreSQL writes
- auth-provider and application workflows

#### Fabric plane

- mirrored PostgreSQL analytics ingress
- SQL analytics / BI-facing read access
- Microsoft-native analytics consumption

#### Databricks plane

- advanced transformations
- lakehouse / model-serving-adjacent engineering
- feature / batch / data-intelligence workloads

#### Foundry plane

- AI apps
- agents / copilots
- AI governance / orchestration / scaling

### Architecture rule

Use the lightest correct plane:

- transaction and business action → Odoo/PostgreSQL
- mirrored analytics and BI → Fabric
- engineering/ML-heavy data work → Databricks
- AI app/agent workflows → Foundry

## 7. Implementation Phases

### Phase 0 — Foundation

- finalize spec
- choose greenfield vs fork baseline
- set repo layout
- define tenant registry model
- create branding direction

### Phase 1 — Add-on shell

- manifest
- homepage trigger
- contextual trigger
- compose trigger
- card navigation scaffolding
- settings/help cards

### Phase 2 — Auth and tenant safety

- login flow
- tenant registry resolution
- session persistence
- logout/re-auth
- identity mode model

### Phase 3 — Odoo operations

- lookup/search
- create contact
- create lead
- create ticket
- create task
- link record
- chatter logging
- open-in-Odoo URLs

### Phase 4 — Hardening

- error handling
- retry behavior
- attachment policy
- observability
- privacy docs
- support docs
- marketplace copy/assets
- multitenancy/identity note

### Phase 5 — Pilot release

- private deployment
- pilot evidence
- defect remediation
- go/no-go review

## 8. Testing Strategy

### 8.1 Unit tests

- card builders
- config parsing
- tenant registry resolution
- authority validation
- request/response mapping
- error translation

### 8.2 Integration tests

- mocked Odoo adapter contract tests
- auth flow tests where feasible
- create/link/log action tests

### 8.3 Pilot smoke tests

- install add-on
- authorize
- connect to approved tenant
- create lead from Gmail
- create ticket from Gmail
- create task from Gmail
- link existing record
- log chatter with and without attachment

### 8.4 Negative-path tests

- rejected tenant domain
- expired auth
- Odoo timeout
- unsupported module
- malformed response
- attachment rejection

## 9. Deployment Plan

### Environments

- local/dev source repo
- Apps Script deployment project
- standard Google Cloud publish project
- private test deployment
- pilot deployment

### Release controls

- versioned manifest
- deployment ID tracked in docs/evidence
- tenant registry separated by environment
- no secrets in repo

### Evidence outputs

Store pilot evidence under `docs/evidence/gmail-inbox-addon/<timestamp>/`.

Include: manifest version, deployment ID, approved tenant registry snapshot, smoke test outcomes, screenshots or structured logs where allowed.

## 10. Risks and Mitigations

- **Too much runtime constraint in Apps Script** — keep shell thin and move heavy logic out.
- **Private deployment drift** — keep deployment metadata in repo and use scripted sync/push workflow.
- **Odoo tenant variability** — feature-flag operations by tenant/module availability.
- **Scope creep into admin console / analytics** — hold that for post-pilot phases.

## 11. Open Decisions

1. Greenfield implementation vs selective fork from Odoo mail plugin sources
2. Whether compose support in v1 is lookup-only or includes structured draft assist
3. Whether attachments are uploaded directly in v1 or logged as references first
4. Whether Odoo adapter is pure JSON-RPC or custom controller-based
5. Whether multi-tenant switching is in v1 or later
6. Whether Entra is only an admin/control-plane authority in v1.5+, or is introduced in v1 for pilot tenant registration
7. Canonical tenant registry backend and schema
8. Whether workload-to-Odoo calls use Entra-managed workload identity for auxiliary services
9. Whether installation is user-installable, admin-installable, or both in the pilot domain
10. Whether compose support in v1 is mandatory or can remain limited while homepage + contextual UI ship first
11. What minimum admin/security review pack is required before pilot deployment
12. Whether every tenant must support both Google and Microsoft Entra, or whether provider support remains tenant-specific
13. Whether local Odoo login remains enabled everywhere as break-glass access
14. Whether Gmail-side connect flows should display provider-aware first-login instructions based on tenant auth metadata
15. Whether Zoho Mail becomes a v1.5 second host or a separate sibling product
16. Whether Zoho-hosted deployments use Zoho OAuth directly from widget runtime or through a backend bridge
17. Which Zoho widget placements are in-scope for the first Zoho host release
18. Whether the first Zoho implementation is a Zoho Mail extension, a Flow integration, or both
19. Whether Sigma is the canonical packaging/runtime surface for a Zoho-native extension release
20. Which downstream workloads should read directly from Fabric-mirrored analytical surfaces versus curated Databricks data products
21. Whether Foundry consumes mirrored Fabric data directly, Databricks-curated products, or both
22. What the canonical contract is between the Odoo operational plane and the Foundry AI plane
