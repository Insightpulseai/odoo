# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 18.0.x  | :white_check_mark: |
| < 18.0  | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report

1. **Email**: Send details to the repository maintainers privately
2. **GitHub Security Advisories**: Use [GitHub's security advisory feature](https://github.com/jgtolentino/odoo-ce/security/advisories/new)

### What to Include

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Location of affected code (file path, line numbers)
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

| Action | Timeline |
|--------|----------|
| Initial response | 48 hours |
| Vulnerability assessment | 1 week |
| Patch development | 2 weeks |
| Security advisory published | After patch release |

## Security Best Practices

### For Contributors

1. **Never commit secrets**
   - Use environment variables
   - Check `.env.example` for patterns
   - Pre-commit hooks will catch common patterns

2. **No Enterprise/IAP dependencies**
   - Our CI blocks Enterprise module imports
   - Avoid `odoo.addons.enterprise.*` imports
   - No IAP service calls

3. **Input validation**
   - Validate all user inputs
   - Use Odoo's ORM (no raw SQL unless necessary)
   - Sanitize outputs in QWeb templates

4. **Authentication & Authorization**
   - Use Odoo's built-in access controls
   - Define proper `ir.model.access.csv` rules
   - Use record rules for row-level security

### For Deployers

1. **Environment Security**
   ```bash
   # Use strong database admin password
   POSTGRES_PASSWORD=$(openssl rand -base64 32)

   # Never expose Odoo admin interface publicly without auth
   # Use reverse proxy with authentication
   ```

2. **Network Security**
   - Deploy behind reverse proxy (nginx)
   - Enable HTTPS with valid certificates
   - Restrict database manager access

3. **Updates**
   - Keep OCA modules updated
   - Monitor security advisories
   - Apply patches promptly

## Security Features

### Automated Checks

Our CI/CD pipeline includes:

- **Policy Check** (`scripts/policy-check.sh`)
  - Detects hardcoded secrets
  - Blocks Enterprise dependencies
  - Identifies debug statements

- **Pre-commit Hooks**
  - `detect-private-key`: Catches key files
  - `bandit`: Python security linter

### Code Scanning

We use:
- GitHub Dependabot for dependency updates
- CodeQL analysis for vulnerability detection
- Pre-commit security hooks

## Known Security Considerations

### Odoo-Specific

1. **XML-RPC/JSON-RPC**
   - API is enabled by default
   - Implement rate limiting in production
   - Use API keys for external access

2. **File Uploads**
   - Odoo has built-in restrictions
   - Additional validation in custom modules recommended

3. **Session Management**
   - Use secure cookies in production
   - Configure proper session timeouts

### Custom Modules (ipai_*)

All custom modules follow secure coding practices:
- Input validation on all user data
- Parameterized queries (ORM only)
- Proper access control definitions
- No hardcoded credentials

## Disclosure Policy

We follow responsible disclosure:

1. Reporter notifies maintainers privately
2. We confirm and assess the vulnerability
3. We develop and test a fix
4. We release the patch
5. We publish a security advisory
6. We credit the reporter (if desired)

## Contact

For security concerns, contact the maintainers through GitHub Security Advisories.

---

*Last updated: 2025-12-22*
