// apps/ops-console/components/platform/SyncPanel.tsx
"use client";

import React from "react";
import { useOpsSyncCheckpoints } from "@/hooks/use-ops-sync-checkpoints";
import { useOpsSyncDlq } from "@/hooks/use-ops-sync-dlq";
import { ago, statusColor } from "@/lib/mock-data";
import { PlatformCard, Badge } from "./Visuals";

export const SyncPanel = () => {
  const { data: checkpoints, isLoading: loadingCheckpoints } = useOpsSyncCheckpoints();
  const { data: dlq, isLoading: loadingDlq } = useOpsSyncDlq();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <PlatformCard
        title="Sync Checkpoints"
        subtitle="Incremental pull — Odoo SOR → Supabase SSOT"
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {loadingCheckpoints ? (
            <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>Fetching checkpoints...</div>
          ) : checkpoints?.map((s) => (
            <div
              key={s.id}
              style={{
                display: "grid",
                gridTemplateColumns: "160px 80px 80px 60px 1fr 90px",
                gap: 8,
                alignItems: "center",
                padding: "8px 10px",
                background: "#0a0a0b",
                borderRadius: 6,
                border: "1px solid #1a1a1e",
              }}
            >
              <span
                style={{
                  fontSize: 11,
                  color: "#e4e4e7",
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                {s.model}
              </span>
              <span style={{ fontSize: 10, color: "#71717a" }}>
                {s.records_synced.toLocaleString()} rows
              </span>
              <span style={{ fontSize: 10, color: "#71717a" }}>{ago(s.last_sync_at)}</span>
              <span style={{ fontSize: 10, color: (s.new_delta || 0) > 0 ? "#22c55e" : "#52525b" }}>
                {(s.new_delta || 0) > 0 ? `+${s.new_delta}` : "—"}
              </span>
              <span
                style={{
                  fontSize: 10,
                  color: "#ef4444",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {s.error_message || ""}
              </span>
              <div style={{ display: "flex", gap: 4, justifyContent: "flex-end" }}>
                <Badge color={statusColor(s.status)}>{s.status}</Badge>
                <button
                  style={{
                    background: "none",
                    border: "1px solid #2e2e33",
                    borderRadius: 4,
                    color: "#71717a",
                    fontSize: 10,
                    padding: "2px 6px",
                    cursor: "pointer",
                  }}
                >
                  ↻
                </button>
              </div>
            </div>
          ))}
          {!loadingCheckpoints && (!checkpoints || checkpoints.length === 0) && (
            <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>No active sync models found.</div>
          )}
        </div>
      </PlatformCard>
      <PlatformCard
        title="Dead Letter Queue"
        subtitle={`${dlq?.length || 0} unresolved exceptions`}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {loadingDlq ? (
            <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>Scanning DLQ...</div>
          ) : dlq?.map((d) => (
            <div
              key={d.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "8px 10px",
                background: "#1a0a0a",
                borderRadius: 6,
                border: "1px solid #3f1111",
              }}
            >
              <span style={{ color: "#ef4444", fontSize: 13 }}>✕</span>
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontSize: 11,
                    color: "#fca5a5",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  {d.model} #{d.odoo_id}
                </div>
                <div style={{ fontSize: 10, color: "#71717a", marginTop: 2 }}>
                  {d.error_message}
                </div>
              </div>
              <Badge color="#ef4444">attempt {d.attempts}/5</Badge>
              <span style={{ fontSize: 10, color: "#52525b" }}>
                {ago(d.created_at)}
              </span>
              <button
                style={{
                  background: "#22c55e20",
                  border: "1px solid #22c55e40",
                  borderRadius: 4,
                  color: "#22c55e",
                  fontSize: 10,
                  padding: "3px 8px",
                  cursor: "pointer",
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                Retry
              </button>
            </div>
          ))}
          {!loadingDlq && (!dlq || dlq.length === 0) && (
            <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>Clean queue. No failures detected.</div>
          )}
        </div>
      </PlatformCard>
    </div>
  );
};
