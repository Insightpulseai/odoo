/**
 * Lakehouse Executor - Type Definitions
 *
 * @module executor/types
 */

// ============================================================================
// RUN CONTEXT
// ============================================================================

export interface RunContext {
  runId: string;
  kind: string;
  spec: Record<string, unknown>;
  artifactBaseUri: string;
}

// ============================================================================
// PHASE RESULT
// ============================================================================

export interface PhaseResult {
  success: boolean;
  errorCode?: string;
  errorMessage?: string;
  artifacts?: ArtifactInfo[];
  outputManifest?: Record<string, unknown>;
}

export interface ArtifactInfo {
  kind: string;
  uri: string;
  sha256: string | null;
  sizeBytes: number | null;
  meta?: Record<string, unknown>;
}

// ============================================================================
// PHASE HANDLER
// ============================================================================

export interface PhaseCallbacks {
  emitEvent: (
    level: "debug" | "info" | "warn" | "error",
    message: string,
    data?: Record<string, unknown>
  ) => Promise<void>;
  registerArtifact: (
    kind: string,
    uri: string,
    sha256: string | null,
    sizeBytes: number | null,
    meta?: Record<string, unknown>
  ) => Promise<void>;
  heartbeat: () => Promise<boolean>;
}

export interface PhaseHandler {
  name: string;
  execute(
    ctx: RunContext,
    phaseSpec: Record<string, unknown>,
    callbacks: PhaseCallbacks
  ): Promise<PhaseResult>;
}

// ============================================================================
// EXECUTOR CONFIG
// ============================================================================

export interface ExecutorConfig {
  executorId: string;
  heartbeatIntervalMs: number;
  maxRetries: number;
  retryBackoffMs: number;
  phaseTimeoutMs: number;
}

// ============================================================================
// PIPELINE SPEC
// ============================================================================

export interface PipelineSpec {
  version: string;
  name: string;
  description?: string;
  phases: string[];
  phase_specs: Record<string, Record<string, unknown>>;
  input_manifest?: Record<string, unknown>;
  tags?: Record<string, string>;
}

// ============================================================================
// DATA QUALITY
// ============================================================================

export interface QualityCheck {
  name: string;
  type: "row_count" | "null_check" | "schema_drift" | "range_check" | "custom";
  column?: string;
  threshold?: number;
  expected?: unknown;
  sql?: string;
}

export interface QualityResult {
  check: QualityCheck;
  passed: boolean;
  actual?: unknown;
  message?: string;
}

// ============================================================================
// STORAGE
// ============================================================================

export interface StorageConfig {
  type: "s3" | "gcs" | "azure" | "local";
  bucket?: string;
  prefix?: string;
  region?: string;
}

// ============================================================================
// SQL EXECUTION
// ============================================================================

export interface SqlResult {
  columns: string[];
  rows: unknown[][];
  rowCount: number;
  executionTimeMs: number;
}
