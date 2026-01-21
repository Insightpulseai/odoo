# Tasks: Supabase Platform Kit Observability

## Phase 1: Schema Foundation

- [x] Create spec bundle
- [x] Create `observability` schema migration
- [x] Add RLS policies
- [x] Create RPC functions

## Phase 2: API Layer

- [x] Create jobs API routes
- [x] Create agents API routes
- [x] Create health API route
- [x] Create topology API route
- [x] Create AI SQL API route

## Phase 3: Platform Kit Integration

- [x] Create ObservabilityManager component
- [x] Create JobsTab component
- [x] Create AgentsTab component
- [x] Create HealthTab component
- [x] Create TopologyTab component

## Phase 4: Topology Visualization

- [x] Create TopologyGraph component (SVG-based, no external deps)
- [x] Add node/edge types
- [x] Add filtering controls
- [ ] Add react-flow for advanced graph (optional, future)

## Phase 5: AI SQL Integration

- [x] Create schema introspection util
- [x] Wire up AI SQL route
- [ ] Add OpenAI dependency to package.json (required for production)
- [ ] Add query result display component

## Verification

- [ ] Run schema migration
- [ ] Test RLS policies
- [ ] Test all API endpoints
- [ ] Test component rendering
- [ ] Test topology graph
- [ ] Test AI SQL generation
