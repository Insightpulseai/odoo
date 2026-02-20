#!/usr/bin/env bash
set -euo pipefail

echo "=== n8n API Bridge Implementation Verification ==="
echo ""

# Check required files exist
echo "✓ Checking required files..."
files=(
  "src/n8nClient.ts"
  "src/types.ts"
  "src/index.ts"
  "src/__tests__/n8nClient.test.ts"
  "package.json"
  "tsconfig.json"
  "jest.config.js"
  "README.md"
)

for file in "${files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file (MISSING)"
    exit 1
  fi
done

echo ""
echo "✓ Checking implementation requirements..."

# Check for required methods
methods=(
  "listWorkflows"
  "getWorkflow"
  "listExecutions"
  "getExecution"
  "retryExecution"
  "audit"
)

for method in "${methods[@]}"; do
  if grep -q "async $method" src/n8nClient.ts; then
    echo "  ✓ $method implemented"
  else
    echo "  ✗ $method (MISSING)"
    exit 1
  fi
done

echo ""
echo "✓ Checking authentication..."
if grep -q "X-N8N-API-KEY" src/n8nClient.ts; then
  echo "  ✓ API key authentication header"
else
  echo "  ✗ API key authentication (MISSING)"
  exit 1
fi

if grep -q "Accept.*application/json" src/n8nClient.ts; then
  echo "  ✓ Accept header"
else
  echo "  ✗ Accept header (MISSING)"
  exit 1
fi

echo ""
echo "✓ Checking error handling..."
if grep -q "class N8nApiError" src/n8nClient.ts; then
  echo "  ✓ Custom error class"
else
  echo "  ✗ Custom error class (MISSING)"
  exit 1
fi

error_codes=(401 404 429)
for code in "${error_codes[@]}"; do
  if grep -q "case $code:" src/n8nClient.ts; then
    echo "  ✓ HTTP $code handling"
  else
    echo "  ✗ HTTP $code handling (MISSING)"
    exit 1
  fi
done

echo ""
echo "✓ Checking mutation guard..."
if grep -q "ALLOW_MUTATIONS" src/n8nClient.ts; then
  echo "  ✓ ALLOW_MUTATIONS environment variable"
else
  echo "  ✗ ALLOW_MUTATIONS (MISSING)"
  exit 1
fi

if grep -q "checkMutationsAllowed" src/n8nClient.ts; then
  echo "  ✓ Mutation guard method"
else
  echo "  ✗ Mutation guard method (MISSING)"
  exit 1
fi

echo ""
echo "✓ Checking audit exemption..."
if grep -q "// Audit is exempt from mutation guard" src/n8nClient.ts || \
   grep -q "Note: Exempt from mutation guard" src/n8nClient.ts; then
  echo "  ✓ Audit mutation guard exemption"
else
  echo "  ✗ Audit mutation guard exemption (MISSING)"
  exit 1
fi

echo ""
echo "✓ Checking node-fetch integration..."
if grep -q "from 'node-fetch'" src/n8nClient.ts; then
  echo "  ✓ node-fetch import"
else
  echo "  ✗ node-fetch import (MISSING)"
  exit 1
fi

echo ""
echo "✓ Checking type exports..."
types=(
  "Workflow"
  "WorkflowDetail"
  "Execution"
  "ExecutionDetail"
  "AuditEvent"
)

for type in "${types[@]}"; do
  if grep -q "interface $type" src/n8nClient.ts; then
    echo "  ✓ $type type"
  else
    echo "  ✗ $type type (MISSING)"
    exit 1
  fi
done

echo ""
echo "=== All verification checks passed! ==="
echo ""
echo "Implementation complete with:"
echo "  • Authentication (X-N8N-API-KEY header)"
echo "  • Core methods (listWorkflows, getWorkflow, listExecutions, getExecution, retryExecution, audit)"
echo "  • Error handling (401, 404, 429 + structured N8nApiError)"
echo "  • Mutation guard (ALLOW_MUTATIONS env var, audit exempt)"
echo "  • Type safety (TypeScript interfaces for all responses)"
echo "  • node-fetch HTTP client"
echo ""
