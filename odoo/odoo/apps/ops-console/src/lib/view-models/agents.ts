import { loadRegistryFamily } from '../registry/loadYamlRegistry'
import type { AgentCard, ToolCard } from '../contracts/types'

export function loadAgentCards(): AgentCard[] {
  const files = loadRegistryFamily('agents')

  return files
    .filter(f => f.filePath.includes('/agents/') && f.data?.kind === 'AgentManifest')
    .map(f => {
      const d = f.data as any
      const meta = d.metadata ?? d
      const spec = d.spec ?? {}
      return {
        id: meta.name ?? f.filePath,
        name: meta.name ?? 'unknown',
        version: meta.version ?? '0.0.0',
        owner: meta.owner ?? 'unknown',
        runtime: spec.runtime ?? 'unknown',
        modelAlias: spec.model_alias ?? 'unknown',
        tools: spec.tools ?? [],
        promotionState: meta.promotion_state ?? 'unknown',
        description: meta.description ?? '',
        sourceFile: f.filePath,
      }
    })
}

export function loadToolCards(): ToolCard[] {
  const files = loadRegistryFamily('agents')

  return files
    .filter(f => f.filePath.includes('/tools/') && f.data?.kind === 'ToolManifest')
    .map(f => {
      const d = f.data as any
      const meta = d.metadata ?? d
      const spec = d.spec ?? {}
      return {
        id: meta.name ?? f.filePath,
        name: meta.name ?? 'unknown',
        version: meta.version ?? '0.0.0',
        provider: spec.provider ?? 'unknown',
        description: meta.description ?? '',
        inputFields: Object.keys(spec.input_schema ?? spec.models ?? {}),
        outputFields: Object.keys(spec.output_envelope?.schema ?? spec.output_schema ?? {}),
        sideEffects: [],
        constraints: spec.global_constraints ?? [],
        sourceFile: f.filePath,
      }
    })
}
