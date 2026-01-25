'use client';

import { use } from 'react';
import Link from 'next/link';
import { ArrowLeft, Table, Key, RefreshCw, Copy, Check } from 'lucide-react';
import { useTableDetails, formatRowCount } from '@/hooks/useTables';
import clsx from 'clsx';
import { useState } from 'react';

interface PageProps {
  params: Promise<{
    schema: string;
    table: string;
  }>;
}

export default function TableDetailPage({ params }: PageProps) {
  const { schema, table } = use(params);
  const decodedSchema = decodeURIComponent(schema);
  const decodedTable = decodeURIComponent(table);

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useTableDetails(decodedSchema, decodedTable, {
    includeRows: true,
    limit: 100,
  });

  const [copiedColumn, setCopiedColumn] = useState<string | null>(null);

  const copyColumnName = (name: string) => {
    navigator.clipboard.writeText(name);
    setCopiedColumn(name);
    setTimeout(() => setCopiedColumn(null), 2000);
  };

  return (
    <div className="min-h-screen bg-surface-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm">
          <Link
            href="/settings/database/tables"
            className="flex items-center gap-1 text-surface-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Tables
          </Link>
          <span className="text-surface-600">/</span>
          <span className="text-surface-400">{decodedSchema}</span>
          <span className="text-surface-600">/</span>
          <span className="text-white font-medium">{decodedTable}</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
                <Table className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-white">
                  {decodedTable}
                </h1>
                <p className="text-sm text-surface-400 mt-0.5">
                  {decodedSchema} schema
                  {data?.row_count !== null && (
                    <span className="ml-2">
                      • {formatRowCount(data.row_count)}
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={() => refetch()}
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

        {/* Error state */}
        {error && (
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
            <p className="font-medium">Failed to load table details</p>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
        )}

        {/* Loading state */}
        {isLoading && !data && (
          <div className="space-y-6">
            <div className="h-64 bg-surface-800 rounded-lg animate-pulse" />
            <div className="h-96 bg-surface-800 rounded-lg animate-pulse" />
          </div>
        )}

        {/* Content */}
        {data && (
          <div className="space-y-6">
            {/* Columns */}
            <div className="bg-surface-800 border border-surface-700 rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-surface-700">
                <h2 className="text-sm font-medium text-white">
                  Columns ({data.columns.length})
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-surface-700 text-left">
                      <th className="px-4 py-2 text-surface-400 font-medium">Name</th>
                      <th className="px-4 py-2 text-surface-400 font-medium">Type</th>
                      <th className="px-4 py-2 text-surface-400 font-medium">Nullable</th>
                      <th className="px-4 py-2 text-surface-400 font-medium">Default</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.columns.map((column) => (
                      <tr
                        key={column.column_name}
                        className="border-b border-surface-700/50 hover:bg-surface-750 transition-colors"
                      >
                        <td className="px-4 py-2">
                          <div className="flex items-center gap-2">
                            {column.is_primary_key && (
                              <Key className="w-3 h-3 text-amber-400" title="Primary Key" />
                            )}
                            <span className="text-white font-mono text-xs">
                              {column.column_name}
                            </span>
                            <button
                              onClick={() => copyColumnName(column.column_name)}
                              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-surface-600 text-surface-400 hover:text-white transition-all"
                              title="Copy column name"
                            >
                              {copiedColumn === column.column_name ? (
                                <Check className="w-3 h-3 text-emerald-400" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        </td>
                        <td className="px-4 py-2 font-mono text-xs text-surface-300">
                          {column.data_type}
                        </td>
                        <td className="px-4 py-2 text-surface-400">
                          {column.is_nullable ? 'Yes' : 'No'}
                        </td>
                        <td className="px-4 py-2 font-mono text-xs text-surface-400 max-w-[200px] truncate">
                          {column.column_default || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Sample Rows */}
            <div className="bg-surface-800 border border-surface-700 rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-surface-700">
                <h2 className="text-sm font-medium text-white">
                  Data Preview ({data.rows.length} rows)
                </h2>
              </div>
              {data.rows.length === 0 ? (
                <div className="px-4 py-8 text-center text-surface-400">
                  No rows to display
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-700 text-left">
                        {data.columns.slice(0, 10).map((column) => (
                          <th
                            key={column.column_name}
                            className="px-4 py-2 text-surface-400 font-medium font-mono text-xs whitespace-nowrap"
                          >
                            {column.column_name}
                          </th>
                        ))}
                        {data.columns.length > 10 && (
                          <th className="px-4 py-2 text-surface-500 font-medium text-xs">
                            +{data.columns.length - 10} more
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.slice(0, 50).map((row, rowIndex) => (
                        <tr
                          key={rowIndex}
                          className="border-b border-surface-700/50 hover:bg-surface-750 transition-colors"
                        >
                          {data.columns.slice(0, 10).map((column) => (
                            <td
                              key={column.column_name}
                              className="px-4 py-2 font-mono text-xs text-surface-300 max-w-[200px] truncate"
                            >
                              {formatCellValue(row[column.column_name])}
                            </td>
                          ))}
                          {data.columns.length > 10 && (
                            <td className="px-4 py-2 text-surface-500 text-xs">...</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {data.rows.length > 50 && (
                <div className="px-4 py-2 border-t border-surface-700 text-xs text-surface-500">
                  Showing 50 of {data.rows.length} rows
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function formatCellValue(value: unknown): string {
  if (value === null) return 'null';
  if (value === undefined) return '';
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return '[object]';
    }
  }
  return String(value);
}
