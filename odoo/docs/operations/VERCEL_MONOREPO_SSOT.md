# Vercel Monorepo SSOT

## Canonical layout

- Vercel projects live under `apps/*`
- Each Vercel Project is linked to a single `apps/<name>` root directory

## Suggested projects

- apps/ops-console (Next.js)
- apps/web (Next.js / marketing)
- apps/agent-hub (optional)

## Notes

- Use separate Vercel Projects per app (preferred)
- Optional "router project" can rewrite /ops to ops-console domain if you want a single domain
