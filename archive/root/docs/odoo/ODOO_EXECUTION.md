# Odoo Execution Patterns

**Quick Reference** for running Odoo in this repository.

---

## ✅ Correct Patterns

| Command | When to Use | Requirements |
|---------|-------------|--------------|
| `./scripts/odoo.sh` | **✅ Recommended** - Auto-detects environment | Bash, Python in PATH |
| `./odoo-bin` | Direct execution (requires proper Python setup) | Bash, `odoo` module available |
| `python -m odoo` | Module invocation | `pip install odoo==19.0` |
| `docker compose exec odoo-core odoo` | Container-based | Docker running |

## ❌ Wrong Pattern

| Command | Error | Why It Fails |
|---------|-------|--------------|
| `python odoo-bin` | `SyntaxError: invalid syntax` | `odoo-bin` is a **bash script**, not Python |
| `python3 odoo-bin` | `SyntaxError: invalid syntax` | Same issue (bash ≠ Python) |

---

## Examples

### Start Odoo in Development Mode

```bash
./scripts/odoo.sh -d odoo_dev -c config/odoo_ide.toml
```

### Run Tests

```bash
./scripts/odoo.sh -d odoo_test --test-enable --stop-after-init
```

### Install Modules

```bash
./scripts/odoo_install_modules.sh -d odoo_dev -m ipai_finance_ppm,ipai_ai_tools
```

### Update Modules

```bash
./scripts/odoo.sh -d odoo_dev -u ipai_finance_ppm,ipai_ai_tools
```

### Shell Mode (for debugging)

```bash
./scripts/odoo.sh shell -d odoo_dev
```

---

## Troubleshooting

### Error: `SyntaxError: invalid syntax` when running Odoo

**Cause**: You tried to run `python odoo-bin` (wrong - odoo-bin is bash)

**Fix**: Use one of these instead:
- `./odoo-bin` (direct bash execution)
- `./scripts/odoo.sh` (recommended - auto-detects environment)
- `python -m odoo` (if odoo package installed via pip)

**Explanation**: The `odoo-bin` file in this repository is a bash wrapper script, not a Python file. When you run `python odoo-bin`, the Python interpreter tries to parse bash code and fails with `SyntaxError`.

### Error: `No module named odoo.__main__`

**Cause**: The `odoo` package is not installed via pip

**Fix**: Use `./scripts/odoo.sh` instead, which handles source-based installations

**Explanation**: This repository uses a source-based Odoo setup (development mode), not a pip-installed package. The `scripts/odoo.sh` launcher detects this and routes accordingly.

### Which pattern should I use?

**For daily development**: Use `./scripts/odoo.sh` - it's the canonical launcher that handles all environments

**For CI/CD**: Use `./odoo-bin` or `./scripts/odoo.sh` - both work in automated environments

**For container-based**: Use `docker compose exec odoo-core odoo` - standard Docker pattern

---

## Architecture Notes

### Why Three Patterns?

This repository supports multiple Odoo execution patterns to accommodate different development environments:

1. **`odoo-bin`** (bash shim): Lightweight wrapper for CI/CD and direct execution
2. **`scripts/odoo.sh`** (intelligent launcher): Auto-detects environment and routes appropriately
3. **Docker**: Container-based execution for production-like environments

### Which Is Canonical?

**`./scripts/odoo.sh`** is the recommended canonical launcher because it:
- Auto-detects source vs. pip installations
- Handles pyenv/virtualenv activation
- Provides consistent interface across environments
- Includes helpful error messages

### Upstream Compatibility

Note: Upstream Odoo (from odoo.com) ships `odoo-bin` as a **Python file**, not bash. This repository uses a **bash wrapper** for flexibility. If you're used to upstream patterns, be aware of this difference.

---

## VS Code Integration

The `.vscode/launch.json` configuration uses the **module invocation pattern**:

```json
{
  "name": "Odoo: Current File",
  "type": "python",
  "request": "launch",
  "module": "odoo",  // Correct - module invocation
  "args": ["-d", "odoo_dev", "-c", "config/odoo_ide.toml"]
}
```

This is correct and works with VS Code's Python debugger.

---

## References

- **Repository CLAUDE.md**: See main project contract for execution rules
- **scripts/lint_odoo_entrypoint.sh**: Linter that blocks wrong patterns
- **CI Validation**: `.github/workflows/ci.yml` enforces correct patterns

---

**Last Updated**: 2026-02-09
**Maintainer**: InsightPulse AI Engineering
