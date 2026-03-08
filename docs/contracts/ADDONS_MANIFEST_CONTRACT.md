# C-27 — Addons Manifest Contract

**File**: `docs/contracts/ADDONS_MANIFEST_CONTRACT.md`
**SSOT**: `config/addons.manifest.yaml`
**Consumers**: `docker/Dockerfile.unified`, `oca-aggregate.yml`, CI workflows
**Validator**: `addons-manifest-guard.yml` → `scripts/odoo/validate_addons_manifest.py`

---

## Purpose

Defines the curated set of OCA repositories and modules included in the
production Odoo runtime image (`ipai-odoo-runtime`). Prevents ad-hoc module
inclusion and ensures deterministic builds.

---

## Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Manifest schema version (currently `2`) |
| `odoo_version` | Yes | Target Odoo version (`19.0`) |
| `image_name` | Yes | Canonical image name (`ipai-odoo-runtime`) |
| `registries` | Yes | Target container registries (GHCR, ACR) |
| `pinning_policy` | Yes | `branch` (rolling) or `sha` (production freeze) |
| `addon_roots` | Yes | Ordered addon path targets in container |
| `oca_repositories[]` | Yes | Array of OCA repo entries |
| `ipai` | Yes | IPAI custom module configuration |
| `deprecated_repos[]` | No | Repos intentionally excluded with reason |

### OCA Repository Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `repo` | Yes | OCA GitHub repo name (e.g. `server-tools`) |
| `url` | Yes | Git clone URL |
| `ref` | Yes | Branch, tag, or commit SHA to pin |
| `tier` | Yes | Priority tier (0 = core infra → 9 = optional) |
| `purpose` | Yes | Why this repo is included |
| `must_have` | No | Specific modules required (null = all installable) |
| `excluded` | No | Modules explicitly excluded |

---

## Addon Path Precedence (SSOT Invariant)

```
1. /usr/lib/python3/dist-packages/odoo/addons   (Odoo CE core — implicit)
2. /opt/odoo/addons/oca                           (OCA curated, flattened)
3. /opt/odoo/addons/ipai                          (IPAI custom)
```

Odoo resolves modules in this order. A module name in OCA overrides CE core.
A module name in IPAI overrides OCA. This is the `_inherit` override chain.

**Never change this order.** The Dockerfile and `odoo.conf` both enforce it.

---

## Invariants

1. **Manifest is the only allowed source for OCA inclusion.** No OCA repo
   may appear in the Docker image unless it has an entry in
   `config/addons.manifest.yaml`.

2. **Manifest must stay in sync with `oca-aggregate.yml`.** Every repo in
   the manifest must have a corresponding entry in `oca-aggregate.yml`
   (and vice versa). The validator enforces this.

3. **No duplicate module names across repos.** If two OCA repos contain a
   module with the same directory name, the build fails (collision detection
   in `Dockerfile.unified`).

4. **IPAI modules are auto-discovered.** All directories under `addons/ipai/`
   with a `__manifest__.py` are included. The manifest does not enumerate
   them individually.

5. **Addon path order is deterministic.** CE → OCA → IPAI. The validator
   checks this against `Dockerfile.unified`.

6. **Must-have modules must exist.** If a repo entry declares `must_have`
   modules, those modules must exist in the hydrated repo directory.
   Validated with `--check-hydrated` flag.

---

## Update Flow

```
1. Edit config/addons.manifest.yaml (add/remove repos or modules)
2. Update oca-aggregate.yml if adding/removing repos
3. Run: gitaggregate -c oca-aggregate.yml
4. Run: python scripts/odoo/validate_addons_manifest.py --check-hydrated -v
5. Commit all changed files together
6. CI (addons-manifest-guard.yml) validates on PR
```

---

## CI Validation

**Workflow**: `.github/workflows/addons-manifest-guard.yml`

**Triggers**: Changes to `config/addons.manifest.yaml`, `oca-aggregate.yml`,
`addons/ipai/**`, `docker/Dockerfile.unified`, or the validator script.

**Checks**:
- Manifest schema valid (version, required fields)
- Repo entries have all required fields
- Manifest ↔ `oca-aggregate.yml` repo sync
- No duplicate module names (when hydrated)
- Must-have modules present (when hydrated)
- IPAI modules have valid `__manifest__.py`
- Dockerfile addon path order matches SSOT invariant

---

## Pinning Policy

| Mode | Behavior | Use Case |
|------|----------|----------|
| `branch` | Track HEAD of OCA 19.0 branch | Development, staging |
| `sha` | Pin exact commit SHA per repo | Production freeze |

To switch to production pinning:
1. Run `gitaggregate` to get current HEADs
2. Record each repo's HEAD SHA in the manifest `ref` field
3. Set `pinning_policy: sha`
4. Commit and tag as a release

---

## Tier Classification

| Tier | Category | Example Repos |
|------|----------|---------------|
| 0 | Core Infrastructure | server-tools, server-ux, queue, connector |
| 1 | Web / UX | web |
| 2 | Reporting | reporting-engine, mis-builder, spreadsheet |
| 3 | Finance / Accounting | account-financial-tools, account-reconcile |
| 4 | HR / People | hr, hr-expense, timesheet |
| 5 | Sales / Purchase / CRM | crm, sale-workflow, purchase-workflow |
| 6 | Knowledge / DMS | knowledge, dms, social |
| 7 | Project / Manufacturing | project, manufacture |
| 8 | AI / Automation / REST | ai, automation, rest-framework, storage |
| 9 | Partner / Contact | partner-contact |

Tiers determine installation priority but do not affect runtime addon path order.

---

## Deprecations

### `config/addons_manifest.oca_ipai.json`

**Status**: Deprecated — retained temporarily for transition only.

- Must not be used by CI, image build, or validation
- `config/addons.manifest.yaml` is the only active SSOT for addon curation
- Removal should happen in a follow-up cleanup PR after this contract is merged

### Excluded OCA Repos

| Source | Status | Replacement |
|--------|--------|-------------|
| `server-env` OCA repo | Excluded | Azure Key Vault handles env-dependent config |
| `bank-statement-import` OCA repo | Excluded | Merged into `account-reconcile` in Odoo 19 |
