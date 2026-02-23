// apps/ops-console/components/platform/HuddlePanels.tsx
"use client";

import React from "react";
import { mocks } from "@/lib/mocks";
import { roleColor } from "@/lib/visuals";
import { PlatformCard, Badge } from "./Visuals";

export const TeamPanel = () => (
  <PlatformCard
    title="Finance Team"
    subtitle="Supabase Auth · JWT role claims for RLS"
  >
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {mocks.TEAM.map((t) => (
        <div
          key={t.code}
          style={{
            display: "grid",
            gridTemplateColumns: "50px 1fr 90px 200px 60px",
            gap: 8,
            alignItems: "center",
            padding: "10px 12px",
            background: "#0a0a0b",
            borderRadius: 6,
            border: "1px solid #1a1a1e",
            opacity: t.active ? 1 : 0.5,
          }}
        >
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: roleColor(t.role),
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {t.code}
          </span>
          <span style={{ fontSize: 12, color: "#e4e4e7" }}>{t.name}</span>
          <Badge color={roleColor(t.role)}>{t.role}</Badge>
          <span
            style={{
              fontSize: 11,
              color: "#52525b",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {t.email}
          </span>
          <span
            style={{ fontSize: 10, color: t.active ? "#22c55e" : "#ef4444" }}
          >
            {t.active ? "active" : "disabled"}
          </span>
        </div>
      ))}
    </div>
  </PlatformCard>
);

export const ModulesPanel = () => {
  const stages = ["production", "staging", "development"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {stages.map((stage) => {
        const mods = mocks.MODULES.filter((m) => m.stage === stage);
        if (mods.length === 0) return null;
        return (
          <PlatformCard
            key={stage}
            title={stage.toUpperCase()}
            subtitle={`${mods.length} modules`}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {mods.map((m) => (
                <div
                  key={m.name}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 120px 60px",
                    gap: 8,
                    alignItems: "center",
                    padding: "6px 10px",
                    background: "#0a0a0b",
                    borderRadius: 4,
                    border: "1px solid #1a1a1e",
                  }}
                >
                  <span
                    style={{
                      fontSize: 12,
                      color: "#e4e4e7",
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {m.name}
                  </span>
                  <span
                    style={{
                      fontSize: 11,
                      color: "#71717a",
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {m.version}
                  </span>
                  {m.oca ? (
                    <Badge color="#a78bfa">OCA</Badge>
                  ) : (
                    <Badge color="#60a5fa">custom</Badge>
                  )}
                </div>
              ))}
            </div>
          </PlatformCard>
        );
      })}
    </div>
  );
};
