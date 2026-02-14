export function MetricCard({
  title,
  value,
  trend
}: {
  title: string;
  value: string;
  trend: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="text-sm font-medium text-gray-600 mb-1">{title}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-green-600 mt-1">{trend}</div>
    </div>
  );
}
