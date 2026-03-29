# Evidence Directory

Evidence packs are derived proof artifacts, not source of truth.

## Structure

```
docs/evidence/
  releases/              # Pipeline-generated release evidence (gitkeep)
  YYYYMMDD-HHMM/         # Session-scoped evidence bundles
    <scope>/
      test.log
      SUMMARY.md
```

## Pipeline Evidence

Azure DevOps pipelines publish evidence as build artifacts using the
`publish-evidence.yml` template. Each artifact contains:

- `release-evidence.json` -- machine-readable record with commit SHA, image ref, timestamp, smoke URL
- `SUMMARY.md` -- human-readable table

Artifact naming: `evidence-{surface}-{build_number}`

Retention: 90 days in Azure DevOps artifact storage.

## Evidence Fields (schema v1.0)

| Field | Type | Description |
|-------|------|-------------|
| `surface` | string | Deployable surface name (web-landing, odoo-erp, databricks) |
| `timestamp` | ISO 8601 | UTC timestamp of evidence generation |
| `build_number` | string | Azure DevOps build number |
| `build_id` | string | Azure DevOps build ID |
| `commit_sha` | string | Full commit SHA |
| `commit_short` | string | Short commit SHA |
| `branch` | string | Source branch |
| `image_ref` | string | Full ACR image reference (if applicable) |
| `smoke_url` | string | URL used for smoke testing |
| `pipeline` | string | Pipeline definition name |
| `triggered_by` | string | User or system that triggered the build |
| `notes` | string | Additional context |

## Rules

- Evidence is NOT SSOT -- it is derived from pipeline execution
- Never hand-edit evidence files
- Evidence does not gate releases directly; pipeline stage status does
- Evidence artifacts are for audit trail and post-incident review
