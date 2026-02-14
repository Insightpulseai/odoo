import { z } from 'zod';

// ============================================================================
// Core Agent Types
// ============================================================================

export type AgentType = 'governor' | 'dom-worker' | 'form-worker' | 'nav-worker' | 'extract-worker' | 'verify-worker';

export type MessageType =
  | 'task-assignment'
  | 'task-result'
  | 'task-error'
  | 'keepalive'
  | 'state-checkpoint'
  | 'hitl-request'
  | 'hitl-response';

export interface AgentMessage {
  id: string;
  from: AgentType;
  to: AgentType;
  type: MessageType;
  payload: unknown;
  timestamp: number;
  timeout: number; // milliseconds
}

// ============================================================================
// Mission Types
// ============================================================================

export type MissionStatus = 'pending' | 'active' | 'completed' | 'failed' | 'paused';

export const MissionSchema = z.object({
  id: z.string(),
  goal: z.string(),
  status: z.enum(['pending', 'active', 'completed', 'failed', 'paused']),
  steps: z.array(z.object({
    id: z.string(),
    description: z.string(),
    status: z.enum(['pending', 'in-progress', 'completed', 'failed']),
    worker: z.string().optional(),
    result: z.unknown().optional(),
    error: z.string().optional(),
    visualSignature: z.string().optional(),
    timestamp: z.number()
  })),
  createdAt: z.number(),
  updatedAt: z.number(),
  completedAt: z.number().optional()
});

export type Mission = z.infer<typeof MissionSchema>;

export interface MissionStep {
  id: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  worker?: AgentType;
  result?: unknown;
  error?: string;
  visualSignature?: string;
  timestamp: number;
}

// ============================================================================
// Vision Types
// ============================================================================

export interface VisualAnchor {
  visualSignature: string; // SHA-256 hash of visual region
  text?: string; // OCR extracted text
  boundingBox: BoundingBox;
  domSelector?: string; // Fallback CSS selector
  confidence: number; // 0-1
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface OCRResult {
  text: string;
  confidence: number;
  boundingBox: BoundingBox;
}

export interface VisualVerificationResult {
  success: boolean;
  confidence: number;
  diff?: ImageData;
  ssim?: number; // Structural similarity index
}

// ============================================================================
// Action Types
// ============================================================================

export type ActionType = 'click' | 'type' | 'scroll' | 'hover' | 'navigate' | 'extract';

export interface DOMAction {
  type: ActionType;
  target: VisualAnchor;
  payload?: {
    text?: string;
    x?: number;
    y?: number;
    url?: string;
  };
  retries: number;
  maxRetries: number;
}

// ============================================================================
// Storage Types
// ============================================================================

export interface Checkpoint {
  id: string;
  missionId: string;
  state: unknown; // Serialized Governor + Worker state
  timestamp: number;
}

export interface MemoryEntry {
  id: string;
  missionId: string;
  content: string;
  embedding?: number[]; // Future: Vector embedding
  timestamp: number;
  tags: string[];
}

// ============================================================================
// Identity Types
// ============================================================================

export interface DeviceIdentity {
  deviceId: string;
  publicKey: string; // Base64 encoded
  privateKey: string; // Base64 encoded, stored in IndexedDB
  createdAt: number;
}

export interface PairingRequest {
  deviceId: string;
  publicKey: string;
  challenge: string; // Nonce for handshake
  timestamp: number;
}

// ============================================================================
// LLM Types
// ============================================================================

export type ModelTier = 'local' | 'cloud-free' | 'cloud-premium';

export interface ModelConfig {
  tier: ModelTier;
  name: string;
  endpoint?: string; // For cloud models
  maxTokens: number;
  temperature: number;
}

export interface LLMResponse {
  text: string;
  model: string;
  tokens: number;
  latency: number; // milliseconds
  cost?: number; // USD
}

// ============================================================================
// Message Payloads
// ============================================================================

export interface TaskAssignmentPayload {
  taskId: string;
  action: DOMAction;
  context?: string;
}

export interface TaskResultPayload {
  taskId: string;
  success: boolean;
  result?: unknown;
  visualSignature?: string;
}

export interface TaskErrorPayload {
  taskId: string;
  error: string;
  recoverable: boolean;
}

export interface HITLRequestPayload {
  taskId: string;
  question: string;
  options?: string[];
  screenshot?: string; // Base64 encoded WebP
  timeout: number; // milliseconds
}

export interface HITLResponsePayload {
  taskId: string;
  approved: boolean;
  selectedOption?: string;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface Logger {
  debug(message: string, ...args: unknown[]): void;
  info(message: string, ...args: unknown[]): void;
  warn(message: string, ...args: unknown[]): void;
  error(message: string, ...args: unknown[]): void;
}

export type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };
