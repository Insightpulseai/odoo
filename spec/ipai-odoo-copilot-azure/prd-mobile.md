# Product Requirements Document: Odoo Copilot Mobile

## Document Status
Draft

## Product Summary
Odoo Copilot Mobile is a mobile-first travel, expense, invoice, and approvals product for Odoo-centered organizations. It is designed as a superior alternative to the current SAP Concur mobile experience by unifying receipt capture, trip management, mileage, AP intake, approvals, policy guidance, and AI-assisted operational actions behind a single Odoo-native copilot surface.

## Background
The reference product positions its mobile app as a tool to create and submit expense reports, manage travel, and approve invoices from a phone. It also layers in ExpenseIt for receipt-photo-based expense creation and AI hotel-bill itemization, TripIt Pro for itinerary organization and travel alerts, and Drive for automatic mileage capture. It connects those experiences back to Concur Expense, Concur Travel, and Concur Invoice.

This creates a strong baseline, but the experience is still product-fragmented:
- receipt capture is a separate branded capability,
- itinerary intelligence is a separate app experience,
- mileage is another separate product surface,
- invoice and expense actions are adjacent rather than fully unified,
- and the system is not centered on an Odoo-native operational authority.

Odoo Copilot Mobile should reverse this by making mobile travel-and-spend operations feel like a single governed assistant rather than a collection of modules.

## Problem Statement
Mobile travel and expense products are still too workflow-fragmented for finance-heavy organizations. Users need one coherent mobile experience that can:

- capture spend evidence at the moment it occurs,
- understand policy and route exceptions immediately,
- sync against the ERP system of record in real time,
- support both employee and finance operator workflows,
- and reduce the gap between "I captured something" and "the business has a valid, reviewable accounting object."

## Goals
1. Make mobile the fastest path from receipt/trip/event to valid Odoo transaction state.
2. Unify expense, travel, invoice, mileage, and approvals into one copilot surface.
3. Reduce manual data entry through OCR, extraction, and policy-aware autofill.
4. Give approvers and finance teams a full mobile command surface, not just lightweight approvals.
5. Support high-integrity finance workflows for expense liquidation, reimbursement, AP intake, and reconciliation follow-up.
6. Preserve auditability, evidence, and exception handling from the first mobile interaction.

## Non-Goals
- Recreating consumer travel booking as the primary product focus.
- Replacing Odoo as the transactional source of truth.
- Launching separate mobile apps for receipts, travel, mileage, and invoice approvals.
- Building a generic chatbot disconnected from structured Odoo actions.
- Making Microsoft, SAP, or third-party assistant surfaces the primary user experience.

## Target Users
### Primary Users
- Traveling employees
- Managers and approvers
- Finance operations staff
- AP reviewers
- Controllers

### Secondary Users
- Travel coordinators
- Compliance reviewers
- Internal auditors
- Treasury / cash-advance administrators

## User Personas
### 1. Traveling Employee
Needs to capture receipts, mileage, and trip context immediately with minimal friction.

### 2. Approver / Line Manager
Needs fast, explainable mobile approvals with policy flags and clear recommendations.

### 3. Finance Operations Analyst
Needs to review extracted data, fix exceptions, and move transactions into valid accounting state.

### 4. Controller / Compliance Reviewer
Needs audit trails, anomaly flags, policy evidence, and mobile visibility into unresolved items.

## Jobs To Be Done
- When I receive a receipt, I want to scan it once and have a draft transaction created automatically.
- When I travel, I want my itinerary, expenses, mileage, and approvals to stay in one timeline.
- When I approve spend, I want the app to tell me what matters, what violates policy, and what action is safe.
- When I am in finance, I want mobile review tools that are operationally real, not just "approve/reject."
- When a document is unclear or policy-sensitive, I want the system to escalate with evidence rather than silently guess.

## Product Principles
1. **One surface, many skills** — no product fragmentation.
2. **Odoo-first authority** — every state-changing action lands in Odoo.
3. **Capture once** — reuse extracted evidence everywhere.
4. **Explain before act** — every recommendation must be reviewable.
5. **Mobile-native finance** — not a shrunk desktop UI.
6. **Evidence-preserving by default** — every key action has traceable artifacts.
7. **Offline-tolerant** — capture should not fail because connectivity is poor.

## Core User Experience
Odoo Copilot Mobile opens to a single home surface with five top-level operational modes:

1. **Capture**
   - Scan receipt
   - Scan invoice
   - Add mileage
   - Add cash expense
   - Add per diem / trip expense

2. **Trips**
   - Upcoming trips
   - Timeline of travel events and related spend
   - Travel alerts
   - Missing receipt / open action prompts

3. **Inbox**
   - Approval tasks
   - Exception tasks
   - Finance review items
   - Policy warnings
   - Escalations

4. **Ask Copilot**
   - "Create a draft expense from this receipt"
   - "What is missing from this hotel bill?"
   - "Can I approve this?"
   - "Show unmatched travel expenses for this trip"
   - "Why was this invoice flagged?"

5. **Me / Team**
   - My expenses
   - My approvals
   - My liquidation cases
   - Team pending items
   - Mobile policy/help

## Functional Requirements

### FR-1: Unified Mobile Capture
The app must allow users to capture receipts with camera input, upload PDFs/images, capture supplier invoices, record mileage, create manual cash entries, attach trip context to captured documents, and continue capture offline for later sync.

### FR-2: OCR and Document Intelligence
The app must extract merchant, date, currency, totals, taxes, line items, and payment clues from receipts and invoices, support complex hotel-bill itemization, identify missing or low-confidence fields, classify document type before routing, and preserve original image/PDF artifacts.

### FR-3: Odoo Draft Object Creation
The app must create structured drafts in Odoo for expense lines, expense reports, liquidation lines, vendor bill drafts, mileage claims, and approval tasks. No mobile workflow may end at "chat answer only" when the user intent is operational.

### FR-4: Trip-Centered Timeline
The app must provide a trip timeline that merges itinerary data, related expenses, mileage, per diem, approvals, exceptions, and missing evidence prompts.

### FR-5: Automatic Mileage Capture
The app must support automatic and manual mileage capture with route trace, trip labeling, business/personal separation, policy-aware reimbursement computation, and manager-review visibility.

### FR-6: Approval Workspace
Managers and finance approvers must be able to approve, reject, request changes, push to review queue, view extracted evidence, see policy flags, see copilot rationale, and act on batches where safe.

### FR-7: Policy Guard
The app must enforce and explain policies for missing receipts, duplicate submissions, out-of-policy merchants, spend caps, per diem violations, mileage anomalies, weekend/holiday exceptions, cash advance liquidation status, and tax/compliance completeness.

### FR-8: Expense Liquidation
The app must support cash advance issuance visibility, liquidation progress, receipt-to-advance matching, remaining balance computation, settlement recommendations, and escalation when supporting evidence is incomplete.

### FR-9: AP Intake and Invoice Approval
The app must support supplier invoice capture, OCR-based invoice extraction, duplicate invoice checks, mobile coding/review workflows, approval routing, and exception handling for missing PO/vendor/matching data.

### FR-10: Copilot Interaction Model
The app must provide a copilot interface that can answer questions grounded in current user/task context, recommend next actions, draft objects in Odoo, explain flags and policies, summarize a trip, report, or invoice state, and hand off to a human workflow when confidence is low.

### FR-11: Offline and Intermittent Connectivity
The app must cache recent tasks and active trips, support capture while offline, queue uploads/actions, show sync state clearly, and prevent duplicate posting on reconnect.

### FR-12: Auditability and Evidence
The system must log original uploaded artifacts, extraction outputs, user edits, approval actions, policy flags, copilot recommendations, final posted object linkage, and exception/escalation history.

### FR-13: Role-Based Experience
The app must tailor actions, fields, and home priorities by role: employee, approver, finance operator, controller, admin.

### FR-14: Global and Compliance Basics
The app must support multi-currency capture, tax field extraction, country-aware policy overlays, localization-ready field formats, and compliance evidence retention.

## Experience Requirements

### EX-1: Time to Draft
A standard receipt should become a reviewable draft in under 10 seconds after successful image capture on a normal connection.

### EX-2: One-Handed Use
Core capture, approve, and explain flows must be operable with one hand on a modern smartphone.

### EX-3: Explainability
Every high-risk recommendation must include why it was flagged, what evidence was used, what fields are uncertain, and what action is recommended.

### EX-4: Low-Fragility UX
The user must not need to know whether a task is "expense," "invoice," "travel," or "mileage" before starting. The system should classify and route where possible.

## Data Requirements
The product must maintain user identity and role context, company/entity context, trip records, receipt/invoice artifacts, extraction outputs, Odoo object references, approval states, policy outcomes, mileage traces, audit logs, and sync status.

## Integration Requirements
### Required Integrations
- Odoo models and workflows
- Document extraction/OCR service (Azure Document Intelligence)
- Notifications and email
- Optional calendar/itinerary sources
- Optional corporate card feeds
- Optional map/location services for mileage

### Optional Integrations
- Microsoft 365 channels
- Travel booking feeds
- Messaging channels
- Identity providers (Entra ID)
- Bank/card connectors

## Success Metrics
### Adoption
- % of active travelers using mobile capture
- % of managers using mobile approvals
- % of AP items first touched on mobile

### Efficiency
- Median time from capture to Odoo draft
- Median time from submission to approval
- Reduction in manual field entry per transaction
- Reduction in finance touch time for standard receipts/invoices

### Quality
- OCR extraction accuracy
- % of reports submitted without finance rework
- Duplicate detection rate
- Policy-violation detection precision
- Approval reversal rate

### Financial / Control
- Faster liquidation completion time
- Reduced missing-receipt rate
- Reduced reimbursement cycle time
- Reduced unclassified spend
- Improved audit evidence completeness

## Release Scope

### MVP
- Receipt capture
- Invoice capture
- OCR extraction
- Draft expense creation in Odoo
- Mobile approvals
- Policy flags
- Basic mileage capture
- Trip timeline
- Copilot Q&A on current item
- Audit trail

### Post-MVP
- Advanced hotel folio itemization
- Cash advance liquidation workspace
- Offline-first sync hardening
- AP coding recommendations
- Per diem automation
- Team dashboard
- Anomaly detection
- Trip disruption intelligence
- Finance operator bulk actions

### Future
- Predictive missing-receipt prompts
- Real-time card-to-receipt matching
- Traveler safety and compliance overlays
- Voice-first capture
- Conversational bulk review for finance teams

## Risks
- OCR quality variance across document types and countries
- Over-automation without sufficient review controls
- Offline sync conflicts
- User distrust if copilot explanations are weak
- Policy drift across entities/business units
- Feature sprawl if travel, expense, and AP are not kept under one coherent model

## Open Questions
1. Should travel booking live inside the app, or remain adapter-based?
2. Which itinerary sources are in scope for MVP?
3. Should mileage auto-capture be opt-in per trip or always available?
4. What is the canonical policy engine surface: Odoo-native, external rules service, or hybrid?
5. Which approval actions are safe for batch mobile execution on day one?
6. Which countries/entities are first-wave launch targets?

## Launch Recommendation
Build this as **one Odoo-native mobile product** with copilot as the interaction layer, not as separate receipt/travel/mileage apps.

The improved differentiation over the reference product is:
- one coherent mobile operating surface,
- tighter ERP authority through Odoo,
- stronger finance-control and liquidation workflows,
- better explainability,
- and a less fragmented experience than separate add-ons for receipts, itineraries, and mileage.
