# Security and Cache Headers

HTTP security and cache-control headers applied at the Azure Front Door edge. Covers CSP, HSTS, X-Frame-Options, and cache policies.

## Convention

- Header policies defined in YAML
- Applied via Azure Front Door rules engine or ACA ingress config
- Security headers follow OWASP recommendations
- Cache policies are per-route (static assets vs API vs HTML)

<!-- TODO: Define header policy YAML -->
