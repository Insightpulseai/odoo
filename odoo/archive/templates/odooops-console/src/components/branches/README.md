# Branches Lane UI Components

Odoo.sh-style 3-lane branch management interface with drag/drop promotions.

## Architecture

### Component Hierarchy

```
BranchesLane (Client)
  ├── DndContext (@dnd-kit/core)
  ├── LaneColumn × 3 (Client)
  │   ├── Production
  │   ├── Staging
  │   └── Development
  ├── BranchCard (Client, draggable)
  └── PromoteDialog (Client)
```

### File Structure

```
src/
├── components/
│   └── branches/
│       ├── BranchesLane.tsx      # Main container with DnD context
│       ├── LaneColumn.tsx        # Drop zone for each stage
│       ├── BranchCard.tsx        # Draggable branch card
│       ├── PromoteDialog.tsx     # Promotion confirmation dialog
│       └── README.md             # This file
├── lib/
│   ├── rpc/
│   │   └── branches.ts           # RPC client wrappers
│   └── types/
│       └── branches.ts           # TypeScript types
└── app/
    └── app/
        └── projects/
            └── [projectId]/
                └── branches/
                    └── page.tsx  # Server component entry point
```

## Components

### BranchesLane

**Type**: Client Component
**Purpose**: Main container managing drag/drop state and branch promotions

**Props**:
- `initialData: BranchCardDTO[]` - Initial branches from server
- `projectId: string` - Current project ID for RPC calls

**Features**:
- DnD context provider
- Branch grouping by stage
- Promotion dialog orchestration
- Optimistic UI updates
- Toast notifications

**State**:
- `branches` - Current branch list
- `activeBranch` - Currently dragging branch
- `promoteDialogOpen` - Dialog visibility
- `promotionDetails` - Promotion metadata

### LaneColumn

**Type**: Client Component
**Purpose**: Drop zone for a specific stage

**Props**:
- `stage: Stage` - Lane stage (dev | staging | production)
- `branches: BranchCardDTO[]` - Branches in this stage
- `onPromote` - Manual promotion handler
- `onRebuild` - Rebuild handler
- `onOpen` - URL open handler

**Features**:
- Drop zone with visual feedback
- Empty state handling
- Stage-specific styling (color coding)

### BranchCard

**Type**: Client Component
**Purpose**: Draggable branch card with actions

**Props**:
- `branch: BranchCardDTO` - Branch data
- `onPromote` - Promotion handler
- `onRebuild` - Rebuild handler
- `onOpen` - URL open handler

**Features**:
- Draggable with @dnd-kit
- Build status badge
- Action dropdown (Open, PR, Rebuild, Promote)
- Commit SHA display
- Timestamp formatting
- Rebuild loading state

**Status Badge Colors**:
- `green` → Success (bg-green-100)
- `yellow` → Warning (bg-yellow-100)
- `red` → Failed (bg-red-100)
- `running` → Building (bg-blue-100)

### PromoteDialog

**Type**: Client Component
**Purpose**: Confirmation dialog with policy checks

**Props**:
- `open: boolean` - Dialog visibility
- `fromStage: Stage` - Source stage
- `toStage: Stage` - Target stage
- `branch: BranchCardDTO | null` - Branch to promote
- `onConfirm: (reason?) => Promise<void>` - Confirm handler
- `onCancel: () => void` - Cancel handler

**Features**:
- Policy validation (build status, permissions)
- Production safeguards (reason required)
- Build status display
- Visual validation feedback (checkmarks/x's)

**Validations**:
- ✅ Successful build (critical for production)
- ✅ Promotion permission (always critical)

## Data Flow

### Server → Client

```
page.tsx (Server)
  → listBranchesWithBuilds(projectId)
  → RPC: ops.branches_with_builds
  → BranchesLane (initialData)
```

### Drag/Drop Promotion

```
User drags branch → LaneColumn (drop)
  → BranchesLane.handleDragEnd
  → Validate direction (no demotion)
  → Check permissions
  → Open PromoteDialog
  → User confirms
  → Optimistic UI update
  → requestPromotion RPC
  → Toast notification
  → Revert on failure
```

### Manual Promotion

```
User clicks Promote → BranchCard dropdown
  → BranchesLane.handlePromote
  → Calculate next stage
  → Open PromoteDialog
  → Same flow as drag/drop
```

## RPC Functions

### `listBranchesWithBuilds(projectId)`

Returns: `BranchCardDTO[]`

**Database RPC**: `ops.branches_with_builds`

### `requestPromotion(projectId, branchId, targetStage, reason?)`

Returns: `{ success: boolean, message?: string }`

**Database RPC**: `ops.request_promotion`

**Triggers**: Deployment workflow in target stage

### `requestRebuild(projectId, branchId)`

Returns: `{ success: boolean, build_id?: string, message?: string }`

**Database RPC**: `ops.request_rebuild`

**Triggers**: New build for branch

### `requestRollback(projectId, branchId, buildId, reason?)`

Returns: `{ success: boolean, message?: string }`

**Database RPC**: `ops.request_rollback`

**Triggers**: Rollback to previous build

## Types

### Stage

```typescript
type Stage = 'dev' | 'staging' | 'production'
```

### BuildStatus

```typescript
type BuildStatus = 'green' | 'yellow' | 'red' | 'running'
```

### BranchCardDTO

```typescript
{
  id: string
  name: string
  stage: Stage
  pinned: boolean
  pr_url?: string | null
  latest_build?: {
    id: string
    status: BuildStatus
    commit_sha: string
    started_at?: string | null
    finished_at?: string | null
    duration_s?: number | null
    url?: string | null
    logs_url?: string | null
  } | null
  permissions: {
    can_promote: boolean
    can_rebuild: boolean
    can_delete: boolean
    can_rollback: boolean
  }
}
```

## Dependencies

### @dnd-kit

- `@dnd-kit/core` - Core DnD functionality
- `@dnd-kit/sortable` - Sortable utilities (future)
- `@dnd-kit/utilities` - Helper utilities

### Radix UI

- `@radix-ui/react-dialog` - PromoteDialog
- `@radix-ui/react-dropdown-menu` - BranchCard actions
- `@radix-ui/react-label` - Form labels

### Other

- `sonner` - Toast notifications
- `lucide-react` - Icons

## Installation

```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
npm install @radix-ui/react-dialog
```

## Usage

### Server Component (page.tsx)

```typescript
import { listBranchesWithBuilds } from '@/lib/rpc/branches'
import { BranchesLane } from '@/components/branches/BranchesLane'

export default async function BranchesPage({ params }) {
  const branches = await listBranchesWithBuilds(params.projectId)

  return (
    <div className="p-6">
      <h1>Branches</h1>
      <BranchesLane initialData={branches} projectId={params.projectId} />
    </div>
  )
}
```

## Mobile Responsive

- Desktop: 3-column grid
- Tablet: 1-column stack (via `md:grid-cols-3`)
- Mobile: Touch-friendly drag/drop

## Future Enhancements

- [ ] Real-time build status updates (Supabase Realtime)
- [ ] Branch search/filter
- [ ] Sortable lanes (@dnd-kit/sortable)
- [ ] Keyboard navigation
- [ ] Bulk operations
- [ ] Branch history timeline
- [ ] Deployment slots (blue/green)
- [ ] Canary deployments
