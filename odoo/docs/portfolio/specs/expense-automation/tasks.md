# Expense Automation — Task Checklist

## Day 1-2: Odoo Configuration

### Module Installation
- [ ] Install `hr_expense` module in Odoo
- [ ] Install `hr` module (dependency)
- [ ] Install `account` module (for posting)
- [ ] Verify modules show as "Installed"

### Basic Configuration
- [ ] Create expense categories:
  - [ ] Travel - Airfare
  - [ ] Travel - Lodging
  - [ ] Travel - Ground Transport
  - [ ] Meals - Client
  - [ ] Meals - Team
  - [ ] Office Supplies
  - [ ] Software & Tools
  - [ ] Training & Education
  - [ ] Other
- [ ] Create expense products (linked to accounts)
- [ ] Configure expense journals
- [ ] Set up manager hierarchy in Employees

### Approval Workflow
- [ ] Enable approval for expenses > $0 (Settings → HR → Expense Approval)
- [ ] Configure approval by manager (hierarchy)
- [ ] Add custom approval rules via automation rules:
  - [ ] Rule: If amount < $100 → Auto-approve
  - [ ] Rule: If amount $100-500 → Require manager
  - [ ] Rule: If amount > $500 → Require manager + director

### Cost Centers
- [ ] Create analytic accounts for cost centers
- [ ] Link to departments
- [ ] Configure default cost center per employee

## Week 1: n8n Integration

### Workflow Setup
- [ ] Install n8n (Docker or npm)
- [ ] Configure n8n to access Odoo API
- [ ] Create webhook for expense submission
- [ ] Test Odoo → n8n connection

### OCR Pipeline
- [ ] Create AWS account (if needed)
- [ ] Set up IAM role for Textract
- [ ] Configure AWS credentials in n8n
- [ ] Build OCR workflow:
  - [ ] Receive receipt image
  - [ ] Upload to S3 (temp)
  - [ ] Call Textract AnalyzeExpense
  - [ ] Parse response for: amount, date, vendor, category
  - [ ] Update Odoo expense via API
  - [ ] Delete temp S3 file

### Notification Workflow
- [ ] Configure Mattermost webhook
- [ ] Build notification workflow:
  - [ ] On expense submit → Notify manager
  - [ ] On expense approve → Notify employee
  - [ ] On expense reject → Notify employee with reason
- [ ] Add email fallback for offline users

### Routing Logic
- [ ] Implement threshold routing:
  - [ ] Get expense amount from Odoo
  - [ ] Determine approver based on thresholds
  - [ ] Assign to correct approver in Odoo
  - [ ] Send notification to approver

## Week 2: Testing & Documentation

### End-to-End Testing
- [ ] Test Case 1: Small expense ($50) - auto-approve
- [ ] Test Case 2: Medium expense ($250) - manager approval
- [ ] Test Case 3: Large expense ($1000) - director approval
- [ ] Test Case 4: OCR receipt upload - auto-fill
- [ ] Test Case 5: Rejection with notes
- [ ] Test Case 6: Re-submission after rejection

### OCR Quality Testing
- [ ] Test with clear receipts
- [ ] Test with poor quality images
- [ ] Test with multi-line receipts
- [ ] Verify extraction accuracy > 90%

### Integration Testing
- [ ] Verify Mattermost notifications arrive
- [ ] Verify email fallback works
- [ ] Verify accounting journal entries post correctly
- [ ] Verify audit trail complete

### Documentation
- [ ] User guide: How to submit expenses
- [ ] Manager guide: How to approve expenses
- [ ] Admin guide: Configuration settings
- [ ] Troubleshooting: Common issues

## Verification

### Day 2 Checkpoint
- [ ] hr_expense module installed and configured
- [ ] Expense categories created
- [ ] Approval workflow enabled
- [ ] Can submit test expense in Odoo

### Week 1 Checkpoint
- [ ] n8n workflow running
- [ ] OCR processing receipts
- [ ] Mattermost notifications working
- [ ] Routing based on thresholds

### Week 2 Checkpoint
- [ ] All test cases passing
- [ ] OCR accuracy > 90%
- [ ] Documentation complete
- [ ] Users trained
