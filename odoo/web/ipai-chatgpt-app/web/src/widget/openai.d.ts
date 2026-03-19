export {};

declare global {
  interface Window {
    openai?: {
      toolOutput?: Record<string, unknown>;
      toolInput?: Record<string, unknown>;
      theme?: string;
      callTool?: (name: string, args?: Record<string, unknown>) => Promise<unknown>;
      sendFollowUpMessage?: (arg: { prompt: string }) => Promise<void>;
      setWidgetState?: (state: unknown) => void;
      widgetState?: unknown;
    };
  }
}
