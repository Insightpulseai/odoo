// apps/ops-console/components/platform/MainConsole.tsx
"use client";

import React, { useState, useEffect } from "react";
import { DashboardPanel } from "./DashboardPanel";
import { EnvironmentPanel } from "./EnvironmentPanel";
import { BuildPanel } from "./BuildPanel";
import { SyncPanel } from "./SyncPanel";
import { SQLPanel } from "./SQLPanel";
import { TeamPanel, ModulesPanel } from "./HuddlePanels";

const TABS = [
  { id: "dash", label: "Dashboard", icon: "◎" },
  { id: "envs", label: "Environments", icon: "⊞" },
  { id: "builds", label: "Builds", icon: "⚡" },
  { id: "sync", label: "Sync", icon: "⇄" },
  { id: "sql", label: "SQL", icon: "⌘" },
  { id: "team", label: "Team", icon: "◉" },
  { id: "modules", label: "Modules", icon: "⧉" },
];

const TabBar = ({
  tabs,
  active,
  onChange,
}: {
  tabs: typeof TABS;
  active: string;
  onChange: (id: string) => void;
}) => (
  <div
    style={{
      display: "flex",
      gap: 2,
      background: "#0a0a0b",
      padding: 3,
      borderRadius: 7,
      border: "1px solid #1e1e22",
    }}
  >
    {tabs.map((t) => (
      <button
        key={t.id}
        onClick={() => onChange(t.id)}
        style={{
          flex: 1,
          padding: "7px 12px",
          borderRadius: 5,
          border: "none",
          background: active === t.id ? "#1e1e22" : "transparent",
          color: active === t.id ? "#e4e4e7" : "#52525b",
          fontSize: 12,
          fontWeight: 600,
          cursor: "pointer",
          fontFamily: "'JetBrains Mono', monospace",
          transition: "all 0.15s",
        }}
      >
        {t.icon} {t.label}
      </button>
    ))}
  </div>
);

export const MainConsole = () => {
  const [tab, setTab] = useState("dash");
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const i = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(i);
  }, []);

  const Panel = () => {
    switch (tab) {
      case "dash":
        return <DashboardPanel />;
      case "envs":
        return <EnvironmentPanel />;
      case "builds":
        return <BuildPanel />;
      case "sync":
        return <SyncPanel />;
      case "sql":
        return <SQLPanel />;
      case "team":
        return <TeamPanel />;
      case "modules":
        return <ModulesPanel />;
      default:
        return <DashboardPanel />;
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#09090b",
        color: "#e4e4e7",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 24px",
          borderBottom: "1px solid #1e1e22",
          background: "#0a0a0b",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              background: "linear-gradient(135deg, #a78bfa 0%, #3b82f6 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
              fontWeight: 800,
              color: "#fff",
            }}
          >
            IP
          </div>
          <div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: "#e4e4e7",
                letterSpacing: -0.3,
              }}
            >
              InsightPulse AI
            </div>
            <div
              style={{
                fontSize: 10,
                color: "#52525b",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Ops Console · Supabase SSOT + Odoo SOR
            </div>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            fontSize: 11,
            color: "#52525b",
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          <span>178.128.112.214</span>
          <span>SGP1</span>
          <span>{time.toISOString().slice(11, 19)} UTC</span>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              background: "#a78bfa30",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 11,
              fontWeight: 700,
              color: "#a78bfa",
            }}
          >
            JT
          </div>
        </div>
      </div>

      {/* Navigation + Content */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "16px 24px" }}>
        <TabBar tabs={TABS} active={tab} onChange={setTab} />
        <div style={{ marginTop: 16 }}>
          <Panel />
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          padding: "12px 24px",
          borderTop: "1px solid #1e1e22",
          marginTop: 24,
          display: "flex",
          justifyContent: "center",
          gap: 24,
          fontSize: 10,
          color: "#3f3f46",
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        <span>Supabase SSOT · spdtwktxdalcfigzeqrz</span>
        <span>Odoo SOR · erp.insightpulseai.com</span>
        <span>Superset · superset.insightpulseai.com</span>
        <span>n8n · n8n.insightpulseai.com</span>
      </div>
    </div>
  );
};
