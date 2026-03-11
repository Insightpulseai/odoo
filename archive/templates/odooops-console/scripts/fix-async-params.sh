#!/usr/bin/env bash
set -euo pipefail

# Fix async params in Next.js 15/16 pages and layouts
# Pattern: params: { ... } → params: Promise<{ ... }>, then await params

files=(
  "app/(app)/projects/[projectId]/upgrade/page.tsx"
  "app/(app)/projects/[projectId]/monitor/page.tsx"
  "app/(app)/projects/[projectId]/builds/[buildId]/monitor/page.tsx"
  "app/(app)/projects/[projectId]/builds/[buildId]/logs/page.tsx"
  "app/(app)/projects/[projectId]/builds/[buildId]/layout.tsx"
  "app/(app)/projects/[projectId]/builds/page.tsx"
  "app/(app)/projects/[projectId]/layout.tsx"
  "app/(app)/projects/[projectId]/branches/page.tsx"
  "app/(app)/projects/[projectId]/backups/page.tsx"
)

for file in "${files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "Fixing $file..."

    # Step 1: Make function async if not already
    sed -i.bak 's/export default function/export default async function/g' "$file"

    # Step 2: Update params type signature
    # params: { projectId: string } → params: Promise<{ projectId: string }>
    sed -i.bak 's/params: { \(.*\) }/params: Promise<{ \1 }>/g' "$file"

    # Step 3: Update searchParams type signature if present
    sed -i.bak 's/searchParams: { \(.*\) }/searchParams: Promise<{ \1 }>/g' "$file"

    # Clean up backup
    rm -f "$file.bak"

    echo "✓ Fixed $file"
  else
    echo "⚠ File not found: $file"
  fi
done

echo ""
echo "✅ All files updated. Manual steps required:"
echo "1. Add 'const resolvedParams = await params;' at start of each component"
echo "2. Replace all 'params.xxx' with 'resolvedParams.xxx'"
echo "3. Do same for searchParams if present"
