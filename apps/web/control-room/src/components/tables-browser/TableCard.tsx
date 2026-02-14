'use client';

import Link from 'next/link';
import { Table, Eye, Layers, Database } from 'lucide-react';
import { DatabaseRelation } from '@/lib/supabase';
import { formatRowCount } from '@/hooks/useTables';
import clsx from 'clsx';

interface TableCardProps {
  relation: DatabaseRelation;
  showSchema?: boolean;
}

const relationTypeIcons: Record<string, typeof Table> = {
  table: Table,
  view: Eye,
  materialized_view: Layers,
  partitioned_table: Database,
  other: Database,
};

const relationTypeColors: Record<string, string> = {
  table: 'text-blue-400',
  view: 'text-purple-400',
  materialized_view: 'text-amber-400',
  partitioned_table: 'text-emerald-400',
  other: 'text-surface-400',
};

export function TableCard({ relation, showSchema = true }: TableCardProps) {
  const Icon = relationTypeIcons[relation.relation_type] || Database;
  const iconColor = relationTypeColors[relation.relation_type] || 'text-surface-400';

  return (
    <Link
      href={`/settings/database/tables/${encodeURIComponent(relation.schema_name)}/${encodeURIComponent(relation.relation_name)}`}
      className={clsx(
        'group block p-4 rounded-lg border transition-all duration-150',
        'bg-surface-800 border-surface-700',
        'hover:bg-surface-750 hover:border-surface-600 hover:shadow-md',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-surface-900'
      )}
    >
      <div className="flex items-start gap-3">
        <div className={clsx('p-2 rounded-md bg-surface-700/50', iconColor)}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-white truncate group-hover:text-blue-400 transition-colors">
              {relation.relation_name}
            </h4>
            {relation.is_exposed && (
              <span className="shrink-0 px-1.5 py-0.5 text-[10px] font-medium bg-emerald-500/20 text-emerald-400 rounded">
                exposed
              </span>
            )}
          </div>
          {showSchema && (
            <p className="text-xs text-surface-400 mt-0.5 truncate">
              {relation.schema_name}
            </p>
          )}
          <p className="text-xs text-surface-300 mt-1">
            {formatRowCount(relation.row_estimate)}
          </p>
        </div>
      </div>
    </Link>
  );
}

interface TableCardSkeletonProps {
  count?: number;
}

export function TableCardSkeleton({ count = 6 }: TableCardSkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="p-4 rounded-lg border bg-surface-800 border-surface-700 animate-pulse"
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-md bg-surface-700" />
            <div className="flex-1">
              <div className="h-4 w-32 bg-surface-700 rounded mb-2" />
              <div className="h-3 w-20 bg-surface-700 rounded mb-1" />
              <div className="h-3 w-16 bg-surface-700 rounded" />
            </div>
          </div>
        </div>
      ))}
    </>
  );
}
