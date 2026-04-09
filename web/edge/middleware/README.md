# Edge Middleware Functions

Edge middleware for request/response transformation at the Azure Front Door layer. Covers auth token forwarding, geo-routing, and A/B testing.

## Convention

- Middleware logic runs at Azure Front Door (rules engine) or ACA sidecar
- No Cloudflare Workers, no Vercel Edge Functions (deprecated)
- Each middleware must be stateless and idempotent

<!-- TODO: Define first edge middleware when A/B or geo-routing is needed -->
