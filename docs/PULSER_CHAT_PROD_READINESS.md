# Pulser Chat Shell — Production Readiness Checklist

Module: `ipai_pulser_chat`
Version: `18.0.1.1.0`
Date: 2026-04-24

---

## Install / upgrade expectations

| Check | Status |
| --- | --- |
| Installs cleanly on fresh Odoo 18 CE DB | Verified by `test_install.py` (requires live Odoo) |
| Upgrades without data regression (`noupdate="1"` on seed params) | XML seed uses `noupdate="1"` — safe on upgrade |
| No Enterprise module dependency | Confirmed — depends only on `base`, `web` |
| `security/ir.model.access.csv` present | Present (header-only; no custom models declared) |
| Module version bumped on hardening patch | Bumped to `18.0.1.1.0` |

---

## Configuration requirements

All three `ir.config_parameter` keys must be present after install.
Seeded by `data/ir_config_parameter.xml` with `noupdate="1"`.

| Parameter | Required value for feature to be active |
| --- | --- |
| `ipai.pulser_chat.enabled` | `"True"` |
| `ipai.pulser_chat.backend_url` | Absolute `https://` URL |
| `ipai.pulser_chat.timeout_seconds` | Integer in `[5, 120]` |

The feature **fails closed**: any missing or invalid value results in
`{"ok": false, "error": "..."}` at the API layer and a non-fatal notice in the UI.

---

## Controller security baseline

| Control | Implementation |
| --- | --- |
| Auth | `auth="user"` on all routes — no anonymous access |
| CSRF | `csrf=True`, `type="json"` on all routes |
| Input length | Message capped at 8 000 chars |
| Context sanitisation | `context_model` validated against `[A-Za-z0-9._]` |
| Response size cap | 512 KB hard cap on upstream body read |
| Timeout | Configurable 5–120 s; clamped in code regardless of stored value |
| Error shape | All branches return `{"ok": bool, ...}` — never exposes tracebacks |
| Secret handling | Backend URL read server-side only; never returned to client |
| URL scheme validation | Only `http`/`https` accepted for backend URL |

---

## Failure modes

| Scenario | Controller behaviour | UI behaviour |
| --- | --- | --- |
| Feature disabled | Returns `ok=false` immediately | Shows "disabled" notice |
| Backend URL empty | Returns `ok=false` immediately | Shows "configure URL" notice |
| Backend URL invalid scheme | Returns `ok=false` immediately | Shows "configure URL" notice |
| Upstream timeout | Catches `TimeoutError` + `socket.timeout`; returns `ok=false` | Shows inline error |
| Upstream HTTP error | Catches `urllib.error.HTTPError`; returns `ok=false, error="HTTP N"` | Shows inline error |
| Upstream unreachable | Catches `urllib.error.URLError`; returns `ok=false` | Shows inline error |
| Upstream non-JSON | Catches `json.JSONDecodeError`; returns `ok=false` | Shows inline error |
| Upstream response too large | Catches `ValueError`; returns `ok=false` | Shows inline error |
| Unexpected exception | Catches `Exception`; logs full traceback server-side; returns `ok=false` | Shows generic error |

---

## Frontend behaviour

| Check | Implementation |
| --- | --- |
| Bootstrap guard | `_bootstrapDone` flag prevents double-bootstrap on rapid toggle |
| Unmount safety | `_destroyed` flag prevents state mutation after `onWillUnmount` |
| Loading state on init | `isBootstrapping` spinner shown until first server round-trip |
| Send guard | `sendMessage()` no-ops if `isLoading`, `!enabled`, or `!backendConfigured` |
| Typing indicator | Shown during `isLoading` in message list |
| Error display | Non-fatal inline banner; cleared on next successful send |
| Clear conversation | Button resets `messages`, `conversationId`, `error` |
| Keyboard submit | `Enter` (without `Shift`) submits; `Shift+Enter` inserts newline |
| Scroll on new message | `_scrollToBottom()` called after push and after RPC resolves |
| Action context safety | `_buildContext()` wrapped in `try/catch`; degrades to `{surface: "erp"}` |

---

## Test coverage

| File | Cases covered |
| --- | --- |
| `tests/test_install.py` | Config params seeded; controller importable; settings fields exist |
| `tests/test_settings.py` | Valid save/load; URL constraint (relative, ftp, plain host); timeout bounds |
| `tests/test_controller.py` | Bootstrap (default, auth, company); message (happy path, empty, oversize, disabled, missing URL, timeout, HTTP error, URL error, JSON error, body size, context sanitisation) |
| `tests/test_assets.py` | All 5 declared JS/XML/SCSS assets on disk; CSV present; data XML present |

---

## Debug notes

- Enable verbose logging: `--log-handler=odoo.addons.ipai_pulser_chat:DEBUG`
- Settings changes take effect immediately (read per request via `ir.config_parameter`).
- No Odoo restart required after changing backend URL or timeout.
- Upstream calls are synchronous (blocking Odoo worker thread for up to `timeout_seconds`).
  Keep timeout low in high-concurrency environments and size worker pool accordingly.

---

## Deferred / out of scope

- Streaming / SSE responses from upstream (single round-trip only).
- Message persistence (in-memory session only; lost on panel close).
- Independent browser-side request timeout.
- Rate limiting per user (relies on upstream Pulser runtime throttling).
- `isDisplayed` driven by live config (currently always `true`; requires async
  systray state management to change).

---

## Verdict

**READY FOR STAGING** — all static validation passes; live Odoo install/upgrade
and full HttpCase suite require a running Odoo 18 instance to confirm.
