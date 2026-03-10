import 'server-only'
import { createWorkspaceServiceClient } from '@/lib/supabase'

interface SearchResult {
  id: string
  title: string | null
  type: string | null
  snippet: string | null
  url: string | null
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams
  const query = q?.trim() ?? ''

  let results: SearchResult[] = []
  let searchError: string | null = null

  if (query) {
    const supabase = createWorkspaceServiceClient()
    const { data, error } = await supabase.rpc('work_search', {
      query_text: query,
    })

    if (error) {
      searchError = error.message
    } else {
      results = (data ?? []) as SearchResult[]
    }
  }

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold mb-6">Search</h1>

      <form method="GET" action="/search" className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            name="q"
            defaultValue={query}
            placeholder="Search pages, blocks, and rows…"
            className="flex-1 px-4 py-2 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            autoFocus
          />
          <button
            type="submit"
            className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Search
          </button>
        </div>
      </form>

      {searchError && (
        <div className="text-destructive text-sm mb-4">
          Search failed: {searchError}
        </div>
      )}

      {query && !searchError && (
        <div>
          <p className="text-xs text-muted-foreground mb-4">
            {results.length} result{results.length !== 1 ? 's' : ''} for &ldquo;{query}&rdquo;
          </p>
          {results.length > 0 ? (
            <ul className="divide-y divide-border rounded-lg border border-border overflow-hidden">
              {results.map((result) => {
                const href = result.url
                  ? result.url
                  : result.type === 'page'
                  ? `/pages/${result.id}`
                  : result.type === 'block'
                  ? `/pages/${result.id}`
                  : `/databases/${result.id}`

                return (
                  <li key={result.id}>
                    <a
                      href={href}
                      className="block px-4 py-3 hover:bg-accent/30 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium px-1.5 py-0.5 rounded bg-muted text-muted-foreground uppercase tracking-wide">
                          {result.type ?? 'result'}
                        </span>
                        <span className="font-medium text-sm">
                          {result.title ?? 'Untitled'}
                        </span>
                      </div>
                      {result.snippet && (
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {result.snippet}
                        </p>
                      )}
                    </a>
                  </li>
                )
              })}
            </ul>
          ) : (
            <p className="text-muted-foreground text-sm">
              No results found for &ldquo;{query}&rdquo;.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
