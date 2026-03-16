<!-- AUTO-GENERATED from blueprints/marketing.site.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: Marketing Site (Next.js + Vercel + content layer)

**ID**: `marketing.site`  
**Category**: `marketing`  
**Target**: `apps/marketing`

---

## Sources

- **vercel-template** — [https://vercel.com/templates/next.js/nextjs-boilerplate](https://vercel.com/templates/next.js/nextjs-boilerplate) (catalog id: `nextjs-shadcn-admin`)
- **vercel-example** — [https://github.com/vercel/next.js/tree/main/examples/with-supabase](https://github.com/vercel/next.js/tree/main/examples/with-supabase) (catalog id: `with-supabase`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `VERCEL_PROJECT_NAME` | Vercel project name for the marketing site | `insightpulseai-marketing` |
| `NEXT_PUBLIC_SITE_URL` | Production URL for canonical links and OG tags | `https://insightpulseai.com` |

---

## Automation Steps

### Step 1: create_app

Scaffold new Next.js app in apps/marketing

**Agent instruction**:

```
Create apps/marketing/ as a new pnpm workspace member:
- package.json with name: @ipai/marketing
- Add to pnpm-workspace.yaml apps/* (already covered by glob)
- Minimal Next.js 15 setup: app/layout.tsx, app/page.tsx, next.config.ts
- tailwind + shadcn/ui (copy config from apps/ops-console as baseline)
- vercel.json with ignoreCommand path-filtered to apps/marketing/**
- .vercelignore excluding all non-marketing paths
```

### Step 2: add_seo_baseline

Add SEO metadata baseline

**Agent instruction**:

```
In apps/marketing/app/layout.tsx, add:
- <Metadata> with title template: %s | InsightPulse AI
- Open Graph defaults (title, description, image)
- Canonical URL using NEXT_PUBLIC_SITE_URL
- robots.txt via app/robots.ts
- sitemap via app/sitemap.ts (static pages only initially)
```

### Step 3: add_ci

Add marketing-scoped CI gates

**Agent instruction**:

```
Create .github/workflows/marketing-check.yml:
- Path filter: apps/marketing/**
- Steps: pnpm --filter @ipai/marketing lint, typecheck, build
- Add to golden-path-gate.yml required checks list
```

---

## Verification

**Required CI checks:**

- `marketing-check`
- `golden-path-summary`

**Preview expectations:**

- vercel-preview-url-posted-to-pr
- site-renders-without-500
- og-tags-present-in-head

---

## Rollback

**Strategy**: `delete_files`

New app — rollback by deleting apps/marketing/ and removing from pnpm-workspace.yaml.

---

## Minor Customization (manual steps after agent applies blueprint)

- Create new Vercel project linked to apps/marketing (vercel link --repo from apps/marketing)
- Set Vercel Root Directory to apps/marketing
- Point vercel.com project DNS to custom domain (www.insightpulseai.com)

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `marketing.site` from docs/catalog/blueprints/marketing.site.blueprint.yaml.

Variables to set before running:
  VERCEL_PROJECT_NAME: <value>
  NEXT_PUBLIC_SITE_URL: <value>

Steps to execute in order:
  1. create_app: Scaffold new Next.js app in apps/marketing
  2. add_seo_baseline: Add SEO metadata baseline
  3. add_ci: Add marketing-scoped CI gates

After completing all steps:
  - Verify required checks pass: marketing-check, golden-path-summary
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```
