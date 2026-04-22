# Golden-Path Schema Realignment Evidence

- Scope: realign the nine golden-path contract files to the minimal schema-style YAML skeletons
- Local stamp: `20260423-0125` (Asia/Manila)
- Source baseline: operator-provided patch-ready skeletons from the thread plus already-established canonical production OAuth and Foundry endpoint values

## Files updated

- `platform/contracts/identity/oauth-matrix.yaml`
- `platform/contracts/foundry/endpoints.yaml`
- `platform/contracts/foundry/auth-policy.yaml`
- `platform/contracts/foundry/rbac-matrix.yaml`
- `platform/contracts/entra/agent-identities.yaml`
- `platform/contracts/release/golden-path.yaml`
- `marketplace-publishing/contracts/golden-path-packaging.yaml`
- `marketplace-publishing/contracts/golden-path-compliance.yaml`
- `marketplace-publishing/contracts/golden-path-gtm.yaml`

## Verification

- `PASS` All nine contract YAML files parsed successfully
- `PASS` Production OAuth redirects for Google and Microsoft match and remain HTTPS
- `PASS` Foundry project endpoint and Azure OpenAI base URL match the canonical baseline
- `PASS` Foundry auth policy distinguishes portal, AI Toolkit, runtime apps, and CI/CD
- `PASS` Foundry RBAC matrix tracks principals and verification state without inventing IDs
- `PASS` Agent identity contract includes an explicitly unmanaged identity
- `PASS` Release contract retains preview-before-live enforcement
- `PASS` Packaging, compliance, and GTM contracts share the same product key

## Notes

- Unknown IDs, scopes, and owners remain blank by design in this schema pass.
- This patch intentionally favors the user-provided minimal schema over the richer metadata shape committed earlier.
