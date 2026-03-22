"use client";

import { ReviewLayout } from "@ipai/ui/patterns/ReviewLayout";
import { CopilotPanel } from "@ipai/ui/patterns/CopilotPanel";
import { ApprovalDrawer } from "@ipai/ui/patterns/ApprovalDrawer";
import { useState } from "react";

interface KeyResult {
  id: string;
  title: string;
  target: string;
  current: string;
  progress: number;
}

interface EvidenceItem {
  id: string;
  timestamp: string;
  source: string;
  summary: string;
}

const PLACEHOLDER_GOAL = {
  id: "goal-001",
  title: "Month-end close cycle < 5 business days",
  description:
    "Reduce the monthly financial close cycle from 8+ business days to under 5 by automating reconciliation, journal entry review, and BIR filing preparation.",
  status: "on_track" as const,
  owner: "Finance Ops",
  keyResults: [
    {
      id: "kr-001",
      title: "Automated reconciliation coverage",
      target: "95%",
      current: "78%",
      progress: 82,
    },
    {
      id: "kr-002",
      title: "Journal entry auto-review rate",
      target: "80%",
      current: "52%",
      progress: 65,
    },
    {
      id: "kr-003",
      title: "BIR filing prep time",
      target: "< 2 hours",
      current: "3.5 hours",
      progress: 57,
    },
  ] as KeyResult[],
  evidence: [
    {
      id: "ev-001",
      timestamp: "2026-03-22T14:30:00+08:00",
      source: "Odoo account.move",
      summary: "March reconciliation batch completed — 412/528 lines auto-matched.",
    },
    {
      id: "ev-002",
      timestamp: "2026-03-21T10:00:00+08:00",
      source: "Copilot action log",
      summary: "Copilot flagged 3 journal entries with missing analytic accounts.",
    },
    {
      id: "ev-003",
      timestamp: "2026-03-20T16:45:00+08:00",
      source: "BIR 2307 generator",
      summary: "Q1 2307 draft generated — 98 withholding certificates, 2 exceptions.",
    },
  ] as EvidenceItem[],
};

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function GoalDetailPage({
  params,
}: {
  params: { goalId: string };
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const goal = PLACEHOLDER_GOAL;

  const mainContent = (
    <div className="space-y-6">
      {/* Goal Header */}
      <div>
        <h1 className="text-2xl font-semibold">{goal.title}</h1>
        <p className="text-gray-600 mt-2">{goal.description}</p>
        <div className="flex gap-4 mt-3 text-sm text-gray-500">
          <span>Owner: {goal.owner}</span>
          <span>ID: {params.goalId}</span>
        </div>
      </div>

      {/* Key Results */}
      <section>
        <h2 className="text-lg font-medium mb-3">Key Results</h2>
        <div className="space-y-3">
          {goal.keyResults.map((kr) => (
            <div key={kr.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium">{kr.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Current: {kr.current} / Target: {kr.target}
                  </p>
                </div>
                <span className="text-sm font-medium">{kr.progress}%</span>
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${kr.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Evidence */}
      <section>
        <h2 className="text-lg font-medium mb-3">Evidence Trail</h2>
        <div className="space-y-2">
          {goal.evidence.map((ev) => (
            <div
              key={ev.id}
              className="border-l-4 border-blue-400 pl-4 py-2"
            >
              <div className="flex justify-between text-sm text-gray-500">
                <span>{ev.source}</span>
                <span>{formatTimestamp(ev.timestamp)}</span>
              </div>
              <p className="mt-1">{ev.summary}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Action Bar */}
      <div className="flex gap-3 pt-4 border-t">
        <button
          onClick={() => setDrawerOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Review & Approve
        </button>
        <button className="px-4 py-2 border rounded-md hover:bg-gray-50">
          Request Evidence
        </button>
      </div>
    </div>
  );

  const sidePanel = (
    <CopilotPanel
      goalId={params.goalId}
      goalTitle={goal.title}
    />
  );

  return (
    <>
      <ReviewLayout main={mainContent} side={sidePanel} />
      <ApprovalDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        goalTitle={goal.title}
        goalId={params.goalId}
      />
    </>
  );
}
