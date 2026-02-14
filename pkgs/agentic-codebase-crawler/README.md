# Agentic Codebase Crawler

CLI tool that scans repositories for missing Supabase Enterprise parity controls, generates patch sets, runs verification, and emits artifacts to `ops.*` schema.

## Features

1. **Repo Scan**: Checks codebase against configurable parity controls
2. **Gap Detection**: Identifies missing security, governance, and ops controls
3. **Patch Generation**: Creates PR-ready patches for missing controls
4. **Verification**: Runs verification commands to validate changes
5. **Artifact Emission**: Stores results in `ops.*` schema for auditability
6. **Firecrawl Integration**: Optional web scraping for documentation ingestion

## Installation

```bash
cd packages/agentic-codebase-crawler
pnpm install
pnpm run build
```

## Usage

### Basic scan (dry-run)

```bash
node dist/index.js \
  --repo-root . \
  --config templates/parity-controls.yml \
  --out ops/agentic-codebase-crawler/out
```

### With patch application

```bash
node dist/index.js \
  --repo-root . \
  --config templates/parity-controls.yml \
  --out ops/agentic-codebase-crawler/out \
  --apply
```

### With verification

```bash
node dist/index.js \
  --repo-root . \
  --out ops/agentic-codebase-crawler/out \
  --verify-cmd "pnpm -w -r typecheck && pnpm -w -r test"
```

### With Firecrawl integration

```bash
export FIRECRAWL_API_KEY="***"
export FIRECRAWL_BASE_URL="https://api.firecrawl.dev"
export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="***"

node dist/index.js \
  --out ops/agentic-codebase-crawler/out \
  --crawl-url https://supabase.com/docs/reference/api/introduction \
  --crawl-url https://supabase.com/docs/guides/platform/access-control
```

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--repo-root <path>` | `.` | Repository root path |
| `--config <path>` | `packages/.../parity-controls.yml` | Parity controls config |
| `--out <path>` | `ops/.../out` | Output directory |
| `--apply` | `false` | Apply generated patches |
| `--verify-cmd <cmd>` | `echo 'No verify...'` | Verification command |
| `--crawl-url <url...>` | - | URLs to crawl via Firecrawl |
| `--firecrawl-base <url>` | `https://api.firecrawl.dev` | Firecrawl API base |
| `--firecrawl-key <key>` | `$FIRECRAWL_API_KEY` | Firecrawl API key |
| `--supabase-url <url>` | `$SUPABASE_URL` | Supabase project URL |
| `--supabase-service-role <key>` | `$SUPABASE_SERVICE_ROLE_KEY` | Service role key |
| `--actor <actor>` | `local` | Run actor identifier |
| `--repo <repo>` | `$GITHUB_REPOSITORY` | Repo identifier |
| `--ref <ref>` | `$GITHUB_SHA` | Git ref/SHA |
| `--skip-verify` | `false` | Skip verification step |
| `--skip-ops-emit` | `false` | Skip emitting to ops schema |

## Parity Controls

Controls are defined in `templates/parity-controls.yml`:

```yaml
controls:
  - id: rls-required
    title: "RLS policies exist for exposed schemas"
    severity: high
    checks:
      - type: glob_exists
        pattern: "supabase/migrations/*.sql"
        must_contain_regex: "(?is)enable row level security"
```

### Check Types

| Type | Description |
|------|-------------|
| `glob_exists` | Files matching glob exist (optionally with content regex) |
| `any_file_exists` | At least one of the listed files exists |
| `deny_glob` | No files should match the glob |
| `repo_regex_deny` | No files should contain the regex |

### Severity Levels

- `high`: Critical security/governance controls
- `medium`: Important operational controls
- `low`: Best practices

## Output Files

| File | Description |
|------|-------------|
| `findings.json` | All control check results |
| `patch-plan.json` | List of files to create/modify |
| `apply-patch.sh` | Executable patch script |
| `verify.json` | Verification command result |
| `crawls.json` | Firecrawl results (if URLs provided) |
| `ops_emit_error.txt` | Ops emission error (if failed) |

## Integration with ops.* Schema

The crawler emits results to Supabase `ops.*` schema:

- `ops.runs` - Run metadata (actor, repo, ref, status)
- `ops.run_events` - Event log during execution
- `ops.artifacts` - Output files (reports, patches, crawls)

Required functions:
- `ops.start_run(p_actor, p_repo, p_ref, p_pack_id, p_input)`
- `ops.log_event(p_run_id, p_level, p_message, p_data)`
- `ops.complete_run(p_run_id, p_output)`
- `ops.add_artifact(p_run_id, p_kind, p_uri, p_meta)`

## GitHub Actions

The crawler runs automatically on PRs touching:
- `supabase/**`
- `packages/**`
- `config/**`
- `AGENTS.md`, `CLAUDE.md`
- `.github/workflows/**`

Manual dispatch available with options to apply patches and crawl URLs.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All controls passed, verification succeeded |
| 1 | One or more controls failed |
| 2 | Verification failed |
