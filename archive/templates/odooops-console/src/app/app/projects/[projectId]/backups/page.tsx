import { createClient } from "@/lib/supabase/server";
import Link from "next/link";

interface Backup {
  id: string;
  name: string;
  size: string;
  createdAt: string;
  type: "manual" | "automatic";
  status: "completed" | "in_progress" | "failed";
}

export default async function BackupsPage({
  params,
}: {
  params: { projectId: string };
}) {
  const supabase = createClient();

  // In production, call ops.ui_backups(p_project_id)
  const backups: Backup[] = [
    {
      id: "1",
      name: "backup-2024-02-12-14-00",
      size: "2.4 GB",
      createdAt: "2024-02-12 14:00:00",
      type: "automatic",
      status: "completed",
    },
    {
      id: "2",
      name: "pre-migration-backup",
      size: "2.3 GB",
      createdAt: "2024-02-11 09:30:00",
      type: "manual",
      status: "completed",
    },
    {
      id: "3",
      name: "backup-2024-02-10-14-00",
      size: "2.2 GB",
      createdAt: "2024-02-10 14:00:00",
      type: "automatic",
      status: "completed",
    },
  ];

  const statusColors = {
    completed: "bg-green-100 text-green-800",
    in_progress: "bg-yellow-100 text-yellow-800",
    failed: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Backups</h1>
          <p className="text-sm text-gray-600 mt-1">
            Database and filestore backups
          </p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Create Manual Backup
        </button>
      </div>

      {/* Backup Schedule Info */}
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
              Automatic Backups Enabled
            </h3>
            <p className="text-sm text-blue-800 mt-1">
              Daily backups at 2:00 AM UTC • Retention: 30 days
            </p>
          </div>
        </div>
      </div>

      {/* Backups List */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Size
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {backups.map((backup) => (
              <tr key={backup.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {backup.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  <span className="capitalize">{backup.type}</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {backup.size}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {backup.createdAt}
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusColors[backup.status]}`}
                  >
                    {backup.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-right text-sm">
                  <div className="flex justify-end gap-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      Download
                    </button>
                    <button className="text-blue-600 hover:text-blue-800">
                      Restore
                    </button>
                    <button className="text-red-600 hover:text-red-800">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
