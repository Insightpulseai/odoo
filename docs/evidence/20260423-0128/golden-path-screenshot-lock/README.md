# Golden-Path Screenshot Lock Evidence

- Scope: fill evidence-backed blanks in the golden-path contracts using operator-reported Entra, Foundry, and Agent ID screenshots
- Local stamp: `20260423-0128` (Asia/Manila)
- Source baseline: screenshot-derived values provided in-thread for tenant/domain, Global Administrator assignment, enterprise app identity, Foundry endpoints, and Agent ID counts

## Files updated

- `platform/contracts/identity/oauth-matrix.yaml`
- `platform/contracts/foundry/rbac-matrix.yaml`
- `platform/contracts/entra/agent-identities.yaml`
- `platform/contracts/release/golden-path.yaml`

## Verification

- `PASS` YAML parse for the affected contract set
- `PASS` OAuth contract now records `insightpulseai.com`, `ceoinsightpulseai.onmicrosoft.com`, and Microsoft app `3446e178-3eba-48c9-b5bd-4283ff729eb1`
- `PASS` Foundry RBAC contract now records the admin user's Global Administrator role hint and marks AI Toolkit access as `failing_or_unverified`
- `PASS` Agent identity contract now records summary counts `total=3`, `active=3`, `unmanaged=1`
- `PASS` Release contract now binds the Microsoft enterprise app name and application ID into `identity_surface`

## Notes

- Exact Microsoft redirect URI inventory, Google redirect URI inventory, Azure RBAC role assignments, and owner/sponsor fields remain intentionally blank pending direct evidence.
- `platform/contracts/foundry/endpoints.yaml` did not require change in this pass because the canonical endpoint values were already aligned.
