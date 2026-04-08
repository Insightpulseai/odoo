# Google Workspace CLI — Pilot Skill Contract

> Status: **Pilot** (phase 1 — read-first, sandbox writes only)
> Upstream: https://github.com/googleworkspace/cli
> Tenant: `w9studio.net` (Google Workspace managed)
> Maturity: Pre-1.0 — expect breaking changes. Pin tested version.

---

## When to use

- Google Workspace actions across Gmail, Drive, Calendar, Docs, Sheets, Chat
- Agent workflows needing structured JSON output from Workspace APIs
- Schema introspection via Google Discovery Service

## When NOT to use

- Business-critical write paths
- Bulk destructive operations (mailbox deletion, mass send, permission mutation)
- Anything that already has a more stable internal integration
- Unattended flows without explicit write approval

## Default mode

- **Read-first** — all commands default to read/list/get
- **JSON output required** — always use structured output for agent consumption
- **Explicit approval for writes** — no write command runs without environment flag
- **Dry-run before writes** — use `--dry-run` where supported

## Auth

| Environment | Auth Mode | Identity |
|-------------|-----------|----------|
| Local desktop (pilot) | Interactive OAuth | `business@w9studio.net` |
| CI/server (future) | Credentials file or access-token | Dedicated automation identity |

**Rules:**
- Do not use the everyday mailbox as the long-term automation principal
- Dedicated automation identity required before moving to CI
- Least-privilege scopes per profile

## Scope control

Split into two profiles:

| Profile | Scopes | Use |
|---------|--------|-----|
| `read-only` | Gmail.readonly, Drive.readonly, Calendar.readonly | Default for all queries |
| `write-enabled` | Gmail.send, Drive.file, Docs.write, Sheets.write | Sandbox only, explicit opt-in |

## Safety

- Use dry-run where supported before writes
- No mailbox deletion / mass send / permission mutation in unattended flows
- All write recipes labeled **sandbox-only** for phase 1
- Pin a tested release/tag — do not auto-upgrade pre-1.0

## Versioning

- Pin tested CLI release internally
- Record tested version in this file
- Do not track `latest` in any automation

## Boundary

Do not let `gws` become the sole authority for admin-sensitive Workspace
operations until proven: auth stability, scope discipline, repeatable
smoke tests, no breaking changes across pinned version.

---

## Phase 1 approved surfaces

| Surface | Read | Write |
|---------|------|-------|
| Gmail | search, read metadata | (blocked) |
| Drive | list, read, download | (sandbox only) |
| Calendar | list, read events | (sandbox only) |
| Docs | read | append/create (sandbox only) |
| Sheets | read | append/create (sandbox only) |
| Chat | read spaces/messages | send to test space (sandbox only) |
| Admin | (blocked) | (blocked) |

---

*Created: 2026-03-27. Review before any phase 2 expansion.*
