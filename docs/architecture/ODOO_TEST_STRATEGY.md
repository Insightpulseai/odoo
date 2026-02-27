# Odoo 19 Testing Strategy

> Coverage matrix, layer definitions, and tagging conventions for `ipai_*` modules.
> Related: `docs/runbooks/ODOO_DEBUGPY.md` (debug vs test decision tree)

---

## Test layers

### Layer 1 — Pure Python (pytest, no Odoo)

No Odoo registry, no database, no ORM.  Runs on any machine with `pip install pytest requests`.

**When to use**: Functions that take plain Python values and return plain Python values.
Anything in `utils/`, standalone parsers, network I/O with mocked `requests`, CLI helpers.

**Speed**: Milliseconds per test.  Run on every save in your editor.

**How to run**:
```bash
# All pure-pytest tests in the repo
pytest addons/ipai/ -v --ignore=addons/ipai/ipai_expense_ocr/tests/test_hr_expense_digitize.py

# Single module
pytest addons/ipai/ipai_expense_ocr/tests/test_ocr_client.py -v
pytest addons/ipai/ipai_expense_ocr/tests/test_ocr_extract.py -v
```

---

### Layer 2 — Odoo TransactionCase

Uses the Odoo test runner.  Each test method runs inside a database transaction that is
rolled back at the end, so tests are isolated without needing a fresh DB per test.

**When to use**: Business logic that touches Odoo models (`self.env[...]`), ORM `create/write`,
computed fields, `ir.config_parameter`, `ir.attachment`, computed `name_get`, etc.

**Speed**: ~1-5 seconds per test (DB round-trips).  Run before pushing.

**How to run**:
```bash
# All tests tagged ipai_expense_ocr (TransactionCase + any others with the same tag)
python odoo-bin --test-enable --test-tags ipai_expense_ocr -d odoo_dev

# All post_install tests across all ipai modules
python odoo-bin --test-enable --test-tags post_install -d odoo_dev

# Specific module only
python odoo-bin --test-enable --test-tags ipai_expense_ocr -d odoo_dev \
  --stop-after-init
```

**TransactionCase vs SavepointCase**:

| Class | Isolation | Use when |
|-------|-----------|----------|
| `TransactionCase` | Full transaction rollback per test method | Most business logic; no `commit()` calls |
| `SavepointCase` | Savepoint per test (faster, shares setUp) | Read-heavy tests sharing expensive fixtures |
| `HttpCase` | Rolls back + spins up HTTP server | Client-side JS, tour tests, portal views |

---

### Layer 3 — Bash contract gates (CI scripts)

Self-contained shell scripts that verify infrastructure contracts without Docker or Odoo.
Output `PASS`/`FAIL` + exit codes usable by GitHub Actions.

**When to use**: Entrypoint behaviour, file presence, config consistency, env var contracts.

**Speed**: Sub-second.

**Examples**:
```bash
bash scripts/ci/check_debugpy_contract.sh     # exit-2 + silent-off contracts
bash scripts/ci/check_odoo_addons_path.sh     # addons-path SSOT consistency
```

---

### Layer 4 — ETL / data smoke (optional, DuckDB)

Lightweight validation of Iceberg/ETL pipeline outputs using DuckDB in-process.
No running Postgres required.

**When to use**: Verify that Iceberg parquet partitions are non-empty and schema-conformant
after a CDC replay.  Validate ETL TOML configs before deployment.

**Status**: Planned (Phase 2 of `spec/supabase-maximization/`).

---

## Tagging conventions

Odoo tags control which tests run on `--test-enable`.

```python
from odoo.tests import tagged

# Standard pattern for ipai_* modules
@tagged("ipai_<module_slug>", "-at_install", "post_install")
class TestFoo(TransactionCase):
    ...
```

| Tag | Meaning |
|-----|---------|
| `ipai_<slug>` | Module-specific selector (e.g. `ipai_expense_ocr`) |
| `-at_install` | Skip during `--install`; only run explicitly or via `post_install` |
| `post_install` | Run after all modules are installed (safe for cross-module tests) |
| `standard` | Odoo default; runs with `--test-enable` without explicit tags |

**Selector examples**:
```bash
# Run only OCR tests
--test-tags ipai_expense_ocr

# Run all ipai tests
--test-tags /ipai_

# Skip slow at_install tests
--test-tags -at_install
```

---

## Coverage matrix

| Module | Layer 1 (pytest) | Layer 2 (TransactionCase) | Layer 3 (bash gate) | Notes |
|--------|-----------------|--------------------------|--------------------|----|
| `ipai_expense_ocr` | `test_ocr_extract.py` (8), `test_ocr_client.py` (9) | `test_hr_expense_digitize.py` (T1–T6) | — | Full coverage |
| `ipai_debugpy_entrypoint` | — | — | `check_debugpy_contract.sh` (2 contracts) | Contract-only; no Odoo layer |
| `ipai_mail_bridge_zoho` | — | — | — | Needs Layer 2 (TODO) |
| `ipai_slack_connector` | — | — | — | Needs Layer 2 (TODO) |
| OCA modules | — (never modify OCA) | — | smoke only via `odoo_dev` install | OCA maintains own tests |

---

## Where tests live

```
addons/ipai/<module>/
└── tests/
    ├── __init__.py               # imports Odoo-layer tests; documents pytest tests
    ├── test_<unit>.py            # Layer 1 (pytest) — pure Python, no Odoo
    └── test_<feature>_<model>.py # Layer 2 (TransactionCase) — Odoo ORM
```

**`__init__.py` pattern**:
```python
# Layer 1 tests (pytest) are NOT imported here — pytest discovers them directly.
# Layer 2 tests (Odoo runner) must be imported here to be discoverable.
from . import test_hr_expense_digitize
```

---

## CI integration

| Workflow | Trigger | Runs |
|----------|---------|------|
| `debugpy-contract.yml` | PR / push / merge_group (path-filtered) | Layer 3: `check_debugpy_contract.sh` |
| `odoo-addons-path-guard.yml` | PR / push (path-filtered) | Layer 3: `check_odoo_addons_path.sh` |
| _(planned)_ `ipai-pytest.yml` | PR / push on `addons/ipai/**` | Layer 1: `pytest addons/ipai/ --ignore=*TransactionCase*` |
| _(planned)_ `ipai-odoo-tests.yml` | PR / push on `addons/ipai/**` | Layer 2: `python odoo-bin --test-enable --test-tags /ipai_ -d odoo_dev` |

---

## Anti-patterns to avoid

| Anti-pattern | Why | Alternative |
|-------------|-----|-------------|
| Asserting inside `try/except` that swallows the assertion | Silently passes on broken code | Use `assertRaises` context manager |
| Patching at the wrong level (`requests` instead of `module.function`) | Mock doesn't intercept | Patch the name used at call site |
| Testing OCA internals directly | OCA maintains its own tests | Test only your `_inherit` overrides |
| `sleep()` in tests | Flaky in CI | Mock time or use `freeze_gun` |
| Committing `.pyc` test artefacts | Noise in git | `.gitignore` covers `__pycache__/` |
| Running Layer 2 tests without `--stop-after-init` in scripts | Odoo stays running | Add `--stop-after-init` in CI |
