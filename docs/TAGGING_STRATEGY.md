# Docker Image Tagging Strategy

## Overview

This project uses **semantic versioning** for git tags and **profile-based Docker image tags** for deployment flexibility.

**Registry**: `ghcr.io/jgtolentino/odoo-ce`

---

## Tag Types

### 1. Release Tags (Immutable)

Created from git tags `v*.*.*` (e.g., `v1.2.0`):

```
ghcr.io/jgtolentino/odoo-ce:1.2.0-standard
ghcr.io/jgtolentino/odoo-ce:1.2.0-parity
ghcr.io/jgtolentino/odoo-ce:1.2.0-dev
```

**Guarantees**:
- ✅ Immutable (never changes)
- ✅ 1:1 mapping with git tag
- ✅ Reproducible builds
- ✅ Safe for production pinning

### 2. Convenience Aliases (Moving Pointers)

```
# Minor version pointer (1.2.x → 1.2-standard)
ghcr.io/jgtolentino/odoo-ce:1.2-standard
ghcr.io/jgtolentino/odoo-ce:1.2-parity

# Major version pointer (1.x.x → 1-standard)
ghcr.io/jgtolentino/odoo-ce:1-standard
ghcr.io/jgtolentino/odoo-ce:1-parity
```

**Use case**: Pin to minor/major version, get patch updates automatically

### 3. Latest (Production Canonical)

```
# Standard profile is canonical production
ghcr.io/jgtolentino/odoo-ce:latest-standard  (DEFAULT)
ghcr.io/jgtolentino/odoo-ce:latest-parity    (legacy compatibility)
```

**Use case**: Always get the latest stable release for a profile

### 4. Edge Channel (Main Branch)

```
# Built on every push to main (never called "latest")
ghcr.io/jgtolentino/odoo-ce:edge-standard
ghcr.io/jgtolentino/odoo-ce:edge-parity

# SHA-specific edge builds
ghcr.io/jgtolentino/odoo-ce:sha-abc1234-standard
ghcr.io/jgtolentino/odoo-ce:sha-def5678-parity
```

**Use case**: Testing unreleased changes, CI/CD validation

---

## Profile Definitions

### `standard` (Production Default)

**Includes**:
- Odoo CE 18.0 base
- OCA essentials (14 repositories)
- 5-module IPAI architecture:
  - `ipai_workspace_core` - Shared knowledge primitives
  - `ipai_ppm` - Project portfolio management
  - `ipai_advisor` - Recommendation engine
  - `ipai_workbooks` - Analytics documentation
  - `ipai_connectors` - IPAI stack integrations

**Image size**: ~1.8 GB
**Use case**: New deployments, minimal footprint, fast builds

### `parity` (Enterprise Feature Set)

**Includes**:
- Everything in `standard`
- OCA extended (32 repositories)
- Legacy IPAI modules (27 total)
- Enterprise SaaS parity modules:
  - `ipai_assets` - Cheqroom-style equipment management
  - `ipai_srm` - SAP SRM supplier relationship management

**Image size**: ~2.4 GB
**Use case**: Existing deployments, full feature set, enterprise parity

### `dev` (Development Tools)

**Includes**:
- Everything in `parity`
- Development dependencies (debugpy, pytest, ipython)
- Test data and fixtures
- Debug-enabled Odoo configuration

**Image size**: ~2.6 GB
**Use case**: Local development, debugging, test environments

---

## Usage Examples

### Production Deployment (Recommended)

```bash
# Pin to specific release (immutable)
docker pull ghcr.io/jgtolentino/odoo-ce:1.2.0-standard

# Or use latest stable (moving pointer)
docker pull ghcr.io/jgtolentino/odoo-ce:latest-standard
```

### Docker Compose

```yaml
version: "3.9"

services:
  odoo:
    # RECOMMENDED: Pin to specific release
    image: ghcr.io/jgtolentino/odoo-ce:1.2.0-standard

    # ALTERNATIVE: Use latest stable (auto-updates on restart)
    # image: ghcr.io/jgtolentino/odoo-ce:latest-standard

    # TESTING ONLY: Edge builds (main branch)
    # image: ghcr.io/jgtolentino/odoo-ce:edge-standard
```

### Development/Testing

```bash
# Test latest main branch build
docker pull ghcr.io/jgtolentino/odoo-ce:edge-standard

# Test specific commit
docker pull ghcr.io/jgtolentino/odoo-ce:sha-abc1234-standard

# Development environment
docker pull ghcr.io/jgtolentino/odoo-ce:1.2.0-dev
```

---

## Creating a New Release

### 1. Prepare Release

```bash
# Ensure main branch is clean and up-to-date
git checkout main
git pull origin main
git status  # Should be clean

# Review changes since last release
git log v1.1.0..HEAD --oneline
```

### 2. Create Git Tag

```bash
# Create annotated tag (semantic version)
git tag -a v1.2.0 -m "Release v1.2.0: Docker Unified Build with Profile Support

- Unified Dockerfile with PROFILE arg (standard/parity/dev)
- 5-module IPAI architecture for standard profile
- Enterprise parity modules (ipai_assets, ipai_srm)
- ADR-0001: Clone SaaS UX natively (no integrations)
- Production-ready Docker builds with OCI labels
"

# Push tag to trigger builds
git push origin v1.2.0
```

### 3. Monitor CI Build

```bash
# GitHub Actions will automatically:
# 1. Build standard profile: ghcr.io/jgtolentino/odoo-ce:1.2.0-standard
# 2. Build parity profile: ghcr.io/jgtolentino/odoo-ce:1.2.0-parity
# 3. Create convenience aliases: 1.2-standard, 1-standard
# 4. Update latest-standard pointer

# Watch build progress
gh run list --workflow=build-unified-image.yml --limit 5
gh run watch
```

### 4. Create GitHub Release

```bash
# Create GitHub Release from tag
gh release create v1.2.0 \
  --title "v1.2.0 - Docker Unified Build" \
  --notes "See CHANGELOG.md for details" \
  --latest
```

---

## Image Inspection

### View OCI Labels

```bash
docker pull ghcr.io/jgtolentino/odoo-ce:1.2.0-standard
docker inspect ghcr.io/jgtolentino/odoo-ce:1.2.0-standard --format '{{json .Config.Labels}}' | jq
```

**Expected labels**:
```json
{
  "org.opencontainers.image.title": "InsightPulse Odoo CE (standard)",
  "org.opencontainers.image.description": "Odoo 18 CE + OCA + IPAI Modules",
  "org.opencontainers.image.vendor": "InsightPulse AI",
  "org.opencontainers.image.version": "1.2.0",
  "org.opencontainers.image.revision": "abc1234567...",
  "com.insightpulseai.profile": "standard",
  "com.insightpulseai.odoo.version": "18.0",
  "com.insightpulseai.build.git-sha": "abc1234567..."
}
```

### Verify Image Size

```bash
docker images ghcr.io/jgtolentino/odoo-ce --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

---

## Migration from Old Tags

### Old Tag Style (Deprecated)

```
❌ v0.5.0-saas-parity          (milestone + feature)
❌ v1.1.0-sso-integration      (version + feature)
❌ v2025-q4-close-final        (calendar + milestone)
```

### New Tag Style (Current)

```
✅ v1.2.0                      (semantic version only)
   └─ Images: 1.2.0-standard, 1.2.0-parity, 1.2.0-dev
```

### Migration Path

**Existing tags**: Keep for historical reference, no deletion
**New releases**: Use semantic versioning only (`v1.2.0`, `v1.3.0`, etc.)
**Release titles**: Use GitHub Release title for descriptive names

---

## Troubleshooting

### Image Pull Fails

```bash
# Verify tag exists
gh api /orgs/jgtolentino/packages/container/odoo-ce/versions | jq -r '.[] | .metadata.container.tags[]' | sort

# Check authentication
echo $GITHUB_TOKEN | docker login ghcr.io -u jgtolentino --password-stdin
```

### Wrong Profile Deployed

```bash
# Check running container labels
docker inspect <container-id> --format '{{index .Config.Labels "com.insightpulseai.profile"}}'

# Should return: "standard" or "parity"
```

### Edge Build Not Found

```bash
# Edge builds only created on main branch push
# Check if workflow ran
gh run list --workflow=build-unified-image.yml --branch=main --limit 5
```

---

## References

- [ADR-0001: Clone Not Integrate](../docs/adr/ADR-0001-clone-not-integrate.md)
- [Docker Unified Dockerfile](../docker/Dockerfile.unified)
- [GitHub Workflow](../.github/workflows/build-unified-image.yml)
- [OCI Image Spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
