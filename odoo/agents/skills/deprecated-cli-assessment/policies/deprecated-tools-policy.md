# Deprecated Tools Policy

## Default Stance

All deprecated tools are REJECTED by default. The burden of proof is on the requestor to demonstrate that ALL 5 exception criteria are met.

## odo — Permanent Reject

odo (Red Hat OpenShift Developer CLI) is permanently rejected:
- Officially deprecated by Red Hat
- GitHub repository is archived
- No IPAI use case requires OpenShift developer tooling
- No exception pathway exists
- Benchmark-only references (comparison documentation) are allowed

## Assessment Process

1. Tool is identified as deprecated (in registry or by external evidence)
2. Default verdict: REJECT
3. If exception requested: evaluate 5 criteria
4. If ALL 5 criteria met: grant time-boxed exception with documentation
5. If ANY criterion not met: REJECT

## CI Enforcement

- Deprecated tools must not appear in CI pipeline definitions
- Periodic scan of .github/workflows/, scripts/, docker/ for deprecated tool references
- Any reference triggers a warning (not a hard failure — may be benchmark documentation)

## Registry Maintenance

- New deprecated tools are added as discovered
- Each entry includes: vendor, deprecation date, canonical alternative, exception criteria
- Registry is source of truth for all deprecation decisions
- Review registry quarterly for expired exceptions

## Benchmark vs. Canonical

- Benchmark reference: studying/comparing deprecated tools for documentation — ALLOWED
- Canonical use: depending on deprecated tools for production operations — REJECTED
- Clear the distinction: reading about odo is fine; installing odo in CI is not
