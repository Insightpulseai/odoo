# Evaluations: SaaS Networking Design

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| PaaS isolation | 25% | No PaaS service accessible on public internet |
| Front Door enforcement | 25% | All inbound traffic passes through Front Door |
| Cross-stamp isolation | 20% | No direct network path between stamps |
| Custom domain TLS | 15% | Custom domains working with auto-renewed certificates |
| WAF effectiveness | 15% | Attack traffic blocked, legitimate traffic passes |

## Eval Scenarios

### Scenario 1: Direct PaaS Access Attempt

- **Input**: Attempt to connect to PostgreSQL via public IP
- **Expected**: Connection refused — private endpoint only
- **Fail condition**: PostgreSQL accessible on public internet

### Scenario 2: Front Door Bypass

- **Input**: Attempt to access Container App directly (bypassing Front Door)
- **Expected**: Request rejected — only Front Door service tag allowed
- **Fail condition**: Direct access to Container App succeeds

### Scenario 3: Custom Domain Onboarding

- **Input**: Enterprise tenant adds custom domain `erp.acme.com`
- **Expected**: CNAME verified, TLS certificate provisioned, routing active within 15 minutes
- **Fail condition**: Manual certificate upload required, or routing not working

### Scenario 4: Cross-Stamp Network Probe

- **Input**: Service in stamp A attempts to reach service in stamp B via private IP
- **Expected**: No network path exists — connection times out
- **Fail condition**: Cross-stamp connectivity exists

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, all 4 scenarios handled |
| B | 4/5 criteria pass, scenarios 1-3 handled |
| C | 3/5 criteria pass, PaaS isolation and Front Door enforcement work |
| F | PaaS services publicly accessible or Front Door bypassable |

## Pass Criteria

Minimum grade B for production. Grade A required for platforms handling regulated data.
