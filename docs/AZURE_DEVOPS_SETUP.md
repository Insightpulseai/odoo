# AZURE_DEVOPS_SETUP.md

> Canonical steps to enable Azure DevOps CLI usage for this repo.
> You run these commands locally or in your cloud IDE; no UI clicks beyond login.

---

## 1. Prerequisites

- macOS or Linux shell (cloud IDE / local)
- Git installed
- GitHub CLI (`gh`) optional but recommended
- An Azure DevOps organization already created (e.g. `https://dev.azure.com/YOUR_ORG`)

Define these **once in your shell** (use your real values):

```bash
export AZDO_ORG_URL="https://dev.azure.com/YOUR_ORG"  # e.g. https://dev.azure.com/ipai-org
export AZDO_PROJECT="YOUR_PROJECT_NAME"               # e.g. odoo-ce
```

You can put these into your shell profile (`~/.zshrc`, `~/.bashrc`) if you want them permanent.

---

## 2. Install Azure CLI

### macOS (Homebrew)

```bash
brew update
brew install azure-cli || brew upgrade azure-cli
```

### Verify

```bash
az version
```

You should see a JSON blob with the CLI version.

---

## 3. Login to Azure

Use **device code** login (friendly for cloud IDEs and terminals):

```bash
az login --use-device-code
```

Steps:

1. Command prints a URL + device code.
2. Open the URL in your browser.
3. Enter the device code and complete sign-in (including MFA if required).
4. Return to the terminal; `az login` finishes and prints your subscriptions.

### Optional: set default subscription

If you have more than one subscription, choose one:

```bash
az account list -o table
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

---

## 4. Install Azure DevOps CLI Extension

```bash
az extension add --name azure-devops || az extension update --name azure-devops
```

Verify the extension is available:

```bash
az devops -h
```

You should see `az devops` command help.

---

## 5. Configure Azure DevOps Defaults

Set org + project defaults once so you don't repeat flags:

```bash
az devops configure \
  --defaults organization="${AZDO_ORG_URL}" \
             project="${AZDO_PROJECT}"
```

To confirm:

```bash
az devops configure --list
```

You should see `organization` and `project` set to your values.

---

## 6. Smoke Test: Projects, Repos, Pipelines

### 6.1. List projects

```bash
az devops project list -o table
```

You should see the project you configured in `AZDO_PROJECT`. If it doesn't exist yet, create it:

```bash
az devops project create --name "${AZDO_PROJECT}"
```

Re-run:

```bash
az devops project list -o table
```

### 6.2. List repos (if any)

```bash
az repos list -o table
```

### 6.3. List pipelines (if any)

```bash
az pipelines list -o table
```

If the commands above return valid data, the CLI is fully wired.

---

## 7. GitHub-Backed Pipeline (Optional Standard Pattern)

If this repo lives on GitHub and you want Azure DevOps to **use GitHub as the source of truth** (no Azure Repos mirror):

1. Create a GitHub service connection.
2. Point a pipeline at the GitHub repo's `azure-pipelines.yml`.

Example (one-time setup):

```bash
# Only needed if not already configured:
export GITHUB_REPO_SLUG="OWNER/REPO"   # e.g. jgtolentino/odoo-ce
export GITHUB_PAT="ghp_REPLACE_ME"     # short-lived PAT with repo read access

# Create GitHub service connection
az devops service-endpoint github create \
  --name "github-${GITHUB_REPO_SLUG##*/}" \
  --github-url "https://github.com/${GITHUB_REPO_SLUG}" \
  --github-pat "${GITHUB_PAT}" \
  --organization "${AZDO_ORG_URL}" \
  --project "${AZDO_PROJECT}" \
  --enable-for-all

# Get its ID (for pipeline binding)
GITHUB_SVC_ID="$(
  az devops service-endpoint list \
    --organization "${AZDO_ORG_URL}" \
    --project "${AZDO_PROJECT}" \
    --query "[?name=='github-${GITHUB_REPO_SLUG##*/}'].id | [0]" \
    -o tsv
)"

echo "GitHub service connection ID: ${GITHUB_SVC_ID}"

unset GITHUB_PAT
```

Create `azure-pipelines.yml` in your GitHub repo, then create the pipeline:

```bash
az pipelines create \
  --name "ci-${AZDO_PROJECT}" \
  --repository "${GITHUB_REPO_SLUG}" \
  --repository-type github \
  --branch "main" \
  --service-connection "${GITHUB_SVC_ID}" \
  --yml-path "azure-pipelines.yml"
```

From that point on:

* Code lives in GitHub.
* Azure DevOps only runs CI/CD.

---

## 8. Rollback / Cleanup

To disable or remove Azure DevOps resources:

### 8.1. Disable a pipeline

```bash
PIPELINE_ID="$(
  az pipelines show --name "ci-${AZDO_PROJECT}" --query id -o tsv
)"

az pipelines update \
  --id "${PIPELINE_ID}" \
  --set enabled=false
```

### 8.2. Delete a pipeline

```bash
az pipelines delete \
  --id "${PIPELINE_ID}" \
  --yes
```

### 8.3. Delete a project **(destructive)**

```bash
PROJECT_ID="$(
  az devops project show --project "${AZDO_PROJECT}" --query id -o tsv
)"

az devops project delete \
  --id "${PROJECT_ID}" \
  --yes
```

> Once deleted, repos and pipelines in that project are gone; use with caution.

---

## 9. Summary

* `az login --use-device-code` is always run **by you** with your credentials.
* This repo only contains:
  * CLI commands
  * Configuration defaults
  * Pipeline definitions
* No secrets or credentials are stored in Git; auth is handled by Azure and your shell environment.
