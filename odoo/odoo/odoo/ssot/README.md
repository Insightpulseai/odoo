# SSOT Inventory

This directory stores machine-readable inventory definitions and generated evidence manifests.

## Rules
- Raw snapshot JSON is CI artifact output and must not be committed.
- Canonical committed assets are:
  - schemas
  - index files
  - normalized summaries
  - evidence manifests
- Every generated snapshot must be reproducible from:
  - `scripts/ssot/snapshot_github_and_vercel.sh`
  - `scripts/ssot/build_snapshot_manifest.py`
  - `scripts/ssot/normalize_snapshot_inventory.py`

## Structure

```
ssot/
  schema/
    snapshot-manifest.schema.json    # manifest contract
  github/
    target-state-repos.yaml          # canonical repo classification (committed)
    org.inventory.yaml               # normalized org summary (committed)
    repos.inventory.yaml             # normalized per-repo summary (committed)
    *.snapshot.json                   # raw API output (gitignored, CI artifact)
    repo-details/                    # per-repo raw API output (gitignored)
  vercel/
    *.snapshot.json                   # raw API output (gitignored, CI artifact)
  runtime/
    environments.inventory.yaml      # normalized environment inventory (committed)
  evidence/
    snapshot-manifest.json           # generated manifest (gitignored, CI artifact)
```

## Workflow

```
collect (snapshot_github_and_vercel.sh)
  -> normalize (normalize_snapshot_inventory.py)
    -> validate (.github/workflows/ssot-validate.yml)
      -> commit normalized YAML only
```

## Providers

| Provider | Status | Script |
|----------|--------|--------|
| GitHub | Active | `scripts/ssot/snapshot_github_and_vercel.sh` |
| Vercel | Active | `scripts/ssot/snapshot_github_and_vercel.sh` |
| Databricks | Planned | `scripts/ssot/providers/databricks_snapshot.sh` |
| Supabase | Planned | `scripts/ssot/providers/supabase_snapshot.sh` |
