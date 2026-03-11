#!/usr/bin/env bash
# Validate seed YAML files against schemas
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEEDS_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$SEEDS_DIR")"

echo "🔍 Validating seed files..."

# Install dependencies if not present
python3 -m pip install -q yamale yamllint 2>/dev/null || true

# Run yamllint (with relaxed rules for readability)
echo "📝 Running yamllint..."
yamllint -d "{extends: default, rules: {line-length: {max: 200}, trailing-spaces: disable, document-start: disable, truthy: disable}}" "$SEEDS_DIR" || {
    echo "⚠️  yamllint warnings (non-blocking)"
}

# Validate AFC workstream
echo "📋 Validating AFC workstream..."
if [ -f "$SEEDS_DIR/workstreams/afc_financial_close/00_workstream.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/afc_workstream.schema.yaml" \
           "$SEEDS_DIR/workstreams/afc_financial_close/00_workstream.yaml" || {
        echo "❌ AFC workstream validation failed"
        exit 1
    }
fi

# Validate AFC templates
echo "📋 Validating AFC templates..."
if [ -f "$SEEDS_DIR/workstreams/afc_financial_close/10_templates.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/afc_templates.schema.yaml" \
           "$SEEDS_DIR/workstreams/afc_financial_close/10_templates.yaml" || {
        echo "❌ AFC templates validation failed"
        exit 1
    }
fi

# Validate AFC tasks
echo "📋 Validating AFC tasks..."
if [ -f "$SEEDS_DIR/workstreams/afc_financial_close/20_tasks.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/afc_tasks.schema.yaml" \
           "$SEEDS_DIR/workstreams/afc_financial_close/20_tasks.yaml" || {
        echo "❌ AFC tasks validation failed"
        exit 1
    }
fi

# Validate STC workstream
echo "📋 Validating STC workstream..."
if [ -f "$SEEDS_DIR/workstreams/stc_tax_compliance/00_workstream.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/stc_workstream.schema.yaml" \
           "$SEEDS_DIR/workstreams/stc_tax_compliance/00_workstream.yaml" || {
        echo "❌ STC workstream validation failed"
        exit 1
    }
fi

# Validate STC checks
echo "📋 Validating STC compliance checks..."
if [ -f "$SEEDS_DIR/workstreams/stc_tax_compliance/20_compliance_checks.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/stc_checks.schema.yaml" \
           "$SEEDS_DIR/workstreams/stc_tax_compliance/20_compliance_checks.yaml" || {
        echo "❌ STC checks validation failed"
        exit 1
    }
fi

# Validate STC scenarios
echo "📋 Validating STC scenarios..."
if [ -f "$SEEDS_DIR/workstreams/stc_tax_compliance/30_scenarios.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/stc_scenarios.schema.yaml" \
           "$SEEDS_DIR/workstreams/stc_tax_compliance/30_scenarios.yaml" || {
        echo "❌ STC scenarios validation failed"
        exit 1
    }
fi

# Validate shared calendars
echo "📋 Validating shared calendars..."
if [ -f "$SEEDS_DIR/shared/calendars.yaml" ]; then
    yamale -s "$SEEDS_DIR/schema/shared_calendars.schema.yaml" \
           "$SEEDS_DIR/shared/calendars.yaml" || {
        echo "❌ Shared calendars validation failed"
        exit 1
    }
fi

echo "✅ All seed validations passed!"
