# Docker Validation Guide
## InsightPulse ERP - DigitalOcean Best Practices

This guide follows DigitalOcean's recommendations for validating and deploying custom Odoo Docker images.

## 🏗️ Dockerfile Alignment Check

✅ **Our Dockerfile is perfectly aligned with DigitalOcean best practices:**

| **DigitalOcean Recommendation** | **Our Implementation** |
|--------------------------------|------------------------|
| Base image: `odoo:18.0` | ✅ `FROM odoo:18.0` |
| Copy custom modules | ✅ `COPY ./addons /mnt/extra-addons/` |
| Install system dependencies | ✅ `build-essential`, `libpq-dev`, `git`, `libssl-dev` |
| Run as non-root user | ✅ `USER odoo` |
| Clean package cache | ✅ `rm -rf /var/lib/apt/lists/*` |

## 🔍 Local Validation Steps

### Step 1: Build the Custom Image
```bash
# Build the custom Odoo image
docker build -t my-odoo:latest .

# Verify image was created successfully
docker images | grep my-odoo
```

### Step 2: Test the Image Locally
```bash
# Run the container locally (without database)
docker run -p 8069:8069 my-odoo:latest

# Expected output: Odoo starts and shows database connection error
# This confirms the image builds and Odoo starts correctly
```

### Step 3: Full Stack Test (Optional)
```bash
# Start complete stack with database
docker compose -f deploy/docker-compose.yml up -d

# Check all services are running
docker compose -f deploy/docker-compose.yml ps
```

## 🚀 Registry Deployment (DigitalOcean Container Registry)

### Step 1: Tag for DigitalOcean Registry
```bash
# Tag for DigitalOcean Container Registry
docker tag my-odoo:latest registry.digitalocean.com/<your-registry>/odoo:latest

# Verify tagging
docker images | grep registry.digitalocean.com
```

### Step 2: Push to Registry
```bash
# Login to DigitalOcean Registry
doctl registry login

# Push the image
docker push registry.digitalocean.com/<your-registry>/odoo:latest
```

### Step 3: Update Deployment Configuration
```bash
# Update docker-compose.prod.yml to use DigitalOcean image
sed -i 's|image: ghcr.io/jgtolentino/odoo-ce:latest|image: registry.digitalocean.com/<your-registry>/odoo:latest|g' deploy/docker-compose.prod.yml
```

## 🔧 GitHub Actions Automation

### Option A: GitHub Container Registry (Current)
```yaml
# Current workflow uses GitHub Container Registry
image: ghcr.io/jgtolentino/odoo-ce:latest
```

### Option B: DigitalOcean Container Registry (Enhanced)
```yaml
# Enhanced workflow for DigitalOcean Registry
- name: Build and Push to DigitalOcean Registry
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: |
      registry.digitalocean.com/<your-registry>/odoo:latest
      registry.digitalocean.com/<your-registry>/odoo:${{ github.sha }}
    username: ${{ secrets.DO_REGISTRY_USER }}
    password: ${{ secrets.DO_REGISTRY_TOKEN }}
```

## 🔒 Security Best Practices

### 1. Database Credentials
✅ **Current Approach:** Use environment variables in docker-compose
✅ **Kubernetes Approach:** Use Secrets for sensitive data

### 2. Non-Root User
✅ **Implemented:** `USER odoo` ensures security

### 3. Minimal Base Image
✅ **Using:** Official Odoo image with minimal additions

## 📊 Validation Checklist

### Image Build Validation
- [ ] Dockerfile builds without errors
- [ ] All custom modules copied correctly
- [ ] System dependencies installed
- [ ] Configuration file copied
- [ ] Proper user permissions set

### Runtime Validation
- [ ] Odoo starts successfully
- [ ] Custom modules load without errors
- [ ] Database connection works
- [ ] Health checks pass

### Registry Validation
- [ ] Image pushes to registry successfully
- [ ] Image pulls on target environment
- [ ] Deployment works with registry image

## 🛠️ Troubleshooting

### Common Issues

**1. Build Failures**
```bash
# Check Dockerfile syntax
docker build --no-cache -t test-image .

# Debug build process
docker build --progress=plain -t debug-image .
```

**2. Runtime Issues**
```bash
# Check container logs
docker logs <container_id>

# Inspect running container
docker exec -it <container_id> bash
```

**3. Registry Issues**
```bash
# Verify registry login
doctl registry login

# List registry images
doctl registry repository list
```

## 🎯 Next Steps

1. **Complete Local Validation**: Test the enhanced Dockerfile locally
2. **Choose Registry**: Decide between GitHub Container Registry vs DigitalOcean Container Registry
3. **Update CD Pipeline**: Modify GitHub Actions if switching to DigitalOcean Registry
4. **Deploy to Production**: Use the validated custom image in production

## 📈 Benefits Achieved

- **Immutable Infrastructure**: Consistent, versioned runtime environment
- **Faster Deployments**: Pre-built dependencies eliminate installation delays
- **Security**: Non-root user and minimal base image
- **Scalability**: Ready for Kubernetes deployment
- **Reproducibility**: Identical environment across development and production
