# Evaluations: Tenant Identity Isolation

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Tenant claim enforcement | 25% | Every API rejects requests without tenant_id claim |
| Cross-tenant prevention | 25% | User in tenant A cannot access tenant B resources |
| RBAC correctness | 20% | Roles scoped to tenant, no cross-tenant grants |
| Managed identity scoping | 15% | Service identities limited to correct tenant resources |
| Migration readiness | 15% | Design supports Keycloak-to-Entra transition |

## Eval Scenarios

### Scenario 1: Token Without Tenant Claim

- **Input**: Valid Entra ID token missing the tenant_id custom claim
- **Expected**: Request rejected with 403, security event logged
- **Fail condition**: Request proceeds with no tenant scoping

### Scenario 2: Cross-Tenant Data Access

- **Input**: User authenticated as tenant A, requests API resource belonging to tenant B
- **Expected**: Request rejected — tenant_id in token does not match resource ownership
- **Fail condition**: Data from tenant B returned to tenant A user

### Scenario 3: Token Tampering

- **Input**: JWT with tenant_id claim manually changed from "acme" to "globex"
- **Expected**: Signature validation fails, request rejected
- **Fail condition**: Tampered token accepted

### Scenario 4: Managed Identity Cross-Boundary

- **Input**: Service in tenant A's stamp attempts to read tenant B's database via managed identity
- **Expected**: RBAC denies access — managed identity not assigned to tenant B resources
- **Fail condition**: Database connection succeeds

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, scenario 1 handled |
| F | Cross-tenant access possible in any scenario |

## Pass Criteria

Minimum grade B for production. Grade A required for platforms handling PII or financial data.
