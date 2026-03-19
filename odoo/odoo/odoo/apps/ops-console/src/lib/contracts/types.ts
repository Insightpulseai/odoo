/** Normalized UI card types — all registry data is mapped to these before rendering */

export interface AgentCard {
  id: string
  name: string
  version: string
  owner: string
  runtime: string
  modelAlias: string
  tools: string[]
  promotionState: string
  description: string
  sourceFile: string
}

export interface ToolCard {
  id: string
  name: string
  version: string
  provider: string
  description: string
  inputFields: string[]
  outputFields: string[]
  sideEffects: string[]
  constraints: string[]
  sourceFile: string
}

export interface ServiceCard {
  id: string
  name: string
  serviceClass: 'approved_core' | 'conditional' | 'not_baseline' | 'unknown'
  resourceGroup?: string
  region?: string
  instances: string[]
  consumedBy: string[]
  sourceFile: string
}

export interface PipelineCard {
  id: string
  name: string
  description: string
  documentClass: string
  stages: PipelineStageCard[]
  sourceFile: string
}

export interface PipelineStageCard {
  name: string
  tool?: string
  type?: string
  config?: Record<string, unknown>
}

export interface PolicyCard {
  id: string
  name: string
  kind: string
  version: string
  description: string
  sourceFile: string
  rules?: string[]
}

export interface ModelAliasCard {
  alias: string
  currentModel: string
  fallback: string | null
  costTier: string
  useCases: string[]
  sourceFile: string
}

export interface DocumentClassCard {
  className: string
  displayName: string
  docintModel: string
  odooModel: string | null
  keyFields: string[]
  confidenceThreshold: number
  sourceFile: string
}

export interface OdooBoundaryCard {
  id: string
  name: string
  kind: string
  odooModel?: string
  description: string
  readOperations: string[]
  writeOperations: string[]
  prohibited: string[]
  sourceFile: string
}
