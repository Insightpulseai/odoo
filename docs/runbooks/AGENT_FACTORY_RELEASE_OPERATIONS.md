# Agent Factory Release Operations

## Promotion Path
1. **Implement Hardening**: Complete the hardening lane for a subsystem.
2. **Review & Accept**: Move from `ready_for_acceptance_review` to `accepted`.
3. **Generate Evidence**: Update `acceptance.json` and provide logs/checks in `docs/evidence/`.
4. **Production Gating**: Run the `Agent Factory Release Gates` workflow.
5. **Release**: Deploy to production only if the workflow passes and `runtime_production_status` is `conditional-approved`.

## Rollback Policy
- **Trigger**: Any deviation from SSOT topology or any `at-least-once` duplication spike detected in metrics.
- **Action**: Immediate rollback to the previous known-good deployment of the affected subsystem.
- **Evidence**: Rollbacks must be accompanied by an incident report justifying the substrate failure or contract violation.

## Fail-Closed Scenarios
- If CI fails on topology mismatch: **DO NOT** manually override `replicas` in prod bypass. Update the manifest and the SSOT contract through the hardening lane.
- If CI fails on missing evidence: Generate the required traces before attempting the next promotion.
