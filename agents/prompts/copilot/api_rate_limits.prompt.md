---
mode: agent
tools:
  - repo
  - tests
description: "Add exponential backoff + jitter to code that hits HTTP 429 or X-RateLimit-Remaining: 0. Stdlib only; 60 s max backoff for CI."
---

# API Rate Limit Handling

Use this prompt when a GitHub Actions workflow, n8n workflow, or Edge Function
hits HTTP 429 or returns `X-RateLimit-Remaining: 0` and needs backoff/retry logic.

Fill in every bracketed section before invoking.

---

## Context

- **File hitting rate limit**: [file path]
- **API endpoint**: [e.g. `https://api.github.com/repos/{owner}/{repo}/issues`]
- **Documented rate limit**: [e.g. `5,000/hr for PATs`, `1,000/hr for GitHub Apps`]
- **Current retry behaviour**: [none / naive `time.sleep(N)` / exponential]
- **Related spec**: [spec/<slug>/ or "none"]

## Constraints

- Use stdlib only (`time`, `math`, `random`) — no new packages without adding to `requirements.txt` first
- Maximum backoff: **60 seconds** (CI context — do not use `time.sleep(600)`)
- Check `X-RateLimit-Remaining` and `Retry-After` headers before retrying
- Reference `GITHUB_TOKEN` / API keys by env var name — never inline values
- Minimal diff: add backoff to the specific function only
- PR-only; no direct push to `main`

## Task

Read the file, locate the HTTP call(s) that can receive 429, and wrap them with:

1. Exponential backoff: `wait = min(base * 2**attempt + jitter, 60)`
2. Jitter: `jitter = random.uniform(0, 1)`
3. `Retry-After` header check: if present, use its value (capped at 60 s)
4. `X-RateLimit-Remaining` guard: if 0, wait until `X-RateLimit-Reset`
5. Max retries: 5 (configurable via env var `MAX_RETRY_ATTEMPTS`)

## Verification Gates (all must pass before opening PR)

```bash
pre-commit run --all-files
```

If the file has tests:
```bash
pytest <test-file> -v
```

## Acceptance Criteria

- [ ] Exponential backoff with jitter implemented
- [ ] `Retry-After` and `X-RateLimit-Remaining` headers checked before retry
- [ ] No `time.sleep` call exceeds 60 s
- [ ] No hardcoded API tokens — env var references only
- [ ] `pre-commit run --all-files` passes
- [ ] PR body includes `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY] [ROLLBACK]`
- [ ] Evidence log saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/rate-limits/logs/retry_test.txt`

## Rollback

```bash
git revert <commit-hash>    # revert backoff addition
```
