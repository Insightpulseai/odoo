# Policy: NO_CLI / NO_DOCKER (Claude Code Web)

## Scope
This policy applies when the execution environment does not provide:
- Docker or container runtimes
- Local shell / CLI tools
- Package managers (apt, brew, choco)
- Systemd or service managers
- Privileged networking

## Hard Constraints
- ❌ DO NOT propose Docker commands, docker-compose, devcontainers, or container exec
- ❌ DO NOT propose OS-level installs (apt/brew/choco)
- ❌ DO NOT assume git CLI available unless confirmed by environment tooling
- ❌ DO NOT request user UI clicks
- ❌ DO NOT claim capabilities without code evidence (see capabilities/manifest.json)

## Allowed Actions
- ✅ Edit repository files only
- ✅ Provide code changes that run in CI or remote runners
- ✅ Provide GitHub Actions workflows for build/test
- ✅ Scripts labeled "CI-only" intended for CI runners, not local execution

## Output Requirements
Every execution block must be tagged as:
- `repo-edit` - File modification in repository
- `ci-runner` - GitHub Actions workflow or CI script
- `remote-api` - API call to external service (Supabase, GitHub API, etc.)

## Refusal Protocol
If a request requires Docker/CLI in this environment, respond:
"Cannot execute in this environment. Provide a CI workflow or remote runner path instead."

## Integration
This policy is enforced by:
- CI workflow: `.github/workflows/policy-no-cli.yml`
- Capability validator: `scripts/validate_capabilities.sh`
- Agents must check environment constraints before proposing actions
