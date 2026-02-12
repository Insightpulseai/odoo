"use client";

import { useState } from "react";

interface FileNode {
  name: string;
  type: "file" | "folder";
  path: string;
  children?: FileNode[];
}

export default function BuildEditorPage() {
  const [selectedFile, setSelectedFile] = useState<string | null>(
    "addons/ipai_core/__manifest__.py"
  );
  const [fileContent, setFileContent] = useState(`{
    "name": "IPAI Core",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "Core functionality for IPAI addons",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}`);

  // Demo file tree
  const fileTree: FileNode[] = [
    {
      name: "addons",
      type: "folder",
      path: "addons",
      children: [
        {
          name: "ipai_core",
          type: "folder",
          path: "addons/ipai_core",
          children: [
            {
              name: "__manifest__.py",
              type: "file",
              path: "addons/ipai_core/__manifest__.py",
            },
            {
              name: "__init__.py",
              type: "file",
              path: "addons/ipai_core/__init__.py",
            },
          ],
        },
      ],
    },
    {
      name: "odoo.conf",
      type: "file",
      path: "odoo.conf",
    },
  ];

  const renderFileTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => (
      <div key={node.path} style={{ paddingLeft: `${depth * 16}px` }}>
        {node.type === "folder" ? (
          <div>
            <div className="py-1 text-sm text-gray-700 font-medium cursor-pointer hover:bg-gray-100">
              📁 {node.name}
            </div>
            {node.children && renderFileTree(node.children, depth + 1)}
          </div>
        ) : (
          <div
            className={`py-1 text-sm cursor-pointer hover:bg-gray-100 ${
              selectedFile === node.path ? "bg-blue-50 text-blue-700" : "text-gray-600"
            }`}
            onClick={() => setSelectedFile(node.path)}
          >
            📄 {node.name}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Code Editor</h2>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">
            Read-only Mode
          </button>
          <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
            Open in IDE
          </button>
        </div>
      </div>

      {/* Editor Layout */}
      <div className="grid grid-cols-4 gap-4 border border-gray-200 rounded-lg overflow-hidden">
        {/* File Tree */}
        <div className="col-span-1 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto max-h-[600px]">
          <h3 className="text-sm font-semibold mb-3">Files</h3>
          {renderFileTree(fileTree)}
        </div>

        {/* Editor */}
        <div className="col-span-3 bg-white">
          {selectedFile ? (
            <div className="flex flex-col h-full">
              {/* File Header */}
              <div className="border-b border-gray-200 px-4 py-2 bg-gray-50">
                <span className="text-sm font-medium">{selectedFile}</span>
              </div>

              {/* Content */}
              <div className="flex-1 p-4">
                <pre className="font-mono text-sm bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
                  {fileContent}
                </pre>
              </div>

              {/* Footer */}
              <div className="border-t border-gray-200 px-4 py-2 bg-gray-50 text-xs text-gray-600">
                Read-only view • Full editing available in IDE
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[600px] text-gray-500">
              Select a file to view
            </div>
          )}
        </div>
      </div>

      <div className="text-sm text-gray-600">
        <p>
          💡 This is a read-only preview. For full editing capabilities, use the
          "Open in IDE" button to launch your local development environment.
        </p>
      </div>
    </div>
  );
}
