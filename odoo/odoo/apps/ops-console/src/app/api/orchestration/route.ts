import { NextResponse } from 'next/server'
import { loadPipelineCards, loadDocumentClassCards } from '@/lib/view-models/pipelines'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const pipelines = loadPipelineCards()
    const documentClasses = loadDocumentClassCards()

    return NextResponse.json({
      pipelines: pipelines.map(p => ({
        id: p.id,
        name: p.name,
        description: p.description,
        documentClass: p.documentClass,
        stages: p.stages,
        sourceFile: p.sourceFile,
      })),
      documentClasses: documentClasses.map(dc => ({
        className: dc.className,
        displayName: dc.displayName,
        docintModel: dc.docintModel,
        odooModel: dc.odooModel,
        keyFields: dc.keyFields,
        confidenceThreshold: dc.confidenceThreshold,
        sourceFile: dc.sourceFile,
      })),
      source: 'registry',
      fetchedAt: new Date().toISOString(),
    })
  } catch (err) {
    console.error('[api/orchestration] Registry load failed:', err)
    return NextResponse.json({
      pipelines: [],
      documentClasses: [],
      source: 'error',
      error: String(err),
      fetchedAt: new Date().toISOString(),
    }, { status: 500 })
  }
}
