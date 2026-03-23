# Release Gates Hardening Architecture

## Doctrine: The Final Barrier
The Release Gating layer is the final control surface that converts architectural narrative into machine-enforced truth. It ensures that the Agent Factory cannot be deployed to production unless all hardened contracts are validated and all evidence is present.

## Promotion Gates
1. **Spec & SSOT Check**: All spec bundles and SSOT files must be valid and internally consistent.
2. **Acceptance Artifacts**: Every subsystem (Supervisor, Router, Eval, Deployments) must have a verified `acceptance.json` artifact.
3. **Topology Verification**: Hard-coded checks in CI ensure that stateful services (like the Supervisor) do not drift into unsafe multi-replica topologies.
4. **Terminology Enforcement**: Prohibited claims for "unconditional" or "absolute" guarantees are blocked to prevent marketing drift from skewing technical reality.

## Production Eligibility
The `production-eligibility.json` artifact acts as the "Passport" for the whole factory. It rollups the state of all components and is the definitive source of truth for the release pipeline.

> [!IMPORTANT]
> The Agent Factory’s production positioning must remain aligned with the bounded claims documented in `docs/architecture/AGENT_FACTORY_VS_SAP_JOULE.md`. No unconditional exactly-once or unconditional production-safety language is permitted.
