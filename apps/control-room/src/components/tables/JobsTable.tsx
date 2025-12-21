'use client';

import { Clock, ExternalLink } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/Badge';
import { DataTable } from './DataTable';
import type { Job } from '@/types/api';

interface JobsTableProps {
  jobs: Job[];
  loading?: boolean;
  onJobClick?: (job: Job) => void;
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '-';
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

function formatTimeAgo(timestamp: string | null): string {
  if (!timestamp) return 'Never';
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function JobsTable({ jobs, loading, onJobClick }: JobsTableProps) {
  const columns = [
    {
      key: 'name',
      header: 'Job Name',
      render: (job: Job) => (
        <span className="font-medium">{job.name}</span>
      ),
    },
    {
      key: 'lastRunStatus',
      header: 'Status',
      render: (job: Job) => <StatusBadge status={job.lastRunStatus} />,
    },
    {
      key: 'lastRunTime',
      header: 'Last Run',
      render: (job: Job) => (
        <span className="text-surface-200">
          {formatTimeAgo(job.lastRunTime)}
        </span>
      ),
    },
    {
      key: 'lastRunDurationSeconds',
      header: 'Duration',
      render: (job: Job) => (
        <span className="flex items-center gap-1 text-surface-200">
          <Clock className="h-3.5 w-3.5" />
          {formatDuration(job.lastRunDurationSeconds)}
        </span>
      ),
    },
    {
      key: 'nextRunTime',
      header: 'Next Run',
      render: (job: Job) => (
        <span className="text-surface-200">
          {job.nextRunTime ? formatTimeAgo(job.nextRunTime) : '-'}
        </span>
      ),
    },
    {
      key: 'schedule',
      header: 'Schedule',
      render: (job: Job) => (
        <span className="text-xs font-mono text-surface-200">
          {job.schedule || '-'}
        </span>
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
        data={jobs}
        keyField="jobId"
        onRowClick={onJobClick}
        loading={loading}
        emptyMessage="No jobs configured"
      />
    </Card>
  );
}
