export type AgentIntent =
  | "capture.current_tab"
  | "capture.active_window"
  | "capture.full_screen"
  | "capture.and_analyze"
  | "capture.summarize_page";

const ALIASES: Record<string, AgentIntent> = {
  ss: "capture.active_window",
  sstab: "capture.current_tab",
  ssscreen: "capture.full_screen",
  "take a screenshot": "capture.active_window",
  "screenshot": "capture.active_window",
  "capture tab": "capture.current_tab",
  "analyze this page": "capture.and_analyze",
  "summarize what i'm viewing": "capture.summarize_page",
};

export function normalizeCommand(input: string): AgentIntent | null {
  const v = input.trim().toLowerCase();
  if (v in ALIASES) return ALIASES[v];

  // Fuzzy: if it contains "screen" or "desktop" → full screen
  if (/\b(screen|desktop)\b/.test(v)) return "capture.full_screen";
  // If it contains "tab" or "page" → current tab
  if (/\b(tab|page)\b/.test(v)) return "capture.current_tab";
  // If it contains "screenshot" or "capture" → active window (default)
  if (/\b(screenshot|capture|ss)\b/.test(v)) return "capture.active_window";

  return null;
}

export function isCapture(intent: AgentIntent): boolean {
  return intent.startsWith("capture.");
}
