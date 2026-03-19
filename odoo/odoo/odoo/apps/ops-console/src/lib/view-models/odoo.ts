import { loadYamlDir } from '../registry/loadYamlRegistry'
import type { OdooBoundaryCard } from '../contracts/types'

export function loadOdooBoundaryCards(): OdooBoundaryCard[] {
  const files = loadYamlDir('odoo/ssot/odoo')

  const cards: OdooBoundaryCard[] = []

  for (const f of files) {
    const d = f.data as any
    if (!d.kind) continue

    // Handle ToolSurfaceContract
    if (d.kind === 'ToolSurfaceContract') {
      const spec = d.spec ?? {}
      cards.push({
        id: d.metadata?.name ?? f.filePath,
        name: d.metadata?.name ?? 'unknown',
        kind: d.kind,
        description: d.metadata?.description ?? 'Odoo RPC tool surface contract',
        readOperations: (spec.read_operations ?? []).map((op: any) => `${op.model}.${(op.methods ?? []).join(',')}`),
        writeOperations: (spec.write_operations ?? []).map((op: any) => `${op.model}.${(op.methods ?? []).join(',')}`),
        prohibited: [
          ...(spec.prohibited?.models ?? []).map((m: string) => `model: ${m}`),
          ...(spec.prohibited?.methods ?? []).map((m: string) => `method: ${m}`),
          ...(spec.prohibited?.patterns ?? []),
        ],
        sourceFile: f.filePath,
      })
    }

    // Handle WorkflowContract
    if (d.kind === 'WorkflowContract') {
      const spec = d.spec ?? {}
      cards.push({
        id: d.metadata?.name ?? f.filePath,
        name: d.metadata?.name ?? 'unknown',
        kind: d.kind,
        odooModel: spec.odoo_model,
        description: spec.description ?? d.metadata?.description ?? '',
        readOperations: [],
        writeOperations: Object.entries(spec.agent_permissions ?? {})
          .filter(([, v]: [string, any]) => v?.allowed)
          .map(([k]) => k),
        prohibited: Object.entries(spec.agent_permissions ?? {})
          .filter(([, v]: [string, any]) => !v?.allowed)
          .map(([k, v]: [string, any]) => `${k}: ${v?.note ?? 'not allowed'}`),
        sourceFile: f.filePath,
      })
    }

    // Handle OCRDestinationMapping
    if (d.kind === 'OCRDestinationMapping') {
      const mappings = d.mappings ?? {}
      cards.push({
        id: d.metadata?.name ?? f.filePath,
        name: d.metadata?.name ?? 'unknown',
        kind: d.kind,
        description: 'Document Intelligence → Odoo field mapping',
        readOperations: Object.keys(mappings).map(k => `mapping: ${k}`),
        writeOperations: [],
        prohibited: [],
        sourceFile: f.filePath,
      })
    }
  }

  return cards
}
