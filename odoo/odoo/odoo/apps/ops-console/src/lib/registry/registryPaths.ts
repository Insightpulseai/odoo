import path from 'path'

// Resolve from the ops-console app root up to the monorepo root
// ops-console is at: odoo/apps/ops-console/
// Repo root is 3 levels up
function repoRoot(): string {
  // In dev: process.cwd() is the ops-console dir
  // Traverse up to find the monorepo root (contains ssot/, agents/, ops-platform/)
  let dir = process.cwd()
  for (let i = 0; i < 5; i++) {
    if (
      require('fs').existsSync(path.join(dir, 'ssot')) ||
      require('fs').existsSync(path.join(dir, 'agents'))
    ) {
      return dir
    }
    dir = path.dirname(dir)
  }
  // Fallback: assume we're 3 levels deep
  return path.resolve(process.cwd(), '..', '..', '..')
}

export const REPO_ROOT = repoRoot()

export const REGISTRY_PATHS = {
  orgPolicies: [
    'ssot/org',
  ],
  opsPlatform: [
    'ops-platform/ssot/foundry',
    'ops-platform/ssot/docint',
    'ops-platform/ssot/finance',
    'ops-platform/ssot/azure',
  ],
  agents: [
    'agents/foundry/agents',
    'agents/foundry/tools',
    'agents/foundry/policies',
    'agents/foundry/evals',
    'agents/foundry/knowledge',
  ],
  odoo: [
    'odoo/ssot/odoo',
  ],
} as const

export type RegistryFamily = keyof typeof REGISTRY_PATHS

export function resolveRegistryDir(relativePath: string): string {
  return path.join(REPO_ROOT, relativePath)
}
