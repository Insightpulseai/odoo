'use client';

import { useState, useEffect } from 'react';
import { PageContainer, PageContent } from '@/components/layout/PageContainer';
import { Header } from '@/components/layout/Header';
import { JobsTable } from '@/components/tables/JobsTable';
import { Card, CardHeader } from '@/components/common/Card';
import { StatusBadge } from '@/components/common/Badge';
import type { Job, JobRun } from '@/types/api';

export default function PipelinesPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobRuns, setJobRuns] = useState<JobRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchJobs = async () => {
    setIsRefreshing(true);
    try {
      const res = await fetch('/api/jobs');
      if (res.ok) {
        const data = await res.json();
        setJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const fetchJobRuns = async (jobId: string) => {
    try {
      const res = await fetch(`/api/job-runs?jobId=${jobId}&limit=10`);
      if (res.ok) {
        const data = await res.json();
        setJobRuns(data.runs || []);
      }
    } catch (error) {
      console.error('Failed to fetch job runs:', error);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (selectedJob) {
      fetchJobRuns(selectedJob.jobId);
    }
  }, [selectedJob]);

  const handleJobClick = (job: Job) => {
    setSelectedJob(job);
  };

  const successCount = jobs.filter(j => j.lastRunStatus === 'SUCCESS').length;
  const failedCount = jobs.filter(j => j.lastRunStatus === 'FAILED').length;
  const runningCount = jobs.filter(j => j.lastRunStatus === 'RUNNING').length;

  return (
    <PageContainer>
      <Header
        title="Pipelines"
        subtitle="Databricks job monitoring"
        onRefresh={fetchJobs}
        isRefreshing={isRefreshing}
      />

      <PageContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{jobs.length}</p>
              <p className="text-sm text-surface-200">Total Jobs</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-400">{successCount}</p>
              <p className="text-sm text-surface-200">Successful</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-400">{runningCount}</p>
              <p className="text-sm text-surface-200">Running</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-red-400">{failedCount}</p>
              <p className="text-sm text-surface-200">Failed</p>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Jobs List */}
          <div className="lg:col-span-2">
            <Card padding="none">
              <div className="p-4 border-b border-surface-700">
                <h3 className="text-lg font-semibold text-white">All Jobs</h3>
              </div>
              <JobsTable
                jobs={jobs}
                loading={loading}
                onJobClick={handleJobClick}
              />
            </Card>
          </div>

          {/* Job Details */}
          <div>
            <Card>
              <CardHeader
                title={selectedJob ? selectedJob.name : 'Select a Job'}
                subtitle={selectedJob ? `ID: ${selectedJob.jobId}` : 'Click on a job to see details'}
              />

              {selectedJob && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-2 border-b border-surface-700">
                    <span className="text-sm text-surface-200">Status</span>
                    <StatusBadge status={selectedJob.lastRunStatus} />
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-surface-700">
                    <span className="text-sm text-surface-200">Schedule</span>
                    <span className="text-sm font-mono text-white">
                      {selectedJob.schedule || 'Manual'}
                    </span>
                  </div>

                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-surface-200 mb-2">Recent Runs</h4>
                    <div className="space-y-2">
                      {jobRuns.length === 0 ? (
                        <p className="text-sm text-surface-400">No recent runs</p>
                      ) : (
                        jobRuns.slice(0, 5).map((run) => (
                          <div
                            key={run.runId}
                            className="flex items-center justify-between p-2 bg-surface-900/50 rounded"
                          >
                            <div className="flex items-center gap-2">
                              <StatusBadge status={run.status} />
                              <span className="text-xs text-surface-400">
                                {run.durationSeconds ? `${run.durationSeconds}s` : '-'}
                              </span>
                            </div>
                            <span className="text-xs text-surface-400">
                              {new Date(run.startTime).toLocaleString()}
                            </span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      </PageContent>
    </PageContainer>
  );
}
