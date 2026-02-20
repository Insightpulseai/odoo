# OCA Porting Toolchain Documentation

> Official OCA tooling reference for Odoo 19.0 module migration

---

## Core Tools

### 1. `oca-port` CLI (Primary Migration Tool)

**Purpose**: Automated migration assistant for OCA modules

**Installation**:
```bash
pip3 install oca-port
```

**Usage**:
```bash
oca-port <addon-name> --from <source-version> --to <target-version> --repo OCA/<repo-name>
```

**Example**:
```bash
oca-port server_environment --from 18.0 --to 19.0 --repo OCA/server-tools
```

**Capabilities**:
- Automated git branch creation (`port/<addon>/<from>-to-<to>`)
- OpenUpgrade script application
- `__manifest__.py` version updates
- Conventional commit message generation

**Reference**: https://pypi.org/project/oca-port/

---

### 2. OpenUpgrade (Migration Data & Scripts)

**Purpose**: Community-maintained migration guides and scripts for Odoo version upgrades

**Repository**: https://github.com/OCA/OpenUpgrade

**Key Components**:
- **Migration scripts**: SQL and Python scripts for data transformation
- **API change documentation**: Comprehensive changelog of Odoo API changes
- **Field mapping**: Old → new field name mappings

**Usage** (via `oca-port`):
- Automatically applied when migration exists in OpenUpgrade database
- Manual consultation for undocumented migrations

**Reference**:
- Migration guides: https://github.com/OCA/OpenUpgrade/tree/19.0/openupgrade_scripts
- API changes: https://github.com/OCA/OpenUpgrade/blob/19.0/docsource/api_changes.rst

---

### 3. OCA Maintainer Tools

**Purpose**: Quality validation and development workflow tools

**Repository**: https://github.com/OCA/maintainer-tools

**Key Tools**:
- `pre-commit` hooks (code quality enforcement)
- `oca-gen-addon-readme` (README generation)
- `oca-towncrier` (changelog management)

**Installation**:
```bash
pip3 install pre-commit
cd /path/to/oca/repo
pre-commit install
```

**Reference**: https://github.com/OCA/maintainer-tools#readme

---

## Workflow Integration

### Standard Port Workflow

```
1. oca-port (automated migration)
     ↓
2. Smoke tests (load + install)
     ↓
3. pre-commit hooks (code quality)
     ↓
4. Evidence capture (logs + status)
     ↓
5. Update port_queue.yml
     ↓
6. Commit & push
     ↓
7. [Optional] PR to OCA upstream
```

### Branch Naming Convention

**Pattern**: `port/<addon>/<from>-to-<to>`

**Examples**:
- `port/server_environment/18.0-to-19.0`
- `port/connector/18.0-to-19.0`
- `port/account_statement_import_base/18.0-to-19.0`

**Rationale**: OCA convention for migration branches, ensures clarity and searchability.

---

## Evidence Capture Requirements

Every port must produce:

1. **Port log**: `web/docs/evidence/<timestamp>/oca-port-<module>/logs/port.log`
2. **Install log**: `web/docs/evidence/<timestamp>/oca-port-<module>/logs/install.log`
3. **Status document**: `web/docs/evidence/<timestamp>/oca-port-<module>/STATUS.md`
4. **Patch (if manual changes)**: `web/docs/evidence/<timestamp>/oca-port-<module>/patch/<module>.patch`

**Timestamp format**: `YYYYMMDD-HHMM+0800` (Asia/Manila timezone)

---

## Acceptance Checklist

Before marking module as "completed":

- [ ] `oca-port` completed without errors (or manual migration documented)
- [ ] Module directory exists in correct OCA repo path
- [ ] `__manifest__.py` version is `19.0.x.y.z`
- [ ] No Python syntax errors (`python3 -m py_compile`)
- [ ] Module loads in Odoo shell
- [ ] Module installs without errors
- [ ] Evidence directory created with all required logs
- [ ] Port queue status updated
- [ ] Commit follows OCA conventions

---

## Common Issues & Solutions

### Issue: `oca-port` not found

**Solution**:
```bash
pip3 install --upgrade oca-port
which oca-port
# Expected: /usr/local/bin/oca-port or similar
```

### Issue: OpenUpgrade migration not found

**Solution**: Manual migration required. Consult:
1. Odoo 19.0 changelog: https://www.odoo.com/documentation/19.0/developer/howtos/upgrade.html
2. OCA community forum: https://github.com/OCA/OpenUpgrade/discussions
3. Manual patch creation

### Issue: Pre-commit hooks fail

**Solution**:
```bash
# Run hooks manually
pre-commit run --all-files

# Common fixes:
# - black formatting
# - isort import sorting
# - flake8 linting
```

---

## References

- **oca-port PyPI**: https://pypi.org/project/oca-port/
- **OpenUpgrade GitHub**: https://github.com/OCA/OpenUpgrade
- **OCA Maintainer Tools**: https://github.com/OCA/maintainer-tools
- **OCA Migration Wiki**: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-X.0
- **Odoo 19.0 Migration Guide**: https://www.odoo.com/documentation/19.0/developer/howtos/upgrade.html
