# LLM Memory Packs

This directory contains LLM-optimized context packs for AI agents (Claude, ChatGPT).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Memory Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Layer A: LLM Packs (Prompt-Optimized)                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  memory/packs/common/    - Shared principles, repo map  │   │
│   │  memory/packs/chatgpt/   - Terse, command-focused       │   │
│   │  memory/packs/claude/    - Detailed, tool-aware         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              ▲                                   │
│                              │ Distillation Pipeline             │
│                              │ (summaries only)                  │
│                              │                                   │
│   Layer B: Operational Memory (Supabase)                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  ops.jobs, ops.job_runs, ops.job_events                 │   │
│   │  marketplace.webhook_events, marketplace.artifact_syncs │   │
│   │  mcp_jobs.jobs, mcp_jobs.metrics                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
memory/
├── packs/
│   ├── common/              # Shared across all LLMs
│   │   ├── 00_constitution.md    # Core principles
│   │   ├── 10_repo_map.md        # Repository structure
│   │   ├── 20_workflows.md       # Common commands
│   │   └── 90_recent_changes.md  # Distilled updates
│   │
│   ├── chatgpt/             # ChatGPT-optimized (~6k tokens)
│   │   ├── README.md
│   │   ├── 30_current_focus.md
│   │   └── 90_recent_changes.md
│   │
│   └── claude/              # Claude-optimized (~12k tokens)
│       ├── README.md
│       ├── 30_current_focus.md
│       ├── 40_error_recovery.md
│       └── 90_recent_changes.md
│
├── snapshots/               # Point-in-time captures
├── sources/                 # Raw input files for distillation
├── memory_policy.yaml       # Separation contract
└── README.md               # This file
```

## Usage

### Loading a Pack

```python
# Python example
def load_pack(llm_type: str = "claude") -> str:
    """Load LLM pack as context string."""
    import glob

    pack_files = []
    # Load common files
    pack_files.extend(sorted(glob.glob("memory/packs/common/*.md")))
    # Load LLM-specific files
    pack_files.extend(sorted(glob.glob(f"memory/packs/{llm_type}/*.md")))

    context = []
    for f in pack_files:
        with open(f) as fp:
            context.append(fp.read())

    return "\n\n---\n\n".join(context)
```

### Distillation

The distillation pipeline runs daily (or on push to main) to update `90_recent_changes.md` files:

```bash
# Manual run
./scripts/memory/distill_packs.sh

# Verify output
find memory/packs -name "90_*.md" -exec wc -l {} \;
```

## Key Principles

1. **Packs are prompt-optimized** - Short, curated, actionable
2. **Supabase is operational** - Logs, runs, artifacts, citations
3. **No raw logs in packs** - Only distilled summaries cross the boundary
4. **Packs are code-reviewed** - Treat like source code (PRs, diffs, CI)
5. **No secrets** - Packs are public within the org

## Token Budgets

| Pack | Target | Max |
|------|--------|-----|
| Common | 2,500 | 3,000 |
| ChatGPT | 5,000 | 6,000 |
| Claude | 10,000 | 12,000 |

## Related Files

- `memory_policy.yaml` - Full separation contract
- `scripts/memory/distill_packs.sh` - Distillation script
- `.github/workflows/memory-distill.yml` - CI automation
