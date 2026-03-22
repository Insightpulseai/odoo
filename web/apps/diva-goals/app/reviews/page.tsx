"use client";

interface GoalSummary {
  id: string;
  title: string;
  status: "on_track" | "at_risk" | "behind" | "completed";
  progress: number;
  confidence: number;
  lastEvidenceAt: string;
  owner: string;
}

const STATUS_COLORS: Record<GoalSummary["status"], string> = {
  on_track: "bg-green-100 text-green-800",
  at_risk: "bg-yellow-100 text-yellow-800",
  behind: "bg-red-100 text-red-800",
  completed: "bg-blue-100 text-blue-800",
};

const PLACEHOLDER_GOALS: GoalSummary[] = [
  {
    id: "goal-001",
    title: "Month-end close cycle < 5 business days",
    status: "on_track",
    progress: 72,
    confidence: 85,
    lastEvidenceAt: "2026-03-22T14:30:00+08:00",
    owner: "Finance Ops",
  },
  {
    id: "goal-002",
    title: "BIR 2307 filing automation > 90% coverage",
    status: "at_risk",
    progress: 45,
    confidence: 60,
    lastEvidenceAt: "2026-03-20T09:15:00+08:00",
    owner: "Tax Compliance",
  },
  {
    id: "goal-003",
    title: "Expense liquidation turnaround < 48h",
    status: "behind",
    progress: 28,
    confidence: 40,
    lastEvidenceAt: "2026-03-18T16:00:00+08:00",
    owner: "HR Finance",
  },
  {
    id: "goal-004",
    title: "EE parity score >= 80%",
    status: "on_track",
    progress: 55,
    confidence: 75,
    lastEvidenceAt: "2026-03-21T11:00:00+08:00",
    owner: "Platform Engineering",
  },
];

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-PH", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ReviewsPage() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold mb-6">Goal Status Reviews</h1>

      <div className="space-y-4">
        {PLACEHOLDER_GOALS.map((goal) => (
          <a
            key={goal.id}
            href={`/reviews/${goal.id}`}
            className="block border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-lg font-medium">{goal.title}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Owner: {goal.owner}
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[goal.status]}`}
              >
                {goal.status.replace("_", " ")}
              </span>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Progress</span>
                <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${goal.progress}%` }}
                  />
                </div>
                <span className="text-xs text-gray-600">{goal.progress}%</span>
              </div>
              <div>
                <span className="text-gray-500">Confidence</span>
                <p className="font-medium">{goal.confidence}%</p>
              </div>
              <div>
                <span className="text-gray-500">Last Evidence</span>
                <p className="font-medium">
                  {formatTimestamp(goal.lastEvidenceAt)}
                </p>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
