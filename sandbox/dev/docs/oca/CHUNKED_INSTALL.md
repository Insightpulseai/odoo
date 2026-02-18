# OCA Chunked Installation Guide

## Problem

Agent execution timeouts (typically 3 minutes) can interrupt long-running OCA module installations, leaving modules in partial states.

## Solution

**Chunked, idempotent installer** that breaks installations into small batches with resumable progress.

---

## Quick Start

### 1. Install Web + REST Baseline

```bash
# From repository root
cd sandbox/dev

# Stop Odoo
docker-compose stop odoo

# Install in chunks of 2 modules
docker-compose run --rm odoo bash -c "
  /mnt/extra-addons/scripts/odoo/install_modules_chunked.sh \
    --db odoo_dev \
    --modules 'web_responsive,web_environment_ribbon,web_dialog_size' \
    --chunk 2
"

# Start Odoo
docker-compose up -d odoo
```

### 2. Check Module States

```bash
docker-compose exec db psql -U odoo -d odoo_dev -c "
  SELECT name, state
  FROM ir_module_module
  WHERE name IN ('web_responsive', 'web_environment_ribbon', 'web_dialog_size')
  ORDER BY name;"
```

---

## Module Sets

Pre-defined module lists in `config/oca/module_sets/`:

### `web_and_rest.txt`

**Web UX enhancements:**
- `web_responsive` - Mobile-friendly responsive layout
- `web_environment_ribbon` - Environment indicator ribbon (dev/staging/prod)
- `web_dialog_size` - Resizable dialogs

**REST API framework:**
- `base_rest` - REST API framework (requires Python deps)
- `base_rest_datamodel` - Data model integration

---

## Troubleshooting

### Module Shows "uninstallable"

Run the external dependencies report:

```bash
docker-compose exec odoo python3 /mnt/extra-addons/scripts/odoo/external_deps_report.py /mnt/oca > deps.json
cat deps.json | python3 -m json.tool | grep -A 5 "module_name"
```

### Install Missing Python Dependencies

Example for `base_rest`:

```bash
# Install Python packages
docker-compose exec odoo pip install apispec cerberus parse-accept-language pyquerystring

# Retry module installation
docker-compose stop odoo
docker-compose run --rm odoo odoo -d odoo_dev --stop-after-init -u "base_rest"
docker-compose up -d odoo
```

### Installation Timeout

**Reduce chunk size:**

```bash
# Use --chunk 1 for modules with heavy asset rebuilds
--chunk 1
```

---

## Scripts Reference

### `scripts/odoo/install_modules_chunked.sh`

**Purpose:** Install Odoo modules in small, timeout-safe batches

**Parameters:**
- `--db <name>` - Database name (required)
- `--modules <csv>` - Comma-separated module list (required)
- `--chunk <n>` - Modules per batch (default: 5)

**Features:**
- Uses `-u` (upgrade) flag for idempotent reruns
- Stops server after each batch (`--stop-after-init`)
- Produces SQL summary from `ir_module_module`

### `scripts/odoo/external_deps_report.py`

**Purpose:** Scan manifests for external dependencies

**Usage:**
```bash
python3 scripts/odoo/external_deps_report.py /path/to/addons > deps.json
```

**Output Format:**
```json
{
  "python": {
    "module_name": ["package1", "package2"]
  },
  "bin": {
    "module_name": ["binary1", "binary2"]
  }
}
```

---

## Evidence and Validation

Each installation run should capture:

1. **Installer output** - Commands executed and results
2. **Module states** - Final states from `ir_module_module`
3. **State summary** - Overall database state (installed/uninstallable/uninstalled counts)
4. **Dependencies report** - External deps for uninstallable modules

**Example Evidence Structure:**
```
docs/evidence/YYYYMMDD-HHMM/oca-chunked-install/
├── SUMMARY.md                   # Human-readable summary
├── installer_output.log         # Command output
├── module_states.txt            # Target module states
├── state_summary.txt            # Overall state counts
└── external_deps_report.json    # Dependency analysis
```

---

## Best Practices

1. **Start Small:** Use `--chunk 2` for first installs to identify issues quickly
2. **Check Dependencies:** Run external deps report before installing uninstallable modules
3. **Idempotent Reruns:** Safe to rerun with same module list - uses `-u` flag
4. **Evidence First:** Always capture evidence for reproducibility
5. **Incremental Progress:** Install core modules first, then expand based on needs

---

## Integration with CI/CD

For automated deployments, use the chunked installer in CI pipelines:

```yaml
# Example GitHub Actions step
- name: Install OCA baseline modules
  run: |
    docker-compose run --rm odoo bash -c "
      /mnt/extra-addons/scripts/odoo/install_modules_chunked.sh \
        --db \${{ secrets.DB_NAME }} \
        --modules \$(cat config/oca/module_sets/web_and_rest.txt | grep -v '^#' | tr '\n' ',') \
        --chunk 3
    "
```

---

## See Also

- [OCA Module Aggregation](../oca-aggregate.yml)
- [Database Hardening](../spec/db-hardening/)
- [Evidence Capture Guidelines](../docs/evidence/README.md)
