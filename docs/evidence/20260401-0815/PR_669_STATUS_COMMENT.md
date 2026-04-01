## Activation status update — #644 / #647 / #649

All three governance items are now **live** with Azure-backed evidence.

### Current status

| Work item | Status | Notes |
|---|---|---|
| #644 PIM governance | **`live`** | 3 PIM eligible assignments verified (Contributor on runtime + data RGs, Owner on subscription). KV Secrets Officer deferred — `kv-ipai-dev` not provisioned. Script fixes: tenant ID + API version corrected. |
| #647 Azure Policy / tag governance | **`live`** | Deployed 2026-04-01T08:44:41Z. 3 assignments in audit-only mode (`DoNotEnforce`) on `rg-ipai-dev-odoo-runtime`. Policy ID corrected to `871b6d14-10aa-478d-b590-94f262ecfa99`. |
| #649 Well-Architected Review | **`live`** | Live Azure-backed run 2026-04-01T09:02:36Z. Score: 86% (13 pass, 1 warn, 1 fail, 3 skip). 1 FAIL = ACA not zone-redundant (dev tier, acceptable). |

### Completed steps

1. ~~Activate #647 first in non-blocking mode and capture assignment/compliance evidence.~~ **Done.**
2. ~~Resolve Entra prerequisites for #644, run dry-run, then activate.~~ **Done.** Groups exist, dry-run passed, live activation confirmed 3/4 assignments.
3. ~~Re-run #649 against live Azure context.~~ **Done.** Live score matches baseline (86%).
4. ~~Update evidence and statuses.~~ **Done.**

### Merge gate

- [x] #647 has live deployment evidence
- [x] #644 has dry-run + live PIM eligible assignments verified (3/4; KV deferred)
- [x] #649 has live Azure-backed WAR evidence

### Evidence directory

- `docs/evidence/20260401-0815/policy/` — **live** (deployment output, assignments, compliance snapshot)
- `docs/evidence/20260401-0815/pim/` — **live** (prereqs, dry-run, live output, result summary)
- `docs/evidence/20260401-0815/war/` — **live** (live output, summary, baseline comparison)

### Known gaps (not blockers)

- `kv-ipai-dev` Key Vault not provisioned — KV Secrets Officer PIM assignment deferred
- PIM activation policies (duration caps, MFA enforcement) not configured via `roleManagementPolicies` API
- Front Door profile name mismatch in WAR script (cosmetic skip, not a real gap)
- Defender for Cloud pricing tier query needs elevated permissions

### Reviewer note

All three items have **live Azure-backed evidence**. This PR is ready for merge review.
