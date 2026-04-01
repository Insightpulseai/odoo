# Runtime API

HTTP API surface for the agent runtime. Exposes health checks, agent dispatch, and status endpoints.

## Endpoints

- `GET /health` — runtime health check
- `POST /dispatch` — submit an agent execution request
- `GET /sessions/:id` — query session status

## Status

Stub implementation. See `index.ts`.
