// apps/ops-console/lib/visuals.ts

export const ago = (iso: string | null) => {
  if (!iso) return "—";
  const d = (Date.now() - new Date(iso).getTime()) / 1000;
  if (d < 60) return `${Math.floor(d)}s ago`;
  if (d < 3600) return `${Math.floor(d / 60)}m ago`;
  if (d < 86400) return `${Math.floor(d / 3600)}h ago`;
  return `${Math.floor(d / 86400)}d ago`;
};

export const statusColor = (s: string) => ({
  success: "#22c55e",
  warning: "#eab308",
  failed: "#ef4444",
  building: "#3b82f6",
  pending: "#6b7280",
  synced: "#22c55e",
  stale: "#eab308",
  error: "#ef4444",
  idle: "#6b7280",
}[s] || "#6b7280");

export const statusIcon = (s: string) => ({
  success: "✓",
  warning: "⚠",
  failed: "✕",
  building: "◉",
  pending: "○",
  synced: "✓",
  stale: "◷",
  error: "✕",
  idle: "○",
}[s] || "○");

export const roleColor = (r: string) => ({
  admin: "#a78bfa",
  manager: "#60a5fa",
  supervisor: "#34d399",
  viewer: "#9ca3af",
}[r] || "#9ca3af");
