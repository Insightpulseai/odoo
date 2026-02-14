# Infrastructure WAF Remediation Runbook

This runbook provides step-by-step instructions to remediate common failures identified by the Infrastructure Well-Architected Assessment.

## Reliability Failures

### `docker_restart_policy` Check Failed

**Issue:** Services are missing `restart: always` or `unless-stopped`.
**Fix:**

1. Open `infra/docker-compose.prod.yaml`.
2. Add `restart: unless-stopped` to the failing service.

```yaml
services:
  web:
    image: nginx
    restart: unless-stopped # <--- Add this
```

### `docker_healthchecks` Check Failed

**Issue:** Exposed services do not have a healthcheck.
**Fix:**

1. Define a healthcheck in `docker-compose.prod.yaml`.

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Security Failures

### `no_hardcoded_secrets_compose` Check Failed

**Issue:** Secrets detected in `docker-compose.prod.yaml`.
**Fix:**

1. Move the secret to `.env` file (not committed) or GitHub Secrets.
2. Reference it in compose:

```yaml
environment:
  - DB_PASSWORD=${DB_PASSWORD} # <--- Use variable
```

### `cloudflare_proxy_enabled` Check Failed

**Issue:** Terraform does not explicitly show Cloudflare proxy enabled.
**Fix:**

1. Ensure your Terraform `cloudflare_record` resources have `proxied = true`.

```hcl
resource "cloudflare_record" "www" {
  name    = "www"
  value   = "192.0.2.1"
  type    = "A"
  proxied = true # <--- Ensure this is true
}
```

## Operational Excellence Failures

### `logging_driver_configured` Check Failed

**Issue:** Docker logging is not configured to rotate logs (risk of disk fill).
**Fix:**

1. Configure `json-file` driver with limits.

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### `image_tags_pinned` Check Failed

**Issue:** Using `latest` tag is unpredictable.
**Fix:**

1. Use a specific version tag.

```yaml
image: odoo:16.0-20231005 # <--- Specific tag
# image: odoo:latest   # <--- AVOID
```
