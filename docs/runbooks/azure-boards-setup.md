# Runbook — Azure Boards Taxonomy Setup (`ipai-platform`)

Canonical procedure for creating the Epic/Area/Iteration taxonomy in the
Azure DevOps project `ipai-platform`, per
[ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml).

This runbook is the ONLY approved procedure. Creating epics or area paths
outside of this runbook is a doctrine violation.

---

## Preconditions

1. Operator holds Project Administrator on `ipai-platform`.
2. `ipai-platform` ADO project uses **Basic** process (Epic → Issue → Task).
3. `az` CLI installed with `azure-devops` extension:
   ```bash
   az extension add --name azure-devops
   az devops configure --defaults organization=https://dev.azure.com/insightpulseai project=ipai-platform
   ```

---

## Inputs

- Taxonomy SSOT: [ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml)
- AAC map: [ssot/architecture/azure-architecture-center-map.yaml](../../ssot/architecture/azure-architecture-center-map.yaml)

---

## Step 1 — Create Area Paths (one-time)

```bash
for area in \
  odoo \
  agent-platform \
  agents \
  web \
  data-intelligence \
  platform \
  infra \
  docs \
  automations \
  design \
  templates \
  identity-security; do
  az boards area project create --name "$area" --path "\\ipai-platform\\Area"
done
```

Evidence: capture area tree to
`docs/evidence/<YYYYMMDD-HHMM>/azure-boards-setup/areas.json`.

---

## Step 2 — Create Iteration Paths (one-time for active quarter)

```bash
az boards iteration project create --name "FY26" --path "\\ipai-platform\\Iteration"
az boards iteration project create --name "Q2"   --path "\\ipai-platform\\Iteration\\FY26"
for n in 01 02 03 04; do
  az boards iteration project create --name "Sprint $n" --path "\\ipai-platform\\Iteration\\FY26\\Q2"
done
```

Rule: iteration paths reflect time cadence only. Do not encode repo names
here — that's the Area Path's job.

---

## Step 3 — Create the first-wave Epics

Per the SSOT `first_wave.priority_order`: EPIC-001, 002, 004, 007, 008, 009.

```bash
create_epic() {
  local title="$1"
  local area="$2"
  az boards work-item create \
    --type Epic \
    --title "$title" \
    --area "ipai-platform\\$area" \
    --iteration "ipai-platform\\FY26\\Q2" \
    --description "Capability domain per ssot/governance/azure-boards-taxonomy.yaml" \
    --fields "System.Tags=capability-domain"
}

create_epic "Business Systems / Odoo ERP"          "odoo"
create_epic "AI Runtime / Agent Platform"          "agent-platform"
create_epic "Web Experience Surfaces"              "web"
create_epic "Infrastructure / Azure / Edge / Hosting" "infra"
create_epic "Identity / Security / Governance"     "identity-security"
create_epic "Docs / Architecture / Runbooks / Evidence" "docs"
```

Capture returned IDs to
`docs/evidence/<YYYYMMDD-HHMM>/azure-boards-setup/epic-ids.json`.

---

## Step 4 — Seed Issues per Epic

For each epic, create the seed issues listed in the taxonomy SSOT under
`epics.EPIC-xxx.seed_issues`. Link each issue to its parent epic.

```bash
create_issue() {
  local title="$1"
  local area="$2"
  local parent_id="$3"
  az boards work-item create \
    --type Issue \
    --title "$title" \
    --area "ipai-platform\\$area" \
    --iteration "ipai-platform\\FY26\\Q2" \
    --fields "System.Tags=deliverable-slice"
  # Then link to parent via az boards work-item relation add
}

# Example — EPIC-002 seed issues:
create_issue "AI Runtime: Bind Foundry provider to ipai-copilot-resource" "agent-platform" "$EPIC_002_ID"
create_issue "AI Runtime: Add Odoo tool adapter baseline"                 "agent-platform" "$EPIC_002_ID"
# ... (see SSOT for full list)

# Link issue to parent epic:
az boards work-item relation add \
  --id "$ISSUE_ID" \
  --relation-type parent \
  --target-id "$EPIC_002_ID"
```

---

## Step 5 — Apply tags

Tag cross-cutting concerns per the SSOT `tags.canonical_set`. Do not invent
new tags without adding them to the SSOT.

```bash
az boards work-item update --id "$WI_ID" --fields "System.Tags=foundry; agent-framework; production"
```

---

## Step 6 — Verify

```bash
az boards query --wiql "SELECT [System.Id], [System.Title], [System.WorkItemType], [System.AreaPath], [System.State] FROM WorkItems WHERE [System.TeamProject] = 'ipai-platform' AND [System.WorkItemType] IN ('Epic', 'Issue') ORDER BY [System.WorkItemType] DESC"
```

Expected:
- 6 Epics from the first wave
- ~30-40 seed Issues across those 6 epics
- All Area Paths populated
- All items under iteration `FY26\Q2\Sprint 01`

Capture to `docs/evidence/<YYYYMMDD-HHMM>/azure-boards-setup/verification.json`.

---

## Naming conventions (enforce at creation time)

Per SSOT `naming`:

| Work item type | Pattern | Example |
|---|---|---|
| Epic | `<Capability domain>` | `AI Runtime / Agent Platform` |
| Issue | `<Domain>: <Deliverable slice>` | `AI Runtime: Bind Foundry provider to ipai-copilot-resource` |
| Task | `<Verb> <concrete implementation step>` | `Add Foundry provider settings loader` |

---

## Workflow states (lean)

Per SSOT `workflow.states`:

```
New → Active → Resolved → Closed
             ↓
           Blocked
```

Do not introduce custom states without a reporting requirement.

---

## Prohibited actions

- Creating Epics or Area Paths outside this runbook.
- Encoding repo names in Iteration Paths.
- Creating parallel taxonomies for sub-teams within the same project.
- Renaming Epics without updating the SSOT first.
- Using tags outside the SSOT `tags.canonical_set` without approval.

---

## Rollback

If step 3 (epic creation) needs to be undone:

```bash
az boards work-item delete --id "$WI_ID" --destroy false
```

`--destroy false` soft-deletes; Entra/AAD trail preserved. `--destroy true`
permanently removes (requires elevated permission).

---

## Links

- Taxonomy SSOT: [../../ssot/governance/azure-boards-taxonomy.yaml](../../ssot/governance/azure-boards-taxonomy.yaml)
- AAC architecture map: [../../ssot/architecture/azure-architecture-center-map.yaml](../../ssot/architecture/azure-architecture-center-map.yaml)
- Existing generic contract: [../../ssot/planning/azure-boards.contract.yaml](../../ssot/planning/azure-boards.contract.yaml)
- Agent Factory boards mapping: [../../ssot/agent-platform/boards_mapping.yaml](../../ssot/agent-platform/boards_mapping.yaml)
- ADO/GitHub authority map: [../../ssot/governance/ado_github_authority_map.yaml](../../ssot/governance/ado_github_authority_map.yaml)
