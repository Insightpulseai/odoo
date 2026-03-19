import { Send } from "lucide-react";

interface CommandBarProps {
  onSubmit: (command: string) => void;
  quickCommands?: string[];
  ButtonComponent?: React.ComponentType<any>;
}

const DEFAULT_QUICK_COMMANDS = [
  "Deploy prod",
  "Check prod status",
  "Generate spec for dashboard",
  "Fix production error"
];

export function CommandBar({ 
  onSubmit, 
  quickCommands = DEFAULT_QUICK_COMMANDS,
  ButtonComponent 
}: CommandBarProps) {
  const [input, setInput] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    onSubmit(input);
    setInput("");
  };

  const Button = ButtonComponent || (({ children, onClick, type, size, className }: any) => (
    <button
      type={type}
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors bg-blue-600 hover:bg-blue-700 text-white ${
        size === "icon" ? "w-12 h-12 p-0" : ""
      } ${className}`}
    >
      {children}
    </button>
  ));

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

// Need React import for useState
import React from "react";
