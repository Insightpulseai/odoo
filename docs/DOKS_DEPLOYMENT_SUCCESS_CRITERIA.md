# DOKS Deployment Success Criteria Specification

This specification defines the measurable signals that confirm the DigitalOcean Kubernetes (DOKS) deployment of Odoo CE is production-ready for the Finance team. Each criterion is paired with a verification command so the automation pipeline can gate progression based on objective outcomes.

## 1. Infrastructure Provisioning (`doctl` CLI)

| Action / Component | Success Metric | Verification Command (`doctl`) |
| --- | --- | --- |
| **Cluster Creation** | Command exits with code `0` and the cluster `status` becomes `running`. | `doctl kubernetes cluster create ...` |
| **Cluster Health** | All node pools are `active` and `ready`; control plane responds to API calls. | `doctl kubernetes cluster list` |
| **Image Registry Link** | GHCR registry credentials allow successful image pulls by cluster service accounts. | Confirmed via successful pod image pulls (see Odoo pod logs). |

## 2. Core Components Deployment (`kubectl` & Manifests)

| Component | Manifest Type | Success Metric (State) | Verification Command (`kubectl`) |
| --- | --- | --- | --- |
| **PostgreSQL** | StatefulSet | Pods show `Running` and `Ready` (e.g., `1/1`); PVCs show `Bound`. | `kubectl get pods -l app=postgres`<br>`kubectl get pvc` |
| **Odoo / Keycloak** | Deployment | All replicas are `Ready` and `Available`; liveness probes succeed. | `kubectl get deployments`<br>`kubectl describe deployment odoo` |
| **Odoo Config** | ConfigMap | Required files (for example, `odoo.conf`) mount at `/etc/odoo` in Odoo pods. | `kubectl describe pod odoo-xxx`<br>`kubectl exec odoo-xxx -- cat /etc/odoo/odoo.conf` |

## 3. External Access & Functional Parity (Ingress & Application)

| Action / Endpoint | Success Metric | Verification Tool |
| --- | --- | --- |
| **Ingress Controller** | Ingress service receives a public IP address. | `kubectl get ingress odoo-ingress` |
| **SSL/HTTPS Access** | `https://erp.insightpulseai.net/` returns HTTP status `200` over HTTPS. | `curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/` |
| **Odoo Functional Check** | Odoo logs show a healthy database connection during startup/initialization. | Review Odoo pod startup logs. |
| **Keycloak Functional Check** | Admin console login screen responds via `https://auth.insightpulseai.net/admin`. | `curl -s -o /dev/null -w "%{http_code}" https://auth.insightpulseai.net/admin` |

## Completion Rule

The deployment is considered successful when all checks in Section 3 pass in succession after the core components are healthy. Automation should fail fast on any unmet criterion to prevent partial rollouts.
