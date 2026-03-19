# Checklist — caf-governance-baseline

- [ ] Governance maturity level assessed (Initial / Defined / Managed / Optimized)
- [ ] Azure Policy assignments audited against CAF recommended baseline
- [ ] Required policies identified: allowed locations, allowed resource types, naming convention
- [ ] Policies deployed as audit-first (not deny) for new assignments
- [ ] Resource naming convention compliance audited
- [ ] Non-compliant resources listed with remediation plan
- [ ] Required tags defined (Environment, Owner, CostCenter minimum)
- [ ] Tagging compliance measured and gaps identified
- [ ] Cost budget configured per resource group or subscription
- [ ] Cost alerts enabled (50%, 80%, 100% thresholds)
- [ ] Azure Advisor recommendations reviewed and triaged
- [ ] RBAC assignments audited (least privilege principle)
- [ ] PIM enabled for privileged roles (or justified why not)
- [ ] Conditional Access policies reviewed
- [ ] IaC coverage assessed (percentage of resources managed by Bicep/Terraform)
- [ ] Deployment gates defined in CI/CD pipeline
- [ ] Governance improvement roadmap created with prioritized actions
- [ ] Evidence captured in `docs/evidence/{stamp}/caf/governance/`
