# Evidence Manifest - Cash Advance UAT Prompt

## Scope

- Added reusable automated UAT prompt for the cash advance / travel advance equivalent.
- Target spec bundle: `spec/expense-liquidation-agent`.
- SAP Concur is benchmark-only unless an explicit SAP Concur sandbox is configured.

## Files

| File | Purpose |
| --- | --- |
| `agent-prompt.md` | Copy of the reusable UAT prompt added under the spec bundle. |
| `repo_health.txt` | Repository health check output. |
| `spec_validate.txt` | Spec bundle validation output. |
| `ci_local.txt` | Local CI wrapper output. |
| `git-status-scoped.txt` | Scoped git status for changed prompt and evidence files. |

## Verification Summary

| Check | Result |
| --- | --- |
| `./scripts/repo_health.sh` | PASS |
| `./scripts/spec_validate.sh` | PASS with 5 pre-existing unrelated warnings |
| `./scripts/ci_local.sh` | PASS |

## Notes

- No production credentials were used.
- No production payment or ERP mutation was attempted.
- No SAP Concur sandbox was assumed or accessed.
