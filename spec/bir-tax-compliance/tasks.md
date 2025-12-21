# BIR Tax Compliance - Task Checklist

## Phase 1: Core Infrastructure

- [ ] Create `ipai_bir_tax_compliance` module scaffold
- [ ] Implement `bir.tax.return` base model
- [ ] Add TIN validation on `res.partner`
- [ ] Create filing deadline calendar data
- [ ] Build compliance dashboard view
- [ ] Add deadline alert cron job
- [ ] Write security access rules

## Phase 2: VAT Module

- [ ] Implement `bir.vat.return` model
- [ ] Create VAT computation logic (standard/zero/exempt)
- [ ] Build Form 2550M generation wizard
- [ ] Build Form 2550Q generation wizard
- [ ] Add VAT input/output reconciliation view
- [ ] Create VAT summary report
- [ ] Test with sample sales/purchase data

## Phase 3: Withholding Tax

- [ ] Implement `bir.withholding.return` model
- [ ] Integrate with `hr.payslip` for compensation WHT
- [ ] Add expanded WHT tracking on vendor bills
- [ ] Build Form 1601-C generation
- [ ] Build Form 1601-E generation
- [ ] Create annual alphalist (1604-CF) generator
- [ ] Test with payroll and vendor data

## Phase 4: Other Taxes

- [ ] Implement income tax return model
- [ ] Add excise tax tracking (stock integration)
- [ ] Build capital gains calculator
- [ ] Add documentary stamp tax tracking
- [ ] Create respective form generators

## Phase 5: Integration

- [ ] Create n8n workflow for deadline alerts
- [ ] Sync filing status to Control Room
- [ ] Add Mattermost notifications
- [ ] Write user documentation
- [ ] Perform UAT with finance team
- [ ] Deploy to production

## Validation Criteria

- [ ] All forms compute correctly vs manual calculation
- [ ] Deadlines trigger alerts 5 days before
- [ ] TIN validation rejects invalid formats
- [ ] Audit trail captures all changes
- [ ] Dashboard shows accurate status
