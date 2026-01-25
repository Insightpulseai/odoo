import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DatabaseRelation, DatabaseSchema, TableColumn } from '@/lib/supabase';

// Query keys
export const tableKeys = {
  all: ['tables'] as const,
  relations: (options?: { includeViews?: boolean; includeSystem?: boolean }) =>
    [...tableKeys.all, 'relations', options] as const,
  schemas: () => [...tableKeys.all, 'schemas'] as const,
  detail: (schema: string, table: string) =>
    [...tableKeys.all, 'detail', schema, table] as const,
};

// Fetch all relations
async function fetchRelations(options?: {
  includeViews?: boolean;
  includeSystem?: boolean;
}): Promise<DatabaseRelation[]> {
  const params = new URLSearchParams();
  if (options?.includeViews !== undefined) {
    params.set('includeViews', String(options.includeViews));
  }
  if (options?.includeSystem !== undefined) {
    params.set('includeSystem', String(options.includeSystem));
  }

  const url = `/api/tables${params.toString() ? `?${params}` : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch relations');
  }

  return response.json();
}

// Fetch all schemas
async function fetchSchemas(): Promise<DatabaseSchema[]> {
  const response = await fetch('/api/tables/schemas');

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch schemas');
  }

  return response.json();
}

// Fetch table details
interface TableDetails {
  schema_name: string;
  table_name: string;
  columns: TableColumn[];
  row_count: number | null;
  rows: Record<string, unknown>[];
}

async function fetchTableDetails(
  schema: string,
  table: string,
  options?: { includeRows?: boolean; limit?: number }
): Promise<TableDetails> {
  const params = new URLSearchParams();
  if (options?.includeRows !== undefined) {
    params.set('includeRows', String(options.includeRows));
  }
  if (options?.limit !== undefined) {
    params.set('limit', String(options.limit));
  }

  const url = `/api/tables/${encodeURIComponent(schema)}/${encodeURIComponent(table)}${params.toString() ? `?${params}` : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch table details');
  }

  return response.json();
}

// Toggle schema exposure
async function toggleSchemaExposure(
  schemaName: string,
  exposed: boolean,
  description?: string
): Promise<void> {
  const response = await fetch('/api/tables/schemas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ schema_name: schemaName, exposed, description }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to toggle schema exposure');
  }
}

// Hook: Fetch relations
export function useRelations(options?: {
  includeViews?: boolean;
  includeSystem?: boolean;
}) {
  return useQuery({
    queryKey: tableKeys.relations(options),
    queryFn: () => fetchRelations(options),
    staleTime: 60 * 1000, // 1 minute
    refetchOnWindowFocus: false,
  });
}

// Hook: Fetch schemas
export function useSchemas() {
  return useQuery({
    queryKey: tableKeys.schemas(),
    queryFn: fetchSchemas,
    staleTime: 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

// Hook: Fetch table details
export function useTableDetails(
  schema: string,
  table: string,
  options?: { includeRows?: boolean; limit?: number; enabled?: boolean }
) {
  return useQuery({
    queryKey: tableKeys.detail(schema, table),
    queryFn: () => fetchTableDetails(schema, table, options),
    staleTime: 30 * 1000, // 30 seconds
    refetchOnWindowFocus: false,
    enabled: options?.enabled !== false,
  });
}

// Hook: Toggle schema exposure
export function useToggleSchemaExposure() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      schemaName,
      exposed,
      description,
    }: {
      schemaName: string;
      exposed: boolean;
      description?: string;
    }) => toggleSchemaExposure(schemaName, exposed, description),
    onSuccess: () => {
      // Invalidate both schemas and relations queries
      queryClient.invalidateQueries({ queryKey: tableKeys.schemas() });
      queryClient.invalidateQueries({ queryKey: tableKeys.relations() });
    },
  });
}

// Utility: Group relations by schema
export function groupRelationsBySchema(
  relations: DatabaseRelation[]
): Map<string, DatabaseRelation[]> {
  const grouped = new Map<string, DatabaseRelation[]>();

  for (const relation of relations) {
    const existing = grouped.get(relation.schema_name) || [];
    existing.push(relation);
    grouped.set(relation.schema_name, existing);
  }

  return grouped;
}

// Utility: Filter relations
export function filterRelations(
  relations: DatabaseRelation[],
  options: {
    search?: string;
    schema?: string;
    exposedOnly?: boolean;
    type?: 'table' | 'view' | 'materialized_view' | 'all';
  }
): DatabaseRelation[] {
  let filtered = relations;

  // Filter by search term
  if (options.search) {
    const searchLower = options.search.toLowerCase();
    filtered = filtered.filter(
      (r) =>
        r.relation_name.toLowerCase().includes(searchLower) ||
        r.schema_name.toLowerCase().includes(searchLower)
    );
  }

  // Filter by schema
  if (options.schema && options.schema !== 'all') {
    if (options.schema === 'exposed') {
      filtered = filtered.filter((r) => r.is_exposed);
    } else {
      filtered = filtered.filter((r) => r.schema_name === options.schema);
    }
  }

  // Filter by exposed only
  if (options.exposedOnly) {
    filtered = filtered.filter((r) => r.is_exposed);
  }

  // Filter by type
  if (options.type && options.type !== 'all') {
    filtered = filtered.filter((r) => r.relation_type === options.type);
  }

  return filtered;
}

// Utility: Sort relations
export function sortRelations(
  relations: DatabaseRelation[],
  by: 'name' | 'rows' | 'schema' = 'name'
): DatabaseRelation[] {
  return [...relations].sort((a, b) => {
    // Exposed schemas always first
    if (a.is_exposed !== b.is_exposed) {
      return a.is_exposed ? -1 : 1;
    }

    switch (by) {
      case 'rows':
        return b.row_estimate - a.row_estimate;
      case 'schema':
        if (a.schema_name !== b.schema_name) {
          return a.schema_name.localeCompare(b.schema_name);
        }
        return a.relation_name.localeCompare(b.relation_name);
      case 'name':
      default:
        return a.relation_name.localeCompare(b.relation_name);
    }
  });
}

// Utility: Format row count
export function formatRowCount(count: number): string {
  if (count === 0) return '0 rows';
  if (count === 1) return '1 row';
  if (count < 1000) return `${count} rows`;
  if (count < 1_000_000) return `${(count / 1000).toFixed(1)}K rows`;
  return `${(count / 1_000_000).toFixed(1)}M rows`;
}
