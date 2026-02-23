// apps/ops-console/components/platform/Visuals.tsx
import React from "react";

export const Badge = ({
  children,
  color = "#6b7280",
  outline = false,
}: {
  children: React.ReactNode;
  color?: string;
  outline?: boolean;
}) => (
  <span
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 4,
      padding: "2px 8px",
      borderRadius: 4,
      fontSize: 11,
      fontWeight: 600,
      fontFamily: "'JetBrains Mono', 'SF Mono', monospace",
      letterSpacing: 0.3,
      background: outline ? "transparent" : color + "18",
      color: color,
      border: outline ? `1px solid ${color}40` : "none",
    }}
  >
    {children}
  </span>
);

export const PlatformCard = ({
  title,
  subtitle,
  children,
  action,
  actionLabel,
  style = {},
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: () => void;
  actionLabel?: string;
  style?: React.CSSProperties;
}) => (
  <div
    style={{
      background: "#111113",
      border: "1px solid #1e1e22",
      borderRadius: 8,
      padding: 20,
      ...style,
    }}
  >
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: subtitle || children ? 14 : 0,
      }}
    >
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, color: "#e4e4e7" }}>
          {title}
        </div>
        {subtitle && (
          <div style={{ fontSize: 11, color: "#71717a", marginTop: 2 }}>
            {subtitle}
          </div>
        )}
      </div>
      {action && (
        <button
          onClick={action}
          style={{
            background: "#1e1e22",
            border: "1px solid #2e2e33",
            borderRadius: 5,
            color: "#a1a1aa",
            fontSize: 11,
            padding: "4px 10px",
            cursor: "pointer",
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          {actionLabel || "Action"}
        </button>
      )}
    </div>
    {children}
  </div>
);

export const Stat = ({
  label,
  value,
  sub,
  color = "#e4e4e7",
}: {
  label: string;
  value: string;
  sub?: string;
  color?: string;
}) => (
  <div style={{ textAlign: "center" }}>
    <div
      style={{
        fontSize: 28,
        fontWeight: 700,
        color,
        fontFamily: "'JetBrains Mono', monospace",
        lineHeight: 1,
      }}
    >
      {value}
    </div>
    <div
      style={{ fontSize: 11, color: "#71717a", marginTop: 4, fontWeight: 500 }}
    >
      {label}
    </div>
    {sub && (
      <div style={{ fontSize: 10, color: "#52525b", marginTop: 2 }}>{sub}</div>
    )}
  </div>
);
