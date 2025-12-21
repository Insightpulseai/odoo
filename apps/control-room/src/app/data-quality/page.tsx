'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, Plus } from 'lucide-react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { Card, CardHeader } from '@/components/common/Card';
import { Badge, StatusBadge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { DataTable } from '@/components/tables/DataTable';
import type { DQIssue } from '@/types/api';

export default function DataQualityPage() {
  const [issues, setIssues] = useState<DQIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');
  const [showResolved, setShowResolved] = useState(false);

  const fetchIssues = async () => {
    setIsRefreshing(true);
    try {
      const params = new URLSearchParams();
      if (filter !== 'all') params.set('severity', filter);
      if (!showResolved) params.set('resolved', 'false');

      const res = await fetch(`/api/dq/issues?${params}`);
      if (res.ok) {
        const data = await res.json();
        setIssues(data.issues || []);
      }
    } catch (error) {
      console.error('Failed to fetch DQ issues:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, [filter, showResolved]);

  const handleCreateAction = async (issue: DQIssue) => {
    try {
      await fetch('/api/notion/actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectId: '',
          title: `DQ Issue: ${issue.description}`,
          source: 'DataQuality',
          sourceRef: `/data-quality#${issue.id}`,
        }),
      });
      alert('Action created in Notion');
    } catch (error) {
      console.error('Failed to create action:', error);
    }
  };

  const criticalCount = issues.filter(i => i.severity === 'critical').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;
  const infoCount = issues.filter(i => i.severity === 'info').length;

  const severityIcon = {
    critical: <AlertTriangle className="h-4 w-4 text-red-400" />,
    warning: <AlertTriangle className="h-4 w-4 text-amber-400" />,
    info: <Info className="h-4 w-4 text-blue-400" />,
  };

  const columns = [
    {
      key: 'severity',
      header: 'Severity',
      render: (issue: DQIssue) => (
        <div className="flex items-center gap-2">
          {severityIcon[issue.severity]}
          <StatusBadge status={issue.severity} />
        </div>
      ),
    },
    {
      key: 'table',
      header: 'Table',
      render: (issue: DQIssue) => (
        <span className="font-mono text-sm">{issue.table}</span>
      ),
    },
    {
      key: 'column',
      header: 'Column',
      render: (issue: DQIssue) => (
        <span className="font-mono text-sm text-surface-200">
          {issue.column || '-'}
        </span>
      ),
    },
    {
      key: 'issueType',
      header: 'Type',
      render: (issue: DQIssue) => (
        <Badge variant="neutral">{issue.issueType.replace('_', ' ')}</Badge>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (issue: DQIssue) => (
        <span className="text-sm">{issue.description}</span>
      ),
    },
    {
      key: 'detectedAt',
      header: 'Detected',
      render: (issue: DQIssue) => (
        <span className="text-sm text-surface-200">
          {new Date(issue.detectedAt).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (issue: DQIssue) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleCreateAction(issue)}
          leftIcon={<Plus className="h-3 w-3" />}
        >
          Action
        </Button>
      ),
    },
  ];

  return (
    <PageContainer>
      <Header
        title="Data Quality"
        subtitle="Data validation and integrity checks"
        onRefresh={fetchIssues}
        isRefreshing={isRefreshing}
      />

      <PageContent>
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{issues.length}</p>
              <p className="text-sm text-surface-200">Total Issues</p>
            </div>
          </Card>
          <Card className="border-red-500/30 bg-red-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-red-400">{criticalCount}</p>
              <p className="text-sm text-surface-200">Critical</p>
            </div>
          </Card>
          <Card className="border-amber-500/30 bg-amber-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-400">{warningCount}</p>
              <p className="text-sm text-surface-200">Warning</p>
            </div>
          </Card>
          <Card className="border-blue-500/30 bg-blue-500/5">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-400">{infoCount}</p>
              <p className="text-sm text-surface-200">Info</p>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-surface-200">Severity:</span>
              {(['all', 'critical', 'warning', 'info'] as const).map((sev) => (
                <button
                  key={sev}
                  onClick={() => setFilter(sev)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    filter === sev
                      ? 'bg-primary-500 text-white'
                      : 'bg-surface-700 text-surface-200 hover:bg-surface-600'
                  }`}
                >
                  {sev.charAt(0).toUpperCase() + sev.slice(1)}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2 text-sm text-surface-200">
                <input
                  type="checkbox"
                  checked={showResolved}
                  onChange={(e) => setShowResolved(e.target.checked)}
                  className="rounded border-surface-600 bg-surface-800 text-primary-500 focus:ring-primary-500"
                />
                Show Resolved
              </label>
            </div>
          </div>
        </Card>

        {/* Issues Table */}
        <Card padding="none">
          <div className="p-4 border-b border-surface-700">
            <h3 className="text-lg font-semibold text-white">Data Quality Issues</h3>
          </div>
          <DataTable
            columns={columns}
            data={issues}
            keyField="id"
            loading={loading}
            emptyMessage="No data quality issues found"
          />
        </Card>
      </PageContent>
    </PageContainer>
  );
}
