import { loadYamlDir } from '../registry/loadYamlRegistry'
import type { PipelineCard, DocumentClassCard } from '../contracts/types'

export function loadPipelineCards(): PipelineCard[] {
  const files = loadYamlDir('ops-platform/ssot/finance')

  const cards: PipelineCard[] = []

  for (const f of files) {
    const d = f.data as any
    if (d.kind !== 'DocumentPipelineRegistry') continue
    for (const p of d.pipelines ?? []) {
      cards.push({
        id: p.name ?? 'unknown',
        name: p.name ?? 'unknown',
        description: p.description ?? '',
        documentClass: p.document_class ?? 'unknown',
        stages: (p.steps ?? []).map((s: any) => ({
          name: s.name ?? 'unknown',
          tool: s.tool,
          type: s.type,
          config: s.config,
        })),
        sourceFile: f.filePath,
      })
    }
  }

  return cards
}

export function loadDocumentClassCards(): DocumentClassCard[] {
  const files = loadYamlDir('ops-platform/ssot/docint')

  for (const f of files) {
    const d = f.data as any
    if (d.kind !== 'DocumentClassRegistry') continue
    return (d.document_classes ?? []).map((dc: any) => ({
      className: dc.class ?? 'unknown',
      displayName: dc.display_name ?? dc.class ?? 'unknown',
      docintModel: dc.docint_model ?? 'unknown',
      odooModel: dc.odoo_model ?? null,
      keyFields: dc.key_fields ?? [],
      confidenceThreshold: dc.confidence_threshold ?? 0,
      sourceFile: f.filePath,
    }))
  }

  return []
}
