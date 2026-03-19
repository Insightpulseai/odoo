# Code Metrics Policy

## Measurement Frequency

- Run cloc after each significant module change
- Generate health report before each release
- Track trends over time (line count growth, test coverage)

## Module Size Guidelines

| Size | Lines | Action |
|------|-------|--------|
| Small | < 500 | Normal — appropriate for bridges and thin modules |
| Medium | 500-2000 | Normal — typical feature module |
| Large | 2000-5000 | Review — consider splitting if multiple concerns |
| Very Large | > 5000 | Split required — module likely violates single responsibility |

## Health Indicators

- Test-to-code ratio target: > 0.3 (30% test code relative to implementation)
- Modules without tests must be classified as "init only" (cannot claim tested)
- Dependency count > 10 is a code smell — review for unnecessary coupling

## Reporting

- Metrics are informational — they do not block CI
- Reports should be stored in docs/evidence/ for trend tracking
- Never use metrics to claim quality without actual test results
- cloc is a proxy for effort, not quality

## Read-Only Skill

- This skill performs no mutations
- All operations are safe to run at any time
- No backup or confirmation required
