# Foundry Client Auth Matrix

> Authority:
> - `platform/contracts/foundry/endpoints.yaml`
> - `platform/contracts/foundry/auth-policy.yaml`

## Canonical matrix

| Client | Endpoint | Preferred auth | Allowed fallback | Notes |
|---|---|---|---|---|
| Portal / quick tests | Foundry portal project surface | `api_key` | none | Acceptable for bootstrap and validation |
| AI Toolkit / local tooling | Foundry project endpoint | `entra_rbac` | `api_key_fallback` | Must be in the correct tenant/subscription/project context |
| Runtime apps / hosted agents | Foundry project endpoint or Azure OpenAI base, depending on client | `managed_identity` | `api_key_fallback` | Runtime should prefer keyless |
| CI/CD | Project endpoint or Azure OpenAI base, depending on task | `federated_identity` | `secret` | Secret path allowed only when keyless is unavailable |

## Operational rules

- Global Administrator in Entra does not automatically grant Azure RBAC on the Foundry resource/project.
- API key use is acceptable for portal bootstrap, but it is not the preferred runtime posture.
- Runtime services must not depend on manual key copy/paste.
- Local tooling failures that mention project connections are usually RBAC/scope/context issues, not endpoint discovery issues.

## AI Toolkit-specific checks

If AI Toolkit cannot read project connections, verify:

1. The user is signed into the correct tenant.
2. The user is targeting the correct subscription.
3. The Toolkit is bound to the canonical project endpoint.
4. The principal has rights to read project connections.

If those pass and the problem remains, treat it as a Foundry project authorization or client-tooling issue, not a tenant-readiness issue.

## Runtime guidance

- Project-native operations should use the Foundry project endpoint.
- OpenAI-compatible SDKs should use the Azure OpenAI base URL.
- Managed identity is the default runtime auth mode.
- API key fallback is allowed only as an explicit bootstrap or break-glass path.
