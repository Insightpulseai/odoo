/**
 * API Response Types for Control Room
 */

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    databricks: 'connected' | 'disconnected';
    notion: 'connected' | 'disconnected';
  };
}

export interface KPIsResponse {
  totalBudget: number;
  totalActual: number;
  varianceAmount: number;
  variancePct: number;
  burnRate: number;
  atRiskProjects: number;
  activeProjects: number;
  lastSyncTime: string;
  dataFreshnessMinutes: number;
  currency: string;
}

export interface Job {
  jobId: string;
  name: string;
  lastRunStatus: 'SUCCESS' | 'FAILED' | 'RUNNING' | 'PENDING' | 'SKIPPED';
  lastRunTime: string | null;
  lastRunDurationSeconds: number | null;
  nextRunTime: string | null;
  schedule: string | null;
}

export interface JobRun {
  runId: string;
  jobId: string;
  jobName: string;
  status: 'SUCCESS' | 'FAILED' | 'RUNNING' | 'PENDING' | 'CANCELLED';
  startTime: string;
  endTime: string | null;
  durationSeconds: number | null;
  errorMessage: string | null;
  triggeredBy: 'SCHEDULE' | 'MANUAL' | 'RETRY';
}

export interface DQIssue {
  id: string;
  table: string;
  column: string | null;
  issueType: 'null_rate' | 'schema_drift' | 'row_count_drop' | 'referential' | 'freshness';
  severity: 'critical' | 'warning' | 'info';
  description: string;
  currentValue: string | null;
  expectedValue: string | null;
  detectedAt: string;
  resolved: boolean;
  resolvedAt: string | null;
}

export interface AdvisorRecommendation {
  id: string;
  category: 'Cost' | 'Security' | 'Reliability' | 'OperationalExcellence' | 'Performance';
  impact: 'High' | 'Medium' | 'Low';
  impactedResource: string;
  resourceType: string;
  shortDescription: string;
  estimatedSavings: number | null;
  currency: string;
  detectedAt: string;
  dismissed: boolean;
}

export interface Project {
  id: string;
  pageId: string;
  name: string;
  programId: string | null;
  programName: string | null;
  budgetTotal: number;
  actualTotal: number;
  varianceAmount: number;
  variancePct: number;
  currency: string;
  startDate: string | null;
  endDate: string | null;
  status: string;
  priority: string;
  owner: string | null;
  riskCount: number;
  atRiskBudgetLines: number;
}

export interface ProjectDetail extends Project {
  budgetLines: BudgetLine[];
  risks: Risk[];
}

export interface BudgetLine {
  id: string;
  projectId: string;
  category: 'CapEx' | 'OpEx';
  vendor: string | null;
  description: string | null;
  amount: number;
  actualAmount: number | null;
  committedDate: string | null;
  invoiceDate: string | null;
  paidDate: string | null;
  currency: string;
}

export interface Risk {
  id: string;
  projectId: string;
  title: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  probability: 'High' | 'Medium' | 'Low';
  status: 'Open' | 'Mitigating' | 'Closed' | 'Accepted';
  mitigation: string | null;
  owner: string | null;
}

export interface CreateActionRequest {
  projectId: string;
  title: string;
  assignee?: string;
  dueDate?: string;
  source: 'Advisor' | 'DataQuality' | 'Manual';
  sourceRef?: string;
}

export interface CreateActionResponse {
  success: boolean;
  notionPageId?: string;
  notionUrl?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface APIError {
  error: string;
  message: string;
  code?: string;
}
