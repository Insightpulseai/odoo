"use client";

import { useState } from "react";

type ApprovalAction = "approve" | "reject" | "defer";

interface ApprovalDrawerProps {
  open: boolean;
  onClose: () => void;
  goalTitle: string;
  goalId: string;
}

export function ApprovalDrawer({
  open,
  onClose,
  goalTitle,
  goalId,
}: ApprovalDrawerProps) {
  const [action, setAction] = useState<ApprovalAction | null>(null);
  const [reason, setReason] = useState("");

  function handleSubmit() {
    if (!action) return;
    // Placeholder — will POST to Odoo bridge
    console.log("Approval submitted:", { goalId, action, reason });
    setAction(null);
    setReason("");
    onClose();
  }

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 flex flex-col">
        <div className="px-6 py-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-medium">Review Decision</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            x
          </button>
        </div>

        <div className="flex-1 overflow-auto px-6 py-4 space-y-6">
          <div>
            <p className="text-sm text-gray-500">Goal</p>
            <p className="font-medium">{goalTitle}</p>
          </div>

          {/* Action selection */}
          <div>
            <p className="text-sm text-gray-500 mb-2">Action</p>
            <div className="flex gap-2">
              {(["approve", "reject", "defer"] as const).map((a) => (
                <button
                  key={a}
                  onClick={() => setAction(a)}
                  className={`px-4 py-2 rounded-md text-sm capitalize border ${
                    action === a
                      ? a === "approve"
                        ? "bg-green-600 text-white border-green-600"
                        : a === "reject"
                          ? "bg-red-600 text-white border-red-600"
                          : "bg-yellow-500 text-white border-yellow-500"
                      : "hover:bg-gray-50"
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          {/* Reason */}
          <div>
            <label className="text-sm text-gray-500 block mb-1">
              Reason {action === "reject" ? "(required)" : "(optional)"}
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={4}
              className="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Provide context for your decision..."
            />
          </div>
        </div>

        <div className="px-6 py-4 border-t flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={!action || (action === "reject" && !reason.trim())}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Submit
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-md text-sm hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </>
  );
}
