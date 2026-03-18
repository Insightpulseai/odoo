# Evaluations: SaaS Compliance Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| GDPR DSR completeness | 25% | Export contains all PII, deletion removes all PII |
| Data residency enforcement | 25% | No data outside designated region, policy enforced |
| Audit trail completeness | 20% | All access and modification events logged immutably |
| Classification coverage | 15% | All data categories classified with handling rules |
| Evidence automation | 15% | Compliance evidence generated without manual collection |

## Eval Scenarios

### Scenario 1: GDPR Data Export

- **Input**: User requests export of all personal data
- **Expected**: Complete data package (contacts, invoices, orders, attachments) delivered within 30 days
- **Fail condition**: Data missing from package, or delivery exceeds 30 days

### Scenario 2: GDPR Data Deletion

- **Input**: User requests erasure of all personal data
- **Expected**: All PII removed from all data stores, verification query confirms zero residual
- **Fail condition**: PII found in any table, backup, or log after deletion

### Scenario 3: Data Residency Violation Attempt

- **Input**: Attempt to create an Azure resource in non-designated region for EU tenant
- **Expected**: Azure Policy denies the deployment
- **Fail condition**: Resource created outside designated region

### Scenario 4: SOC2 Audit Preparation

- **Input**: Auditor requests evidence package for annual review
- **Expected**: Automated evidence package generated covering all control areas
- **Fail condition**: Manual evidence gathering required, or gaps in coverage

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, GDPR DSR and residency work |
| F | GDPR non-compliant or data residency not enforced |

## Pass Criteria

Minimum grade B for production with personal data. Grade A required for SOC2 certified platforms.
