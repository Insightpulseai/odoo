# Drive → GitHub Sync Runbook

## What it does

Exports selected Google Docs (by file ID) into repo paths as Markdown with stable frontmatter + normalization.

## Config

- Manifest: `scripts/drive_sync/drive_manifest.yml`
- Script: `scripts/drive_sync/sync_docs.mjs`

## Auth (choose one)

### A) Service account (recommended)

Secrets:
- `GOOGLE_CLIENT_EMAIL`
- `GOOGLE_PRIVATE_KEY`

Optional:
- `GOOGLE_IMPERSONATE_USER` (Workspace domain-wide delegation)

Notes:
- If not using impersonation, share each Drive Doc with the service account email (Reader).

### B) OAuth refresh token fallback

Secrets:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

## CI Proofs

Workflow uploads artifacts:
- `scripts/drive_sync/sync.log.json`
- optional patch diff `/tmp/drive-sync.diff`

## Troubleshooting

### Permission denied / not found

- Ensure SA has access (shared doc) OR enable domain-wide delegation + impersonation.

### Noisy diffs

- Adjust `normalize_markdown.mjs` rules first.
- Never add timestamps that update every run. Only use Drive `modifiedTime`.

### Google private key formatting

- Store as a GitHub secret preserving newline escaping.
- Script converts `\\n` → `\n`.

## Adding a new document

1. Get the Google Doc file ID from the URL:
   ```
   https://docs.google.com/document/d/FILE_ID_HERE/edit
   ```

2. Add entry to `scripts/drive_sync/drive_manifest.yml`:
   ```yaml
   - id: "FILE_ID_HERE"
     type: doc
     enabled: true
     repo_path: "docs/target/filename.md"
     frontmatter:
       title: "Document Title"
       tags: ["tag1", "tag2"]
   ```

3. Ensure the service account has Reader access to the doc.

4. Run locally to test:
   ```bash
   DRIVE_SYNC_MODE=dry-run node scripts/drive_sync/sync_docs.mjs
   ```
