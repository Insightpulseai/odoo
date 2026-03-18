import { loadRegistryFamily, loadYamlDir } from '../registry/loadYamlRegistry'
import type { ServiceCard, ModelAliasCard, PolicyCard } from '../contracts/types'

export function loadServiceCards(): ServiceCard[] {
  // Load from ops-platform Azure catalog + org policies
  const opsPlatformFiles = loadYamlDir('ops-platform/ssot/azure')
  const orgFiles = loadYamlDir('ssot/org')

  const cards: ServiceCard[] = []

  // Parse Azure service catalog
  for (const f of opsPlatformFiles) {
    const d = f.data as any
    if (d.kind !== 'AzureServiceCatalog') continue
    for (const svc of d.services ?? []) {
      cards.push({
        id: svc.name?.replace(/\s+/g, '-').toLowerCase() ?? 'unknown',
        name: svc.name ?? 'unknown',
        serviceClass: svc.class ?? 'unknown',
        resourceGroup: svc.resource_group,
        region: svc.region,
        instances: svc.instances ?? [],
        consumedBy: svc.consumed_by ?? [],
        sourceFile: f.filePath,
      })
    }
  }

  // Parse org-level Azure service selection policy as additional context
  for (const f of orgFiles) {
    const d = f.data as any
    if (d.kind !== 'ServiceSelectionPolicy') continue
    for (const [className, classData] of Object.entries(d.spec?.service_classes ?? {})) {
      for (const svcName of (classData as any).services ?? []) {
        // Only add if not already present from catalog
        if (!cards.find(c => c.name === svcName)) {
          cards.push({
            id: svcName.replace(/\s+/g, '-').toLowerCase(),
            name: svcName,
            serviceClass: className as any,
            instances: [],
            consumedBy: [],
            sourceFile: f.filePath,
          })
        }
      }
    }
  }

  return cards
}

export function loadModelAliases(): ModelAliasCard[] {
  const files = loadYamlDir('ops-platform/ssot/foundry')

  for (const f of files) {
    const d = f.data as any
    if (d.kind !== 'ModelRegistry') continue
    return (d.aliases ?? []).map((a: any) => ({
      alias: a.alias ?? 'unknown',
      currentModel: a.current_model ?? 'unknown',
      fallback: a.fallback ?? null,
      costTier: a.cost_tier ?? 'unknown',
      useCases: a.use_cases ?? [],
      sourceFile: f.filePath,
    }))
  }

  return []
}

export function loadPolicyCards(): PolicyCard[] {
  const orgFiles = loadYamlDir('ssot/org')
  const agentPolicies = loadYamlDir('agents/foundry/policies')

  const cards: PolicyCard[] = []

  for (const f of [...orgFiles, ...agentPolicies]) {
    const d = f.data as any
    const meta = d.metadata ?? d
    cards.push({
      id: meta.name ?? f.filePath,
      name: meta.name ?? 'unknown',
      kind: d.kind ?? 'unknown',
      version: meta.version ?? '0.0.0',
      description: meta.description ?? d.kind ?? '',
      sourceFile: f.filePath,
      rules: d.spec?.global_rules ?? d.spec?.rules ?? d.rules ?? [],
    })
  }

  return cards
}
