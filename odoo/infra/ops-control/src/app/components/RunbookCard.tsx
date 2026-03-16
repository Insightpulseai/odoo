import { Play, Edit3, AlertTriangle } from "lucide-react";
import { Button } from "./ui/button";
import type { RunbookPlan, Integration } from "../../core/types";

interface RunbookCardProps {
  plan: RunbookPlan;
  onRun: (plan: RunbookPlan) => void;
  onEdit: (plan: RunbookPlan) => void;
}

const INTEGRATION_COLORS: Record<Integration, string> = {
  Vercel: "bg-black text-white",
  Supabase: "bg-emerald-600 text-white",
  GitHub: "bg-gray-800 text-white",
  DigitalOcean: "bg-blue-600 text-white",
  Kubernetes: "bg-indigo-600 text-white"
};

const KIND_COLORS: Record<string, string> = {
  deploy: "bg-blue-500",
  healthcheck: "bg-green-500",
  spec: "bg-purple-500",
  incident: "bg-red-500",
  schema_sync: "bg-orange-500"
};

export function RunbookCard({ plan, onRun, onEdit }: RunbookCardProps) {
  const hasHighRisk = plan.risks.some(r => r.level === "warn" || r.level === "block");
  const hasBlockingRisk = plan.risks.some(r => r.level === "block");

  return (
    <div className="bg-slate-50 border-2 border-slate-200 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 bg-white border-b border-slate-200">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <div className={`w-2 h-2 rounded-full ${KIND_COLORS[plan.kind] || "bg-slate-500"}`} />
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                {plan.kind.replace("_", " ")}
              </span>
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">
              {plan.title}
            </h3>
            <p className="text-sm text-slate-600">
              {plan.summary}
            </p>
          </div>
        </div>

        {/* Integrations */}
        <div className="flex gap-2 mt-3">
          {plan.integrations.map((integration) => (
            <div
              key={integration}
              className={`px-2 py-1 rounded text-xs font-medium ${INTEGRATION_COLORS[integration]}`}
            >
              {integration}
            </div>
          ))}
        </div>
      </div>

      {/* Inputs */}
      <div className="px-5 py-4 space-y-3">
        <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
          Required Inputs
        </h4>
        <div className="grid grid-cols-2 gap-3">
          {plan.inputs.map((input) => (
            <div key={input.key} className="space-y-1">
              <label className="text-xs font-medium text-slate-600">
                {input.label}
              </label>
              <div className="text-sm font-mono bg-white px-3 py-2 rounded-lg border border-slate-200">
                {typeof input.value === "boolean" 
                  ? (input.value ? "✓ Yes" : "✗ No")
                  : input.value || "—"
                }
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risks */}
      {plan.risks.length > 0 && (
        <div className={`px-5 py-3 ${
          hasBlockingRisk 
            ? "bg-red-50 border-t border-red-200" 
            : hasHighRisk 
            ? "bg-amber-50 border-t border-amber-200"
            : "bg-blue-50 border-t border-blue-200"
        }`}>
          <div className="flex gap-2">
            <AlertTriangle className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
              hasBlockingRisk 
                ? "text-red-600" 
                : hasHighRisk 
                ? "text-amber-600"
                : "text-blue-600"
            }`} />
            <div className="flex-1">
              <h4 className={`text-xs font-semibold uppercase tracking-wider mb-1 ${
                hasBlockingRisk 
                  ? "text-red-700" 
                  : hasHighRisk 
                  ? "text-amber-700"
                  : "text-blue-700"
              }`}>
                Risk Flags
              </h4>
              <ul className="space-y-1">
                {plan.risks.map((risk, idx) => (
                  <li key={idx} className={`text-xs ${
                    hasBlockingRisk 
                      ? "text-red-700" 
                      : hasHighRisk 
                      ? "text-amber-700"
                      : "text-blue-700"
                  }`}>
                    • [{risk.level.toUpperCase()}] {risk.message}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-5 py-4 bg-white border-t border-slate-200 flex gap-3">
        <Button
          onClick={() => onRun(plan)}
          className="flex-1 bg-blue-600 hover:bg-blue-700 h-10"
        >
          <Play className="h-4 w-4 mr-2" />
          Run
        </Button>
        <Button
          onClick={() => onEdit(plan)}
          variant="outline"
          className="flex-1 h-10"
        >
          <Edit3 className="h-4 w-4 mr-2" />
          Edit
        </Button>
      </div>
    </div>
  );
}
