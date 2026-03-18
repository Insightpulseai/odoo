'use client';

import { useState, useEffect } from 'react';
import {
  Table,
  TableHeader,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Button,
  Select,
  Input,
  Spinner,
  Tooltip,
} from '@fluentui/react-components';
import {
  ArrowClockwise24Regular,
  Search24Regular,
  Filter24Regular,
  Eye24Regular,
  ArrowSync24Regular,
} from '@fluentui/react-icons';
import type { Job, JobStatus, JobsFilters } from '@/types/observability';

const statusColors: Record<JobStatus, 'success' | 'warning' | 'danger' | 'informative' | 'subtle'> = {
  queued: 'informative',
  processing: 'warning',
  completed: 'success',
  failed: 'danger',
  cancelled: 'subtle',
  dead_letter: 'danger',
};

const statusLabels: Record<JobStatus, string> = {
  queued: 'Queued',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
  dead_letter: 'Dead Letter',
};

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return `${Math.floor(diffMins / 1440)}d ago`;
}

function formatDuration(durationMs?: number): string {
  if (!durationMs) return '-';
  if (durationMs < 1000) return `${durationMs}ms`;
  if (durationMs < 60000) return `${(durationMs / 1000).toFixed(1)}s`;
  return `${(durationMs / 60000).toFixed(1)}m`;
}

export function JobsTab() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<JobsFilters>({});
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const fetchJobs = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (filters.source) params.set('source', filters.source);
      if (filters.job_type) params.set('job_type', filters.job_type);
      if (filters.status) params.set('status', filters.status);
      params.set('limit', '50');

      const response = await fetch(`/api/observability/jobs?${params}`);
      if (!response.ok) throw new Error('Failed to fetch jobs');

      const data = await response.json();
      setJobs(data.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Use mock data for development
      setJobs(getMockJobs());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [filters]);

  const handleRetry = async (jobId: string) => {
    try {
      const response = await fetch(`/api/observability/jobs/${jobId}/retry`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchJobs();
      }
    } catch (err) {
      console.error('Failed to retry job:', err);
    }
  };

  if (isLoading && jobs.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="large" label="Loading jobs..." />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Filter24Regular className="text-surface-400" />
          <Select
            value={filters.source || ''}
            onChange={(_, data) => setFilters({ ...filters, source: data.value || undefined })}
          >
            <option value="">All Sources</option>
            <option value="n8n">n8n</option>
            <option value="odoo">Odoo</option>
            <option value="mcp">MCP</option>
            <option value="control-room">Control Room</option>
          </Select>
        </div>

        <Select
          value={filters.status || ''}
          onChange={(_, data) => setFilters({ ...filters, status: (data.value as JobStatus) || undefined })}
        >
          <option value="">All Status</option>
          <option value="queued">Queued</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="dead_letter">Dead Letter</option>
        </Select>

        <div className="flex-1" />

        <Button
          appearance="subtle"
          icon={<ArrowClockwise24Regular />}
          onClick={fetchJobs}
        >
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 text-sm">
          Using mock data: {error}
        </div>
      )}

      {/* Jobs Table */}
      <div className="border border-surface-100 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHeaderCell className="w-24">Status</TableHeaderCell>
              <TableHeaderCell>Source</TableHeaderCell>
              <TableHeaderCell>Type</TableHeaderCell>
              <TableHeaderCell>Priority</TableHeaderCell>
              <TableHeaderCell>Created</TableHeaderCell>
              <TableHeaderCell>Duration</TableHeaderCell>
              <TableHeaderCell className="w-24">Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id} className="hover:bg-surface-100/50">
                <TableCell>
                  <Badge color={statusColors[job.status]} appearance="filled">
                    {statusLabels[job.status]}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-sm">{job.source}</TableCell>
                <TableCell>{job.job_type}</TableCell>
                <TableCell>
                  <span className={job.priority >= 7 ? 'text-amber-400' : ''}>
                    P{job.priority}
                  </span>
                </TableCell>
                <TableCell className="text-surface-300">
                  {formatRelativeTime(job.created_at)}
                </TableCell>
                <TableCell className="font-mono text-sm text-surface-300">
                  {job.completed_at
                    ? formatDuration(
                        new Date(job.completed_at).getTime() - new Date(job.created_at).getTime()
                      )
                    : '-'}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Tooltip content="View Details" relationship="label">
                      <Button
                        appearance="subtle"
                        icon={<Eye24Regular />}
                        size="small"
                        onClick={() => setSelectedJob(job)}
                      />
                    </Tooltip>
                    {(job.status === 'failed' || job.status === 'dead_letter') && (
                      <Tooltip content="Retry" relationship="label">
                        <Button
                          appearance="subtle"
                          icon={<ArrowSync24Regular />}
                          size="small"
                          onClick={() => handleRetry(job.id)}
                        />
                      </Tooltip>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {jobs.length === 0 && !isLoading && (
        <div className="text-center py-8 text-surface-400">
          No jobs found matching your filters
        </div>
      )}
    </div>
  );
}

// Mock data for development
function getMockJobs(): Job[] {
  return [
    {
      id: '1',
      source: 'n8n',
      job_type: 'sync',
      payload: {},
      priority: 5,
      status: 'completed',
      max_retries: 3,
      retry_count: 0,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date(Date.now() - 3500000).toISOString(),
      completed_at: new Date(Date.now() - 3500000).toISOString(),
    },
    {
      id: '2',
      source: 'mcp',
      job_type: 'discovery',
      payload: {},
      priority: 8,
      status: 'processing',
      max_retries: 3,
      retry_count: 0,
      claimed_by: 'worker-1',
      created_at: new Date(Date.now() - 300000).toISOString(),
      updated_at: new Date(Date.now() - 60000).toISOString(),
    },
    {
      id: '3',
      source: 'odoo',
      job_type: 'validation',
      payload: {},
      priority: 3,
      status: 'queued',
      max_retries: 3,
      retry_count: 0,
      created_at: new Date(Date.now() - 120000).toISOString(),
      updated_at: new Date(Date.now() - 120000).toISOString(),
    },
    {
      id: '4',
      source: 'control-room',
      job_type: 'etl',
      payload: {},
      priority: 5,
      status: 'failed',
      max_retries: 3,
      retry_count: 2,
      created_at: new Date(Date.now() - 7200000).toISOString(),
      updated_at: new Date(Date.now() - 7000000).toISOString(),
    },
    {
      id: '5',
      source: 'n8n',
      job_type: 'notification',
      payload: {},
      priority: 2,
      status: 'dead_letter',
      max_retries: 3,
      retry_count: 3,
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date(Date.now() - 86000000).toISOString(),
    },
  ];
}

export default JobsTab;
