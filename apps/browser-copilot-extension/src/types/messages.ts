export { ExtensionMessage, SidePanelCommand, CaptureComplete, CaptureError } from "@ipai/browser-agent-contract";

export interface SessionContext {
  sessionId: string;
  conversationId?: string;
  attachments: string[];
}
