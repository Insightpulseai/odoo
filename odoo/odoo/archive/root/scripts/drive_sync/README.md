# Drive Sync

Exports Google Docs to Markdown with stable frontmatter for deterministic CI.

## Local run

```bash
npm install
node scripts/drive_sync/sync_docs.mjs
```

## Verify mode

```bash
DRIVE_SYNC_MODE=verify node scripts/drive_sync/sync_docs.mjs
git diff --exit-code
```

## Modes

| Mode | Description |
|------|-------------|
| `pr` | Default. Write files, create sync log |
| `verify` | Write files, intended for CI diff check |
| `dry-run` | No file writes, only log output |

## Secrets

### Service Account (recommended)

- `GOOGLE_CLIENT_EMAIL`
- `GOOGLE_PRIVATE_KEY`
- `GOOGLE_IMPERSONATE_USER` (optional, for domain-wide delegation)

### OAuth fallback

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

## Files

| File | Purpose |
|------|---------|
| `drive_manifest.yml` | Document IDs + repo paths |
| `sync_docs.mjs` | Main sync script |
| `lib/google_auth.mjs` | Auth helper (SA + OAuth) |
| `lib/export_doc_markdown.mjs` | Drive export + Turndown |
| `lib/normalize_markdown.mjs` | Markdown normalization |
| `sync.log.json` | Output log (gitignored) |

## Determinism

- No run timestamps in exported files
- Frontmatter uses Drive `modifiedTime` + `rawChecksum`
- Markdown normalization removes conversion noise
- Verify workflow fails if export would change repo
