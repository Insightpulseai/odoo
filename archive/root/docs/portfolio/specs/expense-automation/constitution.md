# Expense Automation — Constitution

## Purpose

Automate expense claim processing from submission through approval and posting using Odoo CE + n8n + AWS Textract OCR.

## Non-Negotiables

### 1. Use CE-Native Modules Only
- **Rule**: `hr_expense` is a CE module - no Enterprise required
- **Verification**: Module installed via `./scripts/odoo/install-ce-apps.sh`

### 2. OCR Must Be Async
- **Rule**: Receipt processing happens in background via n8n
- **Rationale**: Don't block user submission on OCR completion
- **Flow**: Upload → Queue → Textract → Update expense

### 3. Approval Thresholds Must Be Configurable
- **Rule**: Amount thresholds stored in Odoo configuration
- **Default thresholds**:
  - < $100: Auto-approve
  - $100-500: Manager approval
  - $500-5000: Director approval
  - > $5000: VP approval

### 4. Audit Trail Required
- **Rule**: All expense state changes logged
- **Fields**: Who, when, what changed, approval notes

### 5. Notification Delivery
- **Rule**: Mattermost as primary, email as fallback
- **Events**: Submitted, approved, rejected, payment processed

## Boundaries

### In Scope
- Odoo hr_expense configuration
- n8n workflow for OCR and routing
- AWS Textract integration
- Mattermost notifications
- Manager approval chain

### Out of Scope
- Corporate credit card integration (Phase 2)
- Mileage tracking (Phase 2)
- Multi-currency conversion (Phase 2)

## Success Criteria

| Metric | Target |
|--------|--------|
| OCR accuracy | > 90% |
| Avg processing time | < 24 hours |
| Auto-approval rate | > 30% |
| User satisfaction | > 4/5 |

## Cost Constraints

| Component | Monthly Cost |
|-----------|--------------|
| Odoo hr_expense | $0 |
| n8n Community | $0 |
| AWS Textract | ~$50 (est 33k receipts) |
| **Total** | **~$50** |
