// src/copilot/types.ts
// Shared types for the Copilot system

export type CopilotRole = "user" | "assistant" | "system";

export interface CopilotMessage {
  id: string;
  role: CopilotRole;
  content: string;
  createdAt: string;
  meta?: {
    source?: string;
    actionLabel?: string;
  };
}

export interface CopilotActionTemplate {
  id: string;
  label: string;
  description?: string;
  prompt: string;
}

export interface CopilotProfile {
  id: string;
  name: string;            // e.g. "Finance Copilot"
  slug: string;            // e.g. "finance"
  modelLabel?: string;     // e.g. "Claude", "GPT-4.1"
  targetModel: string;     // Odoo model or domain: "account.move", "project.task", etc.
}

export interface CopilotRecordSummary {
  id: number | string;
  model: string;           // e.g. "account.move"
  displayName: string;     // e.g. "INV/2026/0001"
  icon?: string;           // emoji or short label
  fields: Array<{ key: string; label: string; value: string | number | null }>;
}

export interface CopilotSessionState {
  messages: CopilotMessage[];
  actions: CopilotActionTemplate[];
  isLoading: boolean;
  error: string | null;
}

export interface CopilotSendOptions {
  fromActionId?: string;
  // can extend with temperature, modelOverride, etc.
}
