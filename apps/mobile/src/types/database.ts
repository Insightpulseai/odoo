/**
 * Database Types for InsightPulse Mobile
 * Matches Supabase schema from Control Room
 */

export interface Database {
  public: {
    Tables: {
      control_room_jobs: {
        Row: Job
        Insert: Omit<Job, 'id' | 'created_at'>
        Update: Partial<Job>
      }
      approval_requests: {
        Row: ApprovalRequest
        Insert: Omit<ApprovalRequest, 'id' | 'created_at'>
        Update: Partial<ApprovalRequest>
      }
      kb_artifacts: {
        Row: KBArtifact
        Insert: Omit<KBArtifact, 'id' | 'created_at'>
        Update: Partial<KBArtifact>
      }
      finance_expense_claims: {
        Row: ExpenseClaim
        Insert: Omit<ExpenseClaim, 'id' | 'created_at' | 'claim_number'>
        Update: Partial<ExpenseClaim>
      }
      hr_employees: {
        Row: Employee
        Insert: Omit<Employee, 'id' | 'created_at'>
        Update: Partial<Employee>
      }
      notifications: {
        Row: Notification
        Insert: Omit<Notification, 'id' | 'created_at'>
        Update: Partial<Notification>
      }
    }
  }
}

// Job from control_room_jobs
export interface Job {
  id: string
  name: string
  job_type: 'etl' | 'report' | 'sync' | 'maintenance' | 'custom'
  status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled'
  progress?: number
  started_at?: string
  completed_at?: string
  duration_ms?: number
  error_message?: string
  metadata?: Record<string, unknown>
  created_by: string
  created_at: string
  updated_at: string
}

// Approval request
export interface ApprovalRequest {
  id: string
  request_type: 'expense_claim' | 'purchase_order' | 'leave_request' | 'budget_request'
  ref_id: string
  ref_name?: string
  amount?: number
  status: 'pending' | 'approved' | 'rejected' | 'escalated'
  assigned_to: string
  created_by: string
  approved_by?: string
  rejected_by?: string
  rejection_reason?: string
  created_at: string
  updated_at: string
}

// KB Artifact
export interface KBArtifact {
  id: string
  space_id?: string
  kind: 'prd' | 'architecture' | 'runbook' | 'api_reference' | 'data_dictionary' | 'documentation'
  title: string
  content: string
  personas?: string[]
  tags?: string[]
  created_by: string
  created_at: string
  updated_at: string
}

// Expense Claim
export interface ExpenseClaim {
  id: string
  claim_number: string
  employee_id: string
  department_id?: string
  title: string
  description?: string
  claim_date: string
  total_amount: number
  currency: string
  status: 'draft' | 'submitted' | 'pending_approval' | 'approved' | 'rejected' | 'paid' | 'cancelled'
  submitted_at?: string
  current_approver_id?: string
  approved_at?: string
  approved_by?: string
  rejected_at?: string
  rejected_by?: string
  rejection_reason?: string
  cost_center?: string
  created_at: string
  updated_at: string
}

// Employee
export interface Employee {
  id: string
  user_id?: string
  employee_number: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  department_id?: string
  job_position_id?: string
  manager_id?: string
  status: 'active' | 'on_leave' | 'terminated' | 'suspended'
  is_manager: boolean
  created_at: string
  updated_at: string
}

// Notification
export interface Notification {
  id: string
  type: string
  title: string
  body?: string
  data?: Record<string, unknown>
  read: boolean
  read_at?: string
  user_id: string
  created_at: string
}

// Job Stats for Dashboard
export interface JobStats {
  running: number
  succeeded: number
  failed: number
  queued: number
  total_today: number
  success_rate: number
}

// Approval Stats
export interface ApprovalStats {
  pending: number
  approved_today: number
  rejected_today: number
  avg_approval_time_hours: number
}
