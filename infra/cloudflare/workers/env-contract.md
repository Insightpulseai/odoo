# Cloudflare Workers Environment Contract

## Purpose
Define the required configuration contract for every Worker deployment in the InsightPulseAI platform.

## Status
Canonical. All Worker deployments must satisfy this contract before promotion to production.

## Required Configuration Categories

Every Worker deployment must declare values for each of the following categories. Missing categories must be explicitly marked as `not_applicable` with justification.

### 1. Route and Hostname
- The public route pattern (e.g., `api.insightpulseai.com/v1/*`)
- The Cloudflare zone the route belongs to
- Whether the route is production, staging, or preview

### 2. Upstream Origin
- The self-hosted backend origin URL the Worker forwards to
- Failover behavior if the origin is unreachable
- Timeout thresholds for origin responses

### 3. Auth and Access Model
- How the Worker authenticates inbound requests (API key header, bearer token, HMAC signature, none for public)
- Whether the Worker passes auth context to the origin or the origin authenticates independently
- CORS policy if the Worker serves browser clients

### 4. Rate Limiting
- Per-client rate limit (requests per window)
- Global rate limit if applicable
- Response behavior when rate limit is exceeded (429 with retry-after, custom error)

### 5. Observability
- Whether request/response logging is enabled
- Log destination (Cloudflare Logpush, external sink, none)
- Metrics and alerting integration

### 6. Feature Flags
- Any feature flags that gate Worker behavior
- Default values for each flag
- How flags are toggled (environment variable, KV binding, hardcoded)

## Example Contract YAML

```yaml
worker_name: ipai-copilot-proxy
environment: production

route:
  pattern: "copilot.insightpulseai.com/*"
  zone: insightpulseai.com

upstream:
  origin: "https://ipai-copilot-backend.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io"
  timeout_ms: 30000
  failover: return_503

auth:
  inbound: none  # public advisory copilot
  cors:
    allowed_origins:
      - "https://insightpulseai.com"
      - "https://www.insightpulseai.com"
    allowed_methods: ["POST", "OPTIONS"]
    max_age: 3600
  origin_auth: bearer_token  # Worker attaches token from secret binding

rate_limiting:
  per_client:
    requests: 30
    window_seconds: 60
  on_exceed: 429_retry_after

observability:
  logging: enabled
  destination: cloudflare_logpush
  metrics: cloudflare_analytics

feature_flags:
  enable_streaming: true
  advisory_mode_only: true
```

## Secret Handling Rules

- Secrets are declared as Wrangler secret bindings, never as plaintext in `wrangler.toml` or source code
- Secret values are set via `wrangler secret put <NAME>` from a secure CI pipeline or operator session
- Secrets must never appear in logs, error messages, or response bodies
- Each environment (production, staging, preview) has isolated secret bindings
- Secret rotation does not require code changes; only redeployment of the binding value

## Prohibited Patterns

### No Inline Secrets
```toml
# BANNED — never do this
[vars]
API_KEY = "sk-live-abc123"
```

### No Origin Credentials in Worker Source
```javascript
// BANNED — origin credentials belong on the self-hosted backend
const FOUNDRY_KEY = "abc123";
```

### No Unbounded Upstream Calls
Every fetch to an upstream origin must have a timeout. Workers must not hang indefinitely waiting for a slow backend.

### No Silent Failures
If the upstream origin returns an error, the Worker must return an appropriate HTTP error to the client. Swallowing errors and returning 200 is prohibited.

### No Direct Database Access
Workers must never connect directly to PostgreSQL, Redis, or any operational database. All data access goes through self-hosted API origins.

### No State Accumulation
Workers must not accumulate request state across invocations using global variables. Use KV or Durable Objects (with explicit architectural approval) if cross-request state is required.
