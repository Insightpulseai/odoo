import 'server-only'
import { createWorkspaceServiceClient } from '@/lib/supabase'
import { notFound } from 'next/navigation'

interface DbDatabase {
  id: string
  name: string | null
  description: string | null
}

interface DbColumn {
  id: string
  name: string
  field_type: string
  position: number
}

interface DbRow {
  id: string
  data: Record<string, unknown> | null
}

export default async function DatabaseDetailPage({
  params,
}: {
  params: Promise<{ dbId: string }>
}) {
  const { dbId } = await params
  const supabase = createWorkspaceServiceClient()

  const { data: database, error: dbError } = await supabase
    .schema('work')
    .from('databases')
    .select('id, name, description')
    .eq('id', dbId)
    .single()

  if (dbError || !database) {
    notFound()
  }

  const { data: columns, error: colError } = await supabase
    .schema('work')
    .from('db_columns')
    .select('id, name, field_type, position')
    .eq('database_id', dbId)
    .order('position', { ascending: true })

  const { data: rows, error: rowError } = await supabase
    .schema('work')
    .from('db_rows')
    .select('id, data')
    .eq('database_id', dbId)
    .limit(100)

  const typedDb = database as DbDatabase
  const typedColumns: DbColumn[] = (columns ?? []) as DbColumn[]
  const typedRows: DbRow[] = (rows ?? []) as DbRow[]

  return (
    <div className="p-8">
      <div className="mb-6">
        <a
          href="/databases"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← Databases
        </a>
      </div>
      <h1 className="text-2xl font-bold mb-1">{typedDb.name ?? 'Untitled Database'}</h1>
      {typedDb.description && (
        <p className="text-sm text-muted-foreground mb-6">{typedDb.description}</p>
      )}

      {(colError || rowError) && (
        <div className="text-destructive text-sm mb-4">
          {colError && <div>Failed to load columns: {colError.message}</div>}
          {rowError && <div>Failed to load rows: {rowError.message}</div>}
        </div>
      )}

      {typedColumns.length > 0 ? (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted/50 border-b border-border">
                {typedColumns.map((col) => (
                  <th
                    key={col.id}
                    className="px-4 py-2 text-left font-medium text-muted-foreground whitespace-nowrap"
                  >
                    {col.name}
                    <span className="ml-1 text-xs font-normal opacity-60">
                      ({col.field_type})
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {typedRows.length > 0 ? (
                typedRows.map((row) => (
                  <tr key={row.id} className="hover:bg-accent/20">
                    {typedColumns.map((col) => {
                      const cellValue =
                        row.data && col.name in row.data
                          ? row.data[col.name]
                          : null
                      return (
                        <td
                          key={col.id}
                          className="px-4 py-2 text-sm truncate max-w-[200px]"
                        >
                          {cellValue === null || cellValue === undefined
                            ? <span className="text-muted-foreground/50">—</span>
                            : typeof cellValue === 'object'
                            ? JSON.stringify(cellValue)
                            : String(cellValue)}
                        </td>
                      )
                    })}
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={typedColumns.length}
                    className="px-4 py-6 text-center text-muted-foreground text-sm"
                  >
                    No rows found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">
          No columns defined for this database.
        </p>
      )}

      {typedRows.length === 100 && (
        <p className="text-xs text-muted-foreground mt-3">
          Showing first 100 rows.
        </p>
      )}
    </div>
  )
}
