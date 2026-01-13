# PROD Sandbox Scan Runbook (Odoo 18 CE + OCA)

Working directory: `/Users/tbwa/Downloads/extracted_files/odoo-dev-sandbox`

## 0. Role

You are a Claude/Codex-style coding agent operating inside this local repo sandbox.
Goal: determine EXACTLY what needs to be installed/enabled to reproduce this working Odoo 18 CE sandbox state (and later apply to prod) with minimal custom modules.

Constraints:

- Odoo 18 CE + OCA-first approach.
- Treat any previously created custom modules as **data/import/config assets** whenever possible.
- Prefer configuration-as-code under `data/seed/` and deterministic scripts.
- No UI/manual steps. Everything must be verifiable via CLI.
- Output must be actionable and copy/paste-ready.

## 1. Read and summarize repo-level install/runtime files

Files of interest:

- `docker-compose.yml` / `compose.yaml`
- `README.md` / `STATUS.md` / `EXECUTE_WHEN_DOCKER_STARTS.md`
- `scripts/run_prod_canonical_setup.sh` and any `scripts/*` it calls
- `requirements.txt` / `pyproject.toml` (if present)
- `addons/ipai/ipai_hello/__manifest__.py` and any `ipai_*` manifests
- `data/seed/*.py` (`00_project_stages.py`, `01_menu_cleanup.py`, `02_mail_posture.py`, `99_verify.py`, etc.)

First, prove what actually exists:

```bash
cd /Users/tbwa/Downloads/extracted_files/odoo-dev-sandbox

ls -la
find . -maxdepth 3 -type f \( \
  -name "EXECUTE_WHEN_DOCKER_STARTS.md" -o \
  -name "README_PROD_CANONICAL.md" -o \
  -name "PROD_CANONICAL_INSTALL_REQUIREMENTS.md" -o \
  -name "PROD_CANONICAL_INSTALL_REQUIREMENTS.json" -o \
  -name "docker-compose.yml" -o -name "compose.yaml" -o \
  -path "./scripts/*" -o -path "./data/seed/*" -o \
  -path "./addons/*/*/__manifest__.py" \
\) | sort
```

## 2. Inventory Odoo modules referenced by custom addons

Truth source = manifests:

```bash
python3 - <<'PY'
import glob, ast, os, json
mods = []
for mf in glob.glob("addons/**/**/__manifest__.py", recursive=True):
    try:
        d = ast.literal_eval(open(mf, "r", encoding="utf-8").read())
        mods.append({"path": mf, "name": d.get("name"), "depends": d.get("depends", [])})
    except Exception as e:
        mods.append({"path": mf, "error": str(e)})
print(json.dumps(mods, indent=2))
PY
```

From this, derive:

* Minimal base Odoo modules that MUST be installed.
* OCA modules needed to support those dependencies.

## 3. Inventory models touched by seed scripts

Models imply functional dependencies:

```bash
python3 - <<'PY'
import glob, re, json
hits = []
for f in sorted(glob.glob("data/seed/*.py")):
    s = open(f,"r",encoding="utf-8").read()
    models = sorted(set(re.findall(r"env\\[['\\\"]([a-z0-9_.]+)['\\\"]\\]", s)))
    ircfg  = "ir.config_parameter" in s
    hits.append({"file": f, "models": models, "touches_ir_config_parameter": ircfg})
print(json.dumps(hits, indent=2))
PY
```

Use this to refine:

* Required core modules.
* Any implied automation/config modules.

## 4. Minimal Install Set (structure)

Produce a Minimal Install Set with three sections:

A) **Docker prerequisites**

* Services, ports, volumes, env vars coming from `docker-compose.yml`.

B) **Odoo base modules (CE)**

* List of core modules that MUST be installed (e.g. `project`, `mail`, etc.).

C) **OCA modules**

* OCA repos and modules that replace enterprise features.
* Explicit install order.

## 5. Detect enterprise-only dependencies

Scan manifests + seed scripts for enterprise-like modules:

* e.g. `web_enterprise`, `account_accountant`, `sign`, `documents`, etc.

For each, either:

* Map to CE/OCA replacement, or
* Mark "no replacement needed" if droppable.

## 6. Generate the canonical requirements outputs

Use a generator script (see `tools/generate_prod_canonical_requirements.py`) to create:

* `docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.md`
* `docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.json`

These MUST include:

* Required installs (packages/modules).
* Optional installs (nice-to-have).
* "Enterprise-only detected" table with replacements.
* Installation order checklist.
* Verification commands and expected PASS outputs.

## 7. Rules / Assumptions

* Do NOT ask questions.
* If something is missing, infer best defaults and mark assumptions explicitly.
* Only include what is truly required to reproduce current sandbox behavior.
* That agent summary is **not trustworthy** unless the files actually exist in the repo.
  Don't bless narrative; bless deterministic scans.

## 8. Workflow Integration

This runbook integrates with:

1. **CLAUDE.md** - High-level behavior contract + shortcuts
2. **tools/generate_prod_canonical_requirements.py** - Executable generator
3. **docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.{md,json}** - Output artifacts
4. **CI Guardian** (optional) - `.github/workflows/prod_canonical_guard.yml`

## 9. CI Guardian (Optional)

To prevent drift, add continuous verification:

```yaml
# .github/workflows/prod_canonical_guard.yml
name: Prod Canonical Guard

on:
  push:
    paths:
      - 'addons/**'
      - 'data/seed/**'
      - 'docker-compose.yml'
      - 'compose.yaml'
      - 'tools/generate_prod_canonical_requirements.py'

jobs:
  regen-and-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python tools/generate_prod_canonical_requirements.py
      - run: git diff --exit-code docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.*
```

This ensures generated artifacts stay in sync with repo state.

## 10. Verification Checklist

Before blessing any sandbox → prod baseline:

- [ ] `docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.md` exists
- [ ] `docs/PROD_CANONICAL_INSTALL_REQUIREMENTS.json` exists
- [ ] Generator script just ran successfully
- [ ] No uncommitted changes to manifests/seeds
- [ ] All enterprise conflicts identified and mapped to OCA
- [ ] Installation order verified in test environment
- [ ] Seed scripts execute without errors
- [ ] Verification commands all return PASS

## 11. Related Documentation

- **CLAUDE.md** - Sandbox → Prod section (behavior contract)
- **ENVIRONMENTS.md** - Prod repo vs sandbox roles
- **ENTERPRISE_TO_OCA_MAPPING.md** - Enterprise conflict resolutions
- **PROD_BASELINE_POLICY.md** - Acceptance gate policy
