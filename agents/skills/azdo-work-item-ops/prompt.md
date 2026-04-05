# Skill: azdo.workitem.ops

## Reasoning Strategy

You perform CRUD operations on individual Azure DevOps work items. This skill handles field-level detail that the board-ops skill does not cover.

### Show (Read)

```bash
# Show work item details
az boards work-item show --id {id} --org {org} --project {project} --output table

# Show with specific fields
az boards work-item show --id {id} --fields "System.Title,System.State,System.Parent,System.Tags" --org {org} --project {project}
```

### Create

```bash
# Create with description and tags
az boards work-item create \
  --type {type} \
  --title "{title}" \
  --description "{description}" \
  --org {org} \
  --project {project} \
  --output table

# Create with area and iteration path
az boards work-item create \
  --type Task \
  --title "{title}" \
  --area "{area_path}" \
  --iteration "{iteration_path}" \
  --org {org} \
  --project {project}
```

### Update

```bash
# Update state
az boards work-item update --id {id} --state "Done" --org {org}

# Update multiple fields
az boards work-item update --id {id} --fields "System.Title=New Title" "System.Tags=p0;security" --org {org}

# Set parent
az boards work-item update --id {id} --fields "System.Parent={parent_id}" --org {org}
```

### Comments

```bash
# Add a discussion comment (uses REST API via az devops invoke)
az boards work-item update --id {id} --discussion "Comment text here" --org {org}
```

### Relations

```bash
# Add a related link
az boards work-item relation add --id {id} --relation-type "Related" --target-id {target_id} --org {org}

# Relation types: Related, Parent, Child, Predecessor, Successor, Duplicate
```

### WIQL Query Patterns

```sql
-- All open work items by type
SELECT [System.Id], [System.Title], [System.State]
FROM workitems
WHERE [System.TeamProject] = 'ipai-platform'
  AND [System.WorkItemType] = 'Task'
  AND [System.State] <> 'Done'
ORDER BY [System.Id]

-- Children of a specific parent
SELECT [System.Id], [System.Title]
FROM workitems
WHERE [System.TeamProject] = 'ipai-platform'
  AND [System.Parent] = {parent_id}

-- Tagged items
SELECT [System.Id], [System.Title]
FROM workitems
WHERE [System.TeamProject] = 'ipai-platform'
  AND [System.Tags] CONTAINS 'p0'
```

### Field Reference

| Field | System Name | Notes |
|-------|-------------|-------|
| Title | `System.Title` | Required |
| State | `System.State` | To Do / Doing / Done |
| Type | `System.WorkItemType` | Epic / Issue / Task |
| Parent | `System.Parent` | Integer ID |
| Tags | `System.Tags` | Semicolon-separated |
| Area Path | `System.AreaPath` | `project\area` format |
| Iteration Path | `System.IterationPath` | `project\sprint` format |
| Assigned To | `System.AssignedTo` | Email or display name |
| Description | `System.Description` | HTML content |
| Priority | `Microsoft.VSTS.Common.Priority` | 1-4 (1=critical) |

## Edge Cases

- `--fields` uses `Key=Value` pairs separated by spaces, not JSON
- Tags are semicolon-separated in WIQL `CONTAINS` but space-separated in `--fields`
- `--output table` is best for human-readable output; `--output json` for parsing
- `System.Parent` in WIQL is the direct parent only (not transitive)
- WIQL does not support `DISTINCT`, `GROUP BY`, or `JOIN`
- `az boards work-item show` requires `--project` in some CLI versions but not others

## Notes

- IPAI Basic process states: To Do, Doing, Done (no New, Active, Closed, Resolved)
- Priority field is available but not enforced in Basic process
- Use tags for P0/P1/P2 classification when priority field is insufficient
