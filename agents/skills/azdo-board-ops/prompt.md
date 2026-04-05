# Skill: azdo.board.ops

## Reasoning Strategy

You manage Azure DevOps Boards work items for the IPAI platform project.

### Process Template

IPAI uses the **Basic** process template. Available work item types:
- **Epic** — top-level strategic bundles (max 7 canonical)
- **Issue** — workstreams, execution bundles, evidence-producing deliverables
- **Task** — atomic substeps

**Feature, User Story, Product Backlog Item do NOT exist** in this process. Never attempt to create them.

### CLI Surface

All operations use `az boards` CLI commands:

```bash
# Query
az boards query --wiql "SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.TeamProject] = '{project}' AND [System.WorkItemType] = '{type}'" --org {org} --project {project} --output table

# Create
az boards work-item create --type {type} --title "{title}" --description "{desc}" --org {org} --project {project}

# Update (state, fields, parent)
az boards work-item update --id {id} --state {state} --org {org} --project {project}
az boards work-item update --id {id} --fields "System.Parent={parent_id}" --org {org} --project {project}

# Delete (requires --yes, irreversible)
az boards work-item delete --id {id} --org {org} --project {project} --yes
```

### IPAI Defaults

| Setting | Value |
|---------|-------|
| Organization | `https://dev.azure.com/insightpulseai` |
| Project | `ipai-platform` |
| States | `To Do`, `Doing`, `Done` |

### Hierarchy Rules

1. **Epics** map 1:1 to canonical spec bundles
2. **Issues** are the primary execution layer — each produces artifacts or evidence
3. **Tasks** are substeps only — never promote a Task to carry its own evidence outcome
4. A work item producing a real artifact or evidence pack should be an **Issue**, not a Task

### Safety Rules

- Never delete without `--yes` flag
- Never use `-i` (interactive) flags
- `--project` is required for delete operations but NOT for update
- Verify parent links after reparenting by querying children of the new parent
- When closing legacy work items, reparent children first

## Edge Cases

- `az boards work-item update` does NOT accept `--project` in all versions — omit if it errors
- `--fields "System.Parent=N"` sets the parent link; there is no dedicated `--parent` flag
- WIQL `SELECT DISTINCT` is not supported — use standard `SELECT`
- Empty query results return no output (not an error)
- Backgrounded `&` commands with `--output json` may produce parse errors — use `--output table` for parallel operations

## Notes

- The board was normalized on 2026-04-05: 7 canonical Epics (#238-244), 19 Issues, 171 Tasks
- Legacy OBJ-style Epics (#1-7) and execution Epics (#63-192) were closed to Done after task reparenting
- Cross-cutting objectives #1 (Identity) and #7 (Revenue) remain open
