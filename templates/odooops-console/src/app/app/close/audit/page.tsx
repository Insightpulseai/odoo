import { createClient } from "@/lib/supabase/server";

interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  target: string;
  metadata: Record<string, any>;
  level: "info" | "warning" | "critical";
}

export default async function AuditTrailPage() {
  const supabase = createClient();

  // In production, call audit.ui_events(p_org_id, p_from, p_to)
  const events: AuditEvent[] = [
    {
      id: "1",
      timestamp: "2026-02-12 14:45:23",
      actor: "Finance Ops",
      action: "month_close.task.completed",
      target: "Process employee payroll",
      metadata: {
        workstream: "Payroll & Benefits",
        evidence_count: 3,
        duration_minutes: 45,
      },
      level: "info",
    },
    {
      id: "2",
      timestamp: "2026-02-12 13:30:15",
      actor: "Finance Ops",
      action: "tax.form.filed",
      target: "BIR Form 1601-C",
      metadata: {
        form_code: "1601-C",
        period: "2026-02",
        payable_amount: 45230,
        filing_method: "eBIRForms",
      },
      level: "info",
    },
    {
      id: "3",
      timestamp: "2026-02-12 12:15:00",
      actor: "System",
      action: "month_close.sync_tasks.completed",
      target: "Close Run Feb 2026",
      metadata: {
        tasks_created: 12,
        tasks_updated: 53,
        run_id: "run-2026-02",
      },
      level: "info",
    },
    {
      id: "4",
      timestamp: "2026-02-12 10:00:00",
      actor: "Finance Ops",
      action: "month_close.task.blocked",
      target: "Verify inventory count accuracy",
      metadata: {
        workstream: "AP/AR Management",
        blocker: "Warehouse system unavailable",
        priority: "high",
      },
      level: "warning",
    },
    {
      id: "5",
      timestamp: "2026-02-11 16:45:00",
      actor: "Finance Ops",
      action: "tax.form.payment.confirmed",
      target: "BIR Form 1601-C",
      metadata: {
        form_code: "1601-C",
        payment_ref: "PAY-2026-02-001",
        amount: 45230,
        bank: "BDO",
      },
      level: "info",
    },
    {
      id: "6",
      timestamp: "2026-02-11 14:20:00",
      actor: "System",
      action: "month_close.kpi.computed",
      target: "KPI Rollup",
      metadata: {
        scope: "local",
        metrics_computed: 15,
        period: "2026-02",
      },
      level: "info",
    },
  ];

  const levelColors = {
    info: { bg: "bg-blue-100", text: "text-blue-800", icon: "ℹ️" },
    warning: { bg: "bg-yellow-100", text: "text-yellow-800", icon: "⚠️" },
    critical: { bg: "bg-red-100", text: "text-red-800", icon: "🚨" },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Audit Trail</h1>
          <p className="text-sm text-gray-600 mt-1">
            Immutable event timeline for month-end close operations
          </p>
        </div>
        <div className="flex gap-3">
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option>All Events</option>
            <option>Tasks</option>
            <option>Tax Forms</option>
            <option>System</option>
          </select>
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option>Last 24 hours</option>
            <option>Last 7 days</option>
            <option>Last 30 days</option>
          </select>
        </div>
      </div>

      {/* Event Statistics */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: "Total Events", value: "243", color: "text-gray-900" },
          { label: "Info", value: "225", color: "text-blue-600" },
          { label: "Warnings", value: "15", color: "text-yellow-600" },
          { label: "Critical", value: "3", color: "text-red-600" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white border border-gray-200 rounded-lg p-4"
          >
            <div className="text-sm text-gray-600 mb-1">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Event Timeline */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Event Log</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {events.map((event) => {
            const levelConfig = levelColors[event.level];
            return (
              <div key={event.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start gap-4">
                  {/* Timestamp */}
                  <div className="flex-shrink-0 w-40 text-sm text-gray-600 font-mono">
                    {event.timestamp}
                  </div>

                  {/* Level Badge */}
                  <div className="flex-shrink-0">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${levelConfig.bg} ${levelConfig.text}`}
                    >
                      {levelConfig.icon} {event.level}
                    </span>
                  </div>

                  {/* Event Details */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-medium text-gray-900 mb-1">
                          {event.action}
                        </div>
                        <div className="text-sm text-gray-700 mb-2">
                          <span className="text-gray-500">Target:</span>{" "}
                          {event.target}
                        </div>
                        <div className="text-sm text-gray-600">
                          <span className="text-gray-500">Actor:</span>{" "}
                          {event.actor}
                        </div>

                        {/* Metadata */}
                        {Object.keys(event.metadata).length > 0 && (
                          <details className="mt-3">
                            <summary className="text-sm text-blue-600 cursor-pointer hover:underline">
                              View metadata ({Object.keys(event.metadata).length}{" "}
                              fields)
                            </summary>
                            <div className="mt-2 bg-gray-50 rounded p-3 text-sm">
                              <pre className="text-xs font-mono text-gray-700">
                                {JSON.stringify(event.metadata, null, 2)}
                              </pre>
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Audit Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-blue-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-blue-900">
              Audit Trail Features
            </h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-blue-800 mt-2">
              <li>Immutable event log stored in Supabase audit.events table</li>
              <li>Every close step writes one deterministic audit row</li>
              <li>
                Metadata includes evidence refs, Odoo IDs, and operational context
              </li>
              <li>
                Full traceability from task execution to tax filing to payment
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
