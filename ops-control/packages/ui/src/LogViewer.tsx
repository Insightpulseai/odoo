import { X, Download, Terminal, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react";
import type { RunEvent } from "@ops-control-room/core";
import { useEffect, useRef } from "react";

interface LogViewerProps {
  title: string;
  events: RunEvent[];
  onClose: () => void;
  ButtonComponent?: React.ComponentType<any>;
  ScrollAreaComponent?: React.ComponentType<any>;
}

const LEVEL_CONFIG = {
  debug: { icon: Info, color: "text-slate-500", bg: "bg-slate-50" },
  info: { icon: Info, color: "text-blue-500", bg: "bg-blue-50" },
  success: { icon: CheckCircle, color: "text-green-500", bg: "bg-green-50" },
  warn: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-50" },
  error: { icon: AlertCircle, color: "text-red-500", bg: "bg-red-50" }
};

export function LogViewer({ 
  title, 
  events, 
  onClose, 
  ButtonComponent,
  ScrollAreaComponent 
}: LogViewerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const exportLogs = () => {
    const content = events
      .map(evt => `[${evt.ts}] [${evt.level.toUpperCase()}] [${evt.source}] ${evt.message}`)
      .join("\n");
    
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const summary = {
    total: events.length,
    success: events.filter(e => e.level === "success").length,
    warnings: events.filter(e => e.level === "warn").length,
    errors: events.filter(e => e.level === "error").length
  };

  const isComplete = events.length > 0 && events[events.length - 1]?.message.includes("completed");

  // Default button component
  const Button = ButtonComponent || (({ children, onClick, variant, size, className }: any) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        variant === "outline" ? "border-2 border-slate-300 hover:bg-slate-100" :
        variant === "ghost" ? "hover:bg-slate-100" :
        "bg-blue-600 hover:bg-blue-700 text-white"
      } ${size === "sm" ? "text-sm px-3 py-1.5" : ""} ${size === "icon" ? "w-10 h-10 p-0" : ""} ${className}`}
    >
      {children}
    </button>
  ));

  // Default scroll area (simple div with overflow)
  const ScrollArea = ScrollAreaComponent || (({ children, className }: any) => (
    <div className={`overflow-auto ${className}`}>{children}</div>
  ));

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
              <Terminal className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">Execution Log</h2>
              <p className="text-sm text-slate-600">{title}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={exportLogs}>
              <Download className="h-4 w-4 mr-2 inline-block" />
              Export
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="px-6 py-4 bg-slate-50 border-b grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{summary.total}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Total Events</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{summary.success}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Success</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-600">{summary.warnings}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{summary.errors}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Errors</div>
          </div>
        </div>

        {/* Logs */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div ref={scrollRef} className="p-6 space-y-2 font-mono text-sm">
              {events.length === 0 ? (
                <div className="text-center text-slate-400 py-12">
                  <Terminal className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>Waiting for events...</p>
                </div>
              ) : (
                events.map((evt, idx) => {
                  const config = LEVEL_CONFIG[evt.level];
                  const Icon = config.icon;
                  
                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg ${config.bg} border border-slate-200 animate-in fade-in slide-in-from-bottom-2`}
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      <div className="flex items-start gap-3">
                        <Icon className={`h-4 w-4 mt-0.5 flex-shrink-0 ${config.color}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-xs text-slate-500">
                              {new Date(evt.ts).toLocaleTimeString()}
                            </span>
                            <span className={`text-xs font-semibold uppercase ${config.color}`}>
                              {evt.level}
                            </span>
                            <span className="text-xs px-2 py-0.5 bg-slate-200 rounded">
                              {evt.source}
                            </span>
                          </div>
                          <p className="text-slate-900 break-words">{evt.message}</p>
                          {evt.data && (
                            <div className="mt-2 text-xs text-slate-600 bg-white/50 rounded p-2 border border-slate-200">
                              <pre className="whitespace-pre-wrap break-all">
                                {JSON.stringify(evt.data, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isComplete ? (
              <>
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-sm text-slate-700">Execution completed</span>
              </>
            ) : (
              <>
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-sm text-slate-700">Running...</span>
              </>
            )}
          </div>
          <Button onClick={onClose} variant={isComplete ? "default" : "outline"}>
            {isComplete ? "Close" : "Close (running in background)"}
          </Button>
        </div>
      </div>
    </div>
  );
}
