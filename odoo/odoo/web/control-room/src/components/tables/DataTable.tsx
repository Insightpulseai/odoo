'use client';

import { ReactNode } from 'react';
import clsx from 'clsx';

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: keyof T;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  loading?: boolean;
}

export function DataTable<T>({
  columns,
  data,
  keyField,
  onRowClick,
  emptyMessage = 'No data available',
  loading = false,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-surface-200">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-surface-700">
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className={clsx(
                  'px-4 py-3 text-left text-xs font-medium text-surface-200 uppercase tracking-wider',
                  column.className
                )}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-800">
          {data.map((item) => (
            <tr
              key={String(item[keyField])}
              onClick={() => onRowClick?.(item)}
              className={clsx(
                'transition-colors',
                onRowClick
                  ? 'cursor-pointer hover:bg-surface-800/50'
                  : ''
              )}
            >
              {columns.map((column) => (
                <td
                  key={String(column.key)}
                  className={clsx(
                    'px-4 py-3 text-sm text-white',
                    column.className
                  )}
                >
                  {column.render
                    ? column.render(item)
                    : String((item as any)[column.key] ?? '-')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pageSize, total, onPageChange }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize);
  const startItem = (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-surface-700">
      <p className="text-sm text-surface-200">
        Showing {startItem} to {endItem} of {total} results
      </p>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="px-3 py-1 text-sm rounded-md bg-surface-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-600 transition-colors"
        >
          Previous
        </button>
        <span className="text-sm text-surface-200">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-3 py-1 text-sm rounded-md bg-surface-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-600 transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
