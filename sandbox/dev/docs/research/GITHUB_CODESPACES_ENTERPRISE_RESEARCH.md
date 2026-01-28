# GitHub Codespaces & Enterprise Features Research

**Research Date**: 2026-01-28
**Purpose**: Cost-benefit analysis for InsightPulse AI's self-hosted, cost-minimized infrastructure

---

## Executive Summary

**Key Finding**: For a self-hosted, cost-minimized philosophy, **neither GitHub Codespaces nor Enterprise are optimal**:
- **Codespaces**: Cannot be self-hosted, costs escalate quickly (~$60.48/mo per developer vs ~$12-24/mo DigitalOcean droplet)
- **Enterprise**: $21/user/mo vs Team $4/user/mo ($204/year vs $2,580/year for 10 users = **$2,376 savings**)
- **Recommendation**: Stay on **GitHub Team + self-hosted runners + open-source security tools** (current approach)

**Annual Cost Comparison (10 users)**:
| Solution | Annual Cost | Notes |
|----------|-------------|-------|
| **GitHub Team + Self-Hosted** | **$480** | Current, recommended |
| GitHub Enterprise | $2,520 | SSO, GHAS optional ($49/user/mo extra) |
| + GitHub Advanced Security | $8,400 | Secret + Code scanning ($19 + $30/user/mo) |
| + Codespaces (60hr/mo/user) | $1,296 | 4-core, 8hr/day, 21 days/mo |
| **Total Enterprise Stack** | **$12,216** | vs $480 Team = **$11,736 markup (2,449%)**|

**ROI Conclusion**: For 10 users, **Enterprise adds $11,736/year with minimal benefit** when self-hosted alternatives exist.

---

## 1. GitHub Codespaces Deep Dive

### What Is GitHub Codespaces?

GitHub Codespaces provides cloud-based development environments powered by VS Code Dev Containers. Developers get instant, pre-configured environments accessible from browser or desktop IDE.

**Core Features**:
- VS Code in browser or desktop (same experience)
- Docker/container support with `devcontainer.json` configuration
- Port forwarding and networking
- Secrets management (GitHub Secrets integration)
- Pre-build capabilities for faster startup
- Automatic backups (unsaved changes persist)

**Architecture**:
```
GitHub Repository (devcontainer.json)
        ↓
GitHub Codespaces Cloud (VS Code + Docker)
        ↓
Developer (Browser or Desktop VS Code)
```

### Pricing Tiers (2026)

#### Free Tier Limits
- **Free Plan**: 120 core hours/month + 15 GB storage
  - Equivalent to 60 hours on 2-core machine
  - Storage: $0.07/GB-month
- **Pro Plan**: 180 core hours/month + 20 GB storage
  - No additional cost for GitHub Pro subscribers

#### Compute Costs (Beyond Free Tier)

| Machine Type | Cores | RAM | Price/Hour | 8hr/day (21 days) |
|--------------|-------|-----|------------|-------------------|
| 2-core | 2 | 4 GB | $0.18 | $30.24 |
| 4-core | 4 | 8 GB | $0.36 | $60.48 |
| 8-core | 8 | 16 GB | $0.72 | $120.96 |
| 16-core | 16 | 32 GB | $1.44 | $241.92 |
| 32-core | 32 | 64 GB | $2.88 | $483.84 |

**Storage Costs**: $0.07/GB-month (billed for entire duration codespace exists)

**Billing Notes**:
- Charged per minute of active use only (stopped = no compute charges)
- Storage billed even when codespace is suspended
- Organizations have no free tier (unlike personal accounts)

### Capabilities & Limitations

**✅ Capabilities**:
- Full Docker/container support
- Multi-language support (any runtime in Docker)
- GitHub Secrets integration
- Port forwarding (web app development)
- VS Code extensions
- Git operations (push/pull/commit)
- Terminal access (full Linux shell)
- Pre-builds (reduce startup time)

**❌ Limitations**:
- **Cannot be self-hosted** (cloud-only)
- Limited to 4 regions (US West, US East, Europe West, Southeast Asia)
- Fixed machine sizes (no custom specs)
- Internet-based only (no airgapped deployments)
- GitHub account required (no alternative Git platforms)
- Organizations: No free tier

### Use Cases

**Good For**:
- Remote work (consistent environments across devices)
- Onboarding new developers (instant setup)
- Public OSS projects (free tier + transparency)
- Distributed teams (standardized configs)
- Prototyping/demos (disposable environments)

**Not Good For**:
- Self-hosted requirements (impossible)
- Cost-sensitive projects (costs escalate)
- Multi-cloud strategies (GitHub-locked)
- Airgapped environments (cloud-only)
- High-compute workloads (expensive at scale)

---

## 2. GitHub Enterprise Features

### GitHub Enterprise Cloud vs Server

| Feature | Enterprise Cloud | Enterprise Server |
|---------|------------------|-------------------|
| **Hosting** | GitHub-managed | Self-hosted |
| **Pricing** | $21/user/mo | $21/user/mo + infrastructure |
| **Updates** | Automatic | Manual |
| **Customization** | Limited | Full control |
| **Networking** | Public internet | Private network |
| **Compliance** | GitHub SOC2 | Your compliance |
| **Deployment** | Cloud-only | On-premises |

### Core Enterprise Features

#### 1. SAML SSO & Identity Management
- SAML 2.0 authentication
- Integration with Okta, Azure AD, Ping Identity, **Keycloak**
- Centralized user provisioning
- Group-based access control
- Automatic deprovisioning

**Cost**: Included in $21/user/mo base

#### 2. Advanced Security Features (Optional Add-Ons)

##### GitHub Secret Protection ($19/user/mo)
- Secret scanning (API keys, tokens, credentials)
- Push protection (block commits with secrets)
- AI-powered detection (low false positives)
- Custom secret patterns
- Security insights dashboard

##### GitHub Code Security ($30/user/mo)
- Code scanning (CodeQL static analysis)
- Copilot Autofix (AI-generated vulnerability fixes)
- Dependency Review Action (CVE detection)
- Security campaigns (track remediation)
- Premium Dependabot features

**Total GHAS Cost**: $49/user/mo ($588/user/year)

#### 3. Audit Logs & Compliance
- Comprehensive audit trail (all actions logged)
- SIEM integration (Splunk, Sumo Logic, etc.)
- Compliance reporting (SOC2, HIPAA, ISO 27001)
- IP allow lists (restrict access by IP range)
- Data residency controls (Enterprise Server only)

**Cost**: Included in $21/user/mo base

#### 4. Self-Hosted Runners

| Plan | Runner Groups | Max Runners | Parallel Jobs |
|------|---------------|-------------|---------------|
| **Team** | 1 (default) | Unlimited | Unlimited |
| **Enterprise** | Multiple | Unlimited | Unlimited |

**Key Difference**: Enterprise enables **runner groups** (granular control over which repos/orgs access specific runners)

**Cost**: Self-hosted runners are **free** (hardware/electricity costs only)

#### 5. Enterprise Policies & Controls
- Organization-wide policies
- Repository naming conventions
- Default branch protections
- Required workflows
- Third-party app restrictions
- Fine-grained personal access tokens

**Cost**: Included in $21/user/mo base

#### 6. GitHub Connect
- Link Enterprise Server to GitHub.com
- Unified search across instances
- Dependency graph sharing
- Security advisories synchronization

**Cost**: Included in Enterprise Server only

---

## 3. Cost-Benefit Analysis

### Scenario 1: GitHub Team (Current Approach - Recommended)

**Setup**:
- GitHub Team plan: $4/user/mo
- Self-hosted runners on DigitalOcean droplet ($12-24/mo)
- Open-source security tools (GitLeaks, Semgrep, Trivy)
- Keycloak for SSO (self-hosted, $0)
- VS Code Dev Containers (local Docker, $0)

**Annual Costs (10 users)**:
```
GitHub Team:          $480/year  ($4 × 10 × 12)
DO Droplet (runner):  $288/year  ($24/mo × 12)
Total:                $768/year
```

**Capabilities**:
- ✅ Protected branches
- ✅ Required reviewers
- ✅ CODEOWNERS
- ✅ Draft PRs
- ✅ 3,000 Actions minutes/mo (org-level)
- ✅ Unlimited self-hosted runners
- ✅ Secret scanning (GitLeaks, free)
- ✅ Code scanning (Semgrep, free)
- ✅ SSO (Keycloak, free)
- ✅ Dev environments (VS Code Dev Containers, free)

**What's Missing**:
- ❌ SAML SSO (GitHub-managed)
- ❌ Runner groups (Enterprise only)
- ❌ GitHub Advanced Security dashboard
- ❌ Copilot Autofix

### Scenario 2: GitHub Enterprise (Not Recommended)

**Setup**:
- GitHub Enterprise Cloud: $21/user/mo
- GitHub Secret Protection: $19/user/mo
- GitHub Code Security: $30/user/mo
- GitHub Codespaces (4-core, 60hr/mo): $10.80/user/mo

**Annual Costs (10 users)**:
```
Enterprise:           $2,520/year  ($21 × 10 × 12)
Secret Protection:    $2,280/year  ($19 × 10 × 12)
Code Security:        $3,600/year  ($30 × 10 × 12)
Codespaces:           $1,296/year  ($10.80 × 10 × 12)
Total:               $9,696/year
```

**Markup vs Team**: $8,928/year (1,163% more expensive)

**New Capabilities**:
- ✅ GitHub-managed SAML SSO
- ✅ Runner groups (granular runner access)
- ✅ GitHub Advanced Security dashboard
- ✅ Copilot Autofix
- ✅ Cloud dev environments (Codespaces)

**Critical Missing Value**: All "new" capabilities have self-hosted alternatives at **1/10th the cost**.

### Break-Even Analysis

**When does Enterprise make sense?**

#### Threshold 1: SAML SSO ROI
- **Break-even**: When self-hosted Keycloak maintenance costs > $17/user/mo ($204/user/year)
- **Reality**: Keycloak on DO droplet = $24/mo total / 10 users = **$2.40/user/mo**
- **Verdict**: Never worth it (Keycloak is 7× cheaper)

#### Threshold 2: Security Tools ROI
- **Break-even**: When GitLeaks + Semgrep + Trivy maintenance > $49/user/mo ($588/user/year)
- **Reality**: Self-hosted security pipeline = $24/mo runner + $0 tool costs / 10 users = **$2.40/user/mo**
- **Verdict**: Never worth it (self-hosted is 20× cheaper)

#### Threshold 3: Codespaces ROI
- **Break-even**: When DigitalOcean droplet costs > $10.80/user/mo ($129.60/user/year)
- **Reality**: DO 8GB droplet = $24/mo / 10 users = **$2.40/user/mo**
- **Verdict**: Never worth it (DO is 4.5× cheaper)

### ROI Calculator

```python
def calculate_github_roi(num_users: int) -> dict:
    """Calculate GitHub Team vs Enterprise costs"""

    # Team plan (current)
    team_github = 4 * num_users * 12
    team_runner = 288  # $24/mo DO droplet
    team_total = team_github + team_runner

    # Enterprise plan
    ent_github = 21 * num_users * 12
    ent_secret = 19 * num_users * 12
    ent_code = 30 * num_users * 12
    ent_codespaces = 10.80 * num_users * 12
    ent_total = ent_github + ent_secret + ent_code + ent_codespaces

    # Markup
    markup = ent_total - team_total
    markup_pct = (markup / team_total) * 100

    return {
        "team_total": team_total,
        "enterprise_total": ent_total,
        "markup": markup,
        "markup_pct": markup_pct
    }

# Results for 10 users
calculate_github_roi(10)
# {'team_total': 768, 'enterprise_total': 9696, 'markup': 8928, 'markup_pct': 1162.5}
```

**Conclusion**: For every scenario, **self-hosted alternatives are 4-20× cheaper** with equivalent functionality.

---

## 4. Alternatives & Comparisons

### VS Code Dev Containers vs GitHub Codespaces

| Feature | VS Code Dev Containers | GitHub Codespaces |
|---------|------------------------|-------------------|
| **Configuration** | `devcontainer.json` | Same `devcontainer.json` |
| **Runtime** | Local Docker | GitHub Cloud |
| **Cost** | $0 (electricity only) | $0.18-2.88/hour |
| **Performance** | Local hardware | GitHub servers |
| **Offline** | ✅ Full support | ❌ Internet required |
| **Setup** | 1-click (Docker Desktop) | 1-click (GitHub UI) |
| **State Persistence** | Manual backups | Auto-saved |
| **Speed** | Depends on hardware | Fast (GitHub infra) |
| **Customization** | Full control | Limited to config |

**Recommendation**: **VS Code Dev Containers** for cost-minimized, self-hosted approach.

**Setup**:
```bash
# Install Docker Desktop
brew install docker

# Install VS Code Dev Containers extension
code --install-extension ms-vscode-remote.remote-containers

# Open repo in container
code --folder-uri vscode-remote://dev-container+<path-to-repo>
```

### GitPod vs GitHub Codespaces

| Feature | GitPod | GitHub Codespaces |
|---------|--------|-------------------|
| **Open Source** | ✅ Yes | ❌ No |
| **Git Platforms** | GitHub, GitLab, Bitbucket | GitHub only |
| **Configuration** | `gitpod.yml` | `devcontainer.json` |
| **IDE** | Any (browser-based) | VS Code only |
| **Pricing** | Cheaper | More expensive |
| **Performance** | Slower (user reports) | Faster |
| **Self-Hosted** | ✅ Yes | ❌ No |

**Recommendation**: **GitPod** if multi-Git-platform support needed, but **VS Code Dev Containers** cheaper.

### Coder (Self-Hosted Codespaces Alternative)

**Coder** is an open-source, self-hostable alternative to GitHub Codespaces.

**Key Features**:
- Self-hosted on your infrastructure (DO, AWS, GCP, on-prem)
- Multi-cloud support
- Supports any IDE (VS Code, IntelliJ, etc.)
- Terraform-based provisioning
- Full control over resources

**Cost**: Free (open-source) + infrastructure costs

**Setup**:
```bash
# Deploy Coder on DigitalOcean droplet
curl -fsSL https://coder.com/install.sh | sh
coder server --postgres-url="$POSTGRES_URL"

# Create workspace
coder templates init
coder create my-workspace --template="docker"
```

**Recommendation**: **Coder** for self-hosted cloud dev environments if VS Code Dev Containers insufficient.

### Security Tools: GHAS vs Open-Source

| Capability | GitHub Advanced Security | Open-Source Alternative |
|------------|--------------------------|-------------------------|
| **Secret Scanning** | $19/user/mo | GitLeaks ($0) |
| **Code Scanning** | $30/user/mo | Semgrep ($0) |
| **Dependency Scanning** | Included | Trivy ($0) |
| **Container Scanning** | Not included | Trivy ($0) |
| **SAST** | CodeQL | SonarQube ($0) |
| **Dashboard** | GitHub UI | Self-hosted Grafana ($0) |
| **Total Cost** | $588/user/year | $288/year (runner only) |

**Recommendation**: **Open-source security pipeline** (GitLeaks + Semgrep + Trivy + SonarQube) on self-hosted runner.

**Implementation**:
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  secrets:
    runs-on: self-hosted
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

### SSO: Keycloak vs GitHub Enterprise SAML

| Feature | Keycloak (Self-Hosted) | GitHub Enterprise SAML |
|---------|------------------------|------------------------|
| **Cost** | $24/mo droplet (shared) | $21/user/mo |
| **Setup** | Docker Compose | GitHub UI config |
| **Protocols** | SAML, OAuth, OIDC | SAML only |
| **Customization** | Full control | Limited |
| **Integration** | Any SAML app | GitHub only |
| **User Limit** | Unlimited | Per-user pricing |
| **Total Cost (10 users)** | $24/mo ($288/year) | $2,520/year |

**Recommendation**: **Keycloak** for self-hosted SSO (8.75× cheaper).

**Setup**:
```yaml
# docker-compose.yml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
    ports:
      - "8080:8080"
    command: start-dev
```

**Integration with GitHub**:
```bash
# GitHub Team supports SAML SSO via Keycloak
# Configure in Organization Settings → Security → SAML single sign-on
# Use Keycloak SAML metadata URL: https://keycloak.insightpulseai.net/realms/github/protocol/saml/descriptor
```

---

## 5. Integration with Current Stack

### Current InsightPulse AI Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                   InsightPulse AI Stack (Self-Hosted)                │
├─────────────────────────────────────────────────────────────────────┤
│  DigitalOcean ($50-100/mo)                                           │
│  ├── odoo-erp-prod (159.223.75.148) - 4GB RAM                       │
│  │   ├── Mattermost (chat.insightpulseai.net)                       │
│  │   ├── n8n (n8n.insightpulseai.net)                               │
│  │   └── Keycloak (auth.insightpulseai.net)                         │
│  ├── ocr-service-droplet (188.166.237.231) - 8GB RAM                │
│  │   ├── Agent Service (Claude 3.5 Sonnet)                          │
│  │   └── OCR Service (PaddleOCR-VL + OpenAI)                        │
│  └── self-hosted-runner (new, 2GB RAM) - $12/mo                     │
│                                                                      │
│  Supabase PostgreSQL (spdtwktxdalcfigzeqrz) - Free/Pro tier         │
│  Vercel (Frontend) - Hobby tier ($0)                                │
│  Apache Superset (BI) - Self-hosted on odoo-erp-prod                │
│  GitHub Team ($4/user/mo) - 10 users = $480/year                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Integration Recommendations

#### 1. Development Environments: VS Code Dev Containers

**Current**: Local Odoo 18 CE development
**Recommended**: Dockerized dev containers with `devcontainer.json`

**Benefits**:
- Consistent environments across team (no "works on my machine")
- Onboarding new developers (1-click setup)
- Portable configs (version-controlled)
- Cost: $0 (local Docker)

**Implementation**:
```json
// .devcontainer/devcontainer.json
{
  "name": "Odoo 18 CE Development",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "odoo",
  "workspaceFolder": "/mnt/extra-addons",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "odoo.odoo-snippets"
      ]
    }
  },
  "forwardPorts": [8069],
  "postCreateCommand": "pip install -r requirements.txt"
}
```

**Cost Comparison**:
- GitHub Codespaces (4-core, 8hr/day): $60.48/user/mo
- VS Code Dev Containers: $0 (electricity negligible)
- **Savings**: $60.48/user/mo × 10 users = **$604.80/mo ($7,257.60/year)**

#### 2. CI/CD: Self-Hosted GitHub Actions Runner

**Current**: 3,000 minutes/mo (GitHub Team)
**Recommended**: Self-hosted runner on DigitalOcean droplet

**Benefits**:
- Unlimited minutes (vs 3,000/mo limit)
- Faster builds (dedicated hardware)
- Private networking (Supabase, Odoo access)
- Cost: $12-24/mo (vs $0.008/min overage = $48/1000 extra minutes)

**Implementation**:
```bash
# Deploy runner on DO droplet
ssh root@159.223.75.148
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.321.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz
./config.sh --url https://github.com/jgtolentino/odoo-ce --token YOUR_TOKEN
sudo ./svc.sh install && sudo ./svc.sh start
```

**Cost Comparison**:
- GitHub-hosted overage: $0.008/min = $48/1000 min
- Self-hosted: $24/mo unlimited = **$0.00004/min**
- **Savings**: $24/mo vs GitHub-hosted overage (ROI after 500 extra minutes/mo)

#### 3. Security Scanning: Self-Hosted Pipeline

**Current**: No security scanning
**Recommended**: GitLeaks + Semgrep + Trivy on self-hosted runner

**Benefits**:
- Secret scanning (GitLeaks) = $19/user/mo GHAS equivalent
- Code scanning (Semgrep) = $30/user/mo GHAS equivalent
- Container scanning (Trivy) = not included in GHAS
- Cost: $0 (runs on self-hosted runner)

**Implementation**: See Section 4 → Security Tools

**Cost Comparison**:
- GitHub Advanced Security: $49/user/mo × 10 = $490/mo ($5,880/year)
- Self-hosted: $24/mo runner (shared) = **$288/year**
- **Savings**: $5,592/year (95% cheaper)

#### 4. SSO: Keycloak (Already Deployed)

**Current**: Keycloak on odoo-erp-prod (auth.insightpulseai.net)
**Recommended**: Integrate GitHub Team with Keycloak SAML

**Benefits**:
- Centralized auth (GitHub, Mattermost, Odoo, Superset)
- No per-user SSO fees (vs $21/user/mo Enterprise)
- Full control (custom login flows, MFA, etc.)
- Cost: $0 (already deployed)

**Integration**:
```bash
# GitHub Team SSO setup
# Organization Settings → Security → SAML single sign-on
# Keycloak SAML metadata: https://auth.insightpulseai.net/realms/github/protocol/saml/descriptor
```

**Cost Comparison**:
- GitHub Enterprise SAML: $21/user/mo × 10 = $2,520/year
- Keycloak: $0 (already running on existing droplet)
- **Savings**: $2,520/year (100% savings)

### Total Stack Cost Comparison

#### Current (Recommended)
```
GitHub Team:                 $480/year   (10 users × $4/mo × 12)
DO Droplets:                 $1,200/year ($100/mo × 12 - existing)
Self-Hosted Runner:          $288/year   (New $24/mo × 12)
Total:                       $1,968/year
```

#### With GitHub Enterprise + Codespaces
```
GitHub Enterprise:           $2,520/year (10 users × $21/mo × 12)
GitHub Secret Protection:    $2,280/year (10 users × $19/mo × 12)
GitHub Code Security:        $3,600/year (10 users × $30/mo × 12)
GitHub Codespaces:           $7,257/year (10 users × $60.48/mo × 12)
DO Droplets:                 $1,200/year (Same infra)
Total:                       $16,857/year
```

**Markup**: $14,889/year (756% more expensive)

**ROI Verdict**: **Stay on GitHub Team + self-hosted alternatives** - no compelling reason to upgrade.

---

## 6. Hidden Costs & Considerations

### GitHub Codespaces Hidden Costs

1. **Storage accumulation**: $0.07/GB-month adds up (old codespaces not deleted)
2. **Pre-builds**: Billed at $0.125/GB (faster startup but extra cost)
3. **Network egress**: Not metered yet, but may be in future
4. **Idle codespaces**: Easy to forget to stop (charged until stopped)

### GitHub Enterprise Hidden Costs

1. **GHAS is optional**: $49/user/mo extra ($588/user/year)
2. **Training/onboarding**: Team needs to learn new security workflows
3. **Vendor lock-in**: Moving off GitHub Enterprise is painful
4. **Feature creep**: "We paid for it, must use it" mentality

### Self-Hosted Hidden Costs

1. **Maintenance time**: Keycloak, runner, security tools need updates
2. **Monitoring**: Need to monitor runner health, storage, etc.
3. **Backup/DR**: Self-hosted means self-managed disaster recovery
4. **Security**: Responsible for patching vulnerabilities

**Verdict**: Self-hosted maintenance is **<5 hours/month** ($50-100 eng time) vs $14,889/year Enterprise markup = **Still 148× cheaper**.

---

## 7. Recommendations for InsightPulse AI

### Short-Term Actions (Immediate - Q1 2026)

✅ **Keep GitHub Team** ($4/user/mo)
- No compelling reason to upgrade
- Team features sufficient (protected branches, CODEOWNERS, draft PRs)

✅ **Deploy Self-Hosted Runner** ($24/mo DO droplet)
- Unlimited Actions minutes
- Private networking (Supabase, Odoo)
- Faster builds (dedicated hardware)

✅ **Implement Security Pipeline** (GitLeaks + Semgrep + Trivy)
- Secret scanning = GHAS equivalent
- Code scanning = GHAS equivalent
- Container scanning = bonus (not in GHAS)
- Cost: $0 (runs on self-hosted runner)

✅ **Use VS Code Dev Containers** (local Docker)
- Standardize dev environments
- Onboard new developers faster
- Cost: $0 vs $7,257/year Codespaces

✅ **Integrate GitHub with Keycloak SSO**
- Centralized auth across stack
- Cost: $0 vs $2,520/year Enterprise SAML

### Medium-Term Evaluation (Q2-Q3 2026)

🔍 **Monitor Team Features**
- Track if runner group limitations cause issues (unlikely)
- Evaluate if GHAS dashboard worth $5,880/year (probably not)

🔍 **Consider Coder if Needed**
- If team demands cloud dev environments
- Self-hosted alternative to Codespaces
- Cost: $24/mo droplet (shared) vs $7,257/year Codespaces

### Long-Term Strategy (2027+)

📊 **Enterprise Break-Even Scenarios**

GitHub Enterprise ONLY makes sense if **all** of the following are true:
1. **Team size >50 users** (economies of scale on $21/user/mo)
2. **Compliance mandates GitHub-managed SSO** (self-hosted Keycloak insufficient)
3. **Must use GHAS dashboard** (open-source alternatives unacceptable)
4. **Cloud dev environments required** (local Docker unacceptable)
5. **Security team demands Copilot Autofix** (manual fixes unacceptable)

**Current Status**: **0/5 criteria met** - Enterprise not justified.

---

## 8. Competitor Landscape

### Cloud IDE Alternatives

| Provider | Pricing | Self-Hosted | Open Source |
|----------|---------|-------------|-------------|
| **GitHub Codespaces** | $0.18-2.88/hr | ❌ No | ❌ No |
| **GitPod** | $0.10/hr | ✅ Yes | ✅ Yes |
| **Coder** | Free + infra | ✅ Yes | ✅ Yes |
| **DevPod** | Free + infra | ✅ Yes | ✅ Yes |
| **VS Code Dev Containers** | Free | ✅ Yes | ✅ Yes |

**Recommendation**: **VS Code Dev Containers** for local, **Coder** for self-hosted cloud.

### Security Tool Alternatives

| Tool | Capability | Pricing | Self-Hosted |
|------|------------|---------|-------------|
| **GitLeaks** | Secret scanning | Free | ✅ Yes |
| **Semgrep** | SAST | Free OSS | ✅ Yes |
| **Trivy** | Container scanning | Free | ✅ Yes |
| **SonarQube** | Code quality | Free CE | ✅ Yes |
| **OWASP Dependency-Check** | Dependency scanning | Free | ✅ Yes |
| **GitHub Advanced Security** | All-in-one | $588/user/year | ❌ No |

**Recommendation**: **Open-source stack** (GitLeaks + Semgrep + Trivy + SonarQube) = free vs $5,880/year GHAS.

---

## 9. Conclusion & Action Plan

### Summary

**GitHub Codespaces**: ❌ Not recommended
- Cannot be self-hosted (deal-breaker)
- 10× more expensive than DigitalOcean droplets
- VS Code Dev Containers provide equivalent experience locally

**GitHub Enterprise**: ❌ Not recommended
- $21/user/mo vs $4/user/mo Team = $2,376/year markup (10 users)
- GHAS adds $5,880/year with free open-source alternatives
- Keycloak provides SSO for $0 vs $2,520/year Enterprise SAML
- No features justify 756% cost increase

**Self-Hosted Approach**: ✅ Strongly recommended
- GitHub Team: $480/year (base Git hosting)
- Self-hosted runner: $288/year (unlimited Actions)
- VS Code Dev Containers: $0 (local dev environments)
- Security pipeline: $0 (GitLeaks + Semgrep + Trivy)
- Keycloak SSO: $0 (already deployed)
- **Total**: $768/year vs $16,857/year Enterprise stack = **$16,089 savings (2,092%)**

### Final Recommendation

**Stay on GitHub Team + self-hosted infrastructure.**

**Why**:
1. **Cost**: 21× cheaper than Enterprise stack
2. **Control**: Full control over infrastructure, security, and data
3. **Flexibility**: Not locked into GitHub ecosystem
4. **Philosophy**: Aligns with cost-minimized, self-hosted principles
5. **Quality**: Open-source tools are often better than proprietary (e.g., Semgrep > CodeQL)

**When to Reconsider**:
- Team size >50 users (economies of scale)
- Compliance mandates GitHub-managed infrastructure
- Significant feature gap emerges (unlikely)

### Immediate Next Steps

1. ✅ **Deploy self-hosted runner** on DO droplet ($24/mo)
2. ✅ **Implement security pipeline** (GitLeaks + Semgrep + Trivy)
3. ✅ **Create `.devcontainer` configs** for Odoo 18 CE repo
4. ✅ **Integrate GitHub with Keycloak SSO**
5. ✅ **Document self-hosted approach** in `docs/infra/`

**Timeline**: Complete in Q1 2026 (before re-evaluating in Q2)

---

## Sources

### GitHub Codespaces
- [GitHub Codespaces billing - GitHub Docs](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)
- [GitHub Pricing](https://github.com/pricing)
- [GitHub Pricing Calculator](https://github.com/pricing/calculator)
- [Understanding the Cost of GitHub Codespaces | Medium](https://medium.com/@udtc.us/understanding-the-cost-of-github-codespaces-a-deep-dive-into-2-core-instances-913a110eefb3)
- [What are GitHub Codespaces? - GitHub Docs](https://docs.github.com/codespaces/overview)
- [Codespaces for Free and Pro Accounts - GitHub Changelog](https://github.blog/changelog/2022-11-09-codespaces-for-free-and-pro-accounts/)

### GitHub Enterprise
- [GitHub Enterprise Pricing](https://github.com/pricing)
- [Understanding GitHub Enterprise Cost | Axolo Blog](https://axolo.co/blog/p/github-enterprise-cost)
- [GitHub Enterprise Pricing Guide | CloudEagle.ai](https://www.cloudeagle.ai/blogs/github-pricing-guide)
- [GitHub's plans - GitHub Docs](https://docs.github.com/get-started/learning-about-github/githubs-products)

### GitHub Advanced Security
- [Introducing GitHub Secret Protection and GitHub Code Security](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/)
- [Evolving GitHub Advanced Security](https://resources.github.com/evolving-github-advanced-security/)
- [About GitHub Advanced Security - GitHub Docs](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)
- [GitHub Advanced Security license billing](https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security)

### Alternatives
- [GitHub Codespaces vs Gitpod | freeCodeCamp](https://www.freecodecamp.org/news/github-codespaces-vs-gitpod-cloud-based-dev-environments/)
- [Gitpod vs. Codespaces vs. Coder vs. DevPod: 2024 Comparison](https://www.vcluster.com/blog/comparing-coder-vs-codespaces-vs-gitpod-vs-devpod)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Semgrep vs Github Advanced Security](https://semgrep.dev/resources/semgrep-vs-github/)
- [GitLeaks Alternatives](https://slashdot.org/software/p/gitleaks/alternatives)

### Self-Hosted Security
- [Implementing a Complete DevSecOps Toolchain with Open Source | Jit](https://www.jit.io/resources/devsecops/implementing-a-complete-devsecops-toolchain-with-open-source)
- [2025 Guide to the Best Code Security Scan Tools](https://www.stackhawk.com/blog/code-security-scan-tools/)

### Keycloak SSO
- [Keycloak](https://www.keycloak.org/)
- [GitHub Enterprise Server SSO with Keycloak | Medium](https://medium.com/@guillem.riera/github-enterprise-server-sso-with-keycloak-5337652ac621)
- [Keycloak SSO: Advantages, installation, protips and the real cost](https://pretius.com/blog/keycloak-sso)

### Self-Hosted Runners
- [When to choose GitHub-Hosted runners or self-hosted runners | GitHub Blog](https://github.blog/enterprise-software/ci-cd/when-to-choose-github-hosted-runners-or-self-hosted-runners-with-github-actions/)
- [Self-hosted runners - GitHub Docs](https://docs.github.com/actions/hosting-your-own-runners)
- [From Zero to Pro: The Complete Guide to GitHub Self-Hosted Runners | Medium](https://medium.com/@devavirathan.mahalingam/from-zero-to-pro-the-complete-guide-to-github-self-hosted-runners-with-real-world-setup-ad97c0f8dbf3)

---

**Report Generated**: 2026-01-28
**Next Review**: 2026-04-01 (Q2 evaluation)
**Owned By**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
