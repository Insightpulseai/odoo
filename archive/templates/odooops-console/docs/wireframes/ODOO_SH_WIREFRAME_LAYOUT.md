# Odoo.sh Wireframe & Information Architecture

## Overview

This document describes the UI structure and navigation patterns for the OdooOps Console, mirroring Odoo.sh's proven IA.

## Information Architecture

```
Dashboard (/)
└── Projects (/app/projects)
    └── Project (/app/projects/[projectId])
        ├── Branches (/app/projects/[projectId]/branches)
        │   ├── Production lane
        │   ├── Staging lane
        │   └── Development lane
        ├── Builds (/app/projects/[projectId]/builds)
        │   └── Build (/app/projects/[projectId]/builds/[buildId])
        │       ├── Logs (/app/projects/[projectId]/builds/[buildId]/logs)
        │       ├── Shell (/app/projects/[projectId]/builds/[buildId]/shell)
        │       ├── Editor (/app/projects/[projectId]/builds/[buildId]/editor)
        │       └── Monitor (/app/projects/[projectId]/builds/[buildId]/monitor)
        ├── Backups (/app/projects/[projectId]/backups)
        ├── Upgrade (/app/projects/[projectId]/upgrade)
        ├── Settings (/app/projects/[projectId]/settings)
        └── Monitor (/app/projects/[projectId]/monitor)
```

## Navigation Patterns

### Level 1: Projects List
- Grid or table view of all projects
- Quick status indicators (build status, last deploy, health)
- Search and filter capabilities
- Create new project action

### Level 2: Project Detail
- Project header with metadata
- Horizontal tab navigation:
  - **Branches**: Branch management and deployment lanes
  - **Builds**: Build history and grid view
  - **Backups**: Backup management and restore operations
  - **Upgrade**: Odoo version upgrades and module updates
  - **Settings**: Project configuration and environment variables
  - **Monitor**: Performance metrics and resource usage

### Level 3: Build Detail
- Build header with commit info and status
- Horizontal tab navigation for build tools:
  - **Logs**: Real-time and historical logs
  - **Shell**: Web-based shell access to build container
  - **Editor**: In-browser code editor for quick fixes
  - **Monitor**: Build-specific performance metrics

## Key Features

### Branches View
- **3-Stage Deployment Pipeline**:
  - Production lane (protected)
  - Staging lane (pre-prod testing)
  - Development lane (feature branches)
- Drag-and-drop branch promotion
- Branch creation and deletion
- Merge request integration

### Builds View
- **Grid Layout**: Rows = branches, Cells = builds
- Build status indicators (pending, building, success, failed)
- One-click deploy and rollback
- Build artifacts and logs access

### Build Tools
- **Logs**: Filterable, searchable, real-time streaming
- **Shell**: Secure web terminal with authentication
- **Editor**: Code editing with syntax highlighting
- **Monitor**: CPU, memory, storage, network metrics

## Design Principles

1. **Progressive Disclosure**: Start with overview, drill down for details
2. **Consistent Navigation**: Same patterns across all levels
3. **Action Clarity**: Primary actions always visible and obvious
4. **Status Visibility**: Real-time status indicators throughout
5. **Keyboard Shortcuts**: Power user efficiency via keyboard nav

## Implementation Notes

- Use Next.js App Router for file-based routing
- Implement breadcrumb navigation for deep linking
- Ensure all routes are protected by auth middleware
- Use Supabase Realtime for live status updates
- Implement role-based access (admin/operator/viewer)
