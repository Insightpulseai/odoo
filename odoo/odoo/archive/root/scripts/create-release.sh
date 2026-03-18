#!/bin/bash
# =============================================================================
# Create Semantic Version Release
# =============================================================================
# Usage:
#   ./scripts/create-release.sh 1.2.0 "Docker Unified Build with Profile Support"
#
# What it does:
#   1. Validates version format (semantic)
#   2. Creates annotated git tag
#   3. Pushes tag to origin (triggers CI builds)
#   4. Creates GitHub Release
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
VERSION="${1:-}"
TITLE="${2:-}"

if [[ -z "$VERSION" ]]; then
  echo "❌ Error: Version required"
  echo "Usage: $0 <version> <title>"
  echo "Example: $0 1.2.0 'Docker Unified Build'"
  exit 1
fi

if [[ -z "$TITLE" ]]; then
  echo "❌ Error: Release title required"
  echo "Usage: $0 <version> <title>"
  echo "Example: $0 1.2.0 'Docker Unified Build'"
  exit 1
fi

# Validate semantic version format
if ! echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "❌ Error: Invalid semantic version format"
  echo "Expected: MAJOR.MINOR.PATCH (e.g., 1.2.0)"
  echo "Got: $VERSION"
  exit 1
fi

TAG="v$VERSION"

# -----------------------------------------------------------------------------
# Pre-flight Checks
# -----------------------------------------------------------------------------
echo "🔍 Pre-flight checks..."

# Check if on main branch
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" ]]; then
  echo "⚠️  Warning: Not on main branch (current: $BRANCH)"
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check if working tree is clean
if ! git diff-index --quiet HEAD --; then
  echo "❌ Error: Working tree not clean"
  echo "Commit or stash changes before creating release"
  exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$TAG$"; then
  echo "❌ Error: Tag $TAG already exists"
  exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# -----------------------------------------------------------------------------
# Create Git Tag
# -----------------------------------------------------------------------------
echo "🏷️  Creating git tag: $TAG"

git tag -a "$TAG" -m "Release $TAG: $TITLE

Automated release created by create-release.sh

Docker Images:
- ghcr.io/jgtolentino/odoo-ce:$VERSION-standard
- ghcr.io/jgtolentino/odoo-ce:$VERSION-parity

Convenience Aliases:
- ghcr.io/jgtolentino/odoo-ce:${VERSION%.*}-standard
- ghcr.io/jgtolentino/odoo-ce:${VERSION%%.*}-standard
- ghcr.io/jgtolentino/odoo-ce:latest-standard

See docs/TAGGING_STRATEGY.md for details.
"

# -----------------------------------------------------------------------------
# Push Tag (Triggers CI)
# -----------------------------------------------------------------------------
echo "🚀 Pushing tag to origin (triggers CI builds)..."
git push origin "$TAG"

echo ""
echo "✅ Tag created and pushed successfully!"
echo ""
echo "📊 Monitor CI builds:"
echo "   gh run list --workflow=build-unified-image.yml --limit 5"
echo "   gh run watch"
echo ""
echo "🎉 After CI completes, create GitHub Release:"
echo "   gh release create $TAG \\"
echo "     --title \"$TAG - $TITLE\" \\"
echo "     --generate-notes \\"
echo "     --latest"
echo ""
echo "📦 Docker images will be available at:"
echo "   ghcr.io/jgtolentino/odoo-ce:$VERSION-standard"
echo "   ghcr.io/jgtolentino/odoo-ce:$VERSION-parity"
echo ""
