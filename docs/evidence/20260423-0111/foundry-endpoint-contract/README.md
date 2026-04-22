# Foundry Endpoint Contract Evidence

- Scope: Foundry endpoint and auth contract baseline for `ipai-copilot`
- Local stamp: `20260423-0111` (Asia/Manila)
- Source of endpoint confirmation: operator-provided Azure AI Foundry portal screenshots and narration in this thread

## Files added

- `platform/contracts/foundry/endpoints.yaml`
- `platform/contracts/foundry/auth-policy.yaml`
- `docs/runbooks/FOUNDRY_PROJECT_BASELINE.md`
- `docs/runbooks/FOUNDRY_CLIENT_AUTH_MATRIX.md`

## Verification

- `PASS` YAML parse for both new contract files
- `PASS` Runbooks point to the new contract files as authority
- `PASS` Legacy drift scan confirms older `ipai-copilot-resource` references still exist elsewhere in the repo and are explicitly called out

## Notes

- This evidence pack records the repo contract layer only.
- No live Azure query was executed in this turn to re-verify the Foundry project endpoint.
- The new contract is intentionally narrow so the current `ipai-foundry-sea` baseline can be frozen without rewriting the broader legacy Foundry doctrine in one change.
