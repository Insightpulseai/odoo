# Product Requirements Document — Landing AI Assistant

## 1. Overview

The Landing AI Assistant is a public-facing product assistant embedded on InsightPulseAI landing and marketing pages.

Its purpose is to help visitors:
- understand products and product surfaces
- navigate features, capabilities, and architecture
- compare packaging and plans where publicly documented
- find docs, demos, pricing, and contact paths
- transition to the correct authenticated product surface when needed

This assistant is intentionally distinct from:
- Odoo Copilot
- analytics assistants
- document intelligence assistants
- internal/admin assistants

It is a public product-education surface, not an authenticated operational copilot.

## 2. Problem Statement

Marketing visitors need immediate, accurate, grounded answers about InsightPulseAI without being forced into a generic sales form or being misled into thinking the public assistant can access ERP or tenant data.

Current public AI patterns often fail by:
- mixing public product knowledge with authenticated product capabilities
- being unclear about where answers come from
- overstating access to customer or tenant data
- deflecting technical questions into qualification questions too early

The Landing AI Assistant must solve these problems through explicit scope, provenance, and product-surface separation.

## 3. Goals

1. Answer public product questions directly and credibly.
2. Ground answers in approved public sources.
3. Make source class visible on every substantive response.
4. Clearly disclose what the assistant can and cannot do.
5. Route users to the correct next step after answering.
6. Preserve a hard boundary between public-web assistance and authenticated product assistants.

## 4. Non-Goals

The Landing AI Assistant will not:
- access ERP or tenant data
- read authenticated Odoo records
- execute write actions
- impersonate Odoo Copilot
- manage admin settings
- provision services
- run analytics queries against private data
- review private documents
- serve as a universal cross-product authenticated copilot

## 5. Primary Users

### 5.1 Prospective buyers
Need a fast, trustworthy overview of products, capabilities, packaging, and next steps.

### 5.2 Technical evaluators
Need architecture, capability, integration, and boundary explanations before booking a demo.

### 5.3 Existing prospects in early discovery
Need to understand which surface to use:
- public product assistant
- authenticated Odoo assistant
- analytics assistant
- document intelligence assistant

## 6. Product Positioning

The Landing AI Assistant is:
- public
- read-only
- product-scoped
- docs-grounded
- citation-visible
- CTA-oriented

It is not:
- tenant-aware
- record-aware
- action-capable
- a substitute for in-product copilots

## 7. Source Policy

### 7.1 Allowed sources
- public product documentation
- public architecture pages
- public pricing and packaging pages
- public FAQ content
- public release notes
- approved public benchmark material

### 7.2 Disallowed sources
- tenant/customer data
- private Odoo records
- internal runbooks
- admin-only systems
- private support notes
- hidden telemetry
- service-account-only data
- internal sales notes

### 7.3 Source disclosure requirement
Every substantive response must visibly identify its source class, such as:
- Source: Product Docs
- Source: Architecture
- Source: Pricing
- Source: FAQ
- Source: Release Notes
- Source: Public Web

## 8. Capability Disclosure

The assistant must provide a persistent or first-use disclosure explaining its trust boundary.

### Canonical disclosure
"I'm the InsightPulseAI product assistant. I answer from approved public sources such as our docs, architecture pages, FAQs, pricing pages, and selected release content. I can't access your ERP, company data, tenant records, or perform actions from this page."

This disclosure must be stable, plain, and non-evasive.

## 9. Core User Jobs

### Job 1 — Learn what InsightPulseAI does
The user can ask broad product questions and get grounded, direct answers.

### Job 2 — Understand architecture and product surfaces
The user can understand the difference between:
- marketing assistant
- Odoo Copilot
- analytics assistants
- document intelligence assistants
- runtime/governance layers

### Job 3 — Compare packaging and plans
The user can get plan/pricing or packaging comparisons from public materials.

### Job 4 — Decide the next step
The user can move to:
- docs
- pricing
- demo
- trial
- architecture review
- authenticated product surface

## 10. Functional Requirements

### FR-1 Public product Q&A
The assistant shall answer public product questions using approved public sources only.

### FR-2 Grounding-first response generation
The assistant shall retrieve from approved public knowledge before generation.

### FR-3 Source labeling
The assistant shall display source class on every substantive response.

### FR-4 Hard no-tenant boundary
The assistant shall explicitly refuse or redirect any request that requires tenant, ERP, or authenticated workspace data.

### FR-5 Product-surface separation
The assistant shall distinguish clearly between:
- public marketing assistance
- authenticated Odoo assistance
- authenticated analytics assistance
- authenticated document assistance

### FR-6 CTA after answer
The assistant shall answer in-scope questions first, then offer the relevant CTA.

### FR-7 Technical credibility
The assistant shall answer technical product questions directly within public scope and must not default to qualification questions before answering.

### FR-8 Public-web fallback
If broader public-web retrieval is used beyond the approved public corpus, the response must explicitly label that source mode.

### FR-9 Unsupported-scope handling
If a request requires private or authenticated context, the assistant shall:
- explain that the current surface is public-only
- state what it cannot access
- route the user to the correct next step

### FR-10 Feedback capture
The assistant shall support per-response feedback capture.

## 11. UX Requirements

### UX-1 Visible trust boundary
Users must be able to understand what the assistant knows and does not know without reverse-engineering it.

### UX-2 Visible provenance
Source labeling must be visible and easy to interpret.

### UX-3 No deceptive capability framing
The UI must not imply:
- tenant access
- ERP record access
- action capability
- admin capability

### UX-4 Helpful next steps
CTAs should feel like logical next steps, not sales deflections.

## 12. Interaction Model

### 12.1 Default answer flow
1. classify query
2. retrieve from approved public sources
3. answer directly
4. label source class
5. offer relevant next step

### 12.2 Out-of-scope flow
1. identify private/authenticated need
2. state current surface limitation
3. explain what requires an authenticated assistant
4. offer correct route forward

### 12.3 Response style
Responses should be:
- direct
- technically credible
- scoped
- transparent
- non-hyped

## 13. Safety and Governance Requirements

### GOV-1 Public-only data boundary
No private or authenticated data may be queried from this surface.

### GOV-2 Separate prompts/configs
The marketing assistant must use its own system prompt/config separate from Odoo Copilot and other authenticated assistants.

### GOV-3 No capability inflation
Claims must match actual public product maturity and documented capability.

### GOV-4 No hidden mode switching
The assistant must not silently switch between docs, product memory, and public web without labeling the source class.

## 14. Metrics

### Primary success metrics
- answer helpfulness score
- citation/source-visibility rate
- CTR to docs/pricing/demo/trial
- successful route-to-surface rate
- reduction in unsupported-scope confusion

### Guardrail metrics
- false implication of tenant/ERP access
- unsupported-scope hallucination rate
- source-label omission rate
- technical-question deflection rate
- user confusion about assistant boundaries

## 15. Release Criteria

The Landing AI Assistant is release-ready when:
- the public-only boundary is enforced
- source labels are present on substantive answers
- the disclosure text is visible and stable
- technical product questions are answered directly within scope
- unsupported private-context requests are handled transparently
- CTA behavior follows answer-first, route-second logic

## 16. Out of Scope for V1

- authenticated user personalization
- tenant-aware retrieval
- Odoo record lookup
- action execution
- public upload-and-analyze workflows
- lead scoring
- autonomous outbound sales workflows
- cross-surface identity stitching

## 17. Canonical Product Rule

The Landing AI Assistant is a public, documentation-grounded product guide with explicit provenance and zero tenant access. Any authenticated, record-aware, or action-capable assistance belongs to separate product assistants.
