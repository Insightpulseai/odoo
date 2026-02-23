// apps/ops-console/components/platform/BuildPanel.tsx
"use client";

import React from "react";
import { useOpsDeployments } from "@/hooks/use-ops-deployments";
import { ago, statusColor, statusIcon } from "@/lib/visuals";
import { Badge } from "./Visuals";

export const BuildPanel = () => {
  const { data: deployments, isLoading } = useOpsDeployments(20);

  if (isLoading) {
    return <div style={{ padding: 20, color: "#52525b", fontSize: 13 }}>Fetching deployment history...</div>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "18px 1fr 140px 100px 70px 80px",
          gap: 8,
          padding: "0 10px",
          fontSize: 10,
          color: "#52525b",
          fontWeight: 600,
          textTransform: "uppercase",
          letterSpacing: 0.5,
        }}
      >
        <span />
        <span>Commit</span>
        <span>Branch</span>
        <span>Modules</span>
        <span>Duration</span>
        <span>Status</span>
      </div>
      {deployments?.map((b) => (
        <div
          key={b.id}
          style={{
            display: "grid",
            gridTemplateColumns: "18px 1fr 140px 100px 70px 80px",
            gap: 8,
            alignItems: "center",
            padding: "10px",
            background: "#111113",
            border: "1px solid #1e1e22",
            borderRadius: 6,
          }}
        >
          <span
            style={{
              color: statusColor(b.status),
              fontSize: 14,
              textAlign: "center",
            }}
          >
            {statusIcon(b.status)}
          </span>
          <div>
            <div
              style={{
                fontSize: 12,
                color: "#e4e4e7",
                fontFamily: "'JetBrains Mono', monospace",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {b.commit_message || "No commit message"}
            </div>
            <div style={{ fontSize: 10, color: "#52525b", marginTop: 2 }}>
              {b.commit_sha?.slice(0, 7)} · {b.commit_author || 'system'} · {ago(b.created_at)}
            </div>
          </div>
          <div
            style={{
              fontSize: 11,
              color: "#a1a1aa",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {b.branch}
          </div>
          <div style={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
            {b.modules_updated?.slice(0, 2).map((m: string) => (
              <Badge key={m} color="#71717a">
                {m.replace("ipai_", "").replace("account_", "acc_")}
              </Badge>
            ))}
            {(!b.modules_updated || b.modules_updated.length === 0) && (
              <span style={{ fontSize: 9, color: "#3f3f46" }}>none</span>
            )}
          </div>
          <div
            style={{
              fontSize: 11,
              color: "#71717a",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {b.duration_seconds ? `${b.duration_seconds}s` : "…"}
          </div>
          <Badge color={statusColor(b.status)}>{b.status}</Badge>
        </div>
      ))}
      {!isLoading && (!deployments || deployments.length === 0) && (
        <div style={{ padding: 20, textAlign: "center", color: "#3f3f46", fontSize: 12 }}>
          No deployments found in SSOT.
        </div>
      )}
    </div>
  );
};
