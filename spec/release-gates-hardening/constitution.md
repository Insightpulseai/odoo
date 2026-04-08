# Release Gates Hardening Constitution

## Purpose
Define the final release barrier for the Agent Factory to ensure all hardened contracts are enforced before production deployment.

## Authority Model
- `spec/release-gates-hardening/*` = specification truth
- `ssot/release/*` = release gate truth
- `.github/workflows/agent-factory-release-gates.yml` = implementation truth
- `production-eligibility.json` = operational proof

## Execution Invariants
- Production deployment is blocked unless all subsystem acceptance artifacts exist and validate.
- Release workflows must validate Specs, SSOTs, Schemas, Tests, and Evidence.
- Production eligibility must be machine-verifiable.
- Topology and storage assumptions must be live-verified before release.

## Failure Contract
- Missing/invalid contracts or evidence => Fail closed (blocked release).
- Topology/deployment mismatch => Fail closed.
- Overstated guarantees in docs/logs => Fail closed (Drift enforcement).

## Drift Policy
- Automatically reject any production promotion if `runtime_production_status` is not `approved` or `conditional-approved`.
- Periodically verify that live cluster state matches the SSOT topology.
