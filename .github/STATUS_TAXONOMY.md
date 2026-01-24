# GitHub Member Status Taxonomy

Standardized status signals for org-wide coordination. Use these to communicate your current focus and route work appropriately.

## Status Definitions

| Status | Emoji | Meaning | Others Should |
|--------|-------|---------|---------------|
| **Launching** | :rocket: | Shipping to prod/public | Prioritize reviews, unblock CI, avoid scope creep |
| **Building** | :hammer_and_wrench: | Heads-down implementation | Batch feedback, avoid interrupts |
| **Reviewing** | :eyes: | Clearing PR queue | Send PR links, expect quick turnaround |
| **Oncall** | :rotating_light: | Incident/ops focus | Only page for urgent issues |
| **Planning** | :memo: | Specs/architecture | Comment on PRDs, align scope |

## Usage

### CLI (Recommended)

```bash
# Set launching status
./scripts/status/set_status.sh launching

# With PR reference
./scripts/status/set_status.sh launching -r "odoo-ce#271"

# With expiry (auto-clear after 4 hours)
./scripts/status/set_status.sh building -e 4h

# Custom message
./scripts/status/set_status.sh launching -m "Shipping v2.0 release"

# Clear status
./scripts/status/set_status.sh clear
```

### Direct GraphQL

```bash
gh api graphql -f query='
mutation($input: ChangeUserStatusInput!) {
  changeUserStatus(input: $input) {
    status { message emoji expiresAt }
  }
}' -f input='{
  "message": "Launching — merge → deploy → validate",
  "emoji": ":rocket:"
}'
```

## Message Templates

### Launching

Use when shipping something to production/public:

```
Launching — merge → deploy → validate
Launching — ship + validate (no scope creep)
Launching — reviews welcome; keep changes minimal
Launching — please async; only ping for blockers
```

### Building

Use for focused implementation work:

```
Building — heads-down; batch feedback
Building — deep work on feature X
Building — in flow; will batch responses
```

### Reviewing

Use when clearing the review queue:

```
Reviewing — clearing PR queue
Reviewing — send PR links for fast turnaround
Reviewing — prioritizing repo X PRs
```

### Oncall

Use during incident response or ops focus:

```
Oncall — only ping for urgent issues
Oncall — incident response active
Oncall — ops focus until EOD
```

### Planning

Use during architecture/spec work:

```
Planning — specs/architecture alignment
Planning — PRD review for feature X
Planning — design session active
```

## Best Practices

1. **Keep it short** — Status should be skimmable
2. **Add PR/Issue refs** — e.g., `odoo-ce#271` for context
3. **Set expiry** — Use `-e` flag for time-bounded focus
4. **Clear when done** — Run `./scripts/status/set_status.sh clear`

## Integration with PRs

When opening a PR during a "Launching" window, include status context:

```markdown
## Status Context

**Current:** Launching — merge → deploy → validate

Please prioritize review. CI is green, changes are scoped to the minimum.
```

## Verification

```bash
# Check your current status
gh api graphql -f query='query { viewer { status { message emoji expiresAt } } }'

# Check gh auth
gh auth status
```
