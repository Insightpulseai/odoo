# Supabase UI Library - Prioritized Backlog

**Generated**: 2026-01-27
**Based on**: 55 repositories, 63 blocks discovered
**Target**: shadcn/ui-based blocks with single-command Supabase integration

---

## Epic 1: Authentication & Identity (P0) 🔐

**Goal**: Drop-in auth components with Supabase integration

### Stories:

#### 1.1 Auth Component Library
- **Description**: Port official Supabase Auth component to shadcn/ui
- **Source**: `supabase/ui/src/components/Auth/` (1636 stars)
- **Acceptance Criteria**:
  - Email/password login + signup forms
  - OAuth provider buttons (Google, GitHub, Apple)
  - Magic link flows
  - Phone number verification
  - Configurable via `supabase.auth.config`
- **Security**: RLS policies auto-applied on signup
- **Implementation Sketch**:
  ```tsx
  import { AuthUI } from '@/components/supabase-ui/auth'
  <AuthUI providers={['github', 'google']} />
  ```

#### 1.2 User Profile & Avatar Management
- **Description**: Profile editing + avatar upload to Supabase Storage
- **Source**: `supabase/ui/src/components/Avatar/` + `supabase/ui/src/components/Upload/`
- **Acceptance Criteria**:
  - Avatar upload to `avatars` bucket
  - Profile metadata editor
  - Real-time avatar updates
  - CDN-optimized image transforms
- **Security**: Storage RLS (users can only upload to own folder)
- **DoD**: Profile page works offline, syncs on reconnect

#### 1.3 Session Management UI
- **Description**: User menu, session timeout warnings, multi-device sessions
- **Acceptance Criteria**:
  - Dropdown menu with logout
  - Session expiry countdown
  - "Active on 3 devices" indicator
  - Force logout all sessions
- **Security**: Refresh token rotation enabled

---

## Epic 2: Real-time Collaboration (P0) 🔄

**Goal**: Live data sync components (cursors, presence, notifications)

### Stories:

#### 2.1 Real-time Cursor Tracking
- **Description**: Multi-user cursor positions in collaborative views
- **Source**: `AndyUGA/supabase_ui_library_realtime_cursor`
- **Acceptance Criteria**:
  - Cursor position broadcast via Supabase Realtime
  - User name + color labels
  - Auto-hide inactive cursors (>5s)
  - Smooth cursor interpolation
- **Security**: Presence channel RLS (workspace members only)
- **Implementation Sketch**:
  ```tsx
  <RealtimeCursors channel="document-123" />
  ```

#### 2.2 Presence Indicators
- **Description**: "Who's online" avatars + typing indicators
- **Acceptance Criteria**:
  - Avatar list with online status
  - Typing indicators per field
  - "Last seen" timestamps
  - Idle detection (>5 min)
- **Security**: Presence data scoped per workspace

#### 2.3 Toast Notifications (Real-time)
- **Description**: Toast UI for Supabase DB/Storage events
- **Source**: `supabase/ui/src/components/Toast/`
- **Acceptance Criteria**:
  - Subscribe to table changes → toast
  - File upload progress → toast
  - Collaborative edits → "User X edited field Y"
  - Undo action support
- **DoD**: Notifications persist across page reloads (IndexedDB)

---

## Epic 3: Data Storage & File Management (P0) 📦

**Goal**: Supabase Storage integration with drag-drop UI

### Stories:

#### 3.1 File Upload Dropzone
- **Description**: Drag-drop file uploader with progress
- **Source**: `AndyUGA/supabase_ui_library_dropzone` + `supabase/ui/src/components/Upload/`
- **Acceptance Criteria**:
  - Multi-file drag-drop
  - Upload progress bars
  - File type validation (client + server)
  - Automatic CDN URL generation
  - Chunked upload for large files (>10MB)
- **Security**: Storage RLS policies enforced
- **Implementation Sketch**:
  ```tsx
  <StorageDropzone bucket="documents" path={`users/${userId}`} />
  ```

#### 3.2 File Browser & Gallery
- **Description**: Browse Supabase Storage buckets with previews
- **Acceptance Criteria**:
  - Folder tree navigation
  - Image/video previews
  - Download + delete actions
  - Search by filename
  - Grid/list view toggle
- **Security**: RLS filters files by user access
- **DoD**: Works with 10K+ files (virtualized list)

---

## Epic 4: Admin & Dashboard Blocks (P1) 📊

**Goal**: Ready-to-deploy admin panels for Supabase backends

### Stories:

#### 4.1 Data Table with Server-Side Rendering
- **Description**: TanStack Table + Supabase pagination
- **Source**: `thisisfel1x/supabase-shadcn-database-example` (42 stars)
- **Acceptance Criteria**:
  - Server-side pagination (1000+ rows)
  - Column filters + sorting
  - Inline editing
  - Bulk actions (delete, export)
  - CSV/Excel export
- **Security**: Table RLS policies respected
- **Implementation Sketch**:
  ```tsx
  <SupabaseTable table="products" columns={columns} />
  ```

#### 4.2 Form Builder with Validation
- **Description**: Auto-generate forms from Supabase table schemas
- **Acceptance Criteria**:
  - Dynamic form generation from `public.tables` metadata
  - Zod schema validation
  - Field types: text, number, select, date, file upload
  - Real-time validation feedback
  - Optimistic updates
- **DoD**: Form works offline, queues changes

#### 4.3 Dashboard Stat Cards
- **Description**: KPI cards with Supabase aggregations
- **Acceptance Criteria**:
  - SQL aggregation queries (COUNT, SUM, AVG)
  - Trend indicators (↑/↓)
  - Chart.js integration
  - Auto-refresh (configurable interval)
- **Security**: Row-level filters applied to stats

---

## Epic 5: MCP Integration Blocks (P1) 🧩

**Goal**: Model Context Protocol tool registry + run UI

### Stories:

#### 5.1 MCP Tool Registry Browser
- **Description**: Browse + search available MCP tools
- **Acceptance Criteria**:
  - List all tools from `mcp_tools` table
  - Filter by category (database, file, api, compute)
  - Tool detail view (params, examples)
  - Star/bookmark tools
- **Security**: Public tools only (no service role keys exposed)
- **Implementation Sketch**:
  ```tsx
  <MCPToolBrowser onSelect={tool => /* run tool */} />
  ```

#### 5.2 MCP Run History & Logs
- **Description**: View past MCP tool executions
- **Acceptance Criteria**:
  - List runs from `mcp_runs` table
  - Filter by status (pending, running, success, failed)
  - View input/output artifacts
  - Re-run failed jobs
  - Log streaming for active runs
- **Security**: Users see only their own runs (RLS)
- **DoD**: Real-time log updates via Supabase Realtime

#### 5.3 MCP Artifact Viewer
- **Description**: Render MCP execution artifacts (code, images, JSON)
- **Acceptance Criteria**:
  - Syntax-highlighted code diffs
  - Image preview for screenshots
  - JSON tree explorer
  - Download artifact button
- **Security**: Artifacts scoped per user + run

---

## Epic 6: n8n Workflow Integration (P1) 🔗

**Goal**: Embed n8n workflow triggers/status in UI

### Stories:

#### 6.1 Workflow Trigger Buttons
- **Description**: One-click workflow execution from UI
- **Acceptance Criteria**:
  - Button component calls n8n webhook
  - Pass context params (user_id, record_id)
  - Show loading state during execution
  - Success/failure toast
- **Security**: Webhook URLs stored in Supabase Vault
- **Implementation Sketch**:
  ```tsx
  <N8NTrigger workflow="expense-approval" params={{recordId: 123}} />
  ```

#### 6.2 Workflow Status Dashboard
- **Description**: View n8n workflow runs
- **Acceptance Criteria**:
  - List recent runs from n8n API
  - Status badges (running, success, error)
  - Execution time histogram
  - Error log viewer
- **DoD**: Auto-refresh every 30s

#### 6.3 Workflow Builder UI (Light)
- **Description**: Simple visual workflow editor (not full n8n)
- **Acceptance Criteria**:
  - Drag-drop nodes (trigger, action, condition)
  - Connect nodes visually
  - Save workflow JSON to Supabase
  - Export to n8n format
- **Security**: Workflow definitions stored with RLS
- **DoD**: Works for 90% of simple automation cases

---

## Epic 7: Observability & Logging (P2) 📈

**Goal**: Vercel-style observability UI for Supabase logs

### Stories:

#### 7.1 Log Viewer with Search
- **Description**: Tail Supabase logs with filtering
- **Acceptance Criteria**:
  - Stream logs from Supabase Logs API
  - Filter by level (info, warn, error)
  - Search by message text
  - Time range selector
  - Export logs (JSON/CSV)
- **Security**: Admin-only access (check user role)
- **Implementation Sketch**:
  ```tsx
  <LogViewer source="postgres" level="error" />
  ```

#### 7.2 Distributed Tracing UI
- **Description**: OpenTelemetry trace visualization
- **Acceptance Criteria**:
  - Flamegraph for request traces
  - Span details (duration, attributes)
  - Trace search by trace_id
  - Link spans to code (if available)
- **DoD**: Integrates with Vercel/Datadog/Honeycomb traces

#### 7.3 Metrics Dashboard
- **Description**: Prometheus-style metrics (P50, P95, P99)
- **Acceptance Criteria**:
  - Query latency histograms
  - Error rate % over time
  - Database connection pool stats
  - Storage bandwidth usage
- **Security**: Aggregated data only (no PII)
- **DoD**: Auto-refresh with configurable interval

---

## Epic 8: DataOps & Catalog (P2) 🗂️

**Goal**: Databricks-style data catalog + job orchestration

### Stories:

#### 8.1 Data Catalog Explorer
- **Description**: Browse Supabase tables, views, functions
- **Acceptance Criteria**:
  - Tree view of schemas/tables
  - Column metadata (type, nullable, default)
  - Foreign key relationships diagram
  - Sample data preview (first 10 rows)
  - Table lineage graph
- **Security**: Only show tables user has access to (RLS)
- **Implementation Sketch**:
  ```tsx
  <DataCatalog schema="public" onTableSelect={table => /* query */} />
  ```

#### 8.2 Job Run History
- **Description**: View ETL/cron job executions
- **Acceptance Criteria**:
  - List jobs from `etl_jobs` table
  - Run status timeline (Gantt chart)
  - Retry failed jobs
  - Job duration trends
  - Dependency graph (which jobs trigger others)
- **DoD**: Real-time updates via Supabase Realtime

#### 8.3 Query Builder UI
- **Description**: Visual SQL query builder (no-code)
- **Acceptance Criteria**:
  - Select table + columns
  - Add filters (WHERE clauses)
  - Join tables visually
  - Group by + aggregations
  - Export SQL or run directly
- **Security**: Generated SQL respects RLS
- **DoD**: Saved queries stored in Supabase

---

## Single-Command Integration Plan 🚀

### Installation:
```bash
npx create-supabase-ui-app my-app --blocks=auth,realtime,storage,admin
cd my-app
npm run dev
```

### What It Does:
1. ✅ Scaffolds Next.js 15 + Supabase project
2. ✅ Installs shadcn/ui + selected blocks
3. ✅ Generates Supabase types from schema
4. ✅ Sets up RLS policies (boilerplate)
5. ✅ Creates example pages for each block
6. ✅ Configures Supabase env vars (`.env.local`)

### Block Activation:
```tsx
// app/page.tsx
import { AuthUI, RealtimeCursors, StorageDropzone } from '@supabase-ui/blocks'

export default function Home() {
  return (
    <>
      <AuthUI providers={['github']} />
      <RealtimeCursors channel="lobby" />
      <StorageDropzone bucket="uploads" />
    </>
  )
}
```

### Configuration:
```ts
// supabase-ui.config.ts
export default {
  blocks: {
    auth: { providers: ['github', 'google'], magicLink: true },
    realtime: { cursors: true, presence: true },
    storage: { buckets: ['uploads', 'avatars'], maxSize: '10MB' },
    admin: { tables: ['products', 'orders'], roles: ['admin'] }
  },
  theme: 'default', // or custom shadcn theme
  security: {
    rls: true, // enforce RLS on all queries
    https: true // require HTTPS in production
  }
}
```

---

## Priority Scoring Rationale

| Epic | Priority | Rationale |
|------|----------|-----------|
| Auth & Identity | P0 | Every Supabase app needs auth, 22 components found |
| Real-time | P0 | Core Supabase differentiator, high user value |
| Storage | P0 | File uploads are table stakes for modern apps |
| Admin & Dashboard | P1 | 80% of apps need CRUD UI, 32 components available |
| MCP Integration | P1 | Emerging standard, future-proofs architecture |
| n8n Workflows | P1 | No-code automation = force multiplier |
| Observability | P2 | Nice-to-have, but not blocking MVP |
| DataOps & Catalog | P2 | Power user feature, smaller TAM |

---

## Definition of Done (All Stories)

- [ ] TypeScript component with full type safety
- [ ] Supabase integration tested (local + cloud)
- [ ] RLS policies documented + enforced
- [ ] Storybook story with examples
- [ ] Unit tests (>80% coverage)
- [ ] E2E test (Playwright)
- [ ] Documentation in README
- [ ] Security audit passed
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Performance budget met (<100ms interaction)
