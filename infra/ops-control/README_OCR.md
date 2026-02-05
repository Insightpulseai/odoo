# Ops Control Room - Implementation Guide

## Overview
The **Ops Control Room** is a working prototype that renders runbook cards, triggers Supabase Edge Function execution, streams run logs/artifacts in realtime, and includes an integrated Spec Kit viewer/editor for Continue Orchestrator documentation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Figma Make Frontend                        │
│  ┌──────────┬──────────┬──────────┬────────────────────────┐   │
│  │   Chat   │Templates │  Runs    │      Spec Kit          │   │
│  └──────────┴──────────┴──────────┴────────────────────────┘   │
│                            ↓                                     │
│              IntentBar / RunbookCard / LogViewer                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase Backend                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ops.runs │ ops.run_events │ ops.artifacts               │  │
│  │  ops.run_templates │ ops.spec_docs                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│              Realtime subscriptions (streaming logs)             │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ops-executor Edge Function                       │
│  Claim queued runs → Execute phases → Emit events/artifacts     │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### Tables
- **ops.runs**: Stores runbook execution metadata (status, env, kind, plan)
- **ops.run_events**: Append-only log entries (level, source, message, data)
- **ops.artifacts**: Output files/links (kind: link/diff/file)
- **ops.run_templates**: Predefined runbook templates (YAML definitions)
- **ops.spec_docs**: Spec Kit documents (markdown content, editable in-app)

### RLS Policies
- Users can read/write their own runs
- Service role (executor) can write events/artifacts
- Templates and spec docs are readable/writable by authenticated users

### Realtime
- `ops.run_events` - Live log streaming
- `ops.artifacts` - Live artifact updates
- `ops.runs` - Status changes

## Setup Instructions

### 1. Database Migration
Apply the migration to create the schema + seed data:

```bash
# If using Supabase CLI locally
supabase db push

# Or apply via Supabase Dashboard → SQL Editor
# Copy/paste contents of /supabase/migrations/20250103000000_ops_schema.sql
```

**Verify tables exist:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'ops' 
ORDER BY table_name;
```

Expected output: `artifacts`, `run_events`, `run_templates`, `runs`, `spec_docs`

### 2. Deploy Edge Function
Deploy the `ops-executor` function:

```bash
# Set required secrets (hosted Supabase)
supabase secrets set \
  SUPABASE_URL="https://<project-ref>.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"

# Deploy function
supabase functions deploy ops-executor
```

**Verify deployment:**
```bash
# Check function logs
supabase functions logs ops-executor
```

### 3. Configure Frontend Environment
Set these in your Figma Make project or `.env` file:

```env
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon-key>
```

### 4. Run Locally (Optional)
```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit `http://localhost:5173` and verify:
1. Supabase connection banner is green
2. Templates tab shows 2 seed templates
3. Spec Kit tab shows 4 documents

## Usage Guide

### Running a Runbook

#### Option 1: Chat Interface
1. Go to **Chat** tab
2. Type intent (e.g., "Deploy prod")
3. Review generated runbook card
4. Click **Run** → logs stream in fullscreen viewer

#### Option 2: Templates
1. Go to **Templates** tab
2. Use **IntentBar** for quick runs or click **Run** on a template card
3. Logs stream in realtime viewer
4. View artifacts in right sidebar

#### Option 3: Browse Runs
1. Go to **Runs** tab
2. Click any run to view logs/artifacts
3. Status badges show queued/running/success/error

### Editing Spec Kit
1. Go to **Spec Kit** tab
2. Select a document (constitution/prd/plan/tasks)
3. Edit markdown content
4. Click **Save** → updates `ops.spec_docs` table

## Execution Flow

```
User submits intent
  ↓
Frontend creates ops.runs row (status=queued)
  ↓
Frontend invokes ops-executor Edge Function
  ↓
Executor claims run (atomic, status=running)
  ↓
Executor executes phases:
  - Phase 0: Validate inputs
  - Phase 1: Preflight checks
  - Phase 2: Execute action (deploy/spec/incident/etc.)
  - Phase 3: Verify results
  - Phase 4: Summarize
  ↓
Executor emits events to ops.run_events
  ↓
Executor writes artifacts to ops.artifacts
  ↓
Executor marks run complete (status=success/error)
  ↓
Frontend receives realtime events via Supabase Realtime
  ↓
UI updates logs/artifacts/status in realtime (<1s latency)
```

## Testing Checklist

### ✅ Basic Flow
- [ ] Create run from chat → logs stream
- [ ] Create run from template → logs stream
- [ ] View past run from Runs tab
- [ ] Events appear within 1-2 seconds
- [ ] Artifacts populated after completion

### ✅ Realtime
- [ ] New events appear without refresh
- [ ] Status badge updates automatically
- [ ] Artifacts list updates automatically

### ✅ Spec Kit
- [ ] Load all 4 documents
- [ ] Edit document content
- [ ] Save document → persists in DB
- [ ] Refresh → edits retained

### ✅ RLS
- [ ] User can only see their own runs
- [ ] Cannot read other users' events/artifacts
- [ ] Templates/spec docs readable by all authenticated

## Troubleshooting

### No events streaming
**Check:**
1. Realtime enabled in Supabase Dashboard → Database → Replication
2. Tables added to `supabase_realtime` publication (migration handles this)
3. Browser console for WebSocket errors

**Fix:**
```sql
-- Re-add tables to realtime
ALTER publication supabase_realtime ADD TABLE ops.run_events;
ALTER publication supabase_realtime ADD TABLE ops.artifacts;
ALTER publication supabase_realtime ADD TABLE ops.runs;
```

### Executor not running
**Check:**
1. Function deployed: `supabase functions list`
2. Secrets set: `supabase secrets list`
3. Function logs: `supabase functions logs ops-executor`

**Fix:**
```bash
# Redeploy
supabase functions deploy ops-executor --no-verify-jwt

# Test manually
curl -X POST https://<project-ref>.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer <anon-key>" \
  -H "Content-Type: application/json"
```

### Templates not showing
**Check seed data:**
```sql
SELECT count(*) FROM ops.run_templates;
```

If count is 0, re-run migration or insert manually:
```sql
-- See /supabase/migrations/20250103000000_ops_schema.sql (SEED DATA section)
```

## Extension Points

### Add a new runbook template
```sql
INSERT INTO ops.run_templates (slug, title, description, template_yaml)
VALUES (
  'my-new-runbook',
  'My New Runbook',
  'Does X, Y, Z',
  'version: 1
inputs:
  - key: param1
    label: Parameter 1
    type: string
    required: true
steps:
  - id: step1
    title: Step 1
    kind: system
    action: some_action'
);
```

### Add a new spec doc
```sql
INSERT INTO ops.spec_docs (slug, title, content)
VALUES (
  'continue-orchestrator/architecture',
  'architecture.md',
  '# Architecture\n\nDetailed architecture docs...'
);
```

### Customize executor behavior
Edit `/supabase/functions/ops-executor/index.ts`:
- Add new `kind` handlers in `runAction()`
- Add integration adapters (replace stubs)
- Add policy enforcement logic

## Production Readiness

Before deploying to production:

1. **Enable auth**: Configure OAuth providers or email/password
2. **Add user management**: Restrict runs to authenticated users
3. **Implement real integrations**: Replace adapter stubs with actual API calls
4. **Add policy enforcement**: Implement approval gates + budget limits
5. **Set up monitoring**: Track executor failures, latency, event volumes
6. **Optimize RLS**: Add indexes on `created_by` for large run volumes

## File Reference

```
/supabase/migrations/20250103000000_ops_schema.sql  # DB schema + seed data
/supabase/functions/ops-executor/index.ts           # Executor function
/src/app/App.tsx                                    # Main UI with tabs
/src/app/components/IntentBar.tsx                   # Intent submission
/src/app/components/RunbookTemplateCard.tsx         # Template card UI
/src/app/components/RunLogViewerEnhanced.tsx        # Realtime log viewer
/src/app/components/SpecKitPanel.tsx                # Spec editor
/spec/continue-orchestrator/*.md                    # Spec Kit docs (repo)
```

## Support

For issues:
1. Check Supabase function logs
2. Check browser console for RLS/auth errors
3. Verify migration applied correctly
4. Test realtime connection: `supabase realtime test`
