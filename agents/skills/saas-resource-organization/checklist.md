# Checklist: SaaS Resource Organization

## Subscription Topology

- [ ] Subscription strategy documented (single, per-environment, per-tier, per-tenant)
- [ ] Subscription quota limits validated against expected tenant count
- [ ] Management group hierarchy defined if using multiple subscriptions
- [ ] Billing account structure supports cost attribution requirements

## Resource Group Structure

- [ ] Resource group naming pattern defined with tenant/environment identifiers
- [ ] Grouping strategy documented (per-service, per-tenant, per-region, composite)
- [ ] Resource group lifecycle aligned with tenant lifecycle
- [ ] Cross-resource-group dependencies mapped

## Naming Convention

- [ ] Naming pattern includes: resource type, tenant identifier, environment, region
- [ ] Pattern validated against Azure naming restrictions (length, characters)
- [ ] Naming convention documented and shared with all teams
- [ ] Collision prevention strategy defined for shared resources

## Tagging Policy

- [ ] Required tags defined: tenant-id, environment, cost-center, owner, data-classification
- [ ] Azure Policy created to enforce required tags
- [ ] Tag values standardized (enum where possible)
- [ ] Tag inheritance strategy defined for child resources

## RBAC Scoping

- [ ] RBAC assignments follow least-privilege principle
- [ ] No cross-tenant access possible in shared infrastructure
- [ ] Custom roles created only when built-in roles are insufficient
- [ ] Service principal permissions scoped to minimum required resources
- [ ] Privileged Identity Management (PIM) configured for elevated access
