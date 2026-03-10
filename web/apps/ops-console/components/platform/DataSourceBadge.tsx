// apps/ops-console/components/platform/DataSourceBadge.tsx
"use client";

import React, { useEffect, useState } from "react";

interface Attestation {
  mode: "live" | "mock";
  envName: string;
  buildSha: string;
  supabaseUrl: string;
  odooBaseUrl: string;
}

export const DataSourceBadge = () => {
  const [data, setData] = useState<Attestation | null>(null);

  useEffect(() => {
    fetch("/api/debug/datasources")
      .then((res) => res.json())
      .then(setData)
      .catch((err) => console.error("Failed to fetch attestation:", err));
  }, []);

  if (!data) return null;

  const isLive = data.mode === "live";

  return (
    <div
      style={{
        position: "fixed",
        bottom: 12,
        right: 12,
        background: isLive ? "rgba(34, 197, 94, 0.1)" : "rgba(234, 179, 8, 0.1)",
        border: `1px solid ${isLive ? "#22c55e" : "#eab308"}`,
        borderRadius: 4,
        padding: "4px 8px",
        fontSize: 10,
        fontFamily: "monospace",
        color: isLive ? "#22c55e" : "#eab308",
        pointerEvents: "none",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        gap: 2,
        backdropFilter: "blur(4px)",
      }}
    >
      <div style={{ fontWeight: "bold", display: "flex", alignItems: "center", gap: 4 }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: "currentColor" }} />
        {data.mode.toUpperCase()} MODE
      </div>
      <div style={{ opacity: 0.7 }}>
        {data.supabaseUrl} | {data.buildSha.slice(0, 7)}
      </div>
    </div>
  );
};
