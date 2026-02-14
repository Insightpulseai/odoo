import { z } from 'zod';

// BugBot payload schema
export const BugBotPayloadSchema = z.object({
  source: z.string().default('unknown'),
  message: z.string().min(1, 'Message is required'),
  stack: z.string().optional(),
  service: z.string().optional(),
  severity: z.enum(['critical', 'high', 'medium', 'low']).optional(),
  tags: z.array(z.string()).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export type BugBotPayload = z.infer<typeof BugBotPayloadSchema>;

export interface BugBotResponse {
  ok: boolean;
  bug_analysis?: string;
  probable_cause?: string;
  impact?: string;
  recommended_actions?: string[];
  infra_context?: string;
  github_issue_url?: string;
  error?: string;
}

// Vercel Bot payload schema
export const VercelBotPayloadSchema = z.object({
  projectName: z.string().min(1, 'Project name is required'),
  action: z.enum(['status', 'suggest', 'health']).default('status'),
  deploymentId: z.string().optional(),
});

export type VercelBotPayload = z.infer<typeof VercelBotPayloadSchema>;

export interface VercelDeployment {
  uid: string;
  name: string;
  url: string;
  state: string;
  created: number;
  ready?: number;
  target?: string;
  inspectorUrl?: string;
}

export interface VercelBotResponse {
  ok: boolean;
  deployments?: VercelDeployment[];
  advice?: {
    decision: 'keep_current' | 'rollback' | 'investigate' | 'block_deploys';
    reason: string;
    candidateRollbackId?: string;
  };
  error?: string;
}

// Control Plane payload schema
export const ControlPlanePayloadSchema = z.object({
  secretName: z.string().min(1, 'Secret name is required'),
  mode: z.enum(['raw', 'exchange', 'proxy']).default('raw'),
  proxyTarget: z.string().url().optional(),
  proxyMethod: z.enum(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']).optional(),
  proxyBody: z.record(z.unknown()).optional(),
});

export type ControlPlanePayload = z.infer<typeof ControlPlanePayloadSchema>;

export interface ControlPlaneResponse {
  ok: boolean;
  secretName?: string;
  value?: string;
  proxiedResponse?: unknown;
  error?: string;
}

// DigitalOcean types
export interface DODroplet {
  id: number;
  name: string;
  status: string;
  size_slug: string;
  region: {
    slug: string;
    name: string;
  };
  vcpus: number;
  memory: number;
  disk: number;
  networks: {
    v4: Array<{
      ip_address: string;
      type: string;
    }>;
  };
  created_at: string;
}

export interface DODropletsResponse {
  droplets: DODroplet[];
}

// AI Gateway configuration
export interface AIGatewayConfig {
  provider: 'openai' | 'anthropic';
  model: string;
  temperature?: number;
  maxTokens?: number;
}

export const DEFAULT_AI_CONFIG: AIGatewayConfig = {
  provider: 'openai',
  model: 'gpt-4o-mini',
  temperature: 0.2,
  maxTokens: 2000,
};
