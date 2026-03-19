# Evaluations: SaaS Identity & Access Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Tenant-user separation | 25% | Tenant and user are distinct entities in the design |
| Token claims complete | 25% | tenant-id is required, audience-restricted, role-scoped |
| Cross-tenant prevention | 25% | Token replay and cross-tenant access are impossible by design |
| Zero trust applied | 25% | MFA, conditional access, least-privilege are enforced |

## Eval Scenarios

### Scenario 1: Missing Tenant Claim
- **Input**: API request with valid user token but no tenant-id claim
- **Expected**: Request rejected with 403, not silently processed
- **Fail condition**: Request succeeds or defaults to a "system" tenant

### Scenario 2: Cross-Tenant Token Replay
- **Input**: Token issued for tenant-A used to access tenant-B resources
- **Expected**: Middleware rejects based on tenant-id mismatch
- **Fail condition**: Tenant-B data accessible with tenant-A token

### Scenario 3: Federation Claim Injection
- **Input**: External IdP SAML assertion includes a tenant-id claim
- **Expected**: Platform ignores external tenant-id, uses its own federation-to-tenant mapping
- **Fail condition**: External IdP can control which tenant a user accesses

### Scenario 4: Service-to-Service Tenant Propagation
- **Input**: Backend service call between microservices
- **Expected**: Tenant context propagated via service token, not lost
- **Fail condition**: Downstream service operates without tenant context
