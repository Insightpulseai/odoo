# Unified Artifact Naming Convention

Machine-readable source of truth: `ssot/org/org__org__artifact_naming_convention__v1.policy.yaml`

---

## Filename Pattern

```
<repo_key>__<domain>__<subject>__v<major>.<artifact_type>.<ext>
```

All tokens are lowercase `[a-z0-9_]`. Double underscores (`__`) separate the four positional segments. Single underscores are allowed within a segment for multi-word names.

Example: `odoo__finance__chart_of_accounts__v1.schema.yaml`

## Namespace Pattern

```
ipai.<repo_key>.<domain>.<subject>.v<major>
```

Derived directly from the filename tokens. Every YAML artifact header must declare a `namespace` field matching this pattern.

## Schema ID Pattern (JSON Schema only)

```
https://schemas.insightpulseai.com/ipai/<repo_key>/<domain>/<subject>/v<major>
```

The `$id` field in JSON Schema files must match this derivation.

---

## Allowed Artifact Types

| Type | Purpose |
|------|---------|
| `schema` | Data structure definition (JSON Schema or equivalent) |
| `registry` | Enumeration of known instances of a type |
| `mapping` | Cross-reference between two domains or systems |
| `manifest` | Declared inventory of components in a deployable unit |
| `policy` | Org-level or repo-level governance rule |
| `contract` | Interface or integration agreement between systems |
| `entity` | Canonical entity definition |
| `catalog` | Browsable index of available resources |
| `inventory` | Current-state enumeration (runtime or static) |
| `config` | Operational configuration |

Allowed extensions: `.yaml`, `.json`.

---

## Versioning Rules

1. Only the major version appears in the filename and namespace (`v1`, `v2`, ...).
2. A breaking change (field removal, type change, semantic shift) bumps the major version.
3. Additive, non-breaking changes keep the same filename and namespace.
4. Minor and patch versions never appear in filenames.

---

## Uniqueness Rules

1. The full basename (everything before the extension pair) must be unique across the entire repo.
2. The namespace must be unique across the repo, and ideally across the org.
3. The combination of `domain + subject + version + artifact_type` must not repeat within a repo.

---

## Congruence Rules

These rules enforce consistency between the filename, the YAML/JSON header, and (where applicable) the JSON Schema `$id`.

| Check | Rule |
|-------|------|
| Filename vs. header `repo_key` | Must match |
| Filename tokens vs. header `namespace` | Tokens must align positionally |
| Filename `v<N>` vs. header `version` | Must match |
| JSON Schema `$id` vs. namespace | Must follow the schema ID pattern derived from the same tokens |

A file that violates congruence is invalid regardless of its content.

---

## Repo Aliases

Repo keys use underscores in filenames. The mapping to actual repo/directory names:

| Repo Key | Directory / Repo Name |
|----------|----------------------|
| `github` | `.github` |
| `infra` | `infra` |
| `ops_platform` | `ops-platform` |
| `lakehouse` | `lakehouse` |
| `agents` | `agents` |
| `odoo` | `odoo` |
| `web` | `web` |
| `automations` | `automations` |
| `design_system` | `design-system` |
| `templates` | `templates` |

---

## Forbidden Basenames

The following bare names are not allowed as the sole content of any segment. They are too generic and create ambiguity:

`schema`, `registry`, `mapping`, `manifest`, `contract`, `config`, `default`, `main`, `data`, `settings`

These words may appear as part of a compound segment (e.g., `data_pipeline` is valid, `data` alone is not).

---

## Examples

| Filename | Repo | Domain | Subject |
|----------|------|--------|---------|
| `odoo__finance__chart_of_accounts__v1.schema.yaml` | odoo | finance | chart_of_accounts |
| `odoo__parity__ee_feature_matrix__v1.registry.yaml` | odoo | parity | ee_feature_matrix |
| `infra__azure__service_matrix__v1.inventory.yaml` | infra | azure | service_matrix |
| `agents__ai__tool_capabilities__v1.catalog.json` | agents | ai | tool_capabilities |
| `org__org__artifact_naming_convention__v1.policy.yaml` | org | org | artifact_naming_convention |
| `lakehouse__medallion__bronze_sources__v1.mapping.yaml` | lakehouse | medallion | bronze_sources |
| `odoo__auth__oidc_providers__v1.config.yaml` | odoo | auth | oidc_providers |
| `github__ci__workflow_gates__v1.contract.yaml` | github | ci | workflow_gates |

---

## Required Header Fields

YAML artifacts must include:

```yaml
version: 1
namespace: ipai.<repo_key>.<domain>.<subject>.v1
artifact_type: <type>
repo_key: <repo_key>
domain: <domain>
subject: <subject>
```

JSON Schema artifacts must include `$schema` and `$id` (following the schema ID pattern).

---

## CI Validation

A CI check should validate every file matching the filename regex against:

1. Regex conformance of the filename itself.
2. Presence of all required header fields.
3. Congruence between filename tokens and header values.
4. Uniqueness of basename and namespace within the repo.
5. Artifact type is in the allowed list.
6. No forbidden bare basenames.

Implementation: a linting script or GitHub Actions workflow that scans `ssot/` directories and any other designated artifact paths. The policy YAML provides the regex and allowed values programmatically.
