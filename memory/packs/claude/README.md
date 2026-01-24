# Claude Pack

**Format**: Longer context, explicit tool contracts, structured plans
**Token budget**: ~12,000 tokens max
**Optimized for**: Multi-step workflows, complex reasoning, tool orchestration

## Pack Contents

- `00_constitution.md` (from common) - Core operating principles
- `10_repo_map.md` (from common) - Repository structure
- `20_workflows.md` (from common) - Common commands
- `30_current_focus.md` - Active priorities with detailed context
- `40_error_recovery.md` - Error handling playbooks
- `90_recent_changes.md` - Distilled recent activity with rationale

## Usage Pattern

1. Load full pack at conversation start (fits in context)
2. Use structured tool calls with explicit parameters
3. Plan multi-step workflows before execution
4. Verify each step before proceeding

## Key Differences from ChatGPT Pack

- Longer, more detailed explanations
- Explicit tool contracts and schemas
- Error recovery playbooks included
- Full reasoning chains expected

## Tool Contracts

### File Operations
- `Read`: Always read before edit
- `Edit`: Use exact string matching
- `Write`: Only for new files

### Git Operations
- Always verify branch before push
- Include evidence in commit messages
- Never force push without explicit request

### Database Operations
- Use RPC functions over raw SQL
- Always check RLS policies
- Log operations to ops schema
