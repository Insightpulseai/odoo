import { createClient } from '@supabase/supabase-js';

// Type definitions for ops.* schema
export interface OpsProject {
  project_id: string;
  name: string;
  repo_slug: string;
  odoo_version: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

export interface OpsEnvironment {
  env_id: string;
  project_id: string;
  env_type: 'dev' | 'staging' | 'prod';
  branch_pattern: string;
  db_name: string | null;
  created_at: string;
  updated_at: string;
  config: Record<string, any>;
}

export interface OpsRun {
  run_id: string;
  project_id: string;
  env_id: string;
  git_sha: string;
  git_ref: string;
  status: 'queued' | 'claimed' | 'running' | 'success' | 'failed' | 'cancelled';
  claimed_by: string | null;
  queued_at: string;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

export interface OpsRunEvent {
  event_id: string;
  run_id: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  payload: Record<string, any>;
  created_at: string;
}

export interface OpsArtifact {
  artifact_id: string;
  run_id: string;
  artifact_type: 'image' | 'sbom' | 'logs' | 'evidence' | 'manifest';
  storage_path: string;
  digest: string | null;
  size_bytes: number | null;
  created_at: string;
  metadata: Record<string, any>;
}

export interface OpsBackup {
  backup_id: string;
  env_id: string;
  backup_type: 'auto' | 'manual' | 'pre_migration';
  storage_path: string;
  size_bytes: number | null;
  created_at: string;
  metadata: Record<string, any>;
}

// Create typed Supabase client for ops schema
export function createOpsClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error('Missing Supabase environment variables');
  }

  return createClient(supabaseUrl, supabaseAnonKey);
}

// Typed query helpers
export const opsQueries = {
  // Projects
  async getAllProjects() {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as OpsProject[];
  },

  async getProject(projectId: string) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', projectId)
      .single();
    
    if (error) throw error;
    return data as OpsProject;
  },

  // Environments
  async getEnvironmentsByProject(projectId: string) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('environments')
      .select('*')
      .eq('project_id', projectId)
      .order('env_type', { ascending: true }); // dev, prod, staging
    
    if (error) throw error;
    return data as OpsEnvironment[];
  },

  // Runs
  async getRunsByProject(projectId: string, limit = 10) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('runs')
      .select('*')
      .eq('project_id', projectId)
      .order('created_at', { ascending: false })
      .limit(limit);
    
    if (error) throw error;
    return data as OpsRun[];
  },

  async getRunsByEnvironment(envId: string, limit = 10) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('runs')
      .select('*')
      .eq('env_id', envId)
      .order('created_at', { ascending: false })
      .limit(limit);
    
    if (error) throw error;
    return data as OpsRun[];
  },

  async getRun(runId: string) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('runs')
      .select('*')
      .eq('run_id', runId)
      .single();
    
    if (error) throw error;
    return data as OpsRun;
  },

  // Run Events
  async getRunEvents(runId: string, level?: OpsRunEvent['level']) {
    const supabase = createOpsClient();
    let query = supabase
      .from('run_events')
      .select('*')
      .eq('run_id', runId)
      .order('created_at', { ascending: true });
    
    if (level) {
      query = query.eq('level', level);
    }

    const { data, error } = await query;
    if (error) throw error;
    return data as OpsRunEvent[];
  },

  // Artifacts
  async getArtifactsByRun(runId: string) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('artifacts')
      .select('*')
      .eq('run_id', runId)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as OpsArtifact[];
  },

  // Backups
  async getBackupsByEnvironment(envId: string) {
    const supabase = createOpsClient();
    const { data, error } = await supabase
      .from('backups')
      .select('*')
      .eq('env_id', envId)
      .order('created_at', { ascending: false });
    
    if (error) throw error;
    return data as OpsBackup[];
  }
};

// Real-time subscriptions
export function subscribeToRunEvents(
  runId: string,
  callback: (event: OpsRunEvent) => void
) {
  const supabase = createOpsClient();
  
  const channel = supabase
    .channel(`run:${runId}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'ops',
        table: 'run_events',
        filter: `run_id=eq.${runId}`
      },
      (payload) => {
        callback(payload.new as OpsRunEvent);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}

export function subscribeToRunStatus(
  runId: string,
  callback: (run: OpsRun) => void
) {
  const supabase = createOpsClient();
  
  const channel = supabase
    .channel(`run:${runId}:status`)
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'ops',
        table: 'runs',
        filter: `run_id=eq.${runId}`
      },
      (payload) => {
        callback(payload.new as OpsRun);
      }
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}
