#!/usr/bin/env bash
# Weekly check for OCA rest-framework 19.0 migration readiness

set -euo pipefail

echo "=========================================="
echo "OCA REST Framework 19.0 Migration Check"
echo "=========================================="
echo ""

# Check component module availability
echo "1. Checking component module in OCA/connector:19.0..."
COMPONENT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  https://github.com/OCA/connector/tree/19.0/component)

if [ "$COMPONENT_STATUS" == "200" ]; then
  echo "   ✅ component module available in connector:19.0"
  COMPONENT_READY=1
else
  echo "   ❌ component module not yet migrated (HTTP $COMPONENT_STATUS)"
  COMPONENT_READY=0
fi

echo ""

# Check base_rest version
echo "2. Checking base_rest version..."
BASE_REST_VERSION=$(curl -s \
  https://raw.githubusercontent.com/OCA/rest-framework/19.0/base_rest/__manifest__.py \
  | grep '"version"' | head -1 | cut -d'"' -f4)

echo "   📦 base_rest version: $BASE_REST_VERSION"

if echo "$BASE_REST_VERSION" | grep -q "^19\.0"; then
  echo "   ✅ base_rest version bumped to 19.0.x"
  VERSION_READY=1
else
  echo "   ❌ base_rest still at 18.0.x (not ready)"
  VERSION_READY=0
fi

echo ""

# Check installable flag
echo "3. Checking base_rest installable flag..."
INSTALLABLE=$(curl -s \
  https://raw.githubusercontent.com/OCA/rest-framework/19.0/base_rest/__manifest__.py \
  | grep '"installable"' | head -1)

echo "   📄 $INSTALLABLE"

if echo "$INSTALLABLE" | grep -q "True"; then
  echo "   ✅ base_rest marked as installable"
  INSTALLABLE_READY=1
else
  echo "   ❌ base_rest still marked as not installable"
  INSTALLABLE_READY=0
fi

echo ""
echo "=========================================="
echo "Migration Readiness Summary"
echo "=========================================="

if [ $COMPONENT_READY -eq 1 ] && [ $VERSION_READY -eq 1 ] && [ $INSTALLABLE_READY -eq 1 ]; then
  echo "✅ ALL CRITERIA MET - MIGRATION READY!"
  echo ""
  echo "Next steps:"
  echo "1. Re-aggregate OCA repos: git-aggregator -c oca-aggregate.yml"
  echo "2. Verify local versions: grep version addons/oca/rest-framework/base_rest/__manifest__.py"
  echo "3. Install base_rest: scripts/odoo/install_modules_chunked.sh odoo base_rest,base_rest_datamodel 2"
  echo "4. Migrate from ipai_rest_controllers (see docs/architecture/rest_migration_plan.md)"
  exit 0
else
  echo "⏳ Migration not yet ready. Criteria status:"
  echo "   - Component module available: $([ $COMPONENT_READY -eq 1 ] && echo '✅' || echo '❌')"
  echo "   - Version bumped to 19.0: $([ $VERSION_READY -eq 1 ] && echo '✅' || echo '❌')"
  echo "   - Marked as installable: $([ $INSTALLABLE_READY -eq 1 ] && echo '✅' || echo '❌')"
  echo ""
  echo "Check again next week or monitor:"
  echo "   - https://github.com/OCA/connector/pulls (component migration)"
  echo "   - https://github.com/OCA/rest-framework/commits/19.0 (version updates)"
  exit 1
fi
