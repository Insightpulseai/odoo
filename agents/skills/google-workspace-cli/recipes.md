# Google Workspace CLI — Approved Recipes

> Phase 1: read-first pilot on `w9studio.net`
> All write recipes are **sandbox-only** until phase 2 approval.

---

## Read recipes (approved for production use)

### Gmail — search recent messages

```bash
gws gmail messages list --query "newer_than:7d" --format json
```

### Gmail — read message metadata

```bash
gws gmail messages get <message-id> --format json
```

### Drive — list files in a folder

```bash
gws drive files list --parent <folder-id> --format json
```

### Drive — read file metadata

```bash
gws drive files get <file-id> --format json
```

### Calendar — list upcoming events

```bash
gws calendar events list --calendar primary --time-min "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --format json
```

---

## Write recipes (sandbox-only)

### Docs — append notes

```bash
gws docs documents batchUpdate <doc-id> --body '{"requests":[{"insertText":{"location":{"index":1},"text":"Note: ..."}}]}' --format json
```

### Sheets — append row

```bash
gws sheets spreadsheets values append <spreadsheet-id> --range "Sheet1!A1" --body '{"values":[["col1","col2"]]}' --format json
```

### Chat — send message to test space

```bash
gws chat spaces messages create <space-name> --body '{"text":"Test message from gws CLI"}' --format json
```

---

## Denied operations (phase 1)

- Gmail send/delete
- Drive permission changes
- Calendar event creation/deletion on shared calendars
- Admin directory operations
- Any bulk/batch mutation
- Any operation on domains other than `w9studio.net`

---

*Recipes are illustrative. Verify exact CLI syntax against pinned version.*
