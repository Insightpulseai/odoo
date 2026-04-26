# ipai_pulser_chat — Pulser Chat Shell

Thin Odoo 18 backend module that provides a systray chat panel proxying messages
to an external Pulser runtime.  Odoo owns the UI and authenticated context
handoff; the external runtime owns orchestration, model routing, and tool execution.

---

## Supported surface

- Odoo 18 CE backend (web client).
- Systray icon present on every backend page.
- No website/portal surface — `auth="user"` on all endpoints.

---

## Required configuration

All settings live under **Settings > Technical > Pulser Chat Shell** (inherits
`base_setup.res_config_settings_view_form`).

| Key (`ir.config_parameter`) | Default | Description |
| --- | --- | --- |
| `ipai.pulser_chat.enabled` | `False` | Show the systray icon and enable the proxy. |
| `ipai.pulser_chat.backend_url` | `` (empty) | Absolute `http`/`https` URL of the external Pulser endpoint. |
| `ipai.pulser_chat.timeout_seconds` | `30` | Proxy timeout. Range: 5–120 s. |

The feature **fails closed**: if `enabled` is `False` or `backend_url` is missing
or invalid, every message request returns `{"ok": false, "error": "..."}` and the
UI displays a non-fatal notice.

---

## Security model

- All controller endpoints use `auth="user"` — no anonymous access.
- CSRF protection is enabled (`type="json"`, `csrf=True` on every route).
- The backend URL is read server-side from `ir.config_parameter` via `sudo()`.
  Callers cannot influence which host is contacted.
- Input is validated: `context_model` accepts only alphanumeric + `.` + `_`;
  messages are capped at 8 000 characters; response bodies are capped at 512 KB.
- Upstream secrets (API keys on the Pulser runtime) never transit through this layer.
- Error responses never expose stack traces or `ir.config_parameter` values.

---

## Controller endpoints

### `POST /ipai/pulser_chat/bootstrap`

Returns display flags for the frontend on panel open. Never exposes the backend URL.

```json
{
  "enabled": true,
  "backend_configured": true,
  "user_name": "Alice",
  "company_name": "ACME Corp"
}
```

### `POST /ipai/pulser_chat/message`

Proxies a user message to the external Pulser runtime.

Request params (JSON):

```json
{
  "message": "string (max 8 000 chars)",
  "context": {
    "surface": "erp",
    "context_model": "sale.order",
    "context_res_id": 42
  },
  "conversation_id": "string or null"
}
```

Response shape (all branches):

```json
{
  "ok": true,
  "content": "string",
  "conversation_id": "string or null",
  "citations": [],
  "metadata": {}
}
```

On any failure:

```json
{
  "ok": false,
  "error": "Human-readable error string"
}
```

---

## Failure modes and degradation

| Condition | Behaviour |
| --- | --- |
| Feature disabled in settings | `ok=false`, informative UI notice, no upstream call |
| Backend URL empty or invalid | `ok=false`, UI notice |
| Upstream timeout | `ok=false, error="...did not respond in time"` |
| Upstream HTTP error | `ok=false, error="HTTP <code>"` |
| Upstream unreachable | `ok=false, error="unreachable"` |
| Upstream returns non-JSON | `ok=false` |
| Upstream response > 512 KB | `ok=false` |
| Unexpected server error | `ok=false`, full traceback logged server-side only |

---

## Ownership split

- `odoo` (this module): Owl systray entry, chat drawer UI, authenticated user/company/record context handoff, proxy controller.
- `platform` / `agent-platform`: model/provider routing, tool and MCP policy, orchestration, memory, eval control.
- `data-intelligence`: retrieval and governed semantic grounding.

---

## Known limits

- No streaming / SSE support; responses are returned in a single round-trip.
- No message persistence — conversation history lives only in browser memory for the session.
- Timeout is a server-side read; the browser has no independent timeout and will wait for the Odoo response.
- `isDisplayed` on the systray item is always `true`; the icon is visible even when disabled (the panel shows a config notice).

---

## Operational notes

- Log level for the controller: `WARNING` for upstream errors, `EXCEPTION` for unexpected failures. No `DEBUG` spam.
- To debug: `--log-handler=odoo.addons.ipai_pulser_chat:DEBUG` (adds per-request traces).
- Settings changes take effect immediately (no restart required) — `ir.config_parameter` is read per request.
- Install: `odoo-bin -i ipai_pulser_chat -d <db>`
- Upgrade: `odoo-bin -u ipai_pulser_chat -d <db>`

---

## Authority

- Product authority: `spec/pulser-odoo/prd.md`
- Release-scope authority: `ssot/release/go-live-scope-matrix.yaml`
