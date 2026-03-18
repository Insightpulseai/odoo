# SKILL: Validate Odoo Module Against Odoo19 KB

## Skill ID

validate-odoo-module-against-kb

## Skill Type

Procedural (Deterministic)

## Risk Level

LOW

## Requires Approval

false

## Purpose

Run deterministic validation of an Odoo addon/module (Python + XML + JS) against:

- Odoo 19 documentation KB (vendored + pinned)
- Repo policies (no UI steps, deterministic paths, CE/OCA constraints)
- Style + correctness checks that do NOT require expensive models

Produces a machine-readable validation report and audit evidence.

---

## Preconditions (MUST ALL BE TRUE)

1. `docs/kb/odoo19/UPSTREAM_PIN.json` exists
2. KB pin integrity is valid (must pass `verify_odoo_docs_pin.py`)
3. Index artifacts exist and are non-empty:
   - `docs/kb/odoo19/index/manifest.json`
   - `docs/kb/odoo19/index/sections.json`
   - `docs/kb/odoo19/index/topics.json`
4. Module path exists and contains `__manifest__.py`
5. Validator script exists: `scripts/kb/validate_module_against_kb.py`

If any precondition fails → abort.

---

## Inputs

```yaml
module_path: string                # e.g. addons/ipai/ipai_docflow_review
odoo_version: "19.0"
profile: "strict" | "default"      # strict = fail on warnings
```

---

## Hard Rules (NON-NEGOTIABLE)

- ❌ Never validate against live upstream docs; only vendored KB
- ❌ Never run without KB pin verification
- ❌ Never write results into module directory
- ✅ Always produce evidence under `docs/evidence/...`

---

## Execution Steps (ORDER IS MANDATORY)

### Step 1 — Evidence Run Folder

Create:
`docs/evidence/<YYYY-MM-DD>/kb/validate/<run_id>/`

Record:

- inputs.json
- repo_git_head.txt
- kb_pin.json (copy)
- kb_pinned_commit.txt

---

### Step 2 — Verify KB Pin Integrity

Run:
`python3 scripts/kb/verify_odoo_docs_pin.py`

Fail on any mismatch.

---

### Step 3 — Validate Module Against KB

Run:
`python3 scripts/kb/validate_module_against_kb.py --module <module_path> --profile <profile>`

Validator MUST emit:

- `validation_report.json`
- `validation_summary.md`

Report schema (minimum):

```json
{
  "schema_version": "1.0.0",
  "module": { "path": "...", "name": "...", "version": "..." },
  "kb": { "pinned_commit": "..." },
  "results": {
    "errors": [],
    "warnings": [],
    "info": []
  },
  "checks": [
    { "id": "MANIFEST_PRESENT", "status": "pass|fail", "details": {} },
    { "id": "MANIFEST_KEYS", "status": "pass|fail|warn", "details": {} },
    { "id": "SECURITY_ACCESS_CSV", "status": "pass|fail|warn", "details": {} },
    { "id": "SECURITY_RULES", "status": "pass|fail|warn", "details": {} },
    { "id": "ORM_API_USAGE", "status": "pass|fail|warn", "details": {} },
    { "id": "VIEWS_XML_VALID", "status": "pass|fail|warn", "details": {} },
    { "id": "ACTIONS_WIRING", "status": "pass|fail|warn", "details": {} },
    { "id": "OWL_ASSETS", "status": "pass|fail|warn", "details": {} },
    { "id": "PERF_SMELLS", "status": "pass|fail|warn", "details": {} }
  ]
}
```

---

### Step 4 — Post-Validation Gates

- If profile=strict: any warning → fail
- Else: errors → fail; warnings allowed

---

### Step 5 — Write Evidence Outputs

Copy artifacts into evidence folder:

- validation_report.json
- validation_summary.md

Also write:

- final_status.json (success/fail + reason)

---

## Allowed LLM Routing

Local SLM allowed ONLY for:

- log classification
- summarizing validation output

No model (or local) required for checks. Validation is deterministic.

---

## Failure Modes

- KB pin mismatch → fail
- Missing manifest → fail
- Invalid XML → fail
- Missing security files when models exist → warn/fail (profile dependent)

---

## Postconditions

On success:

- Evidence exists
- Module passes KB-aligned structural + security + wiring checks
