/**
 * Shared activity timeline types for Pulser copilot.
 *
 * Used by both Owl (Odoo systray) and React (web/ops) renderers.
 * Backend emits this contract; frontend renders it.
 */

export type ActivityStatus = "pending" | "active" | "done" | "error" | "blocked";

export interface CopilotActivity {
    id: string;
    label: string;
    status: ActivityStatus;
    ts?: string;
    meta?: Record<string, unknown>;
}

export interface CopilotResponse {
    content: string;
    blocked: boolean;
    reason: string;
    conversation_id?: string | number;
    skill: string;
    activities: CopilotActivity[];
}
