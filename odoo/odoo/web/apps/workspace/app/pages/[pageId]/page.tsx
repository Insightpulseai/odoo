import 'server-only'
import { createWorkspaceServiceClient } from '@/lib/supabase'
import { notFound } from 'next/navigation'

interface Block {
  id: string
  type: string
  content: Record<string, unknown> | null
  position: number
}

interface PageDetail {
  id: string
  title: string | null
  space_id: string | null
  created_by: string | null
  updated_at: string | null
}

function renderBlock(block: Block) {
  const text =
    typeof block.content === 'object' &&
    block.content !== null &&
    'text' in block.content
      ? String(block.content.text ?? '')
      : ''

  switch (block.type) {
    case 'paragraph':
      return (
        <p key={block.id} className="mb-3 leading-relaxed">
          {text}
        </p>
      )
    case 'heading_1':
      return (
        <h1 key={block.id} className="text-2xl font-bold mt-6 mb-3">
          {text}
        </h1>
      )
    case 'heading_2':
      return (
        <h2 key={block.id} className="text-xl font-semibold mt-5 mb-2">
          {text}
        </h2>
      )
    case 'bullet_list_item':
      return (
        <li key={block.id} className="ml-4 mb-1 list-disc">
          {text}
        </li>
      )
    default:
      return (
        <pre
          key={block.id}
          className="bg-muted rounded p-3 text-xs overflow-x-auto mb-3"
        >
          {JSON.stringify(block.content, null, 2)}
        </pre>
      )
  }
}

export default async function PageDetailPage({
  params,
}: {
  params: Promise<{ pageId: string }>
}) {
  const { pageId } = await params
  const supabase = createWorkspaceServiceClient()

  const { data: page, error: pageError } = await supabase
    .schema('work')
    .from('pages')
    .select('id, title, space_id, created_by, updated_at')
    .eq('id', pageId)
    .single()

  if (pageError || !page) {
    notFound()
  }

  const { data: blocks, error: blocksError } = await supabase
    .schema('work')
    .from('blocks')
    .select('id, type, content, position')
    .eq('page_id', pageId)
    .order('position', { ascending: true })

  const typedPage = page as PageDetail
  const typedBlocks: Block[] = (blocks ?? []) as Block[]

  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-6">
        <a
          href="/pages"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← Pages
        </a>
      </div>
      <h1 className="text-3xl font-bold mb-2">{typedPage.title ?? 'Untitled'}</h1>
      {typedPage.updated_at && (
        <p className="text-xs text-muted-foreground mb-8">
          Last updated:{' '}
          {new Date(typedPage.updated_at).toLocaleString('en-US', {
            dateStyle: 'medium',
            timeStyle: 'short',
          })}
        </p>
      )}
      {blocksError && (
        <div className="text-destructive text-sm mb-4">
          Failed to load blocks: {blocksError.message}
        </div>
      )}
      <div className="prose prose-sm max-w-none">
        {typedBlocks.length > 0 ? (
          typedBlocks.map(renderBlock)
        ) : (
          <p className="text-muted-foreground">This page has no content yet.</p>
        )}
      </div>
    </div>
  )
}
