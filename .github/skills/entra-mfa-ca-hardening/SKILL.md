# entra-mfa-ca-hardening

**Impact tier**: P0 -- Security Exposure

## Purpose

Close the identity-security gap where Entra ID MFA enforcement and Conditional
Access policies are not yet deployed. The benchmark audit found: no Conditional
Access policies, Security Defaults status unverified, no P1 license path
documented. All operator and service accounts accessing Azure resources and Odoo
ERP lack MFA enforcement through Entra.

## When to Use

- Hardening identity posture before go-live.
- Implementing Conditional Access policies for Odoo operator access.
- Upgrading from Security Defaults to Conditional Access (requires Entra P1).
- Responding to an audit finding about MFA coverage.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/entra/app-roles-manifest.json` | App registrations, role definitions |
| `infra/entra/role-tool-mapping.yaml` | Role-to-tool mappings for copilot |
| `infra/ssot/azure/resources.yaml` | Key Vault entries (secrets for service principals) |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Identity/MFA line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | MFA/CA gap row |
| `addons/ipai/ipai_security_frontdoor/middleware.py` | Current auth middleware |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Entra ID Security Defaults MFA enforcement")`
   -- confirms what Security Defaults provides and its limitations.
2. `microsoft_docs_search("Entra ID Conditional Access policy MFA require all users")`
   -- retrieves CA policy templates for MFA enforcement.
3. `microsoft_docs_search("Entra ID P1 license Conditional Access comparison Security Defaults")`
   -- clarifies the P1 upgrade path and what CA unlocks over Security Defaults.

Optional deeper fetches:

4. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policies")`
5. `microsoft_docs_search("Entra Conditional Access named locations trusted IP")`

## Workflow

1. **Inspect repo** -- Read `infra/entra/` files. Record existing app
   registrations, role definitions, and any CA policy stubs. Check middleware
   for token validation logic.
2. **Query MCP** -- Run the three searches above. Capture Security Defaults
   scope, CA policy JSON structure, P1 licensing requirements.
3. **Compare** -- Map current state (no CA policies, Security Defaults
   unverified) against Microsoft's recommended baseline (CA policies for all
   users, MFA for admin roles, device compliance for sensitive apps).
4. **Patch** -- Create or update:
   - `infra/entra/conditional-access-policies.json` with baseline CA policies.
   - `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` with MFA/CA verification steps.
   - `infra/entra/app-roles-manifest.json` if role definitions are incomplete.
   Document the P1 license upgrade decision in an ADR or the checklist.
5. **Verify** -- Confirm policy JSON is syntactically valid. Confirm the go-live
   checklist includes MFA verification steps. Confirm the middleware validates
   Entra tokens (not just basic auth).

## Outputs

| File | Change |
|------|--------|
| `infra/entra/conditional-access-policies.json` | Baseline CA policy definitions |
| `infra/entra/app-roles-manifest.json` | Complete app role definitions |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | MFA/CA verification steps |
| `addons/ipai/ipai_security_frontdoor/middleware.py` | Entra token validation (if missing) |
| `docs/evidence/<stamp>/entra-mfa-ca-hardening/` | Policy JSON, MCP excerpts |

## Completion Criteria

- [ ] Security Defaults status is documented (ON or OFF with justification).
- [ ] At least one Conditional Access policy definition exists requiring MFA for
      all users accessing Azure portal and Odoo ERP.
- [ ] P1 license upgrade path is documented with cost and timeline.
- [ ] Go-live checklist includes explicit MFA verification steps.
- [ ] `ipai_security_frontdoor` middleware validates Entra ID tokens (JWT issuer,
      audience, signature).
- [ ] Evidence directory contains CA policy definitions and MCP query excerpts.
