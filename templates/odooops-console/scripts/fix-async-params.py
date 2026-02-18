#!/usr/bin/env python3
"""Fix async params in Next.js 15/16 pages."""

import re
from pathlib import Path

FILES_TO_FIX = [
    "app/(app)/projects/[projectId]/upgrade/page.tsx",
    "app/(app)/projects/[projectId]/monitor/page.tsx",
    "app/(app)/projects/[projectId]/builds/[buildId]/monitor/page.tsx",
    "app/(app)/projects/[projectId]/builds/[buildId]/logs/page.tsx",
    "app/(app)/projects/[projectId]/builds/page.tsx",
    "app/(app)/projects/[projectId]/branches/page.tsx",
    "app/(app)/projects/[projectId]/backups/page.tsx",
]

def fix_file(filepath: Path):
    """Fix async params in a single file."""
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return False

    content = filepath.read_text()
    original = content

    # Step 1: Make function async if not already
    content = re.sub(
        r'export default function (\w+)\(',
        r'export default async function \1(',
        content
    )

    # Step 2: Fix params type signature
    # params: { projectId: string } → params: Promise<{ projectId: string }>
    content = re.sub(
        r'params: \{([^}]+)\}',
        r'params: Promise<{\1}>',
        content
    )

    # Step 3: Fix searchParams type signature
    content = re.sub(
        r'searchParams: \{([^}]+)\}',
        r'searchParams: Promise<{\1}>',
        content
    )

    # Step 4: Add await for params at the start of function body
    # Find the function signature and insert await after opening brace
    def add_await_params(match):
        """Add await params after function opening brace."""
        func_sig = match.group(1)
        rest = match.group(2)

        # Extract param names from signature
        param_match = re.search(r'params: Promise<\{([^}]+)\}>', func_sig)
        if param_match:
            params_str = param_match.group(1).strip()
            # Extract just the keys (e.g., "projectId: string" → "projectId")
            param_names = [p.split(':')[0].strip() for p in params_str.split(',')]
            destructure = ', '.join(param_names)

            return f"{func_sig}) {{\n  const {{ {destructure} }} = await params;\n{rest}"

        return match.group(0)

    content = re.sub(
        r'(export default async function \w+\([^)]+\)) \{(.*)',
        add_await_params,
        content,
        count=1,
        flags=re.DOTALL
    )

    # Step 5: Replace all params.xxx with xxx
    # This is tricky - we need to be careful not to replace other uses
    # For now, do simple replacements for common patterns
    content = re.sub(r'\bparams\.projectId\b', 'projectId', content)
    content = re.sub(r'\bparams\.buildId\b', 'buildId', content)

    if content != original:
        filepath.write_text(content)
        print(f"✅ Fixed: {filepath}")
        return True
    else:
        print(f"⏭️  No changes: {filepath}")
        return False

def main():
    """Fix all files."""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0

    for file_path in FILES_TO_FIX:
        full_path = base_dir / file_path
        if fix_file(full_path):
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count}/{len(FILES_TO_FIX)} files")
    print("\n⚠️  Manual verification required:")
    print("1. Check that await params is correctly placed")
    print("2. Verify all params.xxx are replaced")
    print("3. Run: pnpm typecheck")

if __name__ == "__main__":
    main()
