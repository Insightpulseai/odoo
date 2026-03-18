/**
 * Canonical Azure Product Taxonomy
 *
 * All services in the Ops Console are classified using Azure's official
 * product categories as the outer taxonomy. Console operational domains
 * serve as the inner grouping.
 *
 * Rules:
 * - Every service must have one primary Azure category
 * - Services may have optional secondary categories
 * - External providers (Odoo.sh) are tagged isExternalProvider
 * - Unknown services fall back to 'Unclassified'
 */

// --- Azure canonical categories ---

export const AZURE_CATEGORIES = [
  'AI + Machine Learning',
  'Analytics',
  'Compute',
  'Containers',
  'Databases',
  'Developer Tools',
  'DevOps',
  'Hybrid + multicloud',
  'Identity',
  'Integration',
  'Internet of Things',
  'Management and Governance',
  'Media',
  'Migration',
  'Mixed reality',
  'Mobile',
  'Networking',
  'Security',
  'Storage',
  'Virtual desktop infrastructure',
  'Web',
  'Unclassified',
] as const

export type AzureCategory = (typeof AZURE_CATEGORIES)[number]

// --- Console operational domains ---

export type OperationalDomain =
  | 'runtime'
  | 'ai_agents'
  | 'dev_delivery'
  | 'identity_security'
  | 'governance_compliance'
  | 'data_analytics'
  | 'automation'

export const OPERATIONAL_DOMAIN_LABELS: Record<OperationalDomain, string> = {
  runtime: 'Runtime',
  ai_agents: 'AI & Agents',
  dev_delivery: 'Dev Delivery',
  identity_security: 'Identity & Security',
  governance_compliance: 'Governance & Compliance',
  data_analytics: 'Data & Analytics',
  automation: 'Automation',
}

// --- Classified service contract ---

export interface ClassifiedService {
  serviceId: string
  provider: string
  displayName: string
  category: AzureCategory
  secondaryCategories?: AzureCategory[]
  operationalDomain: OperationalDomain
  deploymentSurface: string
  healthStatus: 'operational' | 'degraded' | 'down' | 'unconfigured' | 'partial'
  maturityScore: number // 0-1
  isExternalProvider: boolean
  environment?: string
  endpoint?: string
  lastSync?: string
  relatedJobs?: string[]
  relatedDeploys?: string[]
  kbCoverage?: string[]
  tags?: string[]
}

// --- Canonical service registry ---

export const SERVICE_TAXONOMY: Record<string, {
  category: AzureCategory
  secondaryCategories?: AzureCategory[]
  operationalDomain: OperationalDomain
  isExternalProvider: boolean
  tags?: string[]
}> = {
  // AI + Machine Learning
  'ai-foundry': {
    category: 'AI + Machine Learning',
    operationalDomain: 'ai_agents',
    isExternalProvider: false,
  },
  'copilot-studio': {
    category: 'AI + Machine Learning',
    operationalDomain: 'ai_agents',
    isExternalProvider: false,
  },
  'odoo-copilot': {
    category: 'AI + Machine Learning',
    operationalDomain: 'ai_agents',
    isExternalProvider: false,
    tags: ['odoo'],
  },

  // Analytics
  'data-explorer': {
    category: 'Analytics',
    operationalDomain: 'data_analytics',
    isExternalProvider: false,
  },
  'fabric': {
    category: 'Analytics',
    operationalDomain: 'data_analytics',
    isExternalProvider: false,
  },

  // Compute / Runtime
  'azure-aca': {
    category: 'Compute',
    secondaryCategories: ['Containers', 'Web', 'Networking'],
    operationalDomain: 'runtime',
    isExternalProvider: false,
  },
  'azure-front-door': {
    category: 'Networking',
    secondaryCategories: ['Security'],
    operationalDomain: 'runtime',
    isExternalProvider: false,
  },
  'azure-postgresql': {
    category: 'Databases',
    operationalDomain: 'runtime',
    isExternalProvider: false,
  },
  'azure-key-vault': {
    category: 'Security',
    secondaryCategories: ['Management and Governance'],
    operationalDomain: 'identity_security',
    isExternalProvider: false,
  },

  // Developer Tools
  'github': {
    category: 'Developer Tools',
    secondaryCategories: ['DevOps'],
    operationalDomain: 'dev_delivery',
    isExternalProvider: false,
  },
  'vscode': {
    category: 'Developer Tools',
    operationalDomain: 'dev_delivery',
    isExternalProvider: false,
  },

  // DevOps
  'devops': {
    category: 'DevOps',
    operationalDomain: 'dev_delivery',
    isExternalProvider: false,
  },

  // Identity
  'entra': {
    category: 'Identity',
    operationalDomain: 'identity_security',
    isExternalProvider: false,
  },

  // Security
  'defender': {
    category: 'Security',
    operationalDomain: 'identity_security',
    isExternalProvider: false,
  },

  // Management and Governance
  'intune': {
    category: 'Management and Governance',
    secondaryCategories: ['Security'],
    operationalDomain: 'identity_security',
    isExternalProvider: false,
  },
  'purview': {
    category: 'Management and Governance',
    secondaryCategories: ['Security'],
    operationalDomain: 'governance_compliance',
    isExternalProvider: false,
  },
  'm365-admin': {
    category: 'Management and Governance',
    operationalDomain: 'governance_compliance',
    isExternalProvider: false,
  },

  // Integration
  'power-automate': {
    category: 'Integration',
    operationalDomain: 'automation',
    isExternalProvider: false,
  },
  'power-platform': {
    category: 'Integration',
    operationalDomain: 'automation',
    isExternalProvider: false,
  },

  // External providers
  'odoosh': {
    category: 'Hybrid + multicloud',
    secondaryCategories: ['Developer Tools'],
    operationalDomain: 'runtime',
    isExternalProvider: true,
    tags: ['odoo'],
  },
  'n8n': {
    category: 'Integration',
    operationalDomain: 'automation',
    isExternalProvider: true,
  },
  'supabase': {
    category: 'Databases',
    secondaryCategories: ['Integration'],
    operationalDomain: 'runtime',
    isExternalProvider: true,
  },
}

// --- Utility functions ---

/**
 * Classify a service by its ID. Returns fallback for unknown services.
 */
export function classifyService(serviceId: string): typeof SERVICE_TAXONOMY[string] {
  return SERVICE_TAXONOMY[serviceId] ?? {
    category: 'Unclassified' as AzureCategory,
    operationalDomain: 'runtime' as OperationalDomain,
    isExternalProvider: false,
  }
}

/**
 * Get display label for an Azure category.
 */
export function categoryLabel(category: AzureCategory): string {
  return category
}

/**
 * Get display label for an operational domain.
 */
export function domainLabel(domain: OperationalDomain): string {
  return OPERATIONAL_DOMAIN_LABELS[domain] ?? domain
}

/**
 * Group services by Azure category.
 */
export function groupByCategory(services: ClassifiedService[]): Record<AzureCategory, ClassifiedService[]> {
  const groups = {} as Record<AzureCategory, ClassifiedService[]>
  for (const svc of services) {
    const cat = svc.category ?? 'Unclassified'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(svc)
  }
  return groups
}

/**
 * Group services by operational domain.
 */
export function groupByDomain(services: ClassifiedService[]): Record<OperationalDomain, ClassifiedService[]> {
  const groups = {} as Record<OperationalDomain, ClassifiedService[]>
  for (const svc of services) {
    const dom = svc.operationalDomain ?? 'runtime'
    if (!groups[dom]) groups[dom] = []
    groups[dom].push(svc)
  }
  return groups
}

/**
 * Compute average maturity per category. Safe for empty/missing data.
 */
export function maturityByCategory(services: ClassifiedService[]): Array<{ category: AzureCategory; score: number; count: number }> {
  const map = new Map<AzureCategory, { total: number; count: number }>()
  for (const svc of services) {
    const cat = svc.category ?? ('Unclassified' as AzureCategory)
    const entry = map.get(cat) ?? { total: 0, count: 0 }
    entry.total += svc.maturityScore ?? 0
    entry.count += 1
    map.set(cat, entry)
  }
  return Array.from(map.entries())
    .map(([category, { total, count }]) => ({
      category,
      score: count > 0 ? total / count : 0,
      count,
    }))
    .sort((a, b) => b.score - a.score)
}

/**
 * Compute average maturity per operational domain. Safe for empty/missing data.
 */
export function maturityByDomain(services: ClassifiedService[]): Array<{ domain: OperationalDomain; label: string; score: number; count: number }> {
  const map = new Map<OperationalDomain, { total: number; count: number }>()
  for (const svc of services) {
    const dom = svc.operationalDomain ?? 'runtime'
    const entry = map.get(dom) ?? { total: 0, count: 0 }
    entry.total += svc.maturityScore ?? 0
    entry.count += 1
    map.set(dom, entry)
  }
  return Array.from(map.entries())
    .map(([domain, { total, count }]) => ({
      domain,
      label: domainLabel(domain),
      score: count > 0 ? total / count : 0,
      count,
    }))
    .sort((a, b) => b.score - a.score)
}

/**
 * Get all unique categories present in a service list.
 */
export function getActiveCategories(services: ClassifiedService[]): AzureCategory[] {
  return [...new Set(services.map(s => s.category ?? ('Unclassified' as AzureCategory)))]
}

/**
 * Filter services by category.
 */
export function filterByCategory(services: ClassifiedService[], category: AzureCategory | 'all'): ClassifiedService[] {
  if (category === 'all') return services
  return services.filter(s => s.category === category || s.secondaryCategories?.includes(category))
}
