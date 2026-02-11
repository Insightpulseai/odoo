#!/bin/bash
set -euo pipefail

echo "=== Alpha Browser Phase 1 Verification ==="
echo ""

# Check required files exist
echo "✓ Checking required files..."
required_files=(
  "package.json"
  "tsconfig.json"
  "vite.config.ts"
  "public/manifest.json"
  "src/background/service-worker.ts"
  "src/content/content-main.ts"
  "src/popup/popup.tsx"
  "src/popup/App.tsx"
  "src/offscreen/offscreen-main.ts"
  "src/storage/db.ts"
  "src/storage/missions.ts"
  "src/storage/checkpoints.ts"
  "src/shared/types.ts"
  "src/shared/logger.ts"
  "src/shared/utils.ts"
  "README.md"
  "docs/architecture.md"
)

for file in "${required_files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (MISSING)"
    exit 1
  fi
done

echo ""
echo "✓ Code statistics:"
echo "  TypeScript files: $(find src -name "*.ts" -o -name "*.tsx" | wc -l)"
echo "  Lines of code: $(wc -l src/**/*.ts src/**/*.tsx 2>/dev/null | tail -1 | awk '{print $1}')"
echo "  Test files: $(find tests -name "*.test.ts" | wc -l)"

echo ""
echo "✓ Project structure validated!"
echo ""
echo "Next steps:"
echo "  1. cd apps/alpha-browser"
echo "  2. pnpm install"
echo "  3. pnpm build"
echo "  4. Load extension in chrome://extensions (Developer mode)"
echo ""
echo "=== Phase 1: Foundation - COMPLETE ==="
