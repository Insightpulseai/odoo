# _template-bridge

Canonical Edge Function template. Copy this directory when creating a new integration bridge.

**Contract**: `docs/contracts/SUPABASE_EDGE_FUNCTIONS_CONTRACT.md`

---

## Actions

| Action | Auth | Method | Description |
|--------|------|--------|-------------|
| `health` | None | GET | Liveness check |
| `example_action` | `x-bridge-secret` | POST | Replace with real action |

## Required Env Vars (names only — values set via `supabase secrets set`)

| Var | Description |
|-----|-------------|
| `TEMPLATE_SECRET` | Shared secret for `x-bridge-secret` auth |
| `SUPABASE_URL` | Injected automatically by Supabase runtime |
| `SUPABASE_SERVICE_ROLE_KEY` | Injected automatically by Supabase runtime |

## Health Check

```bash
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/_template-bridge?action=health
# Expected: {"ok":true,"service":"_template-bridge","request_id":"..."}
```

## Copy to New Function

```bash
cp -r supabase/functions/_template-bridge supabase/functions/your-new-bridge
# Then replace: _template-bridge → your-new-bridge, TEMPLATE_SECRET → YOUR_VAR
```
