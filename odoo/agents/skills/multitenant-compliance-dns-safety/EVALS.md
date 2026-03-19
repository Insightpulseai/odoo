# Evaluations: Multitenant Compliance & DNS Safety

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Compliance mapped per tenant | 25% | Every tenant's requirements documented and controls mapped |
| DNS safety enforced | 25% | No dangling CNAME records, subdomain takeover prevented |
| Data residency validated | 25% | All tenant resources in correct region, verified periodically |
| Certificates automated | 25% | Issuance, renewal, and alerting fully automated |

## Eval Scenarios

### Scenario 1: Subdomain Takeover Attempt
- **Input**: Tenant offboarded, Container App deleted, DNS record still exists
- **Expected**: Dangling CNAME scan detects and removes record within 24 hours
- **Fail condition**: Dangling record persists, attacker claims resource

### Scenario 2: Data Residency Violation
- **Input**: EU-resident tenant's backup replicated to US region
- **Expected**: Azure Policy blocks creation, or validation scan detects and alerts
- **Fail condition**: Data stored outside allowed region without detection

### Scenario 3: Certificate Expiration
- **Input**: Custom domain certificate approaching 30-day expiration
- **Expected**: Auto-renewal triggered, or alert sent if renewal fails
- **Fail condition**: Certificate expires, tenant experiences TLS errors

### Scenario 4: Compliance Gap Discovery
- **Input**: Enterprise tenant adds HIPAA requirement mid-contract
- **Expected**: Gap analysis identifies missing controls, remediation plan created
- **Fail condition**: HIPAA requirement not assessed, tenant operates non-compliant
