import { createClient } from "@/lib/supabase/server";
import Link from "next/link";

interface KPICard {
  label: string;
  value: string;
  trend: string;
  status: "on-track" | "at-risk" | "blocked";
}

interface Workstream {
  id: string;
  name: string;
  progress: number;
  tasksCompleted: number;
  tasksTotal: number;
  status: "on-track" | "at-risk" | "blocked";
}

export default async function MonthCloseOverviewPage() {
  const supabase = await createClient();

  // In production, call ops.month_close_dashboard(p_period, p_org_id)
  const currentPeriod = "2026-02";
  const closeStatus = "in_progress"; // draft | in_progress | review | locked

  const kpiCards: KPICard[] = [
    {
      label: "Days to Close",
      value: "6",
      trend: "vs 8 prev month",
      status: "on-track",
    },
    {
      label: "Tasks Complete",
      value: "42/65",
      trend: "65%",
      status: "on-track",
    },
    {
      label: "BIR Forms Filed",
      value: "3/5",
      trend: "60%",
      status: "at-risk",
    },
    {
      label: "Variance (₱)",
      value: "₱12,450",
      trend: "0.08%",
      status: "on-track",
    },
  ];

  const workstreams: Workstream[] = [
    {
      id: "1",
      name: "Payroll & Benefits",
      progress: 100,
      tasksCompleted: 8,
      tasksTotal: 8,
      status: "on-track",
    },
    {
      id: "2",
      name: "Tax & Provisions",
      progress: 60,
      tasksCompleted: 3,
      tasksTotal: 5,
      status: "at-risk",
    },
    {
      id: "3",
      name: "Bank Reconciliation",
      progress: 75,
      tasksCompleted: 6,
      tasksTotal: 8,
      status: "on-track",
    },
    {
      id: "4",
      name: "AP/AR Management",
      progress: 50,
      tasksCompleted: 10,
      tasksTotal: 20,
      status: "on-track",
    },
    {
      id: "5",
      name: "Accruals & Prepayments",
      progress: 80,
      tasksCompleted: 12,
      tasksTotal: 15,
      status: "on-track",
    },
    {
      id: "6",
      name: "Review & Approval",
      progress: 0,
      tasksCompleted: 0,
      tasksTotal: 9,
      status: "blocked",
    },
  ];

  const statusColors = {
    "on-track": { bg: "bg-green-100", text: "text-green-800" },
    "at-risk": { bg: "bg-yellow-100", text: "text-yellow-800" },
    blocked: { bg: "bg-red-100", text: "text-red-800" },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Month-End Close: {currentPeriod}</h1>
          <p className="text-sm text-gray-600 mt-1">
            Deterministic workflow with Odoo (SoR) + Supabase (control-plane)
          </p>
        </div>
        <div className="flex gap-3">
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option>Local</option>
            <option>Regional</option>
            <option>Global</option>
          </select>
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option value="2026-02">Feb 2026</option>
            <option value="2026-01">Jan 2026</option>
            <option value="2025-12">Dec 2025</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        {kpiCards.map((kpi) => {
          const colors = statusColors[kpi.status];
          return (
            <div
              key={kpi.label}
              className="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-700">
                  {kpi.label}
                </h3>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}
                >
                  {kpi.status}
                </span>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1">
                {kpi.value}
              </div>
              <div className="text-sm text-gray-600">{kpi.trend}</div>
            </div>
          );
        })}
      </div>

      {/* Timeline */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Timeline</h2>
        <div className="flex items-center gap-2">
          {[
            { label: "Start", date: "Feb 1", active: false },
            { label: "Tasks Due", date: "Feb 5", active: true },
            { label: "Review", date: "Feb 8", active: false },
            { label: "Lock", date: "Feb 10", active: false },
          ].map((milestone, idx) => (
            <div key={idx} className="flex-1">
              <div className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    milestone.active
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {idx + 1}
                </div>
                {idx < 3 && (
                  <div className="flex-1 h-1 bg-gray-200 mx-2"></div>
                )}
              </div>
              <div className="mt-2 text-sm">
                <div className="font-medium">{milestone.label}</div>
                <div className="text-gray-600">{milestone.date}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workstream Lanes */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Workstreams</h2>
          <Link
            href="/app/close/tasks"
            className="text-sm text-blue-600 hover:underline"
          >
            View All Tasks →
          </Link>
        </div>

        <div className="divide-y divide-gray-200">
          {workstreams.map((ws) => {
            const colors = statusColors[ws.status];
            return (
              <div key={ws.id} className="px-6 py-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-gray-900">{ws.name}</h3>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}
                      >
                        {ws.status}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {ws.tasksCompleted} / {ws.tasksTotal} tasks completed
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {ws.progress}%
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      ws.status === "on-track"
                        ? "bg-green-600"
                        : ws.status === "at-risk"
                        ? "bg-yellow-600"
                        : "bg-red-600"
                    }`}
                    style={{ width: `${ws.progress}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-3 gap-6">
        <Link
          href="/app/close/tasks"
          className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition"
        >
          <h3 className="font-semibold text-gray-900 mb-2">📋 Tasks</h3>
          <p className="text-sm text-gray-600">
            Execute checklist with evidence tracking
          </p>
        </Link>

        <Link
          href="/app/close/compliance"
          className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition"
        >
          <h3 className="font-semibold text-gray-900 mb-2">📄 Compliance</h3>
          <p className="text-sm text-gray-600">
            BIR forms board (1601-C, 2550Q, SLSP)
          </p>
        </Link>

        <Link
          href="/app/close/audit"
          className="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition"
        >
          <h3 className="font-semibold text-gray-900 mb-2">🔍 Audit Trail</h3>
          <p className="text-sm text-gray-600">Immutable event timeline</p>
        </Link>
      </div>
    </div>
  );
}
