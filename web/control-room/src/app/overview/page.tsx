'use client';

import { useState, useEffect } from 'react';
import { DollarSign, TrendingDown, AlertTriangle, Activity, Clock, CheckCircle } from 'lucide-react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { KPICard } from '@/components/dashboard/KPICard';
import { HealthBadge, ServiceHealth } from '@/components/dashboard/HealthBadge';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { Card, CardHeader } from '@/components/common/Card';
import { BudgetBarChart } from '@/components/charts/BudgetChart';
import type { KPIsResponse, HealthResponse, Job } from '@/types/api';
import type { ActivityItem } from '@/types/models';

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

export default function OverviewPage() {
  const [kpis, setKpis] = useState<KPIsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      const [kpisRes, healthRes, jobsRes] = await Promise.all([
        fetch('/api/kpis'),
        fetch('/api/health'),
        fetch('/api/jobs'),
      ]);

      if (kpisRes.ok) setKpis(await kpisRes.json());
      if (healthRes.ok) setHealth(await healthRes.json());
      if (jobsRes.ok) {
        const data = await jobsRes.json();
        setJobs(data.jobs || []);
      }

      // Generate activities from jobs
      const jobActivities: ActivityItem[] = jobs.slice(0, 5).map((job, idx) => ({
        id: `job-${idx}`,
        type: 'job_run' as const,
        title: job.name,
        description: `${job.lastRunStatus}`,
        status: job.lastRunStatus === 'SUCCESS' ? 'success' :
                job.lastRunStatus === 'FAILED' ? 'error' :
                job.lastRunStatus === 'RUNNING' ? 'info' : 'warning',
        timestamp: job.lastRunTime || new Date().toISOString(),
        link: null,
      }));
      setActivities(jobActivities);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const failingJobs = jobs.filter(j => j.lastRunStatus === 'FAILED').length;
  const runningJobs = jobs.filter(j => j.lastRunStatus === 'RUNNING').length;

  // Sample chart data
  const budgetChartData = [
    { name: 'Infrastructure', budget: 250000, actual: 180000 },
    { name: 'Development', budget: 400000, actual: 350000 },
    { name: 'Operations', budget: 150000, actual: 160000 },
    { name: 'Marketing', budget: 100000, actual: 85000 },
    { name: 'HR', budget: 80000, actual: 75000 },
  ];

  return (
    <PageContainer>
      <Header
        title="Overview"
        subtitle="Control Room Dashboard"
        onRefresh={fetchData}
        isRefreshing={isRefreshing}
      />

      <PageContent>
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <KPICard
            title="Total Budget"
            value={kpis ? formatCurrency(kpis.totalBudget, kpis.currency) : '-'}
            icon={<DollarSign className="h-5 w-5 text-primary-400" />}
          />
          <KPICard
            title="Total Actual"
            value={kpis ? formatCurrency(kpis.totalActual, kpis.currency) : '-'}
            trend={kpis && kpis.burnRate > 80 ? 'up' : 'neutral'}
            trendValue={kpis ? `${kpis.burnRate.toFixed(0)}% burn` : ''}
            icon={<Activity className="h-5 w-5 text-emerald-400" />}
          />
          <KPICard
            title="Variance"
            value={kpis ? formatCurrency(kpis.varianceAmount, kpis.currency) : '-'}
            variant={kpis && kpis.varianceAmount < 0 ? 'error' : 'success'}
            trend={kpis && kpis.varianceAmount < 0 ? 'down' : 'up'}
            trendValue={kpis ? formatPercent(kpis.variancePct) : ''}
            icon={<TrendingDown className="h-5 w-5 text-amber-400" />}
          />
          <KPICard
            title="At-Risk Projects"
            value={kpis?.atRiskProjects ?? '-'}
            variant={kpis && kpis.atRiskProjects > 0 ? 'warning' : 'success'}
            subtitle={`of ${kpis?.activeProjects ?? 0} active`}
            icon={<AlertTriangle className="h-5 w-5 text-red-400" />}
          />
        </div>

        {/* Pipeline Health Summary */}
        <Card className="mb-6">
          <CardHeader
            title="Pipeline Health"
            action={health && <HealthBadge status={health.status} />}
          />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 bg-surface-900/50 rounded-lg">
              <Clock className="h-5 w-5 text-surface-400" />
              <div>
                <p className="text-sm text-surface-200">Last Sync</p>
                <p className="font-medium text-white">
                  {kpis?.dataFreshnessMinutes ?? 0} min ago
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-surface-900/50 rounded-lg">
              <Activity className="h-5 w-5 text-blue-400" />
              <div>
                <p className="text-sm text-surface-200">Running Jobs</p>
                <p className="font-medium text-white">{runningJobs}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-surface-900/50 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <div>
                <p className="text-sm text-surface-200">Failing Jobs</p>
                <p className="font-medium text-white">{failingJobs}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-surface-900/50 rounded-lg">
              <CheckCircle className="h-5 w-5 text-emerald-400" />
              <div>
                <p className="text-sm text-surface-200">Services</p>
                {health && <ServiceHealth services={health.services} />}
              </div>
            </div>
          </div>
        </Card>

        {/* Charts and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <BudgetBarChart data={budgetChartData} />
          </div>
          <div>
            <ActivityFeed activities={activities} maxItems={8} />
          </div>
        </div>
      </PageContent>
    </PageContainer>
  );
}
