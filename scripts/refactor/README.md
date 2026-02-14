# Refactor Subagents

4-track parallel codebase analysis system for systematic refactoring.

## Overview

Runs 4 specialized "subagents" in parallel to analyze:
1. **Duplicate code** (jscpd)
2. **Dead code / unused exports** (depcheck, ts-prune)
3. **Error handling consistency** (ESLint, ripgrep)
4. **Security vulnerabilities** (npm audit, semgrep)

Produces a prioritized `ACTION_PLAN.md` with severity-sorted findings.

## Usage

### Local Run

```bash
./scripts/refactor/run_refactor_subagents.sh
```

### View Results

```bash
# Action plan (prioritized findings)
cat out/refactor/ACTION_PLAN.md

# Raw artifacts
ls -la out/refactor/
```

### CI Integration

Workflow: `.github/workflows/refactor-subagents.yml`
- Runs on PRs and manual dispatch
- Uploads results as GitHub artifact

## Output Structure

```
out/refactor/
├── ACTION_PLAN.md           # Prioritized findings + fixes
├── dupes/                   # jscpd duplicate code reports
│   ├── jscpd-report.md
│   └── jscpd-report.json
├── depcheck.json            # Unused dependencies
├── ts-prune.txt             # Unused TypeScript exports
├── eslint.json              # Linting issues
├── npm-audit.json           # Security vulnerabilities
├── semgrep.json             # SAST findings
└── error-handling.grep.txt  # Error handling patterns
```

## Configuration

### Tuning Thresholds

Edit `run_refactor_subagents.sh`:
- `jscpd`: `--min-lines`, `--min-tokens` (duplicate detection sensitivity)
- `semgrep`: Add baseline file to reduce noise
- `eslint`: Use project's existing config or customize minimal config

### Ignore Patterns

Default ignores: `node_modules`, `dist`, `.next`, `build`, `out`, `coverage`

Adjust glob patterns in script if needed.

## Next Steps

1. **Triage**: Review `ACTION_PLAN.md` and prioritize by severity
2. **Baseline**: For ongoing use, create semgrep/eslint baselines
3. **Automate**: Add pre-commit hooks or CI gates for critical findings
4. **Refactor**: Apply fixes systematically (consider automated codemods)

## Troubleshooting

### Missing Tools

Script auto-installs dev deps. If tools fail:
```bash
npm install -D jscpd depcheck ts-prune eslint semgrep
```

### TypeScript Projects

Requires `tsconfig.json` at repo root for `ts-prune`. Adjust path if needed:
```bash
npx ts-prune -p path/to/tsconfig.json
```

### Package Manager

Script uses `npm`. For `pnpm`/`yarn`, update install commands in script.
