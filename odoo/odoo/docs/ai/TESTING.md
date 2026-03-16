# Testing
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Odoo Tests

```bash
# Run all tests
./scripts/ci/run_odoo_tests.sh

# Run tests for specific module
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm

# Smoke tests
./scripts/ci_smoke_test.sh
```

## Python Linting

```bash
black --check addons/ipai/
isort --check addons/ipai/
flake8 addons/ipai/
python3 -m py_compile addons/ipai/**/*.py
```

## Node.js

```bash
npm run lint
npm run typecheck
npm run build
```
