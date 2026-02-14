# OdooOps Dashboard (Next.js + Tailwind)

Hybrid dashboard that embeds into Odoo QWeb shell (`ipai_odooops_shell`).

## Setup

```bash
cd apps/odooops-dashboard
npm install
```

## Development

```bash
npm run dev
# Runs on http://localhost:3000
```

## Build

```bash
npm run build
npm start
```

## Integration with Odoo

The Odoo module `ipai_odooops_shell` embeds this dashboard via iframe.

**Environment Variables:**

- `NEXTJS_DASHBOARD_URL` - Set in Odoo environment (default: `http://localhost:3000`)

## Design Tokens

Shared tokens are defined in `/design-tokens/tokens.json` and used in:
- Tailwind config (`tailwind.config.ts`)
- Odoo CSS vars (`addons/ipai/ipai_odooops_shell/static/src/css/shell.css`)

## Components

- **MetricCard** - Dashboard metrics (Projects, Deployments, Health, WAF)
- **ProjectCard** - Project status cards with deployments count

## Deployment

### Vercel

```bash
vercel --prod
```

Then update Odoo environment:

```bash
export NEXTJS_DASHBOARD_URL="https://your-deployment.vercel.app"
```
