import React from "react";
import { Toaster } from "./ui/sonner";

interface AppShellProps {
  children: React.ReactNode;
  status?: "operational" | "degraded" | "down";
  statusMessage?: string;
}

export function AppShell({ 
  children, 
  status = "operational",
  statusMessage = "All systems operational" 
}: AppShellProps) {
  const statusColors = {
    operational: "bg-green-500",
    degraded: "bg-amber-500",
    down: "bg-red-500"
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b bg-white/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <span className="text-white font-bold">⚡</span>
          </div>
          <div>
            <h1 className="font-semibold">Ops Control Room</h1>
            <p className="text-sm text-slate-500">ChatGPT Runbook Executor</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${statusColors[status]} ${status === "operational" ? "animate-pulse" : ""}`} />
            <span className="text-slate-600">{statusMessage}</span>
          </div>
        </div>
      </header>

      {children}
      
      <Toaster position="top-right" richColors />
    </div>
  );
}