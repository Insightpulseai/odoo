# GitHub Advanced Security for Azure DevOps (GHAzDO) -- Review & IPAI Stack Relevance

**Source URL**: `https://learn.microsoft.com/en-us/azure/devops/repos/security/configure-github-advanced-security-features`
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> GHAzDO brings GitHub's enterprise security scanning (secrets, dependencies, CodeQL code analysis) into Azure DevOps. This review assesses relevance to our GitHub-based stack and compares against our existing free open-source security pipeline.

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Core Scanning Features](#2-core-scanning-features)
3. [Configuration (YAML Pipelines)](#3-configuration-yaml-pipelines)
4. [Pricing](#4-pricing)
5. [Competitive Landscape](#5-competitive-landscape)
6. [IPAI Stack Parity Analysis](#6-ipai-stack-parity-analysis)
7. [Verdict & Recommendations](#7-verdict--recommendations)

---

## 1. Product Overview

| Attribute | Value |
|-----------|-------|
| **Product** | GitHub Advanced Security for Azure DevOps (GHAzDO) |
| **Owner** | Microsoft / GitHub |
| **Status** | Generally Available |
| **Platform** | Azure DevOps Services only (Azure Repos Git) |
| **Pricing** | $49/active committer/month (bundled) or $19/$30 standalone |
| **Integration** | Native in Azure DevOps; Microsoft Defender for Cloud |

GHAzDO brings GitHub's secret scanning, dependency scanning, and CodeQL code scanning natively into Azure DevOps to protect Azure Repos and Pipelines.

### Important Context

**GHAzDO is for Azure DevOps repos, NOT GitHub repos.** Our codebase lives on **GitHub** (not Azure DevOps), so GHAzDO is not directly applicable. The equivalent product for GitHub repos is **GitHub Advanced Security (GHAS)**, which has been unbundled into standalone products as of April 2025.

---

## 2. Core Scanning Features

### Three Pillars

| Feature | What It Does | Coverage |
|---------|-------------|----------|
| **Secret Scanning** | Detect exposed credentials in commits and repo history | 200+ token types from 100+ service providers |
| **Dependency Scanning** | Find known CVEs in direct and transitive dependencies | SCA (Software Composition Analysis) |
| **Code Scanning** (CodeQL) | Static analysis for code-level vulnerabilities | SQL injection, auth bypass, XSS, etc. |

### Secret Scanning Details

| Capability | Description |
|-----------|-------------|
| **Push Protection** | Block pushes containing secrets before they reach the repo |
| **Repo Scanning** | Background scan of entire commit history across all branches |
| **Token Types** | 200+ patterns from 100+ service providers |
| **Coverage** | Full branch history, not just tip of main |

### Dependency Scanning Details

| Capability | Description |
|-----------|-------------|
| **Direct Dependencies** | Scan declared packages |
| **Transitive Dependencies** | Scan nested dependency trees |
| **CVE Database** | Known vulnerability matching |
| **PR Annotations** | Annotate PRs with found vulnerabilities |

### Code Scanning (CodeQL) Details

| Capability | Description |
|-----------|-------------|
| **Engine** | CodeQL semantic analysis |
| **Languages** | C#, C/C++, Python, JavaScript/TypeScript, Java, Kotlin, Go, Ruby, Swift |
| **Query Suites** | `security-extended` (default), `security-and-quality` (extended) |
| **Detection** | SQL injection, auth bypass, XSS, SSRF, path traversal, etc. |
| **PR Annotations** | Inline security findings on pull requests |

---

## 3. Configuration (YAML Pipelines)

### Enabling GHAzDO

Enable at organization, project, or repository level in Azure DevOps:
- **Project Settings** → **Repos** → **Repositories** → **Advanced Security**

### CodeQL Pipeline YAML

```yaml
# Azure DevOps Pipeline for GHAzDO Code Scanning
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  # Initialize CodeQL
  - task: AdvancedSecurity-Codeql-Init@1
    inputs:
      languages: 'python,javascript'
      querysuite: 'security-and-quality'
      # enableAutomaticCodeQLInstall: true  # for self-hosted agents

  # Auto-build (detects build system)
  - task: AdvancedSecurity-Codeql-Autobuild@1

  # Analyze and publish results
  - task: AdvancedSecurity-Codeql-Analyze@1
```

### Dependency Scanning YAML

```yaml
steps:
  - task: AdvancedSecurity-Dependency-Scanning@1
```

### Full Pipeline (Starter)

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  # 1. Code Scanning (CodeQL)
  - task: AdvancedSecurity-Codeql-Init@1
    inputs:
      languages: 'python,javascript'
      querysuite: 'security-and-quality'

  - task: AdvancedSecurity-Codeql-Autobuild@1

  - task: AdvancedSecurity-Codeql-Analyze@1

  # 2. Dependency Scanning
  - task: AdvancedSecurity-Dependency-Scanning@1
```

### Build Gating

PowerShell script available at `github.com/microsoft/GHAzDO-Resources/tree/main/src/gating`:
- Break build if any criticals > 2 days old
- Break build if any highs > 7 days old
- Break build if any new vulnerabilities

### PR Integration

- Auto-annotations on PRs with build validation policy
- Requires Advanced Security scan on default branch + target branch first

---

## 4. Pricing

### Bundled (Legacy)

| Product | Price | Includes |
|---------|-------|----------|
| **GHAzDO (bundled)** | $49/active committer/month | Secret + Dependency + Code scanning |

### Standalone (April 2025+)

| Product | Price | Includes |
|---------|-------|----------|
| **Secret Protection** | $19/active committer/month | Secret scanning + push protection |
| **Code Security** | $30/active committer/month | Code scanning (CodeQL) + Copilot Autofix + dependency review |

### Billing Details

| Detail | Description |
|--------|-------------|
| **Active Committer** | Any committer with a push in the last 90 days |
| **Deduplication** | Counted once per Azure subscription (across repos/orgs) |
| **Billing** | Daily charges to Azure subscription |
| **MACC** | Eligible for Microsoft Azure Consumption Commitment |
| **Migration** | Bundled → standalone is irreversible; requires support ticket |

### Cost Example for Our Team

| Scenario | Active Committers | Monthly Cost |
|----------|------------------|-------------|
| Full bundle (5 devs) | 5 | $245/mo ($2,940/yr) |
| Secret Protection only (5 devs) | 5 | $95/mo ($1,140/yr) |
| Code Security only (5 devs) | 5 | $150/mo ($1,800/yr) |
| Both standalone (5 devs) | 5 | $245/mo ($2,940/yr) |

---

## 5. Competitive Landscape

### GHAzDO vs GitHub GHAS vs Free Open-Source

| Capability | GHAzDO | GitHub GHAS | Open-Source Stack |
|-----------|--------|------------|-------------------|
| **Platform** | Azure DevOps | GitHub | Any (GitHub Actions) |
| **Secret Scanning** | Built-in (200+ types) | Built-in (200+ types) | **Gitleaks** (free) |
| **Code Scanning (SAST)** | CodeQL | CodeQL | **Semgrep** (free OSS) |
| **Dependency Scanning (SCA)** | Built-in | Dependabot (free) | **Trivy** (free) |
| **Container Scanning** | -- | -- | **Trivy** (free) |
| **IaC Scanning** | -- | -- | **Trivy/Checkov** (free) |
| **Push Protection** | Yes | Yes | Gitleaks pre-commit hook |
| **PR Annotations** | Native | Native | GitHub Actions output |
| **Dashboard** | Azure DevOps UI | GitHub Security tab | Separate tool outputs |
| **Price** | $49/committer/mo | $49/committer/mo* | **Free** |
| **Defender Integration** | Yes | Yes | -- |

*GitHub GHAS now split: Secret Protection $19 + Code Security $30.

### Free Open-Source Security Stack (What CLAUDE.md Already Recommends)

```yaml
# From CLAUDE.md - .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  secrets:
    runs-on: self-hosted  # DO droplet = unlimited minutes
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2   # Secret scanning

  sast:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1  # Code scanning
        with:
          config: p/owasp-top-ten p/python

  deps:
    runs-on: self-hosted
    steps:
      - uses: aquasecurity/trivy-action@master  # Dependency scanning
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

### Detailed Tool Comparison

| Feature | GHAzDO/GHAS ($49/mo) | Gitleaks (Free) | Semgrep (Free) | Trivy (Free) |
|---------|----------------------|-----------------|----------------|--------------|
| **Secret Detection** | 200+ token types | 100+ patterns (customizable regex) | Limited (not primary focus) | Basic secret scanning |
| **SAST** | CodeQL (semantic analysis) | -- | Pattern-based (20+ languages) | -- |
| **SCA** | Built-in | -- | -- | CVE database + SBOM |
| **Container** | -- | -- | -- | Image + filesystem scanning |
| **IaC** | -- | -- | Terraform/K8s rules | Terraform, CloudFormation, Docker |
| **CI Integration** | Azure DevOps native | GitHub Actions | GitHub Actions / pre-commit | GitHub Actions |
| **False Positives** | Low (semantic analysis) | Low | Medium-High (pattern matching) | Low |
| **Custom Rules** | CodeQL QL language | Regex patterns | YAML rules | Rego policies |

---

## 6. IPAI Stack Parity Analysis

### Current Security Pipeline (per CLAUDE.md)

Our `CLAUDE.md` already specifies a self-hosted security pipeline using free tools:

| Security Domain | IPAI Tool | Cost | Coverage |
|----------------|-----------|------|----------|
| **Secret Scanning** | Gitleaks | $0 | 100+ patterns; pre-commit + CI |
| **SAST (Code Scanning)** | Semgrep | $0 | OWASP Top 10; Python focus |
| **SCA (Dependency Scanning)** | Trivy | $0 | CVEs; container images; SBOM |
| **CI Runner** | Self-hosted (DO droplet) | $0 (included) | Unlimited minutes |
| **Total** | -- | **$0/month** | Good coverage |

### Parity Assessment

| GHAzDO Capability | Our Equivalent | Parity | Gap |
|-------------------|---------------|--------|-----|
| Secret scanning (200+ types) | Gitleaks (100+ patterns) | 75% | Fewer built-in patterns; extensible via custom regex |
| Push protection | Gitleaks pre-commit hook | 80% | Requires developer to install pre-commit |
| CodeQL code scanning | Semgrep OWASP rules | 65% | Semgrep is pattern-based vs CodeQL's semantic analysis |
| Dependency scanning | Trivy filesystem scan | 90% | Trivy actually scans more (containers, IaC too) |
| PR annotations | GitHub Actions output | 70% | Less polished UI; requires action config |
| Unified dashboard | Separate tool outputs | 40% | No single pane of glass |
| Defender integration | -- | 0% | Not needed (no Azure/Defender) |

### What GHAzDO Has That We Don't Need

| Feature | Why Not Needed |
|---------|---------------|
| **Azure DevOps integration** | We use GitHub, not Azure DevOps |
| **Defender for Cloud** | We don't use Azure/Microsoft cloud |
| **MACC billing** | No Azure consumption commitment |
| **Azure subscription billing** | We bill through DigitalOcean |

---

## 7. Verdict & Recommendations

### Verdict: **Do NOT adopt GHAzDO** (wrong platform)

| Criterion | Assessment |
|-----------|-----------|
| **Platform** | GHAzDO is for Azure DevOps. **We use GitHub.** Not applicable. |
| **Cost** | $49/committer/mo ($2,940/yr for 5 devs) vs $0 for OSS stack |
| **Coverage** | Our Gitleaks + Semgrep + Trivy stack covers the same domains |
| **Philosophy** | CLAUDE.md already specifies free tools; GitHub Team ($4/user/mo) is our plan |

### Should We Buy GitHub GHAS Instead?

Per CLAUDE.md, the answer is also **No**:

| GitHub GHAS Feature | IPAI Free Alternative | Annual Savings |
|--------------------|----------------------|---------------|
| Secret scanning ($19/committer/mo) | Gitleaks (free) | $1,140/yr |
| Code scanning ($30/committer/mo) | Semgrep (free) | $1,800/yr |
| Dependabot | Already free on GitHub | $0 |
| **Total savings** | | **$2,940/yr** |

From CLAUDE.md:
> | Secret scanning | ❌ (GitHub) | ❌ (GitHub) | $19/user (GHAS) | GitLeaks (free) |
> | Code scanning | ❌ (GitHub) | ❌ (GitHub) | $30/user (GHAS) | Semgrep (free) |

### Recommendations

1. **No action required** -- GHAzDO is for Azure DevOps; we use GitHub. Non-applicable.

2. **Strengthen existing free pipeline** (P2):
   - Ensure `gitleaks/gitleaks-action@v2` is in CI (secret scanning)
   - Ensure `returntocorp/semgrep-action@v1` is in CI (SAST)
   - Ensure `aquasecurity/trivy-action@master` is in CI (SCA + containers)
   - Add pre-commit hook for Gitleaks (push protection equivalent)

3. **If CodeQL-quality analysis becomes critical** (P3):
   - CodeQL is free for public repos on GitHub
   - For private repos, evaluate GitHub Code Security ($30/committer/mo) only if Semgrep proves insufficient
   - CodeQL's semantic analysis catches deeper bugs than Semgrep's pattern matching

4. **Unified dashboard** gap (P4):
   - Consider SARIF output from all tools → GitHub Security tab (free)
   - Or aggregate via GitHub Actions summary annotations

### Cost Comparison

| Solution | Monthly (5 devs) | Annual |
|----------|-----------------|--------|
| **IPAI Stack** (Gitleaks + Semgrep + Trivy) | $0 | $0 |
| **GitHub GHAS** (Secret + Code Security) | $245 | $2,940 |
| **GHAzDO** (bundled) | $245 | $2,940 |
| **Savings using OSS** | $245/mo | **$2,940/yr** |

---

## Configuration Reference (For Our GitHub Stack)

### Recommended Security Workflow

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  secrets:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for deep scan
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  sast:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            p/python
            p/javascript
            p/typescript

  deps:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

### Pre-commit Hook (Push Protection)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

---

## Sources

- [Configure GHAzDO Features (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/devops/repos/security/configure-github-advanced-security-features?view=azure-devops)
- [GHAzDO Product Page (Azure)](https://azure.microsoft.com/en-us/products/devops/github-advanced-security)
- [GHAzDO Product Page (GitHub Resources)](https://resources.github.com/security/github-advanced-security-for-azure-devops/)
- [GHAzDO GA Announcement](https://devblogs.microsoft.com/devops/now-generally-available-github-advanced-security-for-azure-devops-is-ready-for-you-to-use/)
- [GHAzDO Billing (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/devops/repos/security/github-advanced-security-billing?view=azure-devops)
- [GHAzDO Hands-on Lab](https://www.azuredevopslabs.com/labs/azuredevops/advancedsecurity/)
- [GHAzDO Starter Pipeline (Gist)](https://gist.github.com/chtzvt/47d4ac81a80038693b8b3a89e0380fce)
- [GHAzDO Resources (Microsoft GitHub)](https://github.com/microsoft/GHAzDO-Resources)
- [Evolving GitHub Advanced Security](https://resources.github.com/evolving-github-advanced-security/)
- [GitHub Secret Protection & Code Security Announcement](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/)
- [Secret Protection & Code Security for Azure DevOps Roadmap](https://learn.microsoft.com/en-us/azure/devops/release-notes/roadmap/2025/ghazdo/secret-protection)
- [AI Code Security Benchmark: Snyk vs Semgrep vs CodeQL](https://sanj.dev/post/ai-code-security-tools-comparison)
- [Top 13 Open-Source DevSecOps Tools 2025](https://www.upwind.io/glossary/13-best-devsecops-tools-2025s-best-open-source-options-sorted-by-use-case)
- [Trivy GitHub Repository](https://github.com/aquasecurity/trivy)
- [Exploring GHAzDO (Medium)](https://onlyutkarsh.medium.com/exploring-github-advanced-security-in-azure-devops-f4d8fe565419)
- [GHAzDO Consulting (InfoMagnus)](https://www.infomagnus.com/github-consulting/github-azure-devops-advanced-security-ghazdo)

---

*Review compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
