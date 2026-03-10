# Composer Bugbot PRD

## Problem Statement

PHP codebases suffer from common security vulnerabilities (SQL injection, XSS, deserialization) and dependency management issues that escape code review. Manual review cannot scale to catch every vulnerability pattern.

## Goals

1. **Mandatory PHP Security Gates**: Block merge on P0 PHP security vulnerabilities
2. **Composer Audit Integration**: Automatically scan composer.lock for known CVEs
3. **PSR Compliance**: Enforce coding standards without manual review overhead
4. **Developer Education**: Provide actionable feedback on PHP best practices

## Non-Goals

- Performance optimization (use separate perf gates)
- Architectural review (use design review process)
- Business logic validation (manual review)

## User Stories

**As a developer**, I want immediate feedback on PHP security issues so I can fix them before PR review.

**As a security engineer**, I want P0 vulnerabilities blocked automatically so critical issues never reach production.

**As a reviewer**, I want PSR compliance automated so I can focus on business logic review.

## Features

### 1. PHP Security Scanning
**Priority**: P0 (Blocker)

**Patterns**:
- SQL injection via PDO/Eloquent without parameterization
- XSS in Blade/Twig templates without escaping
- Insecure deserialization (`unserialize()` without validation)
- Weak cryptography (MD5/SHA1 for passwords, predictable random)
- Path traversal in file operations
- Command injection in `exec()`/`shell_exec()`/`system()`

**Detection**: PHPStan security rules + custom regex patterns

**Severity Mapping**:
- P0 (Block Merge): SQL injection, RCE, authentication bypass
- P1 (Warn): XSS, CSRF missing, weak crypto
- P2 (Info): PSR violations, complexity warnings

### 2. Composer Dependency Audit
**Priority**: P0 (Blocker)

**Workflow**:
1. Run `composer audit --format=json` on composer.lock
2. Parse CVE list and severity scores (CVSS)
3. Block merge if CVSS ≥ 7.0 (High/Critical)
4. Generate artifact with full CVE details

**Override**: Emergency hotfix requires explicit `skip-composer-audit` label

### 3. PSR Compliance Validation
**Priority**: P1 (Warning)

**Standards**:
- PSR-1: Basic coding standard (opening tags, constants, class names)
- PSR-12: Extended coding style (indentation, line length, imports)
- PSR-4: Autoloading (namespace matches directory structure)

**Tool**: PHP_CodeSniffer with PSR-12 ruleset

**Enforcement**: Warn on violations, block if >50 violations (code quality threshold)

### 4. AI Review Comments
**Priority**: P1 (Warning)

**Workflow**:
1. Changed files → Cursor Bugbot API endpoint
2. Parse response for P0/P1/P2 findings
3. Post inline GitHub comments with line numbers
4. Update PR status check (pass/fail/warn)

**Review Focus**:
- PHP ORM misuse (N+1 queries, missing eager loading)
- Authentication/authorization gaps (missing middleware, insecure sessions)
- Input validation (missing sanitization, type juggling vulnerabilities)
- Error handling (exposing stack traces, logging sensitive data)

## Success Criteria

- **Week 1 (Opt-In)**: ≥10 PRs reviewed, <30% false positives, developer feedback "helpful"
- **Week 3 (Soft-Mandatory)**: P0 precision ≥80%, zero critical security bugs escape
- **Week 6 (Hard-Mandatory)**: Merge blocked on P0 findings, override usage <5%

## Metrics

- **Security**: P0/P1/P2 findings per PR
- **Quality**: False positive rate by severity
- **Adoption**: % PRs with composer-bugbot review, override frequency
- **Performance**: Mean review time, API latency p95

## Dependencies

- GitHub Actions (composer-bugbot-required.yml workflow)
- Composer 2.x (for `composer audit` command)
- PHPStan ≥1.10 (security rules)
- PHP_CodeSniffer ≥3.7 (PSR-12 ruleset)
- Cursor Bugbot API (AI review endpoint)

## Risks

- **False Positives**: Overly aggressive rules frustrate developers → Mitigation: Tuning period (Week 1-2)
- **Composer Audit False Negatives**: Not all CVEs in database → Mitigation: Manual security review for critical components
- **API Latency**: Cursor API timeouts delay PR workflow → Mitigation: Async review with status updates
