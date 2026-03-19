# Vercel Monorepo Contract (Odoo Repo)

This repository contains an Odoo runtime plus optional web apps.

## Vercel deployment model

- Vercel Projects must point to a web app root directory (e.g., `web/apps/<app>`).
- Odoo runtime is not deployed on Vercel.

## Root directories

- `web/apps/ops-console` (Vercel Project: ops-console)
- `web/apps/marketing` (Vercel Project: marketing)

## Notes

Vercel monorepo support allows multiple projects from the same Git repository, each configured with its own Root Directory and build settings.
