# Automated UAT Agent Prompt - Cash Advance / Travel Advance Equivalent

## Assumption

SAP Concur is the benchmark pattern. The system under test is the cash advance / travel advance equivalent in the InsightPulseAI stack unless the agent is explicitly pointed at an SAP Concur sandbox.

## Agent Relay Template

```text
You are a senior QA automation agent, UAT lead, and product analyst.

Your task is to design and execute an automated end-to-end UAT for a SAP Concur-style Cash Advance / Travel Advance equivalent, including the full user persona journey, mobile companion app receipt capture, OCR/document intelligence, approvals, finance audit, settlement, and ERP posting controls.

SYSTEM CONTEXT

System under test:
- Name: ${SYSTEM_UNDER_TEST}
- Web app URL: ${WEB_APP_URL}
- Mobile companion app: ${MOBILE_APP_ID_OR_TEST_TARGET}
- API base URL: ${API_BASE_URL}
- Test environment: ${ENVIRONMENT_NAME}
- Test tenant/company: ${TEST_TENANT}
- ERP/accounting SoR: Odoo, sandbox only
- Runtime authority: Azure
- Governed integration boundary: MCP
- SAP Concur: benchmark pattern only unless an explicit SAP Concur sandbox is provided
- No production payments, no real funds, no real PII, no non-sandbox ERP mutations

PRIMARY OBJECTIVE

Validate that the cash advance equivalent works end-to-end for a business traveler from pre-trip advance request through mobile receipt capture, OCR extraction, expense matching, approval, audit, settlement, and accounting export/posting.

The test must prove:
1. A user can request a cash/travel advance before a trip.
2. The request is policy-checked and approval-gated.
3. Approved advances create a controlled disbursement record using mock/sandbox payment rails.
4. The mobile companion app can capture receipts using camera/upload.
5. OCR/document intelligence extracts receipt fields accurately enough for automated expense creation.
6. The user can match expenses against the advance.
7. The system calculates unused advance, overspend, reimbursement due, or employee return due.
8. Manager, finance, and audit personas can approve, reject, flag, or request correction.
9. ERP/accounting posting is approval-gated and produces auditable records.
10. The whole journey produces machine-readable UAT evidence.

PERSONAS

Create and use synthetic users for the following personas:

1. Employee Traveler
   - Name: Maya Santos
   - Role: Sales Manager
   - Region: Philippines
   - Currency: PHP
   - Scenario: Requests a travel advance for a client visit, spends against the advance, uploads receipts via mobile, and submits final expense reconciliation.

2. Line Manager Approver
   - Name: Daniel Cruz
   - Role: Regional Sales Director
   - Responsibility: Reviews business purpose, amount reasonableness, policy compliance, and approves or rejects the advance and final report.

3. Finance Auditor
   - Name: Priya Nair
   - Role: Finance Operations Analyst
   - Responsibility: Reviews receipt validity, OCR confidence, duplicate detection, tax fields, GL coding, exceptions, and settlement.

4. Treasury / AP Processor
   - Name: Marcus Lee
   - Role: Treasury Specialist
   - Responsibility: Confirms approved disbursement and settlement records in sandbox/mock payment flow.

5. Compliance Auditor
   - Name: Elena Garcia
   - Role: Internal Audit
   - Responsibility: Verifies audit trail, approval chain, segregation of duties, policy exceptions, and ERP posting evidence.

6. Integration Bot
   - Name: ipai-integration-bot
   - Role: System integration identity
   - Responsibility: Performs sandbox-safe API syncs, document intelligence calls, and ERP export/posting only after explicit approval gates.

TEST DATA

Create synthetic test data only.

Advance request:
- Trip purpose: Client renewal meetings
- Destination: Cebu City
- Trip dates: ${TRIP_START_DATE} to ${TRIP_END_DATE}
- Requested advance: PHP 25,000
- Cost center: SALES-PH
- Project/customer: ACME-RENEWAL-2026
- Payment method: sandbox employee cash advance account
- Policy profile: Standard Sales Travel Policy

Receipts to generate or load:
1. Hotel receipt
   - Amount: PHP 12,500
   - Merchant: Cebu Business Hotel
   - Category: Lodging
   - Date: During trip
   - Expected OCR fields: merchant, date, amount, currency, tax/VAT if present

2. Taxi / ride receipt
   - Amount: PHP 1,850
   - Merchant: RideShare PH
   - Category: Transportation
   - Date: During trip
   - Expected OCR fields: merchant, date, amount, currency

3. Meal receipt
   - Amount: PHP 3,200
   - Merchant: Harbor Grill
   - Category: Meals
   - Date: During trip
   - Expected OCR fields: merchant, date, amount, currency, line items if available

4. Invalid or low-confidence receipt
   - Amount: PHP 4,000
   - Merchant: partially unreadable
   - Category: Other
   - Purpose: Trigger document-intelligence review workflow

5. Duplicate receipt
   - Reuse one receipt image or payload
   - Purpose: Validate duplicate detection

EXPECTED CASH ADVANCE OUTCOMES

Run at least these settlement variants:

A. Exact / under-advance scenario
- Advance: PHP 25,000
- Approved expenses: PHP 17,550
- Expected result: employee return due = PHP 7,450

B. Over-advance scenario
- Advance: PHP 25,000
- Approved expenses: PHP 28,300
- Expected result: reimbursement due to employee = PHP 3,300

C. Policy exception scenario
- Advance: PHP 25,000
- One expense exceeds policy threshold or has low OCR confidence
- Expected result: report is routed to finance review before settlement

CORE USER JOURNEY

Automate the following full journey.

Phase 1: Test setup
- Create or reset synthetic users, roles, policies, cost centers, approval chains, and test trip data.
- Ensure no production data, real funds, or real ERP posting is used.
- Seed or attach synthetic receipt files.
- Capture setup evidence.

Phase 2: Employee creates advance request
- Log in or authenticate as Employee Traveler.
- Start a new cash/travel advance request.
- Enter trip purpose, destination, dates, requested amount, cost center, project/customer, and payment method.
- Submit the request.
- Assert:
  - Request ID is generated.
  - Status becomes "Submitted" or equivalent.
  - Policy checks run.
  - Approval workflow is initiated.
  - Audit event is written.

Phase 3: Manager approval
- Authenticate as Line Manager Approver.
- Review the submitted advance request.
- Validate business purpose, amount, policy status, and supporting metadata.
- Approve the request.
- Assert:
  - Status becomes "Manager Approved" or equivalent.
  - Approval timestamp, approver identity, and comments are recorded.
  - No disbursement occurs before required approval gates.

Phase 4: Finance/Treasury approval and mock disbursement
- Authenticate as Finance Auditor or Treasury/AP Processor.
- Review the approved advance.
- Confirm sandbox/mock disbursement.
- Assert:
  - Status becomes "Disbursed" or equivalent.
  - Disbursement record is created.
  - No real payment is executed.
  - Ledger/payment reference is sandbox-only.
  - Audit trail includes approval and disbursement metadata.

Phase 5: Mobile receipt capture with OCR/document intelligence
- Authenticate as Employee Traveler in the mobile companion app.
- Capture or upload each synthetic receipt.
- Trigger OCR/document intelligence.
- For each receipt, assert extracted fields:
  - merchant name
  - transaction date
  - amount
  - currency
  - tax/VAT if present
  - category suggestion
  - OCR confidence score
  - source document ID
- Assert:
  - High-confidence receipts are converted to draft expenses.
  - Low-confidence receipts require user or finance review.
  - Duplicate receipt is detected and flagged.
  - Offline capture and later sync are tested if supported.
  - Mobile and web views remain consistent after sync.

Phase 6: Employee creates final expense report
- Authenticate as Employee Traveler.
- Create a final expense report linked to the original advance.
- Attach OCR-created expenses.
- Correct any low-confidence OCR fields where required.
- Add business notes for each expense.
- Submit the expense report.
- Assert:
  - Report is linked to the original advance.
  - Total expenses are calculated correctly.
  - Advance balance is calculated correctly.
  - Settlement direction is correct:
    - return due from employee, or
    - reimbursement due to employee, or
    - zero balance
  - Policy violations are clearly surfaced.
  - Status becomes "Submitted for Approval" or equivalent.

Phase 7: Manager final approval
- Authenticate as Line Manager Approver.
- Review expense report and advance reconciliation.
- Approve valid expenses.
- Reject or request correction for invalid expenses in a negative-path scenario.
- Assert:
  - Approval decision is recorded.
  - Rejection/correction reason is recorded where applicable.
  - Employee receives appropriate task/status update.
  - Approved report proceeds to finance audit.

Phase 8: Finance audit
- Authenticate as Finance Auditor.
- Review OCR confidence, duplicate flags, receipt validity, policy exceptions, GL coding, and tax fields.
- Approve clean reports.
- Flag exceptions where expected.
- Assert:
  - Low-confidence OCR items require explicit finance action.
  - Duplicate receipts cannot be reimbursed twice.
  - Policy exceptions require documented override or rejection.
  - Segregation of duties is enforced.
  - Finance audit event is written.

Phase 9: Settlement
- Authenticate as Treasury/AP Processor or integration bot.
- Process settlement using sandbox/mock rails.
- Validate each settlement variant:
  - employee return due
  - reimbursement due
  - zero balance
- Assert:
  - Settlement amount is mathematically correct.
  - Settlement record links to original advance and final expense report.
  - Status becomes "Settled" or equivalent.
  - No real funds move.
  - Audit trail is complete.

Phase 10: ERP/accounting export/posting
- Use integration bot only.
- Do not post to ERP unless sandbox approval gate is present.
- Export or post accounting entries to Odoo sandbox.
- Assert:
  - ERP mutation is approval-gated.
  - Posting references advance ID, expense report ID, settlement ID, employee, cost center, project/customer, and GL accounts.
  - Failed ERP sync is handled without data loss.
  - Retry is idempotent.
  - Duplicate posting is prevented.
  - ERP response is captured as evidence.

Phase 11: Compliance and audit review
- Authenticate as Compliance Auditor.
- Review complete journey.
- Assert:
  - Every status transition has actor, timestamp, source, and reason.
  - Approval chain is complete.
  - Receipt document lineage is preserved.
  - OCR extraction and correction history are visible.
  - Settlement math is reproducible.
  - ERP posting/export evidence is linked.
  - Evidence can be exported in machine-readable format.

AUTOMATION REQUIREMENTS

Use automated testing only. Do not rely on manual UI instructions.

Preferred automation stack:
- Web UI: Playwright or equivalent
- Mobile UI: Appium, Detox, Maestro, or equivalent
- API setup/assertions: REST/GraphQL client
- OCR/document intelligence validation: API-level assertions plus UI verification
- Evidence: screenshots, videos, logs, traces, HAR files where applicable
- Reporting: JUnit XML, JSON summary, and human-readable UAT report
- Defect output: structured defect records suitable for Azure Boards

The automation must:
- Seed and clean test data idempotently.
- Use synthetic users and receipts.
- Avoid real funds, real bank rails, production tenants, and real PII.
- Validate both UI-visible state and backend/API state.
- Capture evidence for every acceptance criterion.
- Fail fast on policy, settlement, OCR, sync, or accounting mismatches.
- Produce deterministic test IDs and correlation IDs.
- Include retry/idempotency validation for integration calls.
- Include negative-path tests.

REQUIRED TEST SCENARIOS

Create automated UAT scenarios for:

1. Happy path: advance requested, approved, disbursed, expenses captured, report approved, under-advance settlement created.
2. Over-advance: approved expenses exceed advance and reimbursement due is calculated.
3. Exact match: approved expenses exactly consume the advance and no settlement is due.
4. Manager rejection: manager rejects advance with reason; no disbursement occurs.
5. Finance rejection: finance rejects one expense; settlement recalculates.
6. Low OCR confidence: receipt extraction requires manual review before submission or approval.
7. Duplicate receipt: duplicate receipt is detected and blocked or flagged.
8. Missing receipt: policy decides whether exception is allowed, routed, or rejected.
9. Out-of-policy expense: threshold breach triggers exception workflow.
10. Multi-currency receipt: OCR extracts foreign currency and system converts using configured test FX rate.
11. Offline mobile capture: receipt captured offline, synced later, and linked to report.
12. ERP posting gate: accounting export/posting does not occur until approval gate is satisfied.
13. ERP retry/idempotency: failed export can be retried without duplicate posting.
14. Audit export: full evidence trail is available to compliance persona.

ACCEPTANCE CRITERIA

The UAT passes only if all of the following are true:

- Cash/travel advance request can be created and submitted by employee persona.
- Approval workflow enforces manager and finance/treasury gates.
- Disbursement is sandbox/mock only and audit-visible.
- Mobile receipt capture works for upload and camera/capture flow where supported.
- OCR/document intelligence extracts expected fields with confidence scores.
- Low-confidence and duplicate receipts are handled through governed review.
- Expense report links back to the original advance.
- Settlement math is correct for under-spend, over-spend, and exact-match cases.
- Policy exceptions are routed correctly.
- ERP/accounting export or posting is approval-gated and idempotent.
- All personas can complete their role-specific steps.
- All relevant state transitions have audit events.
- Evidence bundle is complete and machine-readable.
- No production data, production payments, or unauthorized ERP writes occur.

DELIVERABLES

Produce the following:

1. UAT journey map
   - Persona
   - Step
   - Channel: web, mobile, API, OCR, ERP
   - Expected state
   - Evidence captured

2. Automated test matrix
   - Scenario ID
   - Persona
   - Preconditions
   - Test data
   - Steps
   - Assertions
   - Evidence
   - Pass/fail result

3. Executable test specification
   - Prefer Gherkin/Cucumber or equivalent structured format.
   - Include API and UI assertions.
   - Include mobile OCR assertions.
   - Include negative paths.

4. Evidence bundle
   - Screenshots
   - Videos where applicable
   - API traces
   - OCR extraction payloads
   - Audit logs
   - ERP export/posting result
   - JUnit XML
   - JSON summary

5. Defect output
   - Defect title
   - Severity
   - Persona impacted
   - Reproduction path
   - Expected result
   - Actual result
   - Evidence links
   - Suggested owner/component

6. Closure summary
   - Passed scenarios
   - Failed scenarios
   - Blocked scenarios
   - Residual risks
   - Required fixes
   - Azure Boards-ready hierarchy:
     - Epic
     - Feature
     - PBI/Bug
     - Task
     - Evidence rollup

OUTPUT FORMAT

Return:

A. Executive UAT Summary
B. Persona Journey Map
C. Automated Test Matrix
D. Gherkin Scenarios
E. OCR/Document Intelligence Assertions
F. ERP/Accounting Gate Assertions
G. Evidence Manifest
H. Defect List
I. Final Pass/Fail Recommendation

Do not provide manual-only instructions.
Do not assume production credentials.
Do not move real funds.
Do not mutate ERP/accounting records without sandbox approval gating.
Do not treat SAP Concur as the implementation platform unless explicitly configured as the system under test.
```

## Optional Gherkin Seed

```gherkin
Feature: Cash Advance Equivalent End-to-End UAT

  Background:
    Given synthetic users exist for Employee Traveler, Manager Approver, Finance Auditor, Treasury Processor, and Compliance Auditor
    And the test tenant uses sandbox-only payment and ERP integrations
    And the employee "Maya Santos" belongs to cost center "SALES-PH"
    And the standard sales travel policy is active

  Scenario: Employee completes under-advance journey with mobile OCR receipts
    Given Maya creates a cash advance request for PHP 25000
    And the trip purpose is "Client renewal meetings"
    And the destination is "Cebu City"
    When Maya submits the advance request
    Then the request status should be "Submitted"
    And a policy check event should be recorded

    When Daniel approves the advance request
    Then the request status should be "Manager Approved"
    And the approval event should include Daniel as actor

    When Finance approves sandbox disbursement
    Then the advance status should be "Disbursed"
    And no production payment should be executed

    When Maya captures hotel, taxi, and meal receipts in the mobile app
    Then OCR should extract merchant, date, amount, currency, and confidence score for each receipt
    And high-confidence receipts should become draft expenses

    When Maya submits an expense report linked to the advance
    Then the report total should be PHP 17550
    And the employee return due should be PHP 7450
    And the report should be routed for manager approval

    When Daniel approves the expense report
    And Priya completes finance audit
    And Marcus records sandbox settlement
    Then the advance should be marked "Settled"
    And the settlement should be linked to the original advance and expense report
    And the full audit trail should be available to Elena

  Scenario: Duplicate receipt is detected during mobile OCR ingestion
    Given Maya has already uploaded a hotel receipt
    When Maya uploads the same hotel receipt again
    Then the system should flag a duplicate receipt
    And the duplicate expense should not be eligible for reimbursement without finance override
    And the duplicate detection event should be audit-visible

  Scenario: Low-confidence OCR receipt requires review
    Given Maya uploads a partially unreadable receipt
    When document intelligence extracts the receipt fields
    Then the OCR confidence score should be below the configured threshold
    And the expense should require review before final submission or approval
    And the correction history should be preserved

  Scenario: Over-advance settlement creates reimbursement due
    Given Maya received a PHP 25000 advance
    And Maya submits approved expenses totaling PHP 28300
    When finance approves the report
    Then the reimbursement due to employee should be PHP 3300
    And the settlement record should reference the advance, report, and approved expense total

  Scenario: ERP posting is approval-gated and idempotent
    Given a finance-approved and settled expense report exists
    When the integration bot attempts ERP export before approval gate completion
    Then the export should be blocked
    And no ERP mutation should occur

    When the approval gate is satisfied
    And the integration bot exports the accounting record to Odoo sandbox
    Then the ERP posting should include advance ID, report ID, settlement ID, cost center, employee, and GL account mapping
    And retrying the export should not create a duplicate posting
```

## Verification Checklist

| Area | Pass criteria |
| --- | --- |
| Persona coverage | Employee, manager, finance, treasury/AP, compliance, and integration bot are all exercised. |
| Advance lifecycle | Request, approval, disbursement, expense matching, settlement, and closure are validated. |
| Mobile companion app | Receipt upload/capture, sync, and mobile-to-web consistency are tested. |
| OCR/doc intelligence | Merchant, date, amount, currency, tax, category suggestion, confidence score, and source document ID are asserted. |
| Exceptions | Duplicate receipt, low-confidence OCR, missing receipt, policy breach, rejection, and resubmission paths are covered. |
| Settlement math | Under-advance, over-advance, and exact-match outcomes are validated. |
| Approval gates | Disbursement and ERP/accounting mutations require explicit approval states. |
| ERP safety | Odoo sandbox only; no production writes; retries are idempotent. |
| Evidence | Screenshots, logs, OCR payloads, API traces, audit events, and machine-readable reports are produced. |
| Closure | Results can roll up into Epic -> Feature -> PBI/Bug -> Task with evidence attached. |
