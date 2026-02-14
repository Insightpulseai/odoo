# IPAI VS Code Control Plane — Tasks

## Foundation
- [ ] Create VS Code extension scaffold
- [ ] Register commands
- [ ] Implement Spec Kit discovery
- [ ] Block execution on missing specs

## Environment Projection
- [ ] Detect Odoo instances
- [ ] Compute schema hash
- [ ] Read installed modules
- [ ] Render tree views

## Validation
- [ ] Manifest dependency validator
- [ ] EE-only module detector
- [ ] XML ID collision scanner
- [ ] Security rule coverage check
- [ ] Schema drift detector

## Execution
- [ ] Diff generator (SQL/ORM/XML)
- [ ] Dry-run executor
- [ ] Confirmation gate
- [ ] Apply executor
- [ ] Rollback mechanism

## Evidence
- [ ] Evidence directory generator
- [ ] Validation report writer
- [ ] Diff archiver
- [ ] Log capture

## AI
- [ ] AI command registry
- [ ] Patch-only generation
- [ ] Validation enforcement
- [ ] Confirmation workflow

## CI
- [ ] Spec completeness gate
- [ ] Extension build validation
- [ ] Drift detection enforcement

## Quality Gates (CI Required)
- Gate Workflow: `.github/workflows/ipai-vscode-control-plane-gate.yml`
- Must pass on PR:
  - Extension unit tests (vitest)
  - Extension integration tests (@vscode/test-electron)
  - Control-plane tests (pytest)
- Evidence Artifacts (uploaded to workflow):
  - `extension-unit-coverage/` - Coverage reports (HTML)
  - `extension-unit-results/` - JUnit XML test results
  - `extension-integration-results/` - VS Code test artifacts
  - `extension-integration-logs/` - Integration test logs
  - `control-plane-coverage/` - Python coverage reports (HTML)
  - `control-plane-test-results/` - pytest JUnit XML
