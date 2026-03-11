# Tasks: Intake Pipeline for Upstream Anthropic Skills

## Task 1: Create snapshot directory and sync script
- Create `third_party/anthropic_skills/` directory with `.gitkeep`.
- Write `scripts/agents/sync_upstream_skills.sh` to clone/pull upstream repo and copy contents.
- Generate `index.json` listing all available skills with name, path, and description.
- Status: TODO

## Task 2: Create GitHub Actions workflow for weekly sync
- Create `.github/workflows/skill-upstream-sync.yml` with weekly cron schedule.
- Workflow runs sync script and opens a PR if changes are detected.
- Include diff summary in PR description.
- Status: TODO

## Task 3: Build skill converter script
- Create `scripts/agents/convert_skill.py`.
- Accept upstream skill path as input, produce local skill directory as output.
- Generate `metadata.yaml` from upstream skill metadata.
- Generate `io_schema.json` stub from upstream examples or documentation.
- Status: TODO

## Task 4: Define local skill directory structure
- Document required files: `metadata.yaml`, `io_schema.json`, `skill.py`, `test_skill.py`.
- Create template files in `agents/skills/_template/`.
- Validate structure matches `agents/capabilities/manifest.json` expectations.
- Status: TODO

## Task 5: Implement CI quality gates
- Create `.github/workflows/skill-intake-gate.yml`.
- Gate: metadata.yaml exists and has required fields.
- Gate: io_schema.json is valid JSON Schema.
- Gate: no embedded secrets (regex scan for common patterns).
- Gate: test harness exists and is executable.
- Status: TODO

## Task 6: Port first upstream skill
- Select a simple upstream skill with clear inputs/outputs.
- Run converter script and validate output.
- Fix any converter issues discovered during porting.
- Ensure all CI gates pass for the ported skill.
- Status: TODO

## Task 7: Write porting guide documentation
- Document end-to-end porting workflow in `docs/agents/SKILL_PORTING_GUIDE.md`.
- Include troubleshooting section for common conversion issues.
- Status: TODO
