# Ops Control Room - Quick Start

## Overview
A ChatGPT-style app that turns messy user intents into structured, tool-backed workflows. Think "secure delegated executor" with a native UI for DevOps runbooks, spec generation, incident triage, and more.

## Current Status ✅

The app is fully functional with:
- ✅ Tab-based interface (Chat, Templates, Runs, Spec Kit)
- ✅ Runbook card UI with intent parsing
- ✅ Realtime log streaming via Supabase
- ✅ Artifact viewer for outputs
- ✅ Template management
- ✅ Spec Kit editor for Continue Orchestrator docs
- ✅ Enhanced run log viewer

## Quick Setup (5 minutes)

### 1. Database Setup
The app requires Supabase to be configured. You should already have your Supabase credentials in Figma Make.

**Run these SQL scripts in your Supabase Dashboard (SQL Editor):**

1. **Main Schema** - `/supabase/migrations/20250103000000_ops_schema.sql`
   - Creates all tables (runs, run_events, artifacts, run_templates, spec_docs)
   - Sets up indexes and RLS policies
   - Seeds initial data (2 templates, 4 spec docs)

2. **Enable Anonymous Access** - `/supabase/migrations/20250103000001_enable_anon_access.sql`
   - Allows prototyping without authentication
   - Updates RLS policies for anon role access

### 2. Verify Setup
1. Click **"Test Connection"** button in the app header
2. You should see: `• 2 templates • 4 spec docs • 0 runs`
3. If you see errors, check `/SUPABASE_SETUP_GUIDE.md`

### 3. Enable Realtime (Important!)
In Supabase Dashboard → Database → Replication:
- Enable realtime for `ops.runs`
- Enable realtime for `ops.run_events`
- Enable realtime for `ops.artifacts`

### 4. Configure API Settings
In Supabase Dashboard → Settings → API:
- Ensure `ops` is in the list of **Exposed schemas**

## Usage

### Chat Tab
Type natural language commands:
- "Deploy prod"
- "Check prod status"
- "Generate spec for user dashboard"
- "Fix production error"

The app will:
1. Parse your intent into a runbook plan
2. Show a card with inputs, risks, and integrations
3. Click **Run** to execute (streaming logs in real-time)

### Templates Tab
- Browse pre-configured runbook templates
- Click to run a template
- Templates are loaded from `ops.run_templates` table

### Runs Tab
- View all past runbook executions
- Click to see logs and artifacts
- Real-time status updates

### Spec Kit Tab
- View/edit Continue Orchestrator specification documents
- 4 docs: constitution.md, prd.md, plan.md, tasks.md
- Changes save to Supabase

## Architecture

```
Frontend (Figma Make/React)
    ↓
Supabase (Backend)
    ├── Database (ops schema)
    │   ├── runs
    │   ├── run_events
    │   ├── artifacts
    │   ├── run_templates
    │   └── spec_docs
    ├── Edge Functions
    │   └── ops-executor (runbook execution)
    └── Realtime (log streaming)
```

## Key Files

### Frontend
- `/src/app/App.tsx` - Main app with tab navigation
- `/src/app/components/SpecKitPanel.tsx` - Spec Kit editor
- `/src/app/components/RunLogViewerEnhanced.tsx` - Real-time log viewer
- `/src/lib/supabase.ts` - Supabase client (configured for `ops` schema)
- `/src/lib/runs.ts` - Run management functions

### Backend
- `/supabase/migrations/20250103000000_ops_schema.sql` - Main schema
- `/supabase/migrations/20250103000001_enable_anon_access.sql` - Anonymous access
- `/supabase/functions/ops-executor/index.ts` - Runbook executor

### Documentation
- `/SUPABASE_SETUP_GUIDE.md` - Detailed setup instructions
- `/DATABASE_FIX_SUMMARY.md` - Technical details of recent fixes
- `/QUICKSTART_OCR.md` (this file)

## Database Schema

### `ops.runs`
Stores runbook executions
- `id` (uuid) - Unique run ID
- `kind` (text) - deploy | healthcheck | spec | incident | schema_sync
- `env` (text) - prod | staging | dev
- `status` (text) - queued | running | success | error
- `plan` (jsonb) - Full runbook plan
- `created_at`, `started_at`, `finished_at`

### `ops.run_events`
Streaming log entries
- `run_id` (uuid) - FK to runs
- `level` (text) - debug | info | warn | error | success
- `source` (text) - Component that logged the event
- `message` (text) - Log message
- `data` (jsonb) - Additional structured data

### `ops.artifacts`
Output files/links from runs
- `run_id` (uuid) - FK to runs
- `kind` (text) - link | diff | file
- `title` (text) - Artifact name
- `value` (text) - Artifact content/URL

### `ops.run_templates`
Pre-configured runbook templates
- `slug` (text) - Unique identifier
- `title` (text) - Display name
- `description` (text) - What the template does
- `template_yaml` (text) - YAML-formatted runbook definition

### `ops.spec_docs`
Continue Orchestrator specification documents
- `slug` (text) - File path (e.g., "continue-orchestrator/prd")
- `title` (text) - Display name (e.g., "prd.md")
- `content` (text) - Markdown content
- `updated_at` (timestamptz) - Last modification time

## Troubleshooting

### "Failed to load spec docs"
1. Check if migrations were run (Test Connection button)
2. Verify `ops` schema is exposed in Supabase API settings
3. Check browser console for specific error
4. See `/SUPABASE_SETUP_GUIDE.md`

### "No templates found"
Run the main schema migration - it includes seed data

### Logs not streaming
1. Check realtime is enabled for the tables
2. Verify the executor function is deployed
3. Check Supabase logs for errors

### "Permission denied"
Run the anonymous access migration

## Next Steps

### Add Authentication (Optional)
For production, implement proper auth:
1. Enable auth provider in Supabase
2. Implement sign-in UI
3. Update RLS policies to use `auth.uid()`

### Implement Runbook Executor
The `ops-executor` function currently returns demo logs. To make it functional:
1. Parse the runbook YAML template
2. Execute steps sequentially
3. Emit events and artifacts
4. Handle errors and retries

### Add More Runbook Types
Extend the system with:
- Campaign Intelligence
- Data Model Inspector
- Deployment workflows
- Incident response playbooks

### Implement PiP Mode
For long-running workflows:
- Picture-in-picture log viewer
- Background execution status
- Desktop notifications

## Learn More

- [Figma Make Documentation](https://help.figma.com/hc/en-us/articles/...)
- [Supabase Documentation](https://supabase.com/docs)
- [Continue Orchestrator Spec Kit](spec/continue-orchestrator/)

## Support

For issues or questions:
1. Check `/SUPABASE_SETUP_GUIDE.md` for setup help
2. Check browser console for errors
3. Check Supabase Dashboard → API → Logs
4. Review `/DATABASE_FIX_SUMMARY.md` for technical details
