// apps/ops-console/components/platform/EnvironmentPanel.tsx
"use client";

import React from "react";
import { useOpsEnvironments } from "@/hooks/use-ops-environments";
import { useOpsRunMutation } from "@/hooks/use-ops-run-mutation";
import { ago } from "@/lib/mock-data";
import { Badge } from "./Visuals";

export const EnvironmentPanel = () => {
  const { data: environments, isLoading } = useOpsEnvironments();
  const triggerRun = useOpsRunMutation();

  const stageColor = (s: string) =>
    ({ production: "#22c55e", staging: "#eab308", development: "#3b82f6" }[s] || "#6b7280");

  const handleClone = (envId: string) => {
    triggerRun.mutate({
      kind: 'clone',
      env_id: envId,
      metadata: { source: 'prod', target: 'stage' }
    });
  };

  if (isLoading) {
    return <div style={{ padding: 20, color: "#52525b", fontSize: 13 }}>Initializing environments...</div>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {environments?.map((e) => (
        <div
          key={e.slug}
          style={{
            background: "#111113",
            border: "1px solid #1e1e22",
            borderRadius: 8,
            padding: 20,
            borderLeft: `3px solid ${stageColor(e.type)}`,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 14,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: e.status === 'online' ? stageColor(e.type) : '#ef4444',
                  boxShadow: e.status === 'online' ? `0 0 6px ${stageColor(e.type)}` : `0 0 6px #ef4444`,
                }}
              />
              <span
                style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: "#e4e4e7",
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {e.type}
              </span>
              <Badge color={stageColor(e.type)} outline>
                {e.config?.db || `odoo_${e.slug}`}
              </Badge>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              {e.slug === "stage" && (
                <button
                  onClick={() => handleClone(e.id)}
                  disabled={triggerRun.isPending}
                  style={{
                    background: "#1e1e22",
                    border: "1px solid #2e2e33",
                    borderRadius: 5,
                    color: triggerRun.isPending ? "#eab308" : "#a1a1aa",
                    fontSize: 11,
                    padding: "5px 12px",
                    cursor: triggerRun.isPending ? "not-allowed" : "pointer",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  {triggerRun.isPending ? "⟳ Cloning prod…" : "↻ Clone from Prod"}
                </button>
              )}
              <a
                href={e.url ? `https://${e.url}` : "#"}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: stageColor(e.type) + "20",
                  border: `1px solid ${stageColor(e.type)}40`,
                  borderRadius: 5,
                  color: stageColor(e.type),
                  fontSize: 11,
                  padding: "5px 12px",
                  textDecoration: "none",
                  cursor: "pointer",
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 600,
                }}
              >
                Connect →
              </a>
            </div>
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 16,
              fontSize: 11,
            }}
          >
            <div>
              <div style={{ color: "#52525b", marginBottom: 2 }}>URL</div>
              <div
                style={{ color: "#a1a1aa", fontFamily: "'JetBrains Mono', monospace" }}
              >
                {e.url || "TBD"}
              </div>
            </div>
            <div>
              <div style={{ color: "#52525b", marginBottom: 2 }}>Branch Pattern</div>
              <div
                style={{ color: "#a1a1aa", fontFamily: "'JetBrains Mono', monospace" }}
              >
                {e.branch_pattern || "N/A"}
              </div>
            </div>
            <div>
              <div style={{ color: "#52525b", marginBottom: 2 }}>Status</div>
              <div
                style={{ color: e.status === 'online' ? "#22c55e" : "#ef4444", fontWeight: 600 }}
              >
                {e.status?.toUpperCase()}
              </div>
            </div>
            <div>
              <div style={{ color: "#52525b", marginBottom: 2 }}>Last Updated</div>
              <div
                style={{ color: "#a1a1aa", fontFamily: "'JetBrains Mono', monospace" }}
              >
                {ago(e.updated_at)}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
