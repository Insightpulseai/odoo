# Supabase Branching Integration

> **Project ID:** `spdtwktxdalcfigzeqrz`
> **Generated:** 2026-01-21
> **Purpose:** Database migrations and catalog sync for Odoo Go-Live

---

## Overview

Supabase Branching provides isolated database environments for testing schema changes before deploying to production. This integration enables:

1. **Preview Branches** - Test database migrations in isolated environments
2. **Catalog Sync** - Sync Odoo module/capability catalogs to Supabase
3. **CI/CD Integration** - Automated deployments via GitHub Actions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Git Repository (odoo-ce)                     │
│                                                                 │
│  main branch ──────────────────────────────────────────────────►│
│       │                                                         │
│       └── feature/branch ──► Preview Branch (Supabase)          │
│                                   │                             │
│                                   ▼                             │
│                           ┌───────────────┐                     │
│                           │ Supabase      │                     │
│                           │ Preview DB    │                     │
│                           └───────────────┘                     │
│                                   │                             │
│                              Merge PR                           │
│                                   │                             │
│                                   ▼                             │
│                           ┌───────────────┐                     │
│                           │ Production    │                     │
│                           │ Supabase      │                     │
│                           └───────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Branching Workflow

### 1. Branch Creation

When a feature branch is created, Supabase automatically:
- Creates a new preview database instance
- Applies pending migrations from `supabase/migrations/`
- Runs seed files if configured

### 2. Development Cycle

```bash
# Create new migration
supabase migration new add_odoo_catalogs

# Apply locally
supabase db push

# Test changes
supabase db reset
```

### 3. Merge to Production

Supabase deployment workflow (DAG):
1. **Clone** - Checkout repository
2. **Pull** - Retrieve migrations from main
3. **Health** - Wait for services (Auth, API, DB, Storage, Realtime)
4. **Configure** - Apply `config.toml` settings
5. **Migrate** - Run pending migrations
6. **Seed** - Populate initial data
7. **Deploy** - Deploy Edge Functions

---

## Catalog Schema

### capabilities_catalog

```sql
-- supabase/migrations/20260121_odoo_catalogs.sql

CREATE TABLE IF NOT EXISTS public.odoo_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_key TEXT NOT NULL UNIQUE,
    capability_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    requires_modules TEXT[] DEFAULT '{}',
    requires_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_capabilities_category ON public.odoo_capabilities(category);
CREATE INDEX idx_capabilities_active ON public.odoo_capabilities(is_active);
```

### module_install_catalog

```sql
CREATE TABLE IF NOT EXISTS public.odoo_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    category TEXT,
    source TEXT CHECK (source IN ('ce', 'oca', 'ipai', 'community')),
    version TEXT,
    depends TEXT[] DEFAULT '{}',
    install_command TEXT,
    ci_job TEXT,
    is_installed BOOLEAN DEFAULT false,
    installed_version TEXT,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_modules_source ON public.odoo_modules(source);
CREATE INDEX idx_modules_installed ON public.odoo_modules(is_installed);
```

### design_system_catalog

```sql
CREATE TABLE IF NOT EXISTS public.design_system_languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_key TEXT NOT NULL UNIQUE,
    language_name TEXT NOT NULL,
    framework TEXT NOT NULL,
    tokens_url TEXT,
    css_url TEXT,
    npm_package TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed design systems
INSERT INTO public.design_system_languages
    (language_key, language_name, framework, npm_package, config)
VALUES
    ('fluent-ui', 'Microsoft Fluent UI', 'react', '@fluentui/react-components', '{"theme": "webLight"}'),
    ('mui', 'Material UI', 'react', '@mui/material', '{"mode": "light"}'),
    ('tailwind', 'Tailwind CSS', 'utility-first', 'tailwindcss', '{"preset": "default"}'),
    ('shadcn', 'shadcn/ui', 'react', 'shadcn-ui', '{"style": "new-york"}'),
    ('ipai-tokens', 'IPAI Design Tokens', 'custom', '@ipai/design-tokens', '{"brand": "insightpulse"}')
ON CONFLICT (language_key) DO NOTHING;
```

---

## Row Level Security

```sql
-- Enable RLS
ALTER TABLE public.odoo_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.odoo_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.design_system_languages ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow read odoo_capabilities"
    ON public.odoo_capabilities FOR SELECT USING (true);
CREATE POLICY "Allow read odoo_modules"
    ON public.odoo_modules FOR SELECT USING (true);
CREATE POLICY "Allow read design_system_languages"
    ON public.design_system_languages FOR SELECT USING (true);

-- Service role write access
CREATE POLICY "Service role write capabilities"
    ON public.odoo_capabilities FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role write modules"
    ON public.odoo_modules FOR ALL
    USING (auth.role() = 'service_role');
```

---

## Edge Functions

### sync-odoo-modules

```typescript
// supabase/functions/sync-odoo-modules/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { modules } = await req.json()

    // Upsert modules
    const { data, error } = await supabase
      .from('odoo_modules')
      .upsert(
        modules.map((m: any) => ({
          module_name: m.name,
          display_name: m.shortdesc,
          category: m.category,
          source: classifySource(m.name, m.license),
          installed_version: m.installed_version,
          is_installed: true,
          last_synced_at: new Date().toISOString(),
        })),
        { onConflict: 'module_name' }
      )

    if (error) throw error

    return new Response(
      JSON.stringify({ success: true, count: modules.length }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

function classifySource(name: string, license: string): string {
  if (name.startsWith('ipai_')) return 'ipai'
  if (license === 'OEEL-1') return 'ee' // Should never happen
  if (name.includes('oca')) return 'oca'
  return 'ce'
}
```

---

## GitHub Integration

### config.toml

```toml
# supabase/config.toml

[project]
name = "odoo-ce-catalogs"

[db]
major_version = 15

[db.seed]
enabled = true

[api]
enabled = true
port = 54321
schemas = ["public", "mcp_jobs"]

[studio]
enabled = true

[functions]
verify_jwt = false

[auth]
enabled = true
site_url = "https://erp.insightpulseai.net"

[auth.email]
enable_signup = true
double_confirm_changes = true

[realtime]
enabled = true
```

### GitHub Workflow

```yaml
# .github/workflows/supabase-branch.yml

name: Supabase Branch Sync

on:
  push:
    branches:
      - 'feature/*'
      - 'claude/*'
    paths:
      - 'supabase/**'
      - 'scripts/sync_to_supabase.py'

jobs:
  sync-catalogs:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Link to Supabase project
        run: |
          supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Push database changes
        run: |
          supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Deploy Edge Functions
        run: |
          supabase functions deploy sync-odoo-modules
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Sync Odoo modules to catalog
        env:
          ODOO_URL: ${{ secrets.DEV_ODOO_URL }}
          ODOO_PASSWORD: ${{ secrets.ODOO_ADMIN_PASSWORD }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          pip install supabase
          python scripts/sync_to_supabase.py
```

---

## Environment Variables

### Required Secrets

| Secret | Description |
|--------|-------------|
| `SUPABASE_PROJECT_REF` | Project reference ID (`spdtwktxdalcfigzeqrz`) |
| `SUPABASE_ACCESS_TOKEN` | Personal access token for CLI |
| `SUPABASE_URL` | Project URL |
| `SUPABASE_ANON_KEY` | Anonymous API key |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (for writes) |

### .env Configuration

```bash
# Supabase (Catalog Integration)
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

---

## CLI Commands

```bash
# Initialize Supabase locally
supabase init

# Start local development
supabase start

# Create new migration
supabase migration new <name>

# Apply migrations
supabase db push

# Reset database (applies all migrations + seeds)
supabase db reset

# Deploy Edge Functions
supabase functions deploy <function-name>

# Link to remote project
supabase link --project-ref spdtwktxdalcfigzeqrz
```

---

## Validation

```bash
# Check Supabase connection
curl -sf "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY" | jq .

# Verify catalogs exist
curl -sf "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/odoo_modules?limit=5" \
  -H "apikey: $SUPABASE_ANON_KEY" | jq .

# Check Edge Function
curl -sf "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/sync-odoo-modules" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": []}'
```

---

*See [PROGRAMMATIC_CONFIG_PLAN.md](../PROGRAMMATIC_CONFIG_PLAN.md) for full configuration details*
