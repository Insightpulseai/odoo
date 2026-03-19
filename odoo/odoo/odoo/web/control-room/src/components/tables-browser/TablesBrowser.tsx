'use client';

import { useState, useMemo, useCallback } from 'react';
import { Search, LayoutGrid, List, RefreshCw, Settings2 } from 'lucide-react';
import { useRelations, useSchemas, filterRelations, sortRelations, groupRelationsBySchema } from '@/hooks/useTables';
import { TableCard, TableCardSkeleton } from './TableCard';
import { SchemaFilter } from './SchemaFilter';
import clsx from 'clsx';

type ViewMode = 'grid' | 'list';
type SortBy = 'name' | 'rows' | 'schema';

export function TablesBrowser() {
  const [search, setSearch] = useState('');
  const [schemaFilter, setSchemaFilter] = useState('all');
  const [groupBySchema, setGroupBySchema] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('name');
  const [includeViews, setIncludeViews] = useState(true);

  const {
    data: relations,
    isLoading: relationsLoading,
    error: relationsError,
    refetch: refetchRelations,
  } = useRelations({ includeViews });

  const {
    data: schemas,
    isLoading: schemasLoading,
  } = useSchemas();

  // Filter and sort relations
  const filteredRelations = useMemo(() => {
    if (!relations) return [];

    const filtered = filterRelations(relations, {
      search,
      schema: schemaFilter,
    });

    return sortRelations(filtered, sortBy);
  }, [relations, search, schemaFilter, sortBy]);

  // Group by schema if enabled
  const groupedRelations = useMemo(() => {
    if (!groupBySchema) return null;
    return groupRelationsBySchema(filteredRelations);
  }, [filteredRelations, groupBySchema]);

  const handleRefresh = useCallback(() => {
    refetchRelations();
  }, [refetchRelations]);

  const isLoading = relationsLoading || schemasLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-white">Tables</h1>
        <p className="text-sm text-surface-300 mt-1">
          View and manage database tables and records. Click a table to view its structure and data.
        </p>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input
              type="text"
              placeholder="Search tables..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={clsx(
                'w-full sm:w-64 pl-9 pr-4 py-2 rounded-lg text-sm',
                'bg-surface-800 border border-surface-600 text-white placeholder-surface-400',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
              )}
            />
          </div>

          {/* Schema filter */}
          <SchemaFilter
            schemas={schemas || []}
            value={schemaFilter}
            onChange={setSchemaFilter}
            loading={schemasLoading}
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Include views toggle */}
          <label className="flex items-center gap-2 text-sm text-surface-300 cursor-pointer">
            <input
              type="checkbox"
              checked={includeViews}
              onChange={(e) => setIncludeViews(e.target.checked)}
              className="rounded border-surface-600 bg-surface-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-surface-900"
            />
            Views
          </label>

          {/* Group by schema toggle */}
          <label className="flex items-center gap-2 text-sm text-surface-300 cursor-pointer">
            <input
              type="checkbox"
              checked={groupBySchema}
              onChange={(e) => setGroupBySchema(e.target.checked)}
              className="rounded border-surface-600 bg-surface-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-surface-900"
            />
            Group
          </label>

          {/* View mode toggle */}
          <div className="flex items-center border border-surface-600 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={clsx(
                'p-2 transition-colors',
                viewMode === 'grid'
                  ? 'bg-surface-700 text-white'
                  : 'text-surface-400 hover:text-white hover:bg-surface-750'
              )}
              title="Grid view"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={clsx(
                'p-2 transition-colors',
                viewMode === 'list'
                  ? 'bg-surface-700 text-white'
                  : 'text-surface-400 hover:text-white hover:bg-surface-750'
              )}
              title="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className={clsx(
              'p-2 rounded-lg border border-surface-600 transition-colors',
              'text-surface-400 hover:text-white hover:bg-surface-750',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            title="Refresh"
          >
            <RefreshCw className={clsx('w-4 h-4', isLoading && 'animate-spin')} />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4 text-sm text-surface-400">
        <span>
          {filteredRelations.length} {filteredRelations.length === 1 ? 'table' : 'tables'}
        </span>
        {search && (
          <span className="text-surface-500">
            matching "{search}"
          </span>
        )}
      </div>

      {/* Error state */}
      {relationsError && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
          <p className="font-medium">Failed to load tables</p>
          <p className="text-sm mt-1">{relationsError.message}</p>
        </div>
      )}

      {/* Loading state */}
      {isLoading && !relations && (
        <div
          className={clsx(
            viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
              : 'space-y-2'
          )}
        >
          <TableCardSkeleton count={12} />
        </div>
      )}

      {/* Empty state */}
      {!isLoading && filteredRelations.length === 0 && (
        <div className="text-center py-12">
          <Settings2 className="w-12 h-12 text-surface-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No tables found</h3>
          <p className="text-sm text-surface-400">
            {search
              ? 'Try adjusting your search or filter criteria.'
              : 'No tables are available in the selected schema.'}
          </p>
        </div>
      )}

      {/* Tables list */}
      {!isLoading && filteredRelations.length > 0 && (
        <>
          {groupBySchema && groupedRelations ? (
            // Grouped view
            <div className="space-y-8">
              {Array.from(groupedRelations.entries()).map(([schemaName, schemaRelations]) => (
                <div key={schemaName}>
                  <div className="flex items-center gap-2 mb-3">
                    <h3 className="text-sm font-medium text-surface-300">{schemaName}</h3>
                    <span className="text-xs text-surface-500">
                      {schemaRelations.length} {schemaRelations.length === 1 ? 'table' : 'tables'}
                    </span>
                    {schemaRelations[0]?.is_exposed && (
                      <span className="px-1.5 py-0.5 text-[10px] font-medium bg-emerald-500/20 text-emerald-400 rounded">
                        exposed
                      </span>
                    )}
                  </div>
                  <div
                    className={clsx(
                      viewMode === 'grid'
                        ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
                        : 'space-y-2'
                    )}
                  >
                    {schemaRelations.map((relation) => (
                      <TableCard
                        key={`${relation.schema_name}.${relation.relation_name}`}
                        relation={relation}
                        showSchema={false}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            // Flat view
            <div
              className={clsx(
                viewMode === 'grid'
                  ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
                  : 'space-y-2'
              )}
            >
              {filteredRelations.map((relation) => (
                <TableCard
                  key={`${relation.schema_name}.${relation.relation_name}`}
                  relation={relation}
                  showSchema={true}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
