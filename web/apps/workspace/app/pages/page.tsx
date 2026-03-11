import 'server-only'
import { createWorkspaceServiceClient } from '@/lib/supabase'

interface WorkspacePage {
  id: string
  title: string | null
  space_id: string | null
  created_by: string | null
  updated_at: string | null
}

export default async function PagesIndexPage() {
  const supabase = createWorkspaceServiceClient()

  const { data: pages, error } = await supabase
    .schema('work')
    .from('pages')
    .select('id, title, space_id, created_by, updated_at')
    .order('updated_at', { ascending: false })
    .limit(50)

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Pages</h1>
        <div className="text-destructive text-sm">
          Failed to load pages: {error.message}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Pages</h1>
      {pages && pages.length > 0 ? (
        <ul className="divide-y divide-border rounded-lg border border-border overflow-hidden">
          {pages.map((page: WorkspacePage) => (
            <li key={page.id}>
              <a
                href={`/pages/${page.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-accent/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-base">📄</span>
                  <span className="font-medium text-sm">
                    {page.title ?? 'Untitled'}
                  </span>
                </div>
                <div className="flex items-center gap-6 text-xs text-muted-foreground">
                  {page.space_id && (
                    <span className="hidden sm:inline">
                      Space: {page.space_id.slice(0, 8)}…
                    </span>
                  )}
                  {page.updated_at && (
                    <span>
                      {new Date(page.updated_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  )}
                </div>
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted-foreground text-sm">No pages found.</p>
      )}
    </div>
  )
}
