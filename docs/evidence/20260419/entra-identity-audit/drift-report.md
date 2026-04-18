# Entra Identity Drift Report — 2026-04-19

**Scope**: tenant `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` (Azure Sponsorship), domain `insightpulseai.com`.
**Authoritative target**: [ssot/identity/entra_target_state.yaml v2.0](../../../../ssot/identity/entra_target_state.yaml).
**Collected by**: `az ad user list`, `az rest` Graph queries, `az ad sp list`.

---

## Summary

| Dimension | Current | Target | Gap |
|---|---|---|---|
| Member users (humans) | 9 | 4 | **-5** (remove / reclassify 5) |
| Guest users | 0 | 11 (TBWA\SMP) | **+11** (invite) |
| Global Administrators | 7 | 3 | **-4** (demote / remove 4) |
| Break-glass accounts | 5 | 2 | **-3** (consolidate) |
| Service principals total | 378 | tracked + owned | **audit pending** |
| SPs with canonical naming (`sp-*`/`mi-*`/`agent-*`) | 0 | all custom apps | **rename pending** |
| Agent identities unmanaged | 1 | 0 | **-1** (assign sponsor + rename) |
| Identity Secure Score | 43.77% | 65% near-term | **+21.23 pts** |

---

## 1. Member users — violates "4 humans only" target

### Current roster (9)

| Display name | UPN | Disposition |
|---|---|---|
| Jake Tolentino | `admin@insightpulseai.com` | **Migrate**: create `jake.admin@insightpulseai.com`, remove this UPN; `admin@` reverts to Zoho alias |
| Jake Tolentino | `ceo@insightpulseai.com` | **Remove from Entra**; `ceo@` is a Zoho alias on `business@` |
| Break Glass Admin | `breakglass-admin@insightpulseai.com` | **Remove** (duplicate of numbered break-glass) |
| BreakGlass-Admin-01 | `breakglass01@insightpulseai.com` | **Keep** → rename to "Emergency Access 01" |
| BreakGlass-Admin-02 | `breakglass02@insightpulseai.com` | **Keep** → rename to "Emergency Access 02" |
| Emergency Admin | `emergency-admin@insightpulseai.com` | **Remove** (duplicate) |
| Emergency Admin 2 | `emergency-admin-2@insightpulseai.com` | **Remove** (duplicate) |
| DevOps Service | `devops@insightpulseai.com` | **Convert to SP** (`sp-ipai-devops-automation-prod`) or classify as non-human |
| Dataverse Finance | `finance@insightpulseai.com` | **Remove**; `finance@` is a Zoho mailbox |

### Target roster (4)

| Display name | UPN | Role |
|---|---|---|
| Jake Tolentino | `jake.tolentino@insightpulseai.com` | daily-use, no standing roles |
| Jake Tolentino (Admin) | `jake.admin@insightpulseai.com` | PIM-eligible privileged |
| Emergency Access 01 | `breakglass01@insightpulseai.com` | break-glass (FIDO2) |
| Emergency Access 02 | `breakglass02@insightpulseai.com` | break-glass (FIDO2) |

---

## 2. Global Administrators — violates "≤ 5, target 3"

### Current (7)

1. Jake Tolentino (`ceo@insightpulseai.com`) — **demote**, remove UPN
2. Jake Tolentino (`admin@insightpulseai.com`) — **migrate to** `jake.admin@`
3. Emergency Admin (`emergency-admin@insightpulseai.com`) — **remove** (duplicate)
4. Emergency Admin 2 (`emergency-admin-2@insightpulseai.com`) — **remove** (duplicate)
5. BreakGlass-Admin-01 (`breakglass01@insightpulseai.com`) — **keep** as Emergency Access 01
6. BreakGlass-Admin-02 (`breakglass02@insightpulseai.com`) — **keep** as Emergency Access 02
7. Break Glass Admin (`breakglass-admin@insightpulseai.com`) — **remove** (duplicate)

### Target (3)

1. Jake Tolentino (Admin) — PIM-eligible only, not permanently active
2. Emergency Access 01 — active, FIDO2, excluded from CA
3. Emergency Access 02 — active, FIDO2, excluded from CA

**Action**: before removing GAs #3, #4, #7, confirm PIM rolls over to #5/#6 and `jake.admin@` is created and tested via break-glass procedure.

---

## 3. Guests — missing entirely

### Current: 0 guests
### Target: 11 (TBWA\SMP Finance)

Canonical list in [ssot/identity/guest-invite-registry.yaml](../../../../ssot/identity/guest-invite-registry.yaml).
Bulk-invite CSV at [ops/entra/guests/tbwa-smp-finance-import.csv](../../../../ops/entra/guests/tbwa-smp-finance-import.csv).
Onboarding runbook at [docs/runbooks/entra-guest-onboarding.md](../../../runbooks/entra-guest-onboarding.md).

---

## 4. Service principals — 378 total, 0 canonical-named

`az ad sp list --filter "servicePrincipalType eq 'Application'"` returned 378.
Filter for `sp-*` / `mi-*` / `agent-*` prefixes returned 0.

**Action**: separate audit PR — classify into `keep_strategic` / `review_potentially_stale` / `remove`, rename custom apps, and assign owners. Not in scope for this PR.

---

## 5. Agent identities

Per your screenshots: 2 active, 1 unmanaged, 1 blueprint.

**Actions**:
- Assign sponsor + technical owner to the unmanaged agent.
- Rename to `agent-<system>-<purpose>` (e.g. `agent-ipai-copilot-primary`, `agent-ipai-copilot-eval`).
- Record in `ssot/identity/entra_target_state.yaml#agent_identities`.

---

## 6. Authentication methods

- **Gap**: legacy MFA/SSPR policy enforcement may still be active; Microsoft deprecated management via that surface on 2025-09-30.
- **Action**: verify authentication methods policy is the only authority; migrate any residual legacy settings.

---

## 7. Conditional Access — coverage gaps

No named locations, CA coverage incomplete per your snapshot.

**Required target set** (see `ssot/identity/entra_target_state.yaml#conditional_access.required_policies`):

- CA-001 `require_mfa_for_all_users`
- CA-002 `require_strong_mfa_for_admins`
- CA-003 `block_legacy_auth`
- CA-004 `risky_sign_in_response`
- CA-005 `risky_user_response`
- CA-006 `guest_mfa_required`

Break-glass accounts excluded from CA-001 only.

---

## 8. Secure Score lift plan

Current 43.77% → near-term 65% by executing:

1. Reduce GAs to 3 (~+5 pts)
2. Migrate off legacy MFA/SSPR (~+3 pts)
3. Require MFA for all users (~+4 pts)
4. Require MFA for admins (~+2 pts)
5. Risk-based CA (~+3 pts)
6. Restrict guest invite scope (~+1 pt)
7. Enable PIM on privileged roles (~+3 pts)

Estimates are indicative; actual deltas per Secure Score calculator.

---

## 9. Remediation order (dependency-safe)

1. **Codify SSOT** — THIS PR (no live changes).
2. Create guest groups (Step 1 of onboarding runbook) — additive, safe.
3. Bulk-invite 11 TBWA\SMP guests + assign to groups — visible external action.
4. Verify PIM eligibility on `BreakGlass-Admin-01/02`; create `jake.admin@` with PIM-eligible GA.
5. Test break-glass recovery with new accounts.
6. Remove duplicate break-glass accounts (3 of them).
7. Remove mailbox-UPN Entra users (`ceo@`, `finance@`, `admin@` after migration, `devops@` after SP conversion).
8. Reduce GAs to 3.
9. Implement CA-001 through CA-006 with `emergency-access-01/02` in exclusion.
10. Complete authentication methods migration.
11. Enterprise apps + SPs audit + naming normalization (separate PR).

Steps 2–11 are executed changes and each requires its own evidence bundle.

---

## Appendix A — Raw data captured

- User list JSON: `/tmp/entra_users_20260419.json`
- GA role ID: `25fc5549-4496-42f6-96cf-92effad8e76b`
- Total SPs (Application type): 378
- Canonical-named SPs: 0
