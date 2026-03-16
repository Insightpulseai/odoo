# Migration Outcome Gates

> Migration is not one event. It is four sequential gates, each with explicit exit criteria.

## Gate model

```
Ready to Migrate → Technically Live → Operationally Live → Business Live
```

### Gate 1: Ready to Migrate

The target environment exists and the migration path is modeled.

Exit criteria:

- Azure target environment provisioned (Container Apps, PG, Key Vault, Front Door)
- Public ingress path modeled (DNS, Front Door origin group, TLS)
- Canonical runtime contract verified locally (`docker_contract_check.sh` green)
- Secrets/identity boundary valid (Key Vault references, managed identity bindings)
- Rollback plan documented

### Gate 2: Technically Live

The backend is deployed and reachable through the edge.

Exit criteria:

- Container App image deployed and running (`provisioningState: Succeeded`)
- Front Door health probe returns 200 from origin
- Database connectivity verified (read + write)
- `odoo-bin --stop-after-init` exits 0 in the container
- No startup errors in container logs

### Gate 3: Operationally Live

The first target workflow passes through the production path.

Exit criteria:

- User can authenticate via public edge (`erp.insightpulseai.com`)
- First business workflow completes end-to-end (e.g., create invoice, approve expense)
- Rollback plan dry-run completed
- Observability active (App Insights, Log Analytics, Monitor alerts)
- Evidence pack produced in `docs/evidence/<date>/`

### Gate 4: Business Live

Production users are active and compliance workflows are operational.

Exit criteria:

- Production database seeded with real data
- BIR compliance workflows operational (if applicable)
- Monthly close cycle can execute
- Copilot assistant reachable and responding
- SLA/uptime monitoring active

## Solo-maintainer deployment policy

- **Nonprod**: Automatic deployment on merge to main
- **Prod**: Automatic unless change is destructive, RBAC-affecting, topology-changing, data-destructive, or cutover-critical
- Approval gates only on those exceptional classes
- Routine aligned work flows without manual approval

## Current gate status (2026-03-17)

| Gate | Status | Blocker |
|------|--------|---------|
| Ready to Migrate | Green | All 82 Azure resources exist |
| Technically Live | Yellow | Container Apps provisioned but origin health unverified |
| Operationally Live | Red | No end-to-end workflow evidence |
| Business Live | Red | No production users |
