# Composer Bugbot Constitution

**Purpose**: PHP/Composer pre-merge AI review system for mandatory code quality gates

**Principles**:
1. **Security First**: Block SQL injection, XSS, insecure deserialization, weak crypto
2. **Dependency Safety**: Enforce composer audit, block known CVEs
3. **PSR Compliance**: Validate PSR-1/PSR-12 coding standards, PSR-4 autoloading
4. **Evidence-Based**: All findings must cite specific line numbers and examples
5. **Merge-Blocking**: P0 issues prevent merge, emergency override with `skip-composer-bugbot` label

**Scope**: All `.php` files, `composer.json`, `composer.lock` in pull requests

**Out of Scope**: Generated code, vendor directories, legacy migration code with `@legacy` tag

**SSOT Boundaries**:
- **PHP Code**: Source truth for business logic and API contracts
- **Composer Dependencies**: Lock file is canonical dependency graph
- **Review Configuration**: `.ai/composer-bugbot-rules.yml` defines severity thresholds

**Integration Points**:
- GitHub Actions (`.github/workflows/composer-bugbot-required.yml`)
- Composer audit for CVE detection
- PHPStan/Psalm for static analysis
- PHP_CodeSniffer for PSR compliance
