export function ProjectCard({
  name,
  status,
  deployments,
}: {
  name: string;
  status: "healthy" | "warning" | "error";
  deployments: number;
}) {
  const statusColors = {
    healthy: "bg-green-100 text-green-800",
    warning: "bg-yellow-100 text-yellow-800",
    error: "bg-red-100 text-red-800",
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200 hover:border-primary transition-colors">
      <div className="flex items-start justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{name}</h3>
        <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[status]}`}>
          {status}
        </span>
      </div>
      <div className="text-sm text-gray-600">
        <div className="flex justify-between">
          <span>Deployments</span>
          <span className="font-medium">{deployments}</span>
        </div>
      </div>
    </div>
  );
}
