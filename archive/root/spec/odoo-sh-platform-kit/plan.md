# Implementation Plan — Odoo.sh × Supabase Platform Kit

**Objective**: Deliver production-ready OdooOps Console template with Platform Kit integration.

---

## Phase 0: Template Stabilization ✅ (COMPLETED 2026-02-15)

### Completed Work

**Server/Client Boundary Fixes**:
- ✅ Created route groups: `(auth)` and `(app)`
- ✅ Removed `styled-jsx` from Server Components
- ✅ Isolated interactivity to Client Components (`LoginClient.tsx`, etc.)
- ✅ Auth guard: redirect authenticated users from `/login`
- ✅ App guard: redirect unauthenticated users to `/login`

**Async Params Migration**:
- ✅ Migrated 9 pages/layouts to `params: Promise<{ ... }>`
- ✅ Created automation script (`scripts/fix-async-params.py`)
- ✅ Fixed TypeScript errors (Branch types, build status)

**Missing Modules**:
- ✅ Created `src/lib/utils.ts` (cn, hasEnvVars)
- ✅ Created `src/lib/supabase/client.ts` (browser client)
- ✅ Created `src/lib/supabase/server.ts` compatibility layer

### Remaining (P0)

**UI Components**:
- [ ] Install shadcn/ui or create minimal stubs:
  - `components/ui/button.tsx`
  - `components/ui/card.tsx`
  - `components/ui/dialog.tsx`
  - `components/ui/label.tsx`
  - `components/ui/input.tsx`
- [ ] Re-enable `SupabaseManagerDialog.tsx`
- [ ] Verify: `pnpm build` passes with zero errors

---

## Phase 1: Supabase Ops Schema + RLS

**Goal**: Create multi-tenant data model with row-level security.

### Tasks

**1.1 Core Schema**
```sql
CREATE SCHEMA ops;

-- Tenants
CREATE TABLE ops.tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Memberships
CREATE TABLE ops.memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES ops.tenants(id) ON DELETE CASCADE,
  user_id UUID NOT NULL, -- References auth.users
  role TEXT NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, user_id)
);

-- Supabase Projects
CREATE TABLE ops.supabase_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES ops.tenants(id) ON DELETE CASCADE,
  project_ref TEXT UNIQUE NOT NULL,
  label TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Odoo Environments
CREATE TABLE ops.odoo_envs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES ops.tenants(id) ON DELETE CASCADE,
  env_key TEXT NOT NULL, -- dev / staging / prod
  base_url TEXT NOT NULL,
  health_url TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, env_key)
);

-- Jobs
CREATE TABLE ops.jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES ops.tenants(id) ON DELETE CASCADE,
  type TEXT NOT NULL, -- build, health_check, deploy, etc.
  status TEXT NOT NULL, -- pending, running, success, failed
  input JSONB,
  output JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log
CREATE TABLE ops.audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES ops.tenants(id) ON DELETE CASCADE,
  actor_user_id UUID NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT,
  target_id UUID,
  payload JSONB,
  outcome TEXT, -- success / failure
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**1.2 RLS Policies**
```sql
-- Enable RLS
ALTER TABLE ops.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.supabase_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.odoo_envs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.audit_log ENABLE ROW LEVEL SECURITY;

-- Helper function
CREATE OR REPLACE FUNCTION ops.user_tenants(user_uuid UUID)
RETURNS SETOF UUID AS $$
  SELECT tenant_id FROM ops.memberships WHERE user_id = user_uuid;
$$ LANGUAGE SQL STABLE;

-- Policy: Users can only access their tenant's data
CREATE POLICY tenant_isolation ON ops.tenants
  FOR ALL
  USING (id IN (SELECT ops.user_tenants(auth.uid())));

CREATE POLICY tenant_isolation ON ops.memberships
  FOR ALL
  USING (tenant_id IN (SELECT ops.user_tenants(auth.uid())));

-- ... repeat for all tables
```

**1.3 Seed Data**
```sql
-- Create initial tenant
INSERT INTO ops.tenants (slug, name) VALUES
  ('insightpulseai', 'InsightPulse AI');

-- Create membership for current user (replace with actual UUID)
INSERT INTO ops.memberships (tenant_id, user_id, role)
SELECT id, 'USER_UUID_HERE', 'admin'
FROM ops.tenants WHERE slug = 'insightpulseai';

-- Map Supabase project
INSERT INTO ops.supabase_projects (tenant_id, project_ref, label)
SELECT id, 'spdtwktxdalcfigzeqrz', 'Production Supabase'
FROM ops.tenants WHERE slug = 'insightpulseai';

-- Seed Odoo environments
INSERT INTO ops.odoo_envs (tenant_id, env_key, base_url, health_url)
SELECT id, 'dev', 'http://localhost:8069', 'http://localhost:8069/web/health'
FROM ops.tenants WHERE slug = 'insightpulseai'
UNION ALL
SELECT id, 'staging', 'https://staging.erp.insightpulseai.com', 'https://staging.erp.insightpulseai.com/web/health'
FROM ops.tenants WHERE slug = 'insightpulseai'
UNION ALL
SELECT id, 'prod', 'https://erp.insightpulseai.com', 'https://erp.insightpulseai.com/web/health'
FROM ops.tenants WHERE slug = 'insightpulseai';
```

**Verification**:
```bash
# Run migration
supabase db reset

# Test RLS
psql "$POSTGRES_URL" -c "
  SET ROLE authenticated;
  SET request.jwt.claims TO '{\"sub\": \"USER_UUID\"}';
  SELECT * FROM ops.tenants; -- Should return only user's tenant
"
```

---

## Phase 2: Platform Kit Embed + Secure Proxy

**Goal**: Embed Supabase Platform Kit with server-side authZ.

### Tasks

**2.1 Install UI Dependencies**
```bash
# Install Platform Kit
pnpm add @supabase/platform-kit-nextjs

# Install shadcn/ui (if not using manual stubs)
npx shadcn@latest init
npx shadcn@latest add dialog button card label input
```

**2.2 Create Supabase Manager Dialog**
```tsx
// components/SupabaseManagerDialog.tsx
"use client";

import { Dialog, DialogContent } from "@/components/ui/dialog";
import { PlatformKit } from "@supabase/platform-kit-nextjs";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectRef: string;
}

export function SupabaseManagerDialog({ open, onOpenChange, projectRef }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-auto">
        <PlatformKit
          projectRef={projectRef}
          apiUrl="/api/supabase-proxy"
          aiSqlUrl="/api/ai/sql" // Optional
        />
      </DialogContent>
    </Dialog>
  );
}
```

**2.3 Secure Proxy Route** (Already implemented, needs testing)
```tsx
// app/api/supabase-proxy/[...path]/route.ts
// EXISTING FILE - just needs authZ validation tests
```

**2.4 Optional AI SQL Route**
```tsx
// app/api/ai/sql/route.ts
import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import OpenAI from "openai";

export async function POST(req: NextRequest) {
  // 1. Auth check
  const supabase = createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // 2. Get request body
  const { prompt, schema, projectRef } = await req.json();

  // 3. Validate project ownership
  const { data: project } = await supabase
    .from("ops.supabase_projects")
    .select("*")
    .eq("project_ref", projectRef)
    .single();

  if (!project) return NextResponse.json({ error: "Forbidden" }, { status: 403 });

  // 4. Generate SQL via OpenAI
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      { role: "system", content: "You are a SQL expert. Generate PostgreSQL queries only. No explanations." },
      { role: "user", content: `Schema: ${JSON.stringify(schema)}\n\nPrompt: ${prompt}` }
    ],
  });

  const sql = response.choices[0]?.message?.content || "";

  // 5. Audit
  await supabase.from("ops.audit_log").insert({
    tenant_id: project.tenant_id,
    actor_user_id: user.id,
    action: "ai_sql_generate",
    target_type: "supabase_project",
    target_id: project.id,
    payload: { prompt, sql },
    outcome: "success",
  });

  return NextResponse.json({ sql });
}
```

**Verification**:
```bash
# Test dialog opens
curl http://localhost:3000/ -c cookies.txt # Login first
curl -b cookies.txt http://localhost:3000/api/supabase-proxy/projects/spdtwktxdalcfigzeqrz/database/tables

# Should return 200 with data for authorized user
# Should return 403 for wrong project_ref
```

---

## Phase 3: GitHub Integration + Runbot

(Detailed tasks for builds, webhooks, log streaming)

## Phase 4: Promotions + Backups

(Detailed tasks for promotion workflow, token scrubbing, restore)

## Phase 5: Web Shell + Mail Catcher

(Detailed tasks for exec sessions, mailbox)

## Phase 6: Constraint Gates

(Detailed tasks for preflight checks)

---

**Total Estimated Time**: 3-4 weeks (1 week per 2 phases)
**Version**: 1.0
**Last Updated**: 2026-02-15
