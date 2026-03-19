"use client";

import { useState } from "react";

export default function BuildShellPage() {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState<string[]>([
    "Welcome to Odoo Shell",
    "Connected to build environment",
    "Type 'help' for available commands",
    "",
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    // Add command to output
    setOutput((prev) => [...prev, `$ ${command}`, ""]);

    // Simulate command execution
    // In production, this would call an RPC or WebSocket
    setTimeout(() => {
      const mockResponse = `Executed: ${command}\n(Shell execution not yet implemented)`;
      setOutput((prev) => [...prev, mockResponse, ""]);
    }, 100);

    setCommand("");
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Interactive Shell</h2>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">
            Clear
          </button>
          <button className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">
            Download Session
          </button>
        </div>
      </div>

      {/* Shell Terminal */}
      <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-sm">
        {/* Output */}
        <div className="space-y-1 mb-4 min-h-[400px] max-h-[600px] overflow-y-auto">
          {output.map((line, idx) => (
            <div key={idx} className={line.startsWith("$") ? "text-green-400" : ""}>
              {line}
            </div>
          ))}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <span className="text-green-400">$</span>
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            className="flex-1 bg-transparent outline-none text-gray-100"
            placeholder="Enter command..."
            autoFocus
          />
        </form>
      </div>

      <div className="text-sm text-gray-600">
        <p className="mb-2">Available commands:</p>
        <ul className="list-disc list-inside space-y-1 text-xs">
          <li>
            <code className="bg-gray-100 px-1 rounded">odoo shell</code> - Start
            Odoo Python shell
          </li>
          <li>
            <code className="bg-gray-100 px-1 rounded">psql</code> - Connect to
            database
          </li>
          <li>
            <code className="bg-gray-100 px-1 rounded">ls</code>,{" "}
            <code className="bg-gray-100 px-1 rounded">cat</code>,{" "}
            <code className="bg-gray-100 px-1 rounded">grep</code> - File
            operations
          </li>
        </ul>
      </div>
    </div>
  );
}
