# Auth + RLS Function Access Pattern

## Purpose
Server-side database access with user context and Row-Level Security (RLS) enforcement for non-Odoo apps/portals.

## Folder Layout
```
supabase/functions/user-context-operation/
├── index.ts                 # Handler with user context
├── .env.example             # Required env vars
└── README.md                # Function documentation
```

## Required Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Anonymous key for RLS-enforced operations (NOT service role)
- `SUPABASE_SERVICE_ROLE_KEY`: Only for elevated workers with audit trails (optional)

## Minimal Code Skeleton

**User-context function (RLS-enforced):**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY')!

serve(async (req) => {
  try {
    // Extract user JWT from Authorization header
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response('Unauthorized', { status: 401 })
    }

    // Initialize Supabase client with user context (RLS enforced)
    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: { Authorization: authHeader }
      }
    })

    // Verify user session
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response('Invalid token', { status: 401 })
    }

    // RLS-enforced query (only returns rows user has access to)
    const { data, error } = await supabase
      .from('ops.runs')
      .select('*')
      .eq('user_id', user.id) // RLS policy enforces this automatically

    if (error) throw error

    return new Response(
      JSON.stringify({ data, user_id: user.id }),
      { headers: { "Content-Type": "application/json" }, status: 200 }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { "Content-Type": "application/json" }, status: 500 }
    )
  }
})
```

**Service role function (elevated, for workers only):**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

serve(async (req) => {
  try {
    // Service role client (bypasses RLS, use with caution)
    const supabase = createClient(supabaseUrl, supabaseServiceRoleKey)

    // CRITICAL: Emit audit trail for ALL service role operations
    const { data: run } = await supabase
      .from('ops.runs')
      .insert({
        run_id: crypto.randomUUID(),
        function_name: 'elevated-worker',
        started_at: new Date().toISOString(),
        status: 'running',
        metadata: { role: 'service', reason: 'batch-sync' }
      })
      .select()
      .single()

    // Perform elevated operation
    const { data, error } = await supabase
      .from('ops.artifacts')
      .select('*')
      // No RLS restriction, but MUST log in ops.run_events

    if (error) throw error

    // Log operation
    await supabase.from('ops.run_events').insert({
      run_id: run.run_id,
      event_type: 'info',
      message: `Accessed ${data.length} artifacts with service role`,
      created_at: new Date().toISOString()
    })

    // Update run status
    await supabase
      .from('ops.runs')
      .update({ status: 'completed', completed_at: new Date().toISOString() })
      .eq('run_id', run.run_id)

    return new Response(
      JSON.stringify({ data, run_id: run.run_id }),
      { headers: { "Content-Type": "application/json" }, status: 200 }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { "Content-Type": "application/json" }, status: 500 }
    )
  }
})
```

## Failure Modes
- **Missing/invalid JWT**: Always return 401, never bypass authentication
- **RLS policy mismatch**: If query returns unexpected results, check RLS policies in database
- **Service role abuse**: Never expose service role key to clients; only use in backend workers
- **Session expiration**: Handle `401` responses gracefully, refresh token if needed

## SSOT/SOR Boundary Notes
- **RLS perimeter**: All non-Odoo apps/portals MUST use RLS-enforced access (anon key + user JWT)
- **Service role restrictions**: Only workers may use service role; MUST emit audit trail (`ops.runs/run_events`)
- **No SOR exposure**: RLS policies must NEVER grant anon/authenticated access to `odoo_replica.*` tables
- **User context**: Functions inherit user permissions; RLS policies enforce SSOT boundary automatically
- **Audit requirements**: Every service role operation must be logged in `ops.run_events` with justification
