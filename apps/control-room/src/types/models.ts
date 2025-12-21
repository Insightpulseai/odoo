/**
 * Domain Models for Control Room
 */

export interface Program {
  id: string;
  pageId: string;
  name: string;
  owner: string | null;
  startDate: string | null;
  endDate: string | null;
  status: 'Active' | 'On Hold' | 'Completed' | 'Cancelled';
  description: string | null;
  projectCount: number;
  totalBudget: number;
  totalActual: number;
}

export type JobStatus = 'SUCCESS' | 'FAILED' | 'RUNNING' | 'PENDING' | 'SKIPPED';

export type DQIssueType = 'null_rate' | 'schema_drift' | 'row_count_drop' | 'referential' | 'freshness';

export type DQSeverity = 'critical' | 'warning' | 'info';

export type AdvisorCategory = 'Cost' | 'Security' | 'Reliability' | 'OperationalExcellence' | 'Performance';

export type AdvisorImpact = 'High' | 'Medium' | 'Low';

export type RiskSeverity = 'Critical' | 'High' | 'Medium' | 'Low';

export type RiskProbability = 'High' | 'Medium' | 'Low';

export type RiskStatus = 'Open' | 'Mitigating' | 'Closed' | 'Accepted';

export type ProjectStatus = 'Planning' | 'In Progress' | 'Completed' | 'On Hold';

export type ProjectPriority = 'High' | 'Medium' | 'Low';

export type BudgetCategory = 'CapEx' | 'OpEx';

export type ActionSource = 'Advisor' | 'DataQuality' | 'Manual';

export interface SyncWatermark {
  databaseId: string;
  databaseName: string;
  lastSyncedAt: string;
  lastEditedTime: string;
  recordCount: number;
}

export interface PipelineHealth {
  totalJobs: number;
  successfulJobs: number;
  failedJobs: number;
  runningJobs: number;
  lastRunTime: string | null;
  overallStatus: 'healthy' | 'degraded' | 'unhealthy';
}

export interface DataQualitySummary {
  totalIssues: number;
  criticalIssues: number;
  warningIssues: number;
  infoIssues: number;
  tablesAffected: number;
  lastCheckTime: string | null;
}

export interface AdvisorSummary {
  totalRecommendations: number;
  byCategoryCount: Record<AdvisorCategory, number>;
  byImpactCount: Record<AdvisorImpact, number>;
  estimatedTotalSavings: number;
  currency: string;
}

export interface PortfolioSummary {
  totalPrograms: number;
  totalProjects: number;
  activeProjects: number;
  atRiskProjects: number;
  totalBudget: number;
  totalActual: number;
  varianceAmount: number;
  variancePct: number;
  burnRate: number;
  currency: string;
}

export interface ActivityItem {
  id: string;
  type: 'job_run' | 'dq_issue' | 'sync' | 'action';
  title: string;
  description: string | null;
  status: 'success' | 'warning' | 'error' | 'info';
  timestamp: string;
  link: string | null;
}
