# Examples — databricks-app-production-readiness

## Example 1: Internal dashboard app (PASS)

**Input**: Databricks App bundle deployed via CI/CD pipeline. Streamlit-based dashboard reading from Unity Catalog gold tables. SSO via Azure AD. Scaling: 1-3 instances. Health check endpoint configured. Dev/staging/prod workspaces. Data access scoped to `gold.sales` schema only. Version pinning enabled.

**Output**:
- Readiness: PRODUCTION-READY
- All dimensions PASS
- Security: SSO integrated, least-privilege data access confirmed
- Deployment discipline: Fully codified (CI/CD)
- No blocking gaps

## Example 2: App with manual deployment (CONDITIONALLY-READY)

**Input**: Databricks App deployed manually via workspace UI. OAuth configured. Reads from multiple schemas including raw bronze data. No health check endpoint. Dev and prod share workspace.

**Output**:
- Readiness: CONDITIONALLY-READY
- Blocking gaps:
  - Manual deployment — must codify via CI/CD or Databricks CLI
  - No health check endpoint — must add liveness/readiness probe
  - Data access too broad — bronze data access violates least privilege
- Advisory gaps:
  - Workspace separation recommended (dev/prod in same workspace)
- Remediation: Create deployment pipeline, add health endpoint, restrict data access to gold schema

## Example 3: Notebook-served app on Preview feature (NOT-READY)

**Input**: Python notebook served as a web endpoint using a Databricks feature in Private Preview. No auth configured. No deployment pipeline. Single workspace for all environments.

**Output**:
- Readiness: NOT-READY
- Blocking gaps:
  - Feature in Private Preview — not acceptable as canonical production baseline
  - Not packaged as Databricks App bundle (notebook-served)
  - No authentication — security risk
  - No deployment pipeline — manual process
  - No environment separation
- Remediation: Wait for GA. Repackage as Databricks App bundle. Add SSO/OAuth. Create CI/CD pipeline. Separate environments.
