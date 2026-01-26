/**
 * Marketplace Webhook Handler Types
 * Defines interfaces for webhook events, integrations, and sync operations
 */

// Supported providers
export type Provider =
  | 'github'
  | 'google_drive'
  | 'google_docs'
  | 'google_sheets'
  | 'gmail'
  | 'aws_s3'
  | 'cloudflare_r2'
  | 'slack'
  | 'notion'
  | 'n8n'
  | 'vercel'
  | 'digitalocean';

// Webhook event status
export type EventStatus = 'received' | 'processing' | 'processed' | 'failed';

// Sync status
export type SyncStatus = 'pending' | 'syncing' | 'completed' | 'failed' | 'skipped';

// Integration status
export type IntegrationStatus = 'active' | 'paused' | 'disabled' | 'error';

// Health status
export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'unknown';

/**
 * Incoming webhook request
 */
export interface WebhookRequest {
  source: Provider;
  event_type: string;
  event_id?: string;
  payload: Record<string, unknown>;
  signature?: string;
  timestamp?: string;
}

/**
 * Webhook event record in database
 */
export interface WebhookEvent {
  id: string;
  integration_id: string | null;
  source: string;
  event_type: string;
  event_id: string | null;
  payload: Record<string, unknown>;
  headers: Record<string, string>;
  signature: string | null;
  verified: boolean;
  processed: boolean;
  processed_at: string | null;
  error_message: string | null;
  retry_count: number;
  created_at: string;
}

/**
 * Integration configuration
 */
export interface Integration {
  id: string;
  slug: string;
  name: string;
  provider: Provider;
  category: string;
  config: Record<string, unknown>;
  status: IntegrationStatus;
  health_status: HealthStatus;
  last_health_check: string | null;
  error_message: string | null;
}

/**
 * Artifact sync record
 */
export interface ArtifactSync {
  id: string;
  source_provider: string;
  source_path: string;
  source_ref: string | null;
  destination_provider: string;
  destination_path: string;
  destination_ref: string | null;
  artifact_type: string;
  artifact_name: string;
  size_bytes: number | null;
  checksum: string | null;
  status: SyncStatus;
  error_message: string | null;
  metadata: Record<string, unknown>;
  triggered_by: string;
  job_run_id: string | null;
  created_at: string;
  completed_at: string | null;
}

/**
 * Sync rule configuration
 */
export interface SyncRule {
  id: string;
  name: string;
  destination_integration_id: string;
  destination_template: string;
  transform_config: Record<string, unknown>;
  priority: number;
}

/**
 * GitHub-specific event payloads
 */
export interface GitHubWorkflowRunPayload {
  action: 'completed' | 'requested' | 'in_progress';
  workflow_run: {
    id: number;
    name: string;
    head_sha: string;
    head_branch: string;
    conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null;
    html_url: string;
    artifacts_url: string;
    repository: {
      full_name: string;
    };
  };
  repository: {
    full_name: string;
    name: string;
    owner: {
      login: string;
    };
  };
}

export interface GitHubArtifact {
  id: number;
  name: string;
  size_in_bytes: number;
  archive_download_url: string;
  expired: boolean;
  created_at: string;
  updated_at: string;
}

export interface GitHubArtifactsResponse {
  total_count: number;
  artifacts: GitHubArtifact[];
}

/**
 * Google Drive-specific types
 */
export interface GoogleDriveUploadResult {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  parents: string[];
}

export interface GoogleDriveChangeEvent {
  kind: string;
  type: string;
  fileId: string;
  time: string;
  removed: boolean;
  file?: {
    name: string;
    mimeType: string;
    modifiedTime: string;
  };
}

/**
 * S3-specific types
 */
export interface S3UploadResult {
  bucket: string;
  key: string;
  etag: string;
  location: string;
  size_bytes: number;
}

export interface S3EventRecord {
  eventSource: string;
  eventName: string;
  s3: {
    bucket: {
      name: string;
    };
    object: {
      key: string;
      size: number;
      eTag: string;
    };
  };
}

/**
 * Handler response
 */
export interface HandlerResponse {
  success: boolean;
  event_id?: string;
  syncs_created?: number;
  syncs_completed?: number;
  error?: string;
  details?: Record<string, unknown>;
}

/**
 * Vault secret reference
 */
export interface VaultSecret {
  id: string;
  name: string;
  secret: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

/**
 * OAuth token (stored reference, actual token in Vault)
 */
export interface OAuthToken {
  id: string;
  integration_id: string;
  user_id: string | null;
  token_type: string;
  access_token_vault_id: string | null;
  refresh_token_vault_id: string | null;
  scopes: string[];
  expires_at: string | null;
  refresh_expires_at: string | null;
}

/**
 * API quota tracking
 */
export interface ApiQuota {
  id: string;
  integration_id: string;
  quota_type: string;
  period: 'hourly' | 'daily' | 'monthly';
  limit_value: number;
  used_value: number;
  reset_at: string;
}

/**
 * Rate limiter state
 */
export interface RateLimitState {
  remaining: number;
  limit: number;
  reset_at: Date;
  retry_after?: number;
}
