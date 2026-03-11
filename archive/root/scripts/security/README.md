# Security Scripts

Automated security tooling for the Odoo repository.

## Scripts

### `triage_dependabot_alerts.sh`

Fetches and analyzes Dependabot security alerts from GitHub.

**Purpose**: Convert GitHub's vulnerability notifications into structured, actionable reports

**Requirements**:
- GitHub CLI (`gh`) installed and authenticated
- Token scope: `security_events` (for Dependabot alerts)

**Usage**:
```bash
# Fetch and analyze alerts
./scripts/security/triage_dependabot_alerts.sh

# Custom repository
REPO=org/repo ./scripts/security/triage_dependabot_alerts.sh

# Custom output directory
OUTPUT_DIR=/tmp/security ./scripts/security/triage_dependabot_alerts.sh
```

**Output**:
- `docs/security/dependabot/alerts_YYYYMMDD-HHMM.json` - Raw GitHub API response
- `docs/security/dependabot/summary_YYYYMMDD-HHMM.txt` - Severity breakdown and priority list
- `docs/security/dependabot/latest.json` - Symlink to most recent alerts
- `docs/security/dependabot/latest.txt` - Symlink to most recent summary

**Setup GitHub CLI Token**:
```bash
# Refresh token with security_events scope
gh auth refresh -s security_events

# Verify access
gh api repos/Insightpulseai/odoo/dependabot/alerts --paginate | jq length
```

**Severity Breakdown**:
- **Critical**: Immediate action required (exploitable vulnerabilities)
- **High**: Action within 7 days (significant security impact)
- **Moderate**: Action within 30 days (security improvements)
- **Low**: Action within 90 days (minor security issues)

**Workflow**:
1. Run `triage_dependabot_alerts.sh` to generate reports
2. Review `docs/security/dependabot/latest.txt` for priority items
3. Create GitHub issues for critical/high severity alerts:
   ```bash
   gh issue create --title "Security: CVE-YYYY-XXXXX" \
     --body "Priority: Critical\nPackage: npm/package-name\nSee: docs/security/dependabot/latest.txt"
   ```
4. Track remediation in GitHub Projects or task management system
5. Re-run triage after fixes to verify alert closure

**Automation**:
- Add to CI: `.github/workflows/security-triage.yml` (weekly schedule)
- Add to cron: `0 9 * * 1 cd /path/to/odoo && ./scripts/security/triage_dependabot_alerts.sh`

## Directory Structure

```
scripts/security/
├── README.md                      # This file
└── triage_dependabot_alerts.sh    # Dependabot alert analyzer

docs/security/dependabot/
├── alerts_YYYYMMDD-HHMM.json      # Raw alerts (timestamped)
├── summary_YYYYMMDD-HHMM.txt      # Severity summary (timestamped)
├── latest.json -> alerts_...      # Symlink to latest
└── latest.txt -> summary_...      # Symlink to latest
```

## GitHub Token Permissions

Required scope for `triage_dependabot_alerts.sh`:
- `security_events` - Read Dependabot alerts

Check current scopes:
```bash
gh auth status
```

Add missing scopes:
```bash
gh auth refresh -s security_events
```
