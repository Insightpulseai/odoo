# InsightPulse ERP Configuration Guide

## Overview
This guide provides comprehensive configuration settings for the InsightPulse ERP stack, covering both UI settings and CLI updates for automation and emergency access.

---

## Part 1: UI Configuration Settings

### A. System Parameters (Technical Secrets)
**Location:** Settings → Technical → System Parameters

| Key | Value (Example) | Purpose |
| :--- | :--- | :--- |
| `ai.ocr.api.key` | `sk-proj-123...` | OpenAI Key for Receipt Scanning |
| `ocr.service.endpoint` | `http://ocr.insightpulseai.net/predict` | URL of custom PaddleOCR droplet |
| `ocr.service.token` | `my-secure-token` | Security token for OCR droplet |
| `payout.n8n.webhook` | `https://n8n.insightpulseai.net/webhook/payout` | URL for Mass Payment triggering |
| `payout.n8n.secret` | `pulse-secret-888` | Security header for Odoo requests |
| `web.base.url` | `https://erp.insightpulseai.net` | **Crucial** - Ensures email links work |

### B. Payment Providers (Incoming Money)
**Location:** Invoicing → Configuration → Payment Providers

| Setting | Value |
| :--- | :--- |
| **Provider** | Stripe |
| **State** | Test Mode (until ready) |
| **Publishable Key** | `pk_test_...` (From Stripe Dashboard) |
| **Secret Key** | `sk_test_...` (From Stripe Dashboard) |
| **Webhook Secret** | `whsec_...` (From Stripe Dashboard) |

### C. Identity / SSO (Keycloak)
**Location:** Settings → Users & Companies → OAuth Providers
*(Requires `auth_oidc` module)*

| Setting | Value |
| :--- | :--- |
| **Provider Name** | Keycloak |
| **Client ID** | `odoo` |
| **Auth URL** | `https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth` |
| **Scope** | `openid profile email` |

---

## Part 2: CLI Configuration Updates (Emergency/Automation)

### A. Access Odoo Shell
```bash
cd ~/odoo-prod
docker compose -f docker-compose.prod.yml exec odoo odoo-bin shell -c /etc/odoo.conf -d odoo
```

### B. Update System Parameters via CLI
```python
# In the Odoo shell
env['ir.config_parameter'].set_param('ai.ocr.api.key', 'new-sk-key-here')
env.cr.commit()  # IMPORTANT: Save changes
```

### C. Emergency User Password Reset
```python
# In the Odoo shell
admin = env['res.users'].search([('login', '=', 'admin')])
admin.password = 'new_emergency_password'
env.cr.commit()
```

### D. Exit Shell
Type `CTRL+D` to exit the shell.

---

## Part 3: Infrastructure Configuration (File-Based)

### A. Odoo Server Config (`odoo.conf`)
**Location:** `~/odoo-prod/config/odoo.conf`
**Update Command:** `nano config/odoo.conf`

| Setting | Purpose | Recommended Value |
| :--- | :--- | :--- |
| `admin_passwd` | Master password for DB management | **Complex String** (Do not lose this) |
| `workers` | CPU threads | `5` (Formula: 2 * Cores + 1) |
| `limit_memory_hard` | Max RAM before kill | `2684354560` (2.5GB) |
| `limit_time_cpu` | Max request time | `120` (Increase if reports timeout) |

### B. Docker Environment (`docker-compose.prod.yml`)
**Location:** `~/odoo-prod/docker-compose.prod.yml`
**Update Command:** `nano docker-compose.prod.yml`

| Variable | Purpose | Location in File |
| :--- | :--- | :--- |
| `POSTGRES_PASSWORD` | Database access | Under `db:` and `odoo:` services |
| `Host(...)` | Domain routing | Under `labels:` (Traefik section) |
| `KC_DB_PASSWORD` | Keycloak DB access | Under `keycloak:` service |

### C. Apply Infrastructure Changes
After editing any file in Part 3, restart the specific container:

```bash
# Apply Odoo Config Changes
docker compose -f docker-compose.prod.yml restart odoo

# Apply Database/Network Changes (Recreates container)
docker compose -f docker-compose.prod.yml up -d
```

---

## Part 4: Database Configuration

### A. PostgreSQL Connection Parameters
```python
# For scripts and applications
conn = psycopg2.connect(
    host="localhost",  # or "odoo-db-1" within Docker network
    database="odoo",
    user="odoo",
    password="odoo",  # Current production password
    port=5432
)
```

### B. Database Verification
```bash
# Test database connectivity
docker exec odoo-db-1 psql -U odoo -d odoo -c 'SELECT current_database(), current_user;'
```

---

## Part 5: GitHub Actions Configuration

### A. Required Secrets
**Repository Settings → Secrets and variables → Actions**

| Secret Name | Value | Purpose |
| :--- | :--- | :--- |
| `PROD_HOST` | `159.223.75.148` | Production server IP |
| `PROD_USER` | `ubuntu` | SSH username |
| `PROD_SSH_KEY` | `[private key content]` | SSH private key |
| `POSTGRES_PASSWORD` | `odoo` | Database password |

### B. Deployment Workflow
- **File:** `.github/workflows/deploy_prod.yml`
- **Trigger:** Push to `main` branch with module changes
- **Actions:** Code update, module migration, service restart

---

## Part 6: Security Recommendations

### A. Password Security
- Change `POSTGRES_PASSWORD` from default `odoo` for production
- Use strong, unique passwords for all services
- Rotate API keys regularly

### B. Access Control
- Limit admin access to trusted users
- Use SSO (Keycloak) for centralized authentication
- Implement proper user roles and permissions

### C. Monitoring
- Set up health checks for all services
- Monitor database connections and performance
- Implement backup and recovery procedures

---

## Part 7: Troubleshooting

### A. Common Issues
1. **Database Connection Failed**
   - Check container status: `docker ps -a | grep postgres`
   - Verify password: `docker inspect odoo-db-1 | grep POSTGRES_PASSWORD`
   - Test connectivity: `docker exec odoo-db-1 psql -U odoo -d odoo -c 'SELECT version();'`

2. **UI Settings Not Saving**
   - Use CLI method for emergency updates
   - Check user permissions
   - Verify database connectivity

3. **Deployment Failures**
   - Check GitHub secrets configuration
   - Verify SSH access to production server
   - Review deployment logs

### B. Emergency Procedures
1. **Locked Out of Admin**
   - Use CLI password reset procedure
   - Access Odoo shell via Docker exec

2. **Database Issues**
   - Check container health status
   - Verify environment variables
   - Restart database container if needed

---

## Quick Reference Commands

```bash
# Database access
docker exec odoo-db-1 psql -U odoo -d odoo

# Odoo shell access
docker compose -f docker-compose.prod.yml exec odoo odoo-bin shell -c /etc/odoo.conf -d odoo

# Restart services
docker compose -f docker-compose.prod.yml restart odoo
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs odoo
docker compose -f docker-compose.prod.yml logs db
```

This guide provides a complete reference for configuring and maintaining the InsightPulse ERP stack across all environments.
