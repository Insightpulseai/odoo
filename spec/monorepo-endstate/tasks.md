# Monorepo End-State — Task Breakdown

**Status**: Active
**Source**: plan.md

---

## Task Group 1: Audit

### 1.1 List EE-only features
- **Owner**: Engineering
- **Input**: Odoo 19 Enterprise docs, internal feature wishlist
- **Output**: Raw list of desired EE features (markdown)
- **Acceptance**: >=20 features listed

### 1.2 Map to OCA alternatives
- **Owner**: Engineering
- **Input**: Output of 1.1 + OCA GitHub org (v19 branch)
- **Output**: Mapping table: EE feature -> OCA module name (or "no equivalent")
- **Acceptance**: Every feature from 1.1 has a mapping attempt

### 1.3 Populate parity matrix (initial)
- **Owner**: Engineering
- **Input**: Outputs of 1.1 and 1.2
- **Output**: `ssot/parity/ee_to_oca_matrix.yaml` with >=10 entries
- **Acceptance**: YAML validates against schema `ssot.parity.ee_to_oca.v1`

### 1.4 Mark gap types
- **Owner**: Engineering
- **Input**: Output of 1.3
- **Output**: Each matrix entry has `gap_type`: `oca_available | ipai_bridge | no_alternative`
- **Acceptance**: No empty `gap_type` fields in matrix

---

## Task Group 2: Bridge Registry

### 2.1 Audit ipai_* modules for external integrations
- **Owner**: Engineering
- **Command**: `grep -rl "http\|requests\|aiohttp\|urllib" addons/ipai/`
- **Output**: List of modules with external dependencies

### 2.2 Populate bridge catalog
- **Owner**: Engineering
- **Input**: Output of 2.1
- **Output**: `ssot/bridges/catalog.yaml` with all active bridges
- **Acceptance**: Every external integration has a catalog entry

### 2.3 Create MAIL_BRIDGE_CONTRACT.md
- **Path**: `docs/contracts/MAIL_BRIDGE_CONTRACT.md`
- **Content**: Provider (Zoho), auth (OAuth2), env vars, failure behavior, SLA
- **Acceptance**: File exists, references `ssot/secrets/registry.yaml` entries

### 2.4 Create AI_BRIDGE_CONTRACT.md
- **Path**: `docs/contracts/AI_BRIDGE_CONTRACT.md`
- **Content**: Provider (Google Gemini), model, env vars, rate limits, fallback
- **Acceptance**: File exists, references `GEMINI_API_KEY` in secrets registry

### 2.5 Create OCR_BRIDGE_CONTRACT.md
- **Path**: `docs/contracts/OCR_BRIDGE_CONTRACT.md`
- **Content**: Provider (PaddleOCR self-hosted), endpoint, auth, failure behavior
- **Acceptance**: File exists and linked from bridge catalog

### 2.6 Verify bridge completeness
- **Script**: `scripts/ci/check_bridges_complete.py` (future task)
- **Manual check**: `grep 'status: active' ssot/bridges/catalog.yaml` -- all have contract docs

---

## Task Group 3: CI Gate (EE Parity)

### 3.1 Create ee-parity-gate.yml
- **Path**: `.github/workflows/ee-parity-gate.yml`
- **Trigger**: `pull_request` targeting `main`
- **Scan**: `addons/ipai/**/*.py` for `from odoo.addons.enterprise` or `odoo.addons.account_accountant`

### 3.2 Gate -- import scanner
- **Pattern to block**: `from odoo\.addons\.(enterprise|sale_management_enterprise|account_accountant)`
- **Exemption**: Line contains `# ee-parity-exempt`

### 3.3 Gate -- manifest scanner
- **Pattern to block**: Enterprise module names in `depends` list of `__manifest__.py`
- **Reference list**: Maintain in `.github/ci/ee_module_list.txt`

### 3.4 Run gate on PRs
- **Acceptance**: Gate passes on `main` at time of creation
- **Test**: Verify gate would fail if `from odoo.addons.enterprise` added to any ipai module

### 3.5 Document exemption mechanism
- **Doc path**: `docs/ai/CI_WORKFLOWS.md` (add section)
- **Content**: How to add `# ee-parity-exempt` and when it's acceptable

---

## Task Group 4: Documentation

### 4.1-4.5: Verification tasks
Each task is a verification step (read existing doc, confirm it meets acceptance criteria).
If doc is incomplete, extend it.

| Task | File | Acceptance |
|------|------|-----------|
| 4.1 | `docs/architecture/MONOREPO_END_STATE_OKR.md` | All 4 OKRs with KRs |
| 4.2 | `docs/architecture/AI_PROVIDER_BRIDGE.md` | Provider table + route contract |
| 4.3 | `docs/runbooks/SECRETS_SSOT.md` | All 3 approved stores documented |
| 4.4 | `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Sections A-H present |
| 4.5 | `docs/ai/SSOT.md` | References to all new SSOT registries |

---

## Task Group 5 (Future): Automation

- 5.1 Script: `scripts/ci/check_bridges_complete.py` -- validates every active bridge has contract doc
- 5.2 Script: `scripts/parity/generate_matrix_report.py` -- generate human-readable gap report from matrix
- 5.3 Workflow: Monthly parity review trigger via GitHub Actions scheduled workflow
