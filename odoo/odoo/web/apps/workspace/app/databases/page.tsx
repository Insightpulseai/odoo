import 'server-only'
import { createWorkspaceServiceClient } from '@/lib/supabase'

interface WorkspaceDatabase {
  id: string
  name: string | null
  description: string | null
  row_count: number | null
}

export default async function DatabasesIndexPage() {
  const supabase = createWorkspaceServiceClient()

  const { data: databases, error } = await supabase
    .schema('work')
    .from('databases')
    .select('id, name, description, row_count')
    .order('name', { ascending: true })

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Databases</h1>
        <div className="text-destructive text-sm">
          Failed to load databases: {error.message}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Databases</h1>
      {databases && databases.length > 0 ? (
        <ul className="divide-y divide-border rounded-lg border border-border overflow-hidden">
          {databases.map((db: WorkspaceDatabase) => (
            <li key={db.id}>
              <a
                href={`/databases/${db.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-accent/30 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-base">🗃</span>
                  <div>
                    <div className="font-medium text-sm">
                      {db.name ?? 'Untitled Database'}
                    </div>
                    {db.description && (
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {db.description}
                      </div>
                    )}
                  </div>
                </div>
                {db.row_count !== null && (
                  <span className="text-xs text-muted-foreground">
                    {db.row_count.toLocaleString()} rows
                  </span>
                )}
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted-foreground text-sm">No databases found.</p>
      )}
    </div>
  )
}
