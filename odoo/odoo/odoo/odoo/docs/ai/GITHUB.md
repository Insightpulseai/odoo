# GitHub Integration
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Recommended: GitHub Team ($4/user/mo)

Stay on GitHub Team - it provides everything needed:

| Feature | Free | Team | Enterprise | Our Approach |
|---------|------|------|------------|--------------|
| Protected branches | No | Yes | Yes | Use Team |
| Required reviewers | No | Yes | Yes | Use Team |
| CODEOWNERS | No | Yes | Yes | Use Team |
| Draft PRs | No | Yes | Yes | Use Team |
| Actions minutes | 2,000 | 3,000 | 50,000 | Self-hosted runners |
| Secret scanning | No | No | $19/user | GitLeaks (free) |
| Code scanning | No | No | $30/user | Semgrep (free) |
| SAML SSO | No | No | Yes | Keycloak (free) |

**Annual savings**: ~$6,600/year vs Enterprise + GHAS

## GitHub App: pulser-hub

```
App ID: 2191216
Client ID: Iv23liwGL7fnYySPPAjS
Webhook URL: https://n8n.insightpulseai.com/webhook/github-pulser
```

**Capabilities:**
- Webhooks -> n8n -> Odoo task creation
- OAuth -> "Sign in with GitHub" for apps
- Installation tokens -> Secure API access

## Self-Hosted Security Pipeline

Replace GitHub Advanced Security with free tools:

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  secrets:
    runs-on: self-hosted  # Your DO droplet = unlimited minutes
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2

  sast:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: p/owasp-top-ten p/python

  deps:
    runs-on: self-hosted
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

## Self-Hosted Runner Setup

```bash
# On DigitalOcean droplet (178.128.112.214)
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.321.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz
./config.sh --url https://github.com/jgtolentino/odoo --token YOUR_TOKEN
sudo ./svc.sh install && sudo ./svc.sh start
```
