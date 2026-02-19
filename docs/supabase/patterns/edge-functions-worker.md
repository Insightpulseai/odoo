# Edge Functions Worker Pattern

## Purpose
Canonical Edge Function worker structure for Supabase-based orchestration, webhook ingestion, and async job processing with SSOT/SOR boundary enforcement.

## Folder Layout
```
supabase/functions/<name>/
├── index.ts                 # Main handler
├── .env.example             # Template for required env vars
└── README.md                # Function-specific documentation
```

## Required Environment Variables
- `SUPABASE_URL`: Supabase project URL (for client initialization)
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for elevated database access (workers only)
- `SUPABASE_ANON_KEY`: Anonymous key for RLS-enforced operations (optional, for user-context workers)

## Minimal Code Skeleton

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

serve(async (req) => {
  try {
    // Initialize Supabase client with service role (elevated access)
    const supabase = createClient(supabaseUrl, supabaseServiceRoleKey)

    // Parse request body
    const body = await req.json()

    // SSOT/SOR Boundary: Emit ops.runs record
    const { data: run, error: runError } = await supabase
      .from('ops.runs')
      .insert({
        run_id: crypto.randomUUID(),
        function_name: 'worker-name',
        started_at: new Date().toISOString(),
        status: 'running'
      })
      .select()
      .single()

    if (runError) throw runError

    // Worker logic here
    // ...

    // Emit ops.run_events
    await supabase.from('ops.run_events').insert({
      run_id: run.run_id,
      event_type: 'info',
      message: 'Processing completed',
      created_at: new Date().toISOString()
    })

    // Update run status
    await supabase
      .from('ops.runs')
      .update({ status: 'completed', completed_at: new Date().toISOString() })
      .eq('run_id', run.run_id)

    return new Response(
      JSON.stringify({ success: true, run_id: run.run_id }),
      { headers: { "Content-Type": "application/json" }, status: 200 }
    )

  } catch (error) {
    // Error handling with ops.run_events emission
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { "Content-Type": "application/json" }, status: 500 }
    )
  }
})
```

## Failure Modes
- **Network timeout**: Set `Deno.serve` timeout, implement exponential backoff for retries
- **Database connection failure**: Use connection pooling, catch and log errors
- **Missing environment variables**: Validate at startup, fail fast with clear error messages
- **Idempotency violation**: Check `ops.runs` for duplicate `run_id` before processing

## SSOT/SOR Boundary Notes
- **Required**: Every Edge Function worker MUST emit `ops.runs`, `ops.run_events`, `ops.artifacts` to maintain audit trail
- **Service role usage**: Only workers may use service role key; app clients use RLS-enforced anon key
- **No SOR writes**: Edge Functions must NEVER write to Odoo-owned domains (ledger, posted docs, inventory moves)
- **Exception queues**: If worker detects SOR conflict, route to exception queue instead of direct write
- **Provenance**: All SSOT data created by workers must include `source` field pointing to originating system
