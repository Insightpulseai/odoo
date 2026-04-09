# Risks, Blind Spots & Next Highest-Leverage Additions

## Known Risks

### R1: PH Tax Compliance is Non-Deferrable
**Risk**: BIR 2307 (withholding tax certificates) and SLSP (summary lists) are legally required. No OCA module covers PH-specific BIR requirements at 18.0.
**Impact**: Cannot operate legally without these.
**Mitigation**: Build ipai_bir_2307 and ipai_bir_slsp as P1 custom modules. Engage tax advisor for validation.
**Status**: Not started.

### R2: OCA Module Quality at 18.0
**Risk**: Some OCA modules may not have stable 18.0 branches, or may have regressions.
**Impact**: Installation failures, data corruption, upgrade blocks.
**Mitigation**: Test every OCA module on disposable DB before baseline inclusion. Pin specific commits. Budget time for porting.

### R3: Single-Person Implementation Risk
**Risk**: Solo builder means no peer review, no separation of duties in development, no backup.
**Impact**: Knowledge concentration, slower progress, quality risk.
**Mitigation**: Knowledge base (this repo) serves as async peer review. Agent-assisted development. Documentation-first approach.

### R4: Odoo Upgrade Path
**Risk**: When Odoo 19 or later arrives, all custom modules and OCA dependencies need migration.
**Impact**: Significant rework every ~18 months.
**Mitigation**: Minimize custom code (Config → OCA → Delta). Write migration scripts proactively. Track OCA upgrade status.

### R5: Performance at Scale
**Risk**: Odoo performance degrades with large datasets (>100K journal entries, >10K partners).
**Impact**: Slow reports, timeout on batch operations, poor UX.
**Mitigation**: Baseline performance early. Use queue_job for batch processing. Offload reporting to Databricks/Power BI. PostgreSQL tuning.

### R6: Integration Fragility
**Risk**: Multi-service architecture (Odoo + Azure + Databricks + n8n) creates many failure points.
**Impact**: Data inconsistency, cascading failures, complex debugging.
**Mitigation**: Async processing with retry. Dead letter queues. Monitoring and alerting. Integration tests.

## Blind Spots

### B1: Real-World Business Process Complexity
The knowledge base captures standard patterns. Real businesses have:
- Non-standard payment terms
- Vendor-specific billing requirements
- Legacy data migration edge cases
- User resistance to process change
- Exceptions that become the rule

**Mitigation**: Add decision records and edge cases as they are discovered. The skill packs have "Edge Cases" sections — populate them from real experience.

### B2: Regulatory Change
PH tax rules change frequently (TRAIN law, e-invoicing mandates, new BIR forms).
**Mitigation**: Reference BIR circulars by number. Date-stamp all compliance rules. Build compliance modules to be configurable (tables, not code).

### B3: Multi-Currency Depth
The knowledge base covers basic multi-currency. Enterprise scenarios include:
- Hedge accounting
- Realized vs unrealized gain/loss
- Intercompany in different currencies
- Transfer pricing in multi-currency

**Mitigation**: Mark as L4 (expert) capability. Build incrementally as needed.

### B4: Payroll Depth
CE payroll is extremely basic. PH payroll has complex statutory requirements (SSS bracket tables, PhilHealth tiers, Pag-IBIG schedules, BIR annualized tax tables).
**Mitigation**: Plan custom ipai_hr_ph_* modules. Consider if a standalone payroll system (with Odoo integration) is more practical.

### B5: Audit Readiness
The knowledge base covers audit trail implementation but not audit preparation:
- Preparing for external auditors
- Generating audit-ready reports
- Managing audit queries
- Regulatory examination responses

**Mitigation**: Add "audit-readiness" skill pack when the first audit approaches.

## Next Highest-Leverage Additions

### Priority Order

1. **PH tax compliance skill pack** (fills legal gap)
   - BIR form specifications (2307, 2316, 1601-EQ, 1604-E, SLSP)
   - Tax table configurations
   - Filing calendar and deadlines
   - Sample computations with edge cases

2. **Data migration toolkit** (enables go-live)
   - CSV templates per model
   - Validation scripts
   - Reconciliation queries
   - Rollback procedures

3. **Operational runbook** (enables Day 2+)
   - Daily operations checklist
   - Weekly maintenance tasks
   - Monthly close procedure (already started)
   - Incident response playbook
   - Backup/restore verification

4. **Performance benchmark dataset** (enables optimization)
   - Seed data generators for realistic volumes
   - Query performance baselines
   - Load test scenarios
   - Tuning parameters with expected impact

5. **Integration test suite** (reduces R6)
   - End-to-end test scenarios per integration
   - Failure simulation tests
   - Recovery verification
   - Monitoring validation

6. **User training materials** (enables adoption)
   - Role-based quick start guides
   - Process walkthrough videos/screenshots
   - FAQ per module
   - Common error resolution guide

7. **Localization reference** (PH-specific)
   - Chart of accounts for PH PFRS
   - BIR tax codes mapping
   - DOLE compliance requirements
   - BSP reporting requirements (if applicable)
