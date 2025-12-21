'use client';

import { ExternalLink, AlertTriangle } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { StatusBadge, Badge } from '@/components/common/Badge';
import { DataTable, Pagination } from './DataTable';
import type { Project } from '@/types/api';

interface ProjectsTableProps {
  projects: Project[];
  total: number;
  page: number;
  pageSize: number;
  loading?: boolean;
  onPageChange: (page: number) => void;
  onProjectClick?: (project: Project) => void;
}

function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatPercent(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
}

export function ProjectsTable({
  projects,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onProjectClick,
}: ProjectsTableProps) {
  const columns = [
    {
      key: 'name',
      header: 'Project',
      render: (project: Project) => (
        <div>
          <span className="font-medium">{project.name}</span>
          {project.programName && (
            <p className="text-xs text-surface-400">{project.programName}</p>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (project: Project) => <StatusBadge status={project.status} />,
    },
    {
      key: 'priority',
      header: 'Priority',
      render: (project: Project) => <StatusBadge status={project.priority} />,
    },
    {
      key: 'budgetTotal',
      header: 'Budget',
      render: (project: Project) => (
        <span className="font-mono">
          {formatCurrency(project.budgetTotal, project.currency)}
        </span>
      ),
    },
    {
      key: 'actualTotal',
      header: 'Actual',
      render: (project: Project) => (
        <span className="font-mono">
          {formatCurrency(project.actualTotal, project.currency)}
        </span>
      ),
    },
    {
      key: 'varianceAmount',
      header: 'Variance',
      render: (project: Project) => (
        <div className="flex items-center gap-2">
          <span
            className={`font-mono ${
              project.varianceAmount >= 0 ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {formatCurrency(project.varianceAmount, project.currency)}
          </span>
          <span
            className={`text-xs ${
              project.variancePct >= 0 ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            ({formatPercent(project.variancePct)})
          </span>
        </div>
      ),
    },
    {
      key: 'riskCount',
      header: 'Risks',
      render: (project: Project) => (
        <div className="flex items-center gap-1">
          {project.riskCount > 0 ? (
            <>
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <span className="text-amber-400">{project.riskCount}</span>
            </>
          ) : (
            <span className="text-surface-400">-</span>
          )}
        </div>
      ),
    },
    {
      key: 'owner',
      header: 'Owner',
      render: (project: Project) => (
        <span className="text-surface-200">{project.owner || '-'}</span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: () => (
        <ExternalLink className="h-4 w-4 text-surface-400 hover:text-white transition-colors" />
      ),
      className: 'w-10',
    },
  ];

  return (
    <Card padding="none">
      <DataTable
        columns={columns}
        data={projects}
        keyField="id"
        onRowClick={onProjectClick}
        loading={loading}
        emptyMessage="No projects found"
      />
      <Pagination
        page={page}
        pageSize={pageSize}
        total={total}
        onPageChange={onPageChange}
      />
    </Card>
  );
}
