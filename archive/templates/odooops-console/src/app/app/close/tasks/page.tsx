import { createClient } from "@/lib/supabase/server";

interface CloseTask {
  id: string;
  name: string;
  workstream: string;
  assignee: string;
  status: "pending" | "in_progress" | "completed" | "blocked";
  priority: "high" | "medium" | "low";
  dueDate: string;
  evidenceCount: number;
}

export default async function CloseTasksPage() {
  const supabase = createClient();

  // In production, call ops.month_close_tasks(p_run_id) + ops.ui_close_task_evidence
  const tasks: CloseTask[] = [
    {
      id: "1",
      name: "Process employee payroll",
      workstream: "Payroll & Benefits",
      assignee: "Finance Ops",
      status: "completed",
      priority: "high",
      dueDate: "Feb 3",
      evidenceCount: 3,
    },
    {
      id: "2",
      name: "File BIR Form 1601-C (Withholding Tax)",
      workstream: "Tax & Provisions",
      assignee: "Finance Ops",
      status: "in_progress",
      priority: "high",
      dueDate: "Feb 10",
      evidenceCount: 1,
    },
    {
      id: "3",
      name: "Reconcile BDO checking account",
      workstream: "Bank Reconciliation",
      assignee: "Finance Ops",
      status: "completed",
      priority: "high",
      dueDate: "Feb 5",
      evidenceCount: 2,
    },
    {
      id: "4",
      name: "Review outstanding customer invoices",
      workstream: "AP/AR Management",
      assignee: "Finance Ops",
      status: "in_progress",
      priority: "medium",
      dueDate: "Feb 6",
      evidenceCount: 0,
    },
    {
      id: "5",
      name: "Record prepaid insurance accrual",
      workstream: "Accruals & Prepayments",
      assignee: "Finance Ops",
      status: "pending",
      priority: "medium",
      dueDate: "Feb 7",
      evidenceCount: 0,
    },
    {
      id: "6",
      name: "Verify inventory count accuracy",
      workstream: "AP/AR Management",
      assignee: "Finance Ops",
      status: "blocked",
      priority: "high",
      dueDate: "Feb 5",
      evidenceCount: 1,
    },
  ];

  const statusColors = {
    pending: { bg: "bg-gray-100", text: "text-gray-800" },
    in_progress: { bg: "bg-blue-100", text: "text-blue-800" },
    completed: { bg: "bg-green-100", text: "text-green-800" },
    blocked: { bg: "bg-red-100", text: "text-red-800" },
  };

  const priorityColors = {
    high: "text-red-600",
    medium: "text-yellow-600",
    low: "text-gray-600",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Close Tasks</h1>
          <p className="text-sm text-gray-600 mt-1">
            Task execution with evidence tracking
          </p>
        </div>
        <div className="flex gap-3">
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option>All Workstreams</option>
            <option>Payroll & Benefits</option>
            <option>Tax & Provisions</option>
            <option>Bank Reconciliation</option>
            <option>AP/AR Management</option>
            <option>Accruals & Prepayments</option>
          </select>
          <select className="px-3 py-2 border border-gray-300 rounded">
            <option>All Statuses</option>
            <option>Pending</option>
            <option>In Progress</option>
            <option>Completed</option>
            <option>Blocked</option>
          </select>
        </div>
      </div>

      {/* Tasks Summary */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: "Total Tasks", value: "65", color: "text-gray-900" },
          { label: "Completed", value: "42", color: "text-green-600" },
          { label: "In Progress", value: "15", color: "text-blue-600" },
          { label: "Blocked", value: "3", color: "text-red-600" },
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

      {/* Tasks Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Task
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Workstream
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Assignee
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Evidence
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tasks.map((task) => {
              const statusColor = statusColors[task.status];
              return (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {task.name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {task.workstream}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {task.assignee}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`text-xs font-medium ${
                        priorityColors[task.priority]
                      }`}
                    >
                      {task.priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {task.dueDate}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusColor.bg} ${statusColor.text}`}
                    >
                      {task.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      <svg
                        className="w-4 h-4 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                        />
                      </svg>
                      <span className="text-sm text-gray-600">
                        {task.evidenceCount}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-sm">
                    <button className="text-blue-600 hover:text-blue-800">
                      View
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
