# Tasks — Odoo on Azure Operating Model

## 1. Establish target and ownership
- [ ] Create Azure Boards Epic for the org-wide target
- [ ] Create child Features for each workstream
- [ ] Confirm source-of-truth repo for each workstream
- [ ] Confirm Area Path ownership per Feature

## 2. Author foundation artifacts
- [ ] WRITE: docs/odoo-on-azure/README.md
- [ ] WRITE: docs/odoo-on-azure/overview/index.md
- [ ] WRITE: docs/odoo-on-azure/reference/benchmark-map.md
- [ ] WRITE: docs/odoo-on-azure/reference/sap-to-odoo-doc-parity.md

## 3. Author workload-center and monitoring docs
- [ ] WRITE: platform/docs/workload-center/index.md
- [ ] WRITE: platform/docs/workload-center/odoo-system-instance.md
- [ ] WRITE: platform/docs/workload-center/drift-and-exceptions.md
- [ ] WRITE: platform/docs/monitoring/azure-monitor-for-odoo.md
- [ ] WRITE: platform/docs/monitoring/alerts-and-workbooks.md

## 4. Author automation and runtime docs
- [ ] WRITE: infra/docs/deployment-automation/index.md
- [ ] WRITE: infra/docs/deployment-automation/azd-and-iac-pattern.md
- [ ] WRITE: odoo/docs/runtime/index.md
- [ ] WRITE: odoo/docs/runtime/container-apps-reference-architecture.md
- [ ] WRITE: infra/docs/runtime/postgres-patterns.md

## 5. Validate platform claims
- [ ] EVIDENCE: validate live inventory assumptions
- [ ] EVIDENCE: validate IaC / SSOT alignment
- [ ] EVIDENCE: validate monitoring/workbook ownership
- [ ] EVIDENCE: validate repo authority map

## 6. Finish execution traceability
- [ ] EVIDENCE: confirm Boards Epic/Feature hierarchy is complete
- [ ] EVIDENCE: confirm PR linkage and build evidence on work items
- [ ] INDEX: add cross-repo navigation where needed

## 7. UAT scenario pack

- [ ] create and baseline `spec/odoo-on-azure-operating-model/uat-scenarios.md`
- [ ] assign owner for every required scenario in the scenario pack
- [ ] maintain scenario execution register during UAT
- [ ] collect process-tower sign-off using the scenario pack templates

## 8. Browser tooling and regression coverage

- [ ] add TransactionCase + Form regression for Project settings save
- [ ] add Playwright smoke for Project settings open/save
- [ ] add Playwright smoke for action/menu client crashes
- [ ] capture traces/screenshots for browser regressions
- [ ] use Chrome DevTools MCP for structured investigation of unresolved browser failures

## 9. Improve the process
- [ ] RETRO: capture issues from the sprint
- [ ] RETRO: create follow-up improvement items
