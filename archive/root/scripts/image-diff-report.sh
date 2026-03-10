#!/usr/bin/env bash
# =============================================================================
# Docker Image Diff Report Generator
# =============================================================================
# Purpose: Compare custom image vs base image (filesystem, packages, SBOM, vulns)
# Usage:
#   ./scripts/image-diff-report.sh <base-tag> <custom-tag>
#
# Example:
#   ./scripts/image-diff-report.sh odoo:18.0 erp-saas:2.0
#
# Dependencies (install first):
#   brew install container-diff syft grype
#
# Output: image_audit.tgz (complete diff report bundle)
# =============================================================================

set -euo pipefail

BASE_TAG="${1:-odoo:18.0}"
CUSTOM_TAG="${2:-erp-saas:2.0}"

echo "=========================================="
echo "Docker Image Diff Report"
echo "=========================================="
echo "Base:   $BASE_TAG"
echo "Custom: $CUSTOM_TAG"
echo ""

# Check dependencies
command -v container-diff >/dev/null 2>&1 || {
  echo "ERROR: container-diff not found"
  echo "Install: brew install container-diff"
  exit 1
}

command -v syft >/dev/null 2>&1 || {
  echo "ERROR: syft not found"
  echo "Install: brew install syft"
  exit 1
}

command -v grype >/dev/null 2>&1 || {
  echo "ERROR: grype not found"
  echo "Install: brew install grype"
  exit 1
}

# Create output directory
mkdir -p image_audit
cd image_audit

# =============================================================================
# 1. Filesystem/Package Diff (container-diff)
# =============================================================================
echo "1/5 Running filesystem and package diff..."
container-diff diff \
  daemon://"$BASE_TAG" daemon://"$CUSTOM_TAG" \
  --type=file --type=apt --type=pip \
  --json > image-diff.json

echo "    ✓ Saved: image-diff.json"

# =============================================================================
# 2. SBOM Generation (syft)
# =============================================================================
echo "2/5 Generating SBOMs..."
syft "$BASE_TAG" -o json > sbom.base.json
syft "$CUSTOM_TAG" -o json > sbom.custom.json

echo "    ✓ Saved: sbom.base.json"
echo "    ✓ Saved: sbom.custom.json"

# =============================================================================
# 3. Vulnerability Scans (grype)
# =============================================================================
echo "3/5 Running vulnerability scans..."
grype "$BASE_TAG" -o json > vulns.base.json
grype "$CUSTOM_TAG" -o json > vulns.custom.json

echo "    ✓ Saved: vulns.base.json"
echo "    ✓ Saved: vulns.custom.json"

# =============================================================================
# 4. Layer History Diff
# =============================================================================
echo "4/5 Comparing image layers..."
docker history --no-trunc "$BASE_TAG" > history.base.txt
docker history --no-trunc "$CUSTOM_TAG" > history.custom.txt

diff -u history.base.txt history.custom.txt > history.diff.txt || true

echo "    ✓ Saved: history.base.txt"
echo "    ✓ Saved: history.custom.txt"
echo "    ✓ Saved: history.diff.txt"

# =============================================================================
# 5. Generate Summary Report
# =============================================================================
echo "5/5 Generating summary report..."

BASE_VULNS=$(jq '.matches | length' vulns.base.json)
CUSTOM_VULNS=$(jq '.matches | length' vulns.custom.json)
VULN_DELTA=$((CUSTOM_VULNS - BASE_VULNS))

BASE_PACKAGES=$(jq '.artifacts | length' sbom.base.json)
CUSTOM_PACKAGES=$(jq '.artifacts | length' sbom.custom.json)
PKG_DELTA=$((CUSTOM_PACKAGES - BASE_PACKAGES))

cat > SUMMARY.txt <<EOF
========================================
Docker Image Diff Report Summary
========================================
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

Base Image:   $BASE_TAG
Custom Image: $CUSTOM_TAG

========================================
Vulnerability Comparison
========================================
Base vulnerabilities:   $BASE_VULNS
Custom vulnerabilities: $CUSTOM_VULNS
Delta:                  $VULN_DELTA ($(if [ $VULN_DELTA -gt 0 ]; then echo "+"; fi)$VULN_DELTA)

========================================
Package Comparison
========================================
Base packages:   $BASE_PACKAGES
Custom packages: $CUSTOM_PACKAGES
Delta:           $PKG_DELTA packages

========================================
Files Generated
========================================
- image-diff.json       Filesystem + package diff
- sbom.base.json        Base image SBOM
- sbom.custom.json      Custom image SBOM
- vulns.base.json       Base image vulnerabilities
- vulns.custom.json     Custom image vulnerabilities
- history.base.txt      Base image layer history
- history.custom.txt    Custom image layer history
- history.diff.txt      Layer history diff
- SUMMARY.txt           This summary

========================================
Next Steps
========================================
1. Review SUMMARY.txt for high-level changes
2. Check vulns.custom.json for critical vulnerabilities
3. Inspect image-diff.json for unexpected file changes
4. Compare SBOM files for package version drift
5. Archive bundle: tar -czf image_audit.tgz image_audit/

See: https://docs.docker.com/dhi/about/what/ for DHI baseline info
========================================
EOF

echo "    ✓ Saved: SUMMARY.txt"

# =============================================================================
# Bundle Report
# =============================================================================
cd ..
tar -czf image_audit.tgz image_audit

echo ""
echo "=========================================="
echo "Report Complete!"
echo "=========================================="
echo ""
cat image_audit/SUMMARY.txt
echo ""
echo "Archive: $(pwd)/image_audit.tgz ($(du -h image_audit.tgz | cut -f1))"
echo ""
