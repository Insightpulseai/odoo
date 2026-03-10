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

## Phase 6: Config Registry (Git SSOT + Supabase Control Plane)

- [x] Create ops.config_artifacts table
- [x] Create ops.config_versions table (immutable snapshots)
- [x] Create ops.config_consumers table (health tracking)
- [x] Create ops.config_checks table (detailed probes)
- [x] Create ops.config_rollouts table (deployment tracking)
- [x] Create ops.config_drift_events table
- [x] Add Config Registry RLS policies
- [x] Create publish_config_version RPC
- [x] Create consumer_heartbeat RPC
- [x] Create record_config_check RPC
- [x] Create detect_config_drift RPC
- [x] Create rollback_config RPC
- [x] Create config-publish Edge Function
- [x] Create consumer-heartbeat Edge Function
- [x] Create design tokens SSOT (config/tokens/tokens.json)
- [x] Create consumers registry (config/consumers/consumers.json)
- [x] Create config-publish CI workflow
- [x] Create backlog_scan.py script
- [x] Create backlog-coverage CI workflow

## Phase 7: Config Console UI (Future)

- [ ] Create ConfigTab component in Control Room
- [ ] Create TokensView component
- [ ] Create ConsumersView component with health status
- [ ] Create DriftView component
- [ ] Create RolloutsView component
- [ ] Wire up Realtime subscriptions for config updates
- [ ] Add config publish dialog
- [ ] Add rollback confirmation dialog

## Verification

- [ ] Run schema migration (ops.config_* tables)
- [ ] Test RLS policies
- [ ] Test all API endpoints
- [ ] Test component rendering
- [ ] Test topology graph
- [ ] Test AI SQL generation
- [ ] Test config-publish Edge Function
- [ ] Test consumer-heartbeat Edge Function
- [ ] Test drift detection
- [ ] Verify backlog scan produces correct report
