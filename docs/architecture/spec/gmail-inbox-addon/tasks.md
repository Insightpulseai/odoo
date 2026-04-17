# Tasks — InsightPulse Inbox for Odoo

## 1. Task Rules

- Status values: `todo`, `in_progress`, `blocked`, `done`
- Priority values: `P0`, `P1`, `P2`
- Each task must produce a visible artifact, code change, or validation result.
- No task is complete without acceptance evidence.

---

## 2. Phase 0 — Spec and structure

### T-001 — Create spec bundle

- Status: done
- Priority: P0
- Output: `spec/gmail-inbox-addon/constitution.md`, `prd.md`, `plan.md`, `tasks.md`
- Acceptance: all four files exist, slug and product naming are consistent

### T-002 — Create project subtree

- Status: in_progress
- Priority: P0
- Output: `apps/gmail-inbox-addon/` (or evolve from `web/apps/gmail-odoo-addon/`)
- Acceptance: repo layout exists, no ambiguous placeholder paths remain

### T-003 — Decide greenfield vs fork baseline

- Status: done
- Priority: P0
- Output: greenfield Apps Script implementation. Existing prototype at `web/apps/gmail-odoo-addon/` serves as Phase 1 baseline.
- Acceptance: decision recorded, no upstream Odoo mail-client-extensions code reused

---

## 3. Phase 1 — Add-on shell

### T-010 — Implement common homepage trigger

- Status: done
- Priority: P0
- Acceptance: homepage loads in Gmail, unauthenticated and authenticated states both render

### T-011 — Implement Gmail contextual trigger

- Status: done
- Priority: P0
- Acceptance: opening a Gmail message displays the contextual card

### T-012 — Implement compose trigger

- Status: todo
- Priority: P1
- Acceptance: add-on appears in compose UI, at least one compose-side action is functional

### T-013 — Implement card navigation scaffolding

- Status: done
- Priority: P0
- Acceptance: cards can push/pop cleanly, errors return recoverable navigation states

---

## 4. Phase 2 — Auth, registry, and tenant safety

### T-020 — Implement config model

- Status: done
- Priority: P0
- Acceptance: approved tenants are loaded from a clear source of truth, non-approved domains fail closed

### T-021 — Implement login flow

- Status: done
- Priority: P0
- Acceptance: pilot user can authenticate successfully, expired sessions surface a clean re-auth path

### T-022 — Implement tenant allowlist validator

- Status: todo
- Priority: P0
- Acceptance: approved tenant passes, unapproved tenant fails, malformed URL fails

### T-023 — Implement connection status card

- Status: todo
- Priority: P1
- Acceptance: user can see active tenant and connection state, logout/reset action exists

### T-024 — Define tenant registry schema

- Status: todo
- Priority: P0
- Output: tenant schema/types, registry resolution rules
- Acceptance: application tenant ID is distinct from any Entra tenant/directory identifier, Odoo URL, capabilities, and identity mode are first-class fields

### T-025 — Define identity mode matrix

- Status: todo
- Priority: P0
- Output: supported identity modes document
- Acceptance: native Odoo auth and Entra-governed mode are explicitly modeled, fallback behavior is documented

### T-026 — Add authority/issuer validation model

- Status: todo
- Priority: P1
- Acceptance: issuer metadata is validated separately from Odoo tenant URL

### T-027 — Define Odoo auth provider schema

- Status: todo
- Priority: P0
- Output: tenant auth-provider fields in schema/types
- Acceptance: tenant can declare `local_odoo`, `google_oauth`, and `microsoft_entra_oauth`. Canonical Odoo base URL is stored for provider redirect registration.

### T-028 — Write self-hosted Odoo auth-provider architecture note

- Status: todo
- Priority: P0
- Output: `docs/architecture/odoo-auth-providers.md`
- Acceptance: clearly separates mailbox plugins from Odoo login providers, documents Google and Microsoft Entra setup assumptions for self-hosted Azure

### T-029 — Add provider-aware connect UX requirements

- Status: todo
- Priority: P1
- Output: UX notes / flow definitions
- Acceptance: Gmail-side flows do not assume Gmail identity equals Odoo auth identity

---

## 5. Phase 3 — Odoo adapter

### T-030A — Write Azure-native ingress and URL authority note

- Status: todo
- Priority: P0
- Output: `docs/architecture/azure-native-ingress.md`
- Acceptance: defines canonical public Odoo URL authority, separates Azure-native ingress/DNS from mailbox-host concerns, documents how tenant URL metadata is derived per environment

### T-030B — Add Azure-native tenant URL metadata rules

- Status: todo
- Priority: P0
- Output: tenant schema update or note
- Acceptance: canonical URL is explicitly sourced from Azure-native infrastructure, OAuth redirect / deep-link / validation paths all use the same authority

### T-030 — Define Odoo adapter contract

- Status: done
- Priority: P0
- Acceptance: search, create, link, and chatter-log methods have stable contracts

### T-031 — Implement contact/company lookup

- Status: done
- Priority: P0
- Acceptance: sender-based lookup returns candidate matches, manual search fallback works

### T-032 — Implement create contact

- Status: todo
- Priority: P0
- Acceptance: contact can be created from current message context

### T-033 — Implement create lead/opportunity

- Status: done
- Priority: P0
- Acceptance: lead can be created from Gmail, success result shows open-in-Odoo link

### T-034 — Implement create helpdesk ticket

- Status: done
- Priority: P0
- Acceptance: ticket can be created from Gmail, unsupported-module state is handled cleanly

### T-035 — Implement create project task

- Status: todo
- Priority: P0
- Acceptance: task can be created from Gmail, target project/task defaults are handled sensibly

### T-036 — Implement link existing record

- Status: todo
- Priority: P0
- Acceptance: message can be linked to existing record without duplicate creation

### T-037 — Implement chatter logging

- Status: done
- Priority: P0
- Acceptance: user can choose what to send, chatter entry is created as expected

### T-038 — Implement attachment handling policy

- Status: todo
- Priority: P1
- Acceptance: supported path documented, oversized or unsupported cases fail clearly

---

## 6. Phase 4 — Hardening and docs

### T-040 — Add structured error handling

- Status: todo
- Priority: P0
- Acceptance: auth, tenant, Odoo, and validation failures are user-readable

### T-041 — Add unit tests

- Status: todo
- Priority: P0
- Acceptance: key modules have baseline coverage, tests run cleanly

### T-042 — Add integration contract tests

- Status: todo
- Priority: P1
- Acceptance: search/create/link/log flows validate against stable payloads

### T-043 — Write Marketplace listing copy

- Status: todo
- Priority: P0
- Output: `docs/marketplace-listing.md`
- Acceptance: title, summary, overview, permissions rationale, support copy exist

### T-044 — Write privacy and support docs

- Status: todo
- Priority: P0
- Output: `docs/privacy.md`, `docs/support.md`
- Acceptance: docs match actual data flows, docs are brand-clean and pilot-ready

### T-045 — Create brand assets

- Status: todo
- Priority: P1
- Acceptance: no Odoo SA brand reuse, icon works at small Gmail sizes

### T-046 — Write multitenancy and identity architecture note

- Status: todo
- Priority: P0
- Output: `docs/architecture/multitenancy-identity.md`
- Acceptance: clearly distinguishes Gmail runtime user, application tenant, and Microsoft Entra tenant

### T-047 — Create Marketplace release pack

- Status: todo
- Priority: P0
- Acceptance: pack is complete enough for private Marketplace publication

### T-048 — Create standard Google Cloud publish project plan

- Status: todo
- Priority: P0
- Acceptance: plan explicitly avoids using the default Apps Script project for publication

### T-049 — Write admin install/governance note

- Status: todo
- Priority: P0
- Output: `docs/admin-install-governance.md`
- Acceptance: explains audience, visibility choice, install model, permissions summary, and support path

---

## 7. Phase 5 — Pilot deployment

### T-050 — Create private deployment

- Status: in_progress
- Priority: P0
- Notes: Script ID `1QaH14jbBl7PcvjLXgkzZogh6SzqS_kXoTJ_MzzmavW6CRLMANG24Ko4q`, GCP Project `916601142061` (w9-studios-integration), current deployment v1.2 @4
- Acceptance: add-on is installable by pilot users, deployment ID/version recorded

### T-051 — Run smoke tests

- Status: todo
- Priority: P0
- Acceptance: create lead, ticket, task, and link flows each pass at least once

### T-052 — Capture evidence pack

- Status: todo
- Priority: P0
- Output: `docs/evidence/gmail-inbox-addon/<timestamp>/`
- Acceptance: manifest version recorded, tenant list snapshot recorded, smoke results recorded

### T-053 — Pilot go/no-go review

- Status: todo
- Priority: P0
- Acceptance: open defects triaged, decision taken on wider private rollout

### T-054 — Record release visibility decision

- Status: todo
- Priority: P0
- Acceptance: explicitly records private vs public rationale, notes that visibility selection is not changeable later

### T-055 — Validate Google OAuth against self-hosted Odoo base URL

- Status: todo
- Priority: P0
- Acceptance: Google OAuth redirect and Odoo login succeed using the canonical public base URL

### T-056 — Validate Microsoft Entra OAuth against self-hosted Odoo base URL

- Status: todo
- Priority: P0
- Acceptance: Entra redirect and Odoo login succeed using the canonical public base URL, first-login linking behavior is documented for pilot users

---

### T-057 — Write host-channels and Zoho lanes architecture note

- Status: todo
- Priority: P1
- Output: `docs/architecture/host-channels.md`, `docs/architecture/zoho-lanes.md`
- Acceptance: distinguishes Gmail host from future Zoho host, separates Zoho Mail host / Zoho tooling / Zoho OAuth-OIDC roles

### T-058 — Define Zoho capability matrix

- Status: todo
- Priority: P1
- Output: matrix for `sigma`, `flow`, `creator`, `catalyst`, `apis`, `oauth`, `oidc`
- Acceptance: identifies which Zoho capability is appropriate for mailbox host, workflow, backend, and identity use cases

### T-059 — Define Zoho Mail widget placement strategy

- Status: todo
- Priority: P2
- Output: placement note for `zoho.mail.preview.rightpanel`, `zoho.mail.pinnedview.rightpanel`, and related locations
- Acceptance: primary initial location selected

### T-060 — Define Zoho auth usage model

- Status: todo
- Priority: P2
- Output: note describing where Zoho OAuth or OIDC is used
- Acceptance: clearly separates Zoho service access from Odoo auth-provider configuration

### T-061 — Prototype host-neutral action adapter

- Status: todo
- Priority: P2
- Output: interface stub showing Gmail host and future Zoho host calling the same Odoo action layer
- Acceptance: create/link/log flows can be reused without host-specific rewrites

---

## 7.X Fabric mirroring and analytics

### T-062 — Write Fabric mirroring architecture note

- Status: todo
- Priority: P0
- Output:
  - `docs/architecture/fabric-mirroring.md`
- Acceptance:
  - defines Azure PostgreSQL `odoo` as operational source
  - defines Fabric mirrored database as canonical analytics ingress
  - documents OneLake + SQL analytics endpoint consumption model

### T-063 — Add mirrored-database metadata to tenant schema

- Status: todo
- Priority: P0
- Output:
  - tenant schema or metadata note
- Acceptance:
  - captures source server, source DB (`odoo`), mirror item name, readiness/status, workspace/capacity reference

### T-064 — Document PostgreSQL mirroring prerequisites

- Status: todo
- Priority: P0
- Output:
  - prerequisite note or checklist
- Acceptance:
  - includes SAMI, `wal_level=logical`, `azure_cdc`, `max_worker_processes`, and role/ownership requirements

### T-065 — Validate Fabric mirroring for `odoo`

- Status: todo
- Priority: P0
- Output:
  - smoke result / evidence note
- Acceptance:
  - `odoo` is selectable as allowed database
  - mirror enters Running state
  - initial refresh completes
  - SQL analytics endpoint becomes queryable

### T-066 — Define analytics read-path policy

- Status: todo
- Priority: P1
- Output:
  - policy note
- Acceptance:
  - default read path for analytics is Fabric mirrored data
  - exceptions for direct PostgreSQL reads are explicitly documented

### T-067 — Write Microsoft-native data-planes architecture note

- Status: todo
- Priority: P0
- Output:
  - `docs/architecture/data-planes.md`
- Acceptance:
  - distinguishes Odoo/PostgreSQL operational plane, Fabric analytics plane, Databricks data-intelligence plane, and Foundry AI plane

### T-068 — Write Foundry AI plane architecture note

- Status: todo
- Priority: P0
- Output:
  - `docs/architecture/foundry-ai-plane.md`
- Acceptance:
  - defines Foundry's role in AI app/agent/governance/scaling workflows
  - separates it from Databricks and Fabric responsibilities

### T-069 — Define cross-plane read/write policy

- Status: todo
- Priority: P0
- Output:
  - policy note
- Acceptance:
  - operational writes stay in Odoo/PostgreSQL
  - analytical reads default to Fabric where sufficient
  - engineering/ML workloads are routed to Databricks
  - AI runtime/orchestration is routed to Foundry

### T-070 — Define data-product handoff model

- Status: todo
- Priority: P1
- Output:
  - handoff note between Fabric, Databricks, and Foundry
- Acceptance:
  - documents when Fabric-mirrored data is enough
  - documents when Databricks-curated outputs are required
  - documents what inputs Foundry is allowed to consume

---

## 7.W Entra MCP Server

### T-074 — Provision Microsoft MCP Server for Enterprise in tenant

- Status: todo
- Priority: P0
- Output: tenant provisioning confirmed
- Acceptance: `Grant-EntraBetaMCPServerPermission` completes, VS Code MCP extension connects, tenant queries return data

### T-075 — Write Entra MCP Server skill contract

- Status: done
- Priority: P0
- Output: `agents/skills/entra-mcp-server/SKILL.md`
- Acceptance: covers setup, tools, query categories, auth model, integration points

### T-076 — Validate Entra MCP queries for IPAI use cases

- Status: todo
- Priority: P0
- Output: smoke results for user audit, app registration list, sign-in logs, Conditional Access review
- Acceptance: at least 4 query categories return valid results against the tenant

### T-077 — Register custom MCP client for Claude Code

- Status: todo
- Priority: P1
- Output: MCP client app registration with MCP.* scopes
- Acceptance: Claude Code can query Entra tenant data via the MCP server

---

## 7.Y Wix headless lane

### T-071 — Write Wix headless lane architecture note

- Status: todo
- Priority: P1
- Output: `docs/architecture/wix-headless-lane.md`
- Acceptance: classifies Wix as an experience/business-solution lane, separates self-managed vs wix-managed modes, preserves Azure-native/Odoo baseline

### T-072 — Define Wix capability matrix

- Status: todo
- Priority: P1
- Output: capability matrix for bookings, events, contacts, stores, pricing plans, blog, groups, inbox, loyalty, marketing tags
- Acceptance: records which capabilities are candidates for adoption, identifies whether each stays isolated to experience layer or needs Odoo synchronization

### T-073 — Define Wix-to-Odoo contract

- Status: todo
- Priority: P1
- Output: interface/policy note
- Acceptance: specifies which records stay authoritative in Wix and which must synchronize into Odoo

---

## 8. Backlog / Post-v1

### T-100 — AI-assisted summary

- Status: todo
- Priority: P2

### T-101 — Suggested record type classification

- Status: todo
- Priority: P2

### T-102 — Multi-tenant account switching

- Status: todo
- Priority: P2

### T-103 — Admin visibility/reporting

- Status: todo
- Priority: P2

### T-104 — Public Marketplace readiness assessment

- Status: todo
- Priority: P2
