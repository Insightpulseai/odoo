import React, { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "./ui/button";

interface CommandBarProps {
  onSubmit: (command: string) => void;
  quickCommands?: string[];
}

const DEFAULT_QUICK_COMMANDS = [
  "Deploy prod",
  "Check prod status",
  "Generate spec for dashboard",
  "Fix production error"
];

export function CommandBar({ 
  onSubmit, 
  quickCommands = DEFAULT_QUICK_COMMANDS
}: CommandBarProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    onSubmit(input);
    setInput("");
  };

  return (
    <div className="border-t bg-white px-6 py-4">
      <div className="max-w-4xl mx-auto space-y-3">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {quickCommands.map((cmd) => (
            <button
              key={cmd}
              onClick={() => setInput(cmd)}
              className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg whitespace-nowrap transition-colors"
            >
              {cmd}
            </button>
          ))}
        </div>
        
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a command... (e.g., 'deploy prod', 'check status')"
            className="flex-1 px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Button type="submit" size="icon" className="h-12 w-12 rounded-xl">
            <Send className="h-5 w-5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
