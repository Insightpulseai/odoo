# IPAI Agent Factory V2: Evidence Manifest

A deterministic index of all artifacts, verifications, and proofs generated during the V2 Pilot.

| Artifact Name | Workstream | Evidence Type | Status | Source Path | Generated Timestamp | Verifier |
|---|---|---|---|---|---|---|
| `SIGN_OFF_PACK.md` | Core | Executive Decision | **READY** | `docs/SIGN_OFF_PACK.md` | 2026-03-21T05:10 | IPAI Agent |
| `CREDENTIAL_GUIDE.md` | Platform | Operational Auth | **READY** | `docs/setup/CREDENTIAL_GUIDE.md` | 2026-03-21T05:10 | IPAI Agent |
| `phase-29-verification.md` | Expense | Runtime Proof | **VERIFIED** | `docs/evidence/...` | 2026-03-21T01:25 | V2 Validator |
| `bank-reconciliation-acceptance.md` | Bank Recon | Stress Test Proof | **VERIFIED** | `brain/.../bank-reconciliation-acceptance.md` | 2026-03-20T22:15 | Red-Team |
| `ap-invoice-board.md` | AP Invoice | Lifecycle Audit | **READY** | `brain/.../ap-invoice-board.md` | 2026-03-20T18:40 | IPAI Auditor |
| `test_expense_liquidation_flow.py` | Expense | Verification Code | **PASS** | `scripts/test_expense_liquidation_flow.py` | 2026-03-21T01:20 | Python 3.x |
| `seed_finance_ppm_full.py` | Finance | Operational Seeder | **READY** | `scripts/seed_finance_ppm_full.py` | 2026-03-21T07:55 | Python 3.x |
| `ODOO_CANONICAL_SCHEMA.dbml` | Core | Schema Evidence | **GENERATED** | `docs/data-model/ODOO_CANONICAL_SCHEMA.dbml` | 2026-03-21T08:26 | DBML |
| `ODOO_MODULE_DELTAS.md` | Core | ORM Mapping | **VERIFIED** | `docs/data-model/ODOO_MODULE_DELTAS.md` | 2026-03-21T08:26 | Report |
| `factory_v2_validator.py` | Core | Governance Agent | **PASS** | `scripts/factory_v2_validator.py` | 2026-03-20T15:30 | Release Gate |

**Notes**:
- All `brain/` paths refer to the conversation-id: `706fb290-55e8-41c0-82d6-358506acd2c3`.
- Evidence status indicates that the repo-level validation is complete; production-level validation remains a Go-Live constraint.
