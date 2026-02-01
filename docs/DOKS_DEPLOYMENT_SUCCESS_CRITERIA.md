# DOKS Deployment Success Criteria – Infra + Custom Features

For a DigitalOcean Kubernetes (DOKS) deployment to be considered successful, **all infra conditions (1–5)** and **all custom feature conditions (6)** must be satisfied.

---

## 1. Cluster Status (DOKS / `doctl`)

* **Condition**
  * The cluster shows `running` status in the DigitalOcean Control Panel or via:
    ```bash
    doctl kubernetes cluster get <cluster-id>
    ```

* **Pass Criteria**
  * `status` = `running`
  * Command exits with code `0`

---

## 2. Node Health (`kubectl get nodes`)

* **Condition**
  * All worker nodes report `Ready` and have no `NotReady` or `Unknown` conditions

* **Pass Criteria**
  * `kubectl get nodes` shows all nodes in `STATUS=Ready`
  * `kubectl describe node <node>` shows no repeating `NotReady`, disk pressure, or memory pressure conditions

---

## 3. Pod Health (Odoo, Keycloak, Postgres, Aux Services)

* **Condition**
  * Every pod in the target namespace (Odoo, Keycloak, Postgres, and any auxiliary services) is:
    * `STATUS=Running`
    * `READY` containers fully available (e.g., `1/1`, `2/2`)

* **Pass Criteria**
  * `kubectl get pods -n <ns>` shows:
    * No `CrashLoopBackOff`, `Error`, or long-term `Pending`
  * Liveness/readiness probes for Odoo and Postgres succeed

---

## 4. Services & Ingress (Connectivity + TLS)

* **Condition**
  * ClusterIP / NodePort services expose correct ports
  * Ingress routes are reachable over HTTPS

* **Pass Criteria**
  * `kubectl get svc -n <ns>`:
    * Services for Odoo, Keycloak, and Postgres exist with correct `PORT(S)`
  * `kubectl get ingress -n <ns>`:
    * Ingress resources have an `ADDRESS` and expected `HOSTS`
  * External checks:
    ```bash
    curl -k -I https://erp.insightpulseai.com
    curl -k -I https://auth.insightpulseai.com
    ```
    * Return HTTP `200` or `302` status codes

---

## 5. Stability & Metrics (No Restarts, Healthy Metrics)

* **Condition**
  * No unexpected restarts in the last 24 hours
  * kube-state-metrics reports each expected pod as healthy

* **Pass Criteria**
  * `kubectl get pods -n <ns>`:
    * `RESTARTS` count does not increase over a 24-hour window
  * `kubectl logs <pod> -n <ns>`:
    * No crash loops or fatal errors
  * kube-state-metrics:
    * `pod_status_phase{phase="Running"}` (or equivalent) = `1` for each expected pod
    * No alerts fired for `pod_status != 1`

---

## 6. Application Feature Success Criteria (Custom Modules & Data)

These validate that **the custom Odoo features you care about are actually working**, not just that pods are "up".

### 6.1 Installed Modules (Baseline)

| Feature Implemented      | PMP Terminology            | InsightPulse Module         |
| ------------------------ | -------------------------- | --------------------------- |
| WBS Auto-Numbering       | Work Breakdown Structure   | `ipai_ppm_advanced`         |
| Budget Control Interface | Procure-to-Pay (P2P)       | `ipai_internal_shop`        |
| Email/Mobile Alerts      | Communications Management  | `ipai_finance_ppm` (Alerts) |
| External Auth            | Identity Management        | `auth_oidc` (Keycloak)      |
| Image Deployment         | Continuous Deployment (CD) | `deploy.yml` (image-based)  |

**Pass Criteria**

From inside the Odoo pod:
```bash
kubectl exec -it <odoo-pod> -- odoo-bin -c /etc/odoo.conf -d <DB_NAME> --log-level=info --stop-after-init --modules
```

* All of the following must appear in the installed or installable module list **without** dependency errors:
  * `ipai_ppm_advanced`
  * `ipai_internal_shop`
  * `ipai_finance_ppm`
  * `auth_oidc`

And migrations must succeed:
```bash
kubectl exec -it <odoo-pod> -- odoo-bin -c /etc/odoo.conf \
  -d <DB_NAME> -u ipai_ppm_advanced,ipai_internal_shop,ipai_finance_ppm,auth_oidc --stop-after-init
```

Exit code must be `0`.

---

### 6.2 WBS Auto-Numbering (`ipai_ppm_advanced`)

* **Condition**
  * Project tasks under a Month-End Close project automatically receive WBS codes and stay consistent when re-ordered

* **Pass Criteria**
  * In Odoo UI (or via API/RPC), create a test project "Month-End Close – DOKS" and tasks under it
  * For child tasks:
    * First-level tasks show codes like `1.1`, `1.2`, `1.3`
    * Reordering tasks updates codes deterministically (no duplicates, no gaps)
  * Optional DB check:
    ```sql
    SELECT name, wbs_code FROM project_task WHERE project_id = <new_project_id> ORDER BY wbs_code;
    ```
    * Returns sequential `wbs_code` values

---

### 6.3 Budget Control Interface (`ipai_internal_shop` – P2P Flow)

* **Condition**
  * Internal procurement flow works and creates purchase requests (not sales orders)

* **Pass Criteria**
  * From the Website:
    * User adds an item to cart and submits a request
  * In backend:
    * A `purchase.request` (or equivalent model defined by `ipai_internal_shop`) is created
    * **No** `sale.order` is created for this internal request
  * Required budget fields (e.g., project, cost center, budget line) are visible and stored
  * Query-level sanity check:
    ```sql
    SELECT COUNT(*) FROM purchase_request WHERE origin ILIKE '%Website Internal Request%';
    ```
    * Returns `>= 1` after test

---

### 6.4 Email/Mobile Alerts (`ipai_finance_ppm`)

* **Condition**
  * Finance alerts trigger correctly based on defined thresholds (e.g., overspend, late close)

* **Pass Criteria**
  * Create a test condition (e.g., over-budget WBS or late milestone)
  * Trigger relevant scheduler / cron job:
    ```bash
    kubectl exec -it <odoo-pod> -- odoo-bin -c /etc/odoo.conf \
      -d <DB_NAME> -u ipai_finance_ppm --stop-after-init
    ```
  * Verify:
    * An alert record is created in Odoo (e.g., log table / message / activity)
    * Integration target (email or Mattermost webhook) logs at least one test notification

---

### 6.5 External Auth (`auth_oidc` / Keycloak SSO)

* **Condition**
  * Login to Odoo via Keycloak SSO works end-to-end

* **Pass Criteria**
  * `auth_oidc` module is installed and configured with the correct Keycloak realm and client
  * From browser:
    * Navigating to `https://erp.insightpulseai.com/web` redirects to Keycloak (or shows SSO option)
    * Logging in via Keycloak successfully creates / maps Odoo user and returns to Odoo home
  * There must be **no** requirement to use local Odoo passwords for SSO users

---

### 6.6 Image-Based CD (Image Deployment / `deploy/k8s/`)

* **Condition**
  * The DOKS workload actually runs your custom image with the baked-in modules, not `odoo:18.0`

* **Pass Criteria**
  * Odoo deployment spec uses:
    ```yaml
    image: ghcr.io/jgtolentino/odoo-ce:latest
    ```
  * From the cluster:
    ```bash
    kubectl get deploy odoo-deployment -n odoo-prod -o jsonpath='{.spec.template.spec.containers[0].image}'
    ```
    * Returns `ghcr.io/jgtolentino/odoo-ce:latest` (or `:sha` tag)
  * A new push of main triggers CI → new image → new pods with updated image digest (confirmed via `kubectl rollout status deployment/odoo-deployment -n odoo-prod` and image digest change)

---

## Completion Rule

* The deployment is considered **successful** only when:
  * **Infra conditions 1–5** are all met, **and**
  * **All feature checks in 6.1–6.6** pass (modules installed, WBS working, P2P flow correct, alerts firing, SSO working, and Odoo running your custom image)

---

## Deployment Path: A → Registry → B

### 1️⃣ A → Registry (build + push)

From your **odoo-ce repo root** (laptop or CI runner):
```bash
# From repo root where Dockerfile lives
export IMAGE=ghcr.io/jgtolentino/odoo-ce:latest

# 1. Login to GHCR (GHCR_PAT = GitHub PAT with `read:packages, write:packages`)
echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin

# 2. Build the custom Odoo 18 image with your addons baked in
docker build -t "$IMAGE" .

# 3. Push image A → GHCR
docker push "$IMAGE"
```

At this point **image A is in GHCR**.

### 2️⃣ Registry → B1 (DigitalOcean VPS with docker-compose.prod.yml)

On the **VPS** (`159.223.75.148`), where `docker-compose.prod.yml` already references `ghcr.io/jgtolentino/odoo-ce:latest`:
```bash
ssh ubuntu@159.223.75.148

cd ~/odoo-prod
git pull origin main

# Pull new image from GHCR
docker compose -f docker-compose.prod.yml pull odoo

# Restart Odoo using the freshly pulled image
docker compose -f docker-compose.prod.yml up -d
```

That's **image A now running as B (prod Odoo container)**.

### 3️⃣ Registry → B2 (DOKS / Kubernetes)

Assuming your **Odoo Deployment** in DOKS uses this image:
```yaml
# deploy/k8s/odoo-deployment.yaml (spec snippet)
containers:
  - name: odoo
    image: ghcr.io/jgtolentino/odoo-ce:latest
```

Apply or bump the image like this:
```bash
# Make sure kubeconfig for DOKS is set
doctl kubernetes cluster kubeconfig save <cluster-name>

# Option 1: Apply manifests (GitOps-style)
kubectl apply -f deploy/k8s/
kubectl rollout status deployment/odoo-deployment -n odoo-prod

# Option 2: Imperative image bump
kubectl set image deployment/odoo-deployment -n odoo-prod odoo=ghcr.io/jgtolentino/odoo-ce:latest
kubectl rollout status deployment/odoo-deployment -n odoo-prod
```

Now **the same image A** is running in **B = DOKS cluster**.

---

**Net-net:**

> **Build → push to `ghcr.io/jgtolentino/odoo-ce:latest` → `docker compose pull/up` on VPS or `kubectl set image/apply` on DOKS.**
> That's the full path from custom image A to running state B.
