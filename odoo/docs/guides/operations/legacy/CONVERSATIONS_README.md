# Conversations Index System

## Naming
NNN — YYYY-MM-DD — short-title.md

## Required frontmatter
```yaml
---
scope: ""
inputs: ""
outputs: ""
decisions: ""
next_actions: ""
tags: []
---
```

## Indexing
- docs/ops/conversations/INDEX.md (human)
- docs/ops/conversations/index.json (machine)

## Usage
```bash
# Create new conversation entry
./scripts/new_conversation_entry.sh "title" "YYYY-MM-DD"

# Example
./scripts/new_conversation_entry.sh "DOLE submission checklist" "2025-12-22"
```

## Structure
Each conversation entry contains:
- Summary
- Evidence / Artifacts
- Notes
- Frontmatter metadata (scope, inputs, outputs, decisions, next_actions, tags)
