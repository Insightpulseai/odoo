# Final Deployment Runbook: Switching to Image-Based CD

This runbook documents the server-side steps to replace the legacy file-sync deployment with the new image-based continuous delivery pipeline for Odoo CE on the DigitalOcean VPS (`159.223.75.148`). Execute the steps sequentially on the droplet to pull the latest artifacts, start containers with the custom image, and apply database migrations.

## Prerequisites
- Latest changes (including `docker-compose.prod.yml` and the `Dockerfile`) are merged into `main` and published to the image registry.
- The droplet has a local clone of the repository at `~/odoo-prod/`.
- You have SSH access as `ubuntu` and permission to run `docker compose`.

## Step 1: Log In and Sync Documentation
```bash
# 1. SSH into the Droplet
ssh ubuntu@159.223.75.148

# 2. Navigate to the project root
cd ~/odoo-prod

# 3. Pull the latest repository changes (gets the new compose file)
git pull origin main
```

## Step 2: Activate the New Image-Based Pipeline
```bash
# Export environment variables for module updates and database selection
export ODOO_MODULES="ipai_finance_ppm,ipai_equipment,ipai_payment_payout"
export DB_NAME="odoo"

# Pull the latest Odoo image referenced by docker-compose.prod.yml
docker compose -f docker-compose.prod.yml pull odoo

# Restart the service to run with the newly pulled image
docker compose -f docker-compose.prod.yml up -d --force-recreate odoo
```

## Step 3: Apply Final Database Migrations
```bash
# Run schema updates inside the refreshed Odoo container
# (adjust DB_NAME/ODOO_MODULES if your environment differs)
docker compose -f docker-compose.prod.yml exec odoo odoo-bin -c /etc/odoo.conf \
    -d ${DB_NAME} -u ${ODOO_MODULES} --stop-after-init
```

## Final Verification
1. **Image Tag**: `docker ps` should show the Odoo container running `ghcr.io/jgtolentino/odoo-ce:latest` (or a `main` commit SHA tag).
2. **Functional Check**: Log into Odoo and confirm WBS Auto-Numbering still operates correctly after the image swap.
3. **Ingress/HTTPS**: If routed through Ingress, ensure the public endpoints return HTTP 200 over HTTPS.

Following these steps retires the file-sync workflow and fully activates the image-based CD pipeline.
