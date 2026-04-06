# Capability Maturity Rubric

## Maturity Levels

| Level | Label | Definition | Evidence Required |
|-------|-------|-----------|-------------------|
| L1 | Foundational | Can explain the concept, navigate the UI/code, identify components | Written explanation or verbal walkthrough |
| L2 | Working | Can configure, implement, and troubleshoot standard scenarios | Working implementation on test database |
| L3 | Advanced | Can handle edge cases, optimize, design for scale, mentor others | Production-grade implementation with tests |
| L4 | Expert | Can architect enterprise-grade solutions, evaluate trade-offs, lead implementation | Architecture document + running system + evaluation of alternatives |

## Assessment Criteria

### For Each Capability

1. **Knowledge test**: Can explain the business purpose and technical implementation
2. **Build test**: Can implement a working solution from requirements
3. **Debug test**: Can diagnose and fix a broken implementation
4. **Design test**: Can evaluate trade-offs and propose architecture
5. **Edge case test**: Can handle non-standard scenarios correctly

### Scoring

| Score | Meaning |
|-------|---------|
| 0 | No evidence of capability |
| 1 | Partial evidence, significant gaps |
| 2 | Meets level requirements with minor gaps |
| 3 | Exceeds level requirements, demonstrates depth |

### Progression Rules

- Must score >= 2 on all criteria at current level before advancing
- L1 → L2: Demonstrate on test database
- L2 → L3: Demonstrate on production-like environment with real data patterns
- L3 → L4: Demonstrate across multiple implementations or domains

## Domain-Specific Evidence

### Finance (L3+ requires)
- Multi-company chart of accounts with intercompany transactions
- Month-end close procedure executed successfully
- Bank reconciliation with complex matching rules
- Tax compliance reports generating correct figures

### Procurement (L3+ requires)
- Multi-level approval workflow with budget validation
- 3-way matching (PO → receipt → invoice)
- Vendor evaluation scorecard in use
- Purchase agreement lifecycle demonstrated

### Integration (L3+ requires)
- API contract documented and tested
- Async processing with error handling and retry
- Data synchronization with conflict resolution
- Monitoring and alerting for integration health

### Identity/Security (L3+ requires)
- Role hierarchy with SoD matrix
- Record rules preventing cross-company data access
- OIDC/SAML federation working with Entra ID
- Audit log review procedure documented
