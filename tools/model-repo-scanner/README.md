# Model Repo Scanner

Discovers and ranks repositories in a GitHub organization to identify the best "model repository" for integration and automation patterns.

## Overview

The Model Repo Scanner analyzes repositories based on four categories:

| Category | Max Points | What It Measures |
|----------|------------|------------------|
| CI & Governance | 30 | CI scripts, workflows, CODEOWNERS, Spec Kit |
| Integration | 35 | Supabase, MCP, n8n, Vercel, Ops platform |
| Automation | 25 | Drift gates, branch hygiene, security scanning |
| Recency | 10 | Documentation, recent activity |

## Quick Start

### Local Usage

```bash
# Set GitHub org (or use -o flag)
export GITHUB_ORG="your-org"

# Run scanner
./scripts/find_model_repo.sh

# View results
cat artifacts/model-repo-report.md
```

### CI Usage

Trigger manually:
```bash
gh workflow run model-repo-scan.yml -f organization=your-org
```

Or use the weekly scheduled run.

## Scripts

### `find_model_repo.sh`

Discovers and scores all repositories in an organization.

```bash
./scripts/find_model_repo.sh [options]

Options:
  -o, --org <org>       GitHub organization
  -c, --config <file>   Config file (default: config/scoring.yaml)
  -v, --verbose         Verbose output
  -h, --help            Show help
```

**Output:**
- `artifacts/model-repo-scores.json` - Machine-readable scores
- `artifacts/model-repo-report.md` - Human-readable report

### `adopt_model_repo.sh`

Generates a patch set to adopt baseline automation from a model repository.

```bash
./scripts/adopt_model_repo.sh <target-repo-path> [options]

Options:
  -m, --model <repo>    Model repo to copy from
  -b, --branch <name>   Branch name (default: adopt-model-automation)
  -n, --dry-run         Preview without making changes
  -h, --help            Show help
```

**Example:**
```bash
# Adopt automation from top-scored model repo
./scripts/adopt_model_repo.sh /path/to/my-repo

# Preview what would be copied
./scripts/adopt_model_repo.sh /path/to/my-repo --dry-run
```

## Configuration

Edit `config/scoring.yaml` to customize weights and patterns:

```yaml
weights:
  ci_governance: 30      # CI & governance maturity
  integration: 35        # Integration surfaces
  automation: 25         # Automation maturity
  recency: 10            # Recency & adoption readiness

ci_governance:
  ci_scripts:
    weight: 10
    patterns:
      - "scripts/ci/**/*.sh"
      # ...
```

## Output Format

### scores.json

```json
[
  {
    "repo": "odoo-ce",
    "total_score": 85,
    "scores": {
      "ci_governance": 28,
      "integration": 32,
      "automation": 18,
      "recency": 7
    },
    "evidence": {
      "ci_governance": "  - Found: scripts/ci\n  - Workflows: 47 files\n",
      "integration": "  - Supabase config: present\n  - MCP directory: present\n",
      "automation": "  - Generator scripts: 15\n  - Drift gates: found\n",
      "recency": "  - README: present\n  - Recent commits (30d): 42\n"
    }
  }
]
```

### report.md

Human-readable report with:
- Ranked table of all repositories
- Top recommendation with evidence
- Scoring breakdown

## CI Workflow

The included GitHub Actions workflow:

1. Runs on manual trigger or weekly schedule
2. Scans the specified organization
3. Generates scores and report
4. Uploads `model-repo-scanner.zip` as artifact

### Workflow Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `organization` | GitHub org to scan | `jgtolentino` |
| `verbose` | Enable verbose output | `false` |

## Requirements

- `gh` CLI (authenticated)
- `jq`
- `ripgrep` (optional, falls back to grep)

## Directory Structure

```
model-repo-scanner/
├── scripts/
│   ├── find_model_repo.sh    # Main scanner
│   └── adopt_model_repo.sh   # Adoption helper
├── config/
│   └── scoring.yaml          # Weights and patterns
├── artifacts/                 # Generated output
│   ├── model-repo-scores.json
│   └── model-repo-report.md
├── .github/
│   └── workflows/
│       └── model-repo-scan.yml
└── README.md
```

## Composite Model

Often the best approach is a **composite model**:

- **Governance repo** (e.g., `.github`) for org-wide policies
- **Platform repo** (e.g., `odoo-ce`, `pulser-agent-framework`) for integration patterns

The scanner identifies both and recommends based on total score.

## Extending

### Adding New Scoring Signals

1. Edit `config/scoring.yaml` to add patterns
2. Update the corresponding `score_*` function in `find_model_repo.sh`
3. Test with `./scripts/find_model_repo.sh -v`

### Custom Adoption Templates

Edit `adopt_model_repo.sh` to customize:
- `ADOPT_FILES` array for files to copy
- `generate_*` functions for template files

## License

MIT
