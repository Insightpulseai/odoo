# Tasks — Target Platform Architecture

## Architecture docs
- [x] Add `docs/architecture/target-platform-architecture.md`
- [x] Add `docs/architecture/plane-boundaries.md`
- [x] Add `docs/architecture/domain-workbench-map.md`
- [x] Add `docs/architecture/diagram-conventions.md`

## Machine-readable SSOT
- [x] Add `ssot/architecture/planes.yaml`
- [x] Add `ssot/architecture/system-context.yaml`
- [x] Add `ssot/architecture/tenant-model.yaml`
- [x] Add `ssot/architecture/data-flows.yaml`
- [x] Add `ssot/architecture/runtime-authority-map.yaml`

## Spec kit
- [x] Add `spec/target-platform-architecture/constitution.md`
- [x] Add `spec/target-platform-architecture/prd.md`
- [x] Add `spec/target-platform-architecture/plan.md`
- [x] Add `spec/target-platform-architecture/tasks.md`

## Validation
- [ ] Validate all YAML files
- [ ] Cross-link from platform architecture index / contracts index if present
- [ ] Ensure terminology matches current canonical memory:
  - Azure Boards planned truth
  - GitHub code truth
  - Azure Pipelines release truth
  - Resource Graph live Azure inventory truth
  - Foundry agent/runtime/eval truth
  - Repo SSOT intended-state truth

## Follow-on
- [ ] Create draw.io source diagrams
- [ ] Export deterministic PNG/SVG artifacts
- [ ] Add CI drift check for exported diagrams if desired
