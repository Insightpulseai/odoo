# Vendor Backlog Exports

This directory contains automatically synced backlog exports from integrated vendor applications.

## Structure

```
backlog/vendors/
├── shelf/
│   ├── issues.json        # GitHub Issues from Shelf-nu/shelf.nu
│   └── project_export.json # GitHub ProjectV2 items (if enabled)
├── atomic-crm/
│   └── issues.json        # GitHub Issues from marmelab/atomic-crm
└── README.md              # This file
```

## How It Works

1. **Automated Sync**: The `vendor-backlog-sync.yml` workflow runs hourly
2. **Source**: Issues and ProjectV2 items are fetched via GitHub API
3. **Diff Detection**: Changes are compared against previous exports
4. **PR Comments**: Non-zero diffs are posted as PR comments
5. **Commit**: Changes are auto-committed to main branch

## Configuration

Vendor apps are configured in `integrations/apps.yml`:

```yaml
apps:
  - slug: shelf
    backlog:
      github:
        owner: "Shelf-nu"
        repo: "shelf.nu"
        include_prs: false
        state: "open"
      projectv2:
        enabled: true
        owner: "Shelf-nu"
        number: 1
```

## Manual Sync

Trigger a manual sync:

```bash
# All apps
python3 scripts/integrations/vendor_backlog_sync.py

# Requires GH_TOKEN environment variable
export GH_TOKEN="your-github-token"
```

## Integration with Backlog Coverage

These exports are automatically ingested by `scripts/backlog_scan.py` to produce
the unified `docs/BACKLOG_COVERAGE_REPORT.md`.

## Do Not Edit Manually

Files in this directory are auto-generated. Manual edits will be overwritten.
