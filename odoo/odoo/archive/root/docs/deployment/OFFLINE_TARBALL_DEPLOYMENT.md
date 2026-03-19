# Offline/Tarball Deployment Path

Use this workflow when the target host cannot pull from GitHub Container Registry (GHCR) or when you need an offline artifact for audit/backup.

## 1) Build and Package the Image Locally

Run the helper script from the repository root. Override `IMAGE_NAME` or `OUTPUT_TARBALL` if you need a different tag or filename.

```bash
IMAGE_NAME=ghcr.io/jgtolentino/odoo:latest \
OUTPUT_TARBALL=odoo-latest.tar.gz \
./scripts/package_image_tarball.sh
```

This will:
- Build the image locally using the project `Dockerfile`.
- Save it as a compressed tarball (`OUTPUT_TARBALL`).

## 2) Transfer the Tarball to the Target Host

Use any file transfer mechanism (e.g., `scp`, SFTP). Example with `scp`:

```bash
scp odoo-latest.tar.gz <user>@<host>:/opt/odoo/
```

## 3) Load and Run the Image on the Target Host

On the host, load the image and restart the Odoo service using the existing compose file.

```bash
ssh <user>@<host>
cd /opt/odoo

# Load the image into the local Docker cache
docker load < odoo-latest.tar.gz

# Recreate the Odoo container with the freshly loaded image
docker compose -f docker-compose.prod.yml up -d odoo
```

Optional: remove the tarball after successful deployment to free disk space.

```bash
rm odoo-latest.tar.gz
```
