# GitHub ↔ Azure Operating Model

## Overview

The platform supports GitHub as a first-class engineering surface for Azure delivery.

---

## Preferred pattern

- Repository-hosted workflows
- Azure authentication through OIDC
- Azure Key Vault for secret retrieval
- Infrastructure and policy as code
- Optional trigger path from GitHub Actions into governed Azure Pipelines flows

---

## Tool roles

| Tool | Role | When to use |
|------|------|-------------|
| **GitHub Actions** | Repo-local automation | Fast feedback, build, test, direct Azure deploy, CI |
| **Azure Pipelines** | Governed release orchestration | Multi-stage promotion, enterprise controls, central release governance |
| **Azure Key Vault** | Managed secret store | Any workflow needing sensitive values |
| **Entra ID federation** | Trust boundary | GitHub-to-Azure OIDC authentication |

---

## Authentication model

| Method | Preference | Use case |
|--------|-----------|----------|
| OIDC (federated identity) | **Preferred** | GitHub Actions → Azure, no stored secrets |
| Managed identity | **Preferred** | Self-hosted runners on Azure VMs |
| Service principal + secret | **Exception only** | Legacy scenarios with documented justification |

---

## Coexistence model

GitHub Actions and Azure Pipelines are complementary, not competing:

- **GitHub Actions** owns repo-local workflows: CI, build, test, package, direct deploy
  to non-production, and policy/compliance scans
- **Azure Pipelines** owns governed release flows: multi-stage production promotion,
  approval gates, protected branch enforcement, enterprise-level orchestration
- **GitHub → Azure Pipelines trigger**: use `azure/pipelines` action when a repo-local
  workflow needs to initiate a governed release

---

## Secret handling

1. Authenticate to Azure via OIDC (no stored secret)
2. Retrieve runtime secrets from Azure Key Vault
3. Mask secrets in workflow logs
4. Never embed secrets in YAML files

---

*Last updated: 2026-04-10*
