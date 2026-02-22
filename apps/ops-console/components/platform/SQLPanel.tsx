// apps/ops-console/components/platform/SQLPanel.tsx
"use client";

import React, { useState } from "react";
import { QUERIES } from "@/lib/mock-data";
import { PlatformCard } from "./Visuals";

export const SQLPanel = () => {
  const [query, setQuery] = useState(QUERIES[0]);
  const [aiPrompt, setAiPrompt] = useState("");

  const handleSuggest = (s: string) => {
    setAiPrompt(s);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {/* AI Prompt */}
      <PlatformCard
        title="AI SQL Assistant"
        subtitle="Powered by Claude · Scoped to doctrine schemas"
      >
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="e.g. Show me top 10 overdue invoices with partner names…"
            style={{
              flex: 1,
              background: "#0a0a0b",
              border: "1px solid #2e2e33",
              borderRadius: 6,
              color: "#e4e4e7",
              fontSize: 12,
              padding: "8px 12px",
              outline: "none",
              fontFamily: "'JetBrains Mono', monospace",
            }}
          />
          <button
            style={{
              background: "#a78bfa20",
              border: "1px solid #a78bfa40",
              borderRadius: 6,
              color: "#a78bfa",
              fontSize: 12,
              padding: "8px 16px",
              cursor: "pointer",
              fontFamily: "'JetBrains Mono', monospace",
              fontWeight: 600,
              whiteSpace: "nowrap",
            }}
          >
            ✦ Generate SQL
          </button>
        </div>
        <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
          {[
            "overdue invoices",
            "monthly revenue",
            "sync failures",
            "expense summary",
          ].map((s) => (
            <button
              key={s}
              onClick={() => handleSuggest(s)}
              style={{
                background: "#1e1e22",
                border: "1px solid #2e2e33",
                borderRadius: 12,
                color: "#71717a",
                fontSize: 10,
                padding: "3px 10px",
                cursor: "pointer",
              }}
            >
              {s}
            </button>
          ))}
        </div>
      </PlatformCard>

      {/* Editor */}
      <PlatformCard title="SQL Editor" subtitle="Schemas: odoo_replica · ops · mdm · ai">
        <div
          style={{
            background: "#0a0a0b",
            border: "1px solid #1a1a1e",
            borderRadius: 6,
            padding: 12,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 12,
            color: "#e4e4e7",
            minHeight: 80,
            whiteSpace: "pre-wrap",
            lineHeight: 1.6,
          }}
        >
          <span style={{ color: "#c084fc" }}>SELECT </span>
          <span style={{ color: "#e4e4e7" }}>count(*) </span>
          <span style={{ color: "#c084fc" }}>FROM </span>
          <span style={{ color: "#60a5fa" }}>odoo_replica</span>
          <span style={{ color: "#71717a" }}>.</span>
          <span style={{ color: "#34d399" }}>account_move</span>
          {"\n"}
          <span style={{ color: "#c084fc" }}>WHERE </span>
          <span style={{ color: "#e4e4e7" }}>state = </span>
          <span style={{ color: "#fbbf24" }}>'posted'</span>
          {"\n"}
          <span style={{ color: "#c084fc" }}>AND </span>
          <span style={{ color: "#e4e4e7" }}>date {">"}= </span>
          <span style={{ color: "#fbbf24" }}>'2026-01-01'</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
          <div style={{ display: "flex", gap: 4 }}>
            {QUERIES.map((q, i) => (
              <button
                key={i}
                onClick={() => setQuery(q)}
                style={{
                  background: "#1e1e22",
                  border: "1px solid #2e2e33",
                  borderRadius: 4,
                  color: "#71717a",
                  fontSize: 10,
                  padding: "3px 8px",
                  cursor: "pointer",
                }}
              >
                Query {i + 1}
              </button>
            ))}
          </div>
          <button
            style={{
              background: "#22c55e20",
              border: "1px solid #22c55e40",
              borderRadius: 5,
              color: "#22c55e",
              fontSize: 11,
              padding: "5px 14px",
              cursor: "pointer",
              fontFamily: "'JetBrains Mono', monospace",
              fontWeight: 600,
            }}
          >
            ▶ Run
          </button>
        </div>
      </PlatformCard>

      {/* Mock result */}
      <PlatformCard title="Result" subtitle="1 row · 12ms">
        <div
          style={{
            background: "#0a0a0b",
            border: "1px solid #1a1a1e",
            borderRadius: 6,
            padding: 12,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 12,
            color: "#22c55e",
          }}
        >
          count: <span style={{ color: "#e4e4e7", fontWeight: 700 }}>1,247</span>
        </div>
      </PlatformCard>
    </div>
  );
};
