# Constitution — Odoo Seed Import

## Governance principles

1. CE-first: use standard `project.project` and `project.task` models
2. Custom fields only where seed data requires (x_* prefix)
3. Import order matters: people → projects → milestones → tasks
4. Milestones are tasks with `x_is_milestone=true`, not a separate model
5. Seed data is from real TBWA\SMP finance operating workbook — not synthetic
6. Email addresses use `@demo.local` to prevent accidental production email
7. Board views are saved filters, not custom models
8. This is for Khalil's finance team — accuracy of roles and assignments matters

## Authority

- Finance Director: CKVC (Khalil Vera Cruz) — approves final board layout
- Daily monitor: JPAL (JP Loterte) — validates data matches operating reality
- Technical: Claude Code executes; Azure Boards tracks

## Stage gate

Import is complete when:
- [ ] 10 people exist as Odoo users with correct roles
- [ ] 8 projects visible in Project app
- [ ] 40 milestones visible as flagged tasks
- [ ] 45 tasks with correct assignments + stages
- [ ] 5 kanban board views created
- [ ] Databricks gold views reflect the same data via Lakehouse Federation
