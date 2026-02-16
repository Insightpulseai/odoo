# Vercel (Integration Surface)

Project manifests, env templates, and deployment contracts for Vercel-hosted apps.

## Layout

```
infra/vercel/
├── README.md          # This file
├── env/               # Env templates per app (examples only)
└── contracts/         # Deployment contracts (project ↔ domain mapping)
```

## Rules

- Secrets must never be committed; use env examples only.
- Vercel apps live under `web/` in the repo; this directory holds IaC/config only.
- Templates may bootstrap `web/*` apps but must not create repos for `odoo/` runtime.

## Environment Mapping

| Vercel Environment | Maps To | Notes |
|--------------------|---------|-------|
| Preview | staging / per-PR ephemeral | auto-deploy on push |
| Production | prod | main branch only |

## SSOT

- App source: `web/<app>/`
- Config contracts: `infra/vercel/`
- Secrets: Vercel dashboard env vars (never git)
