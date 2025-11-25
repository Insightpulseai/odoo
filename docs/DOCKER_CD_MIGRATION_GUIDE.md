# Docker Image-Based CD Migration Guide

## Overview

This guide documents the migration from file-based deployments to Docker image-based continuous deployment for your Odoo CE project.

## Migration Benefits

- **Faster Deployments**: No more `git pull` + manual module updates
- **Consistent Environments**: Eliminates "works on my machine" issues
- **Rollback Capability**: Can easily revert to previous image versions
- **Professional CD**: Matches enterprise deployment patterns
- **Atomic Updates**: Single image swap instead of multiple file changes

## New Architecture

### Before (File-Based)
```
GitHub → VPS (git pull) → Volume Mounts → Odoo Container
```

### After (Image-Based)
```
GitHub → Build Image → Push to Registry → VPS (pull image) → Odoo Container
```

## Files Created

1. **`Dockerfile`** - Custom Odoo image with baked-in modules
2. **`.github/workflows/deploy.yml`** - CD pipeline for building and deploying
3. **`deploy/docker-compose.prod.yml`** - Production template using custom image

## Migration Steps

### Step 1: Prepare GitHub Secrets

Ensure these secrets are configured in your GitHub repository:

- `PROD_HOST` - Your VPS IP (159.223.75.148)
- `PROD_USER` - SSH username
- `PROD_SSH_KEY` - SSH private key
- `GITHUB_TOKEN` - Built-in (automatically available)

### Step 2: Update VPS Configuration

On your VPS (`~/odoo-prod/`), update the docker-compose file:

```bash
# Backup current setup
cp docker-compose.yml docker-compose.yml.backup

# Update to use custom image
# Replace the 'image: odoo:18.0' line with:
# image: ghcr.io/jgtolentino/odoo-ce:latest

# Remove volume mounts for custom modules (commented out in template)
```

### Step 3: First Deployment

1. **Commit the new files** to your `main` branch
2. **GitHub Actions will automatically**:
   - Build the custom Docker image
   - Push it to GitHub Container Registry
   - Deploy to your VPS
   - Apply database migrations

### Step 4: Verify Deployment

Check that the deployment was successful:

```bash
# On VPS
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs odoo

# Check custom modules are working
# Access Odoo and verify ipai_finance_ppm module functionality
```

## Rollback Procedure

If issues occur, you can rollback to a previous image:

```bash
# On VPS - check available images
docker images | grep ghcr.io/jgtolentino/odoo-ce

# Rollback to specific commit SHA
docker compose -f docker-compose.prod.yml stop odoo
docker compose -f docker-compose.prod.yml up -d --image ghcr.io/jgtolentino/odoo-ce:COMMIT_SHA
```

## Custom Modules Included

The Docker image includes these custom modules:
- `ipai_finance_ppm` - Finance Project Portfolio Management
- `ipai_finance_ppm_dashboard` - PPM Dashboard
- `ipai_ppm_monthly_close` - Monthly Close Automation
- `tbwa_spectra_integration` - TBWA Spectra Integration
- `flutter_receipt_ocr` - Receipt OCR
- `ipai_ce_cleaner` - CE Cleanup Tools
- `ipai_docs` - Documentation Management
- `ipai_docs_project` - Project Documentation

## Database Migration

The CD workflow automatically applies database migrations:

```bash
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
```

## Monitoring & Troubleshooting

### Health Checks
- GitHub Actions workflow status
- Docker container health checks
- Odoo application health endpoint

### Common Issues

1. **Image Build Failures**
   - Check Dockerfile syntax
   - Verify module dependencies

2. **Deployment Failures**
   - Check SSH connectivity
   - Verify GitHub Container Registry access
   - Check database connectivity

3. **Module Issues**
   - Verify module installation in Odoo
   - Check database migration logs

## Security Considerations

- GitHub Container Registry authentication
- Secure SSH key management
- Database password handling
- Image scanning for vulnerabilities

## Future Enhancements

- Multi-stage builds for smaller images
- Automated testing in CI pipeline
- Blue-green deployment strategy
- Database backup before migrations
- Health checks and auto-rollback

## Support

For issues with the CD pipeline:
1. Check GitHub Actions logs
2. Verify VPS Docker logs
3. Review Odoo application logs
4. Check database migration status
