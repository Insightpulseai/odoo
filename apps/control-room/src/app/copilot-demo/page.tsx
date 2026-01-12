'use client';

import { useState } from 'react';
import {
  CopilotPanel,
  CopilotProfile,
  CopilotRecordSummary,
} from '@/components/copilot';

// Demo record configurations
const DEMO_RECORDS: Record<string, { profile: CopilotProfile; record: CopilotRecordSummary }> = {
  invoice: {
    profile: {
      id: 'finance_invoice',
      name: 'Finance Copilot',
      slug: 'finance-invoice',
      modelLabel: 'Claude',
      targetModel: 'account.move',
    },
    record: {
      id: 123,
      model: 'account.move',
      displayName: 'INV/2026/0001',
      icon: 'P',
      fields: [
        { key: 'partner', label: 'Customer', value: 'TBWA\\SMP' },
        { key: 'date', label: 'Date', value: '2026-01-13' },
        { key: 'amount_total', label: 'Total', value: 'P 250,000' },
        { key: 'status', label: 'Status', value: 'To Invoice' },
        { key: 'due_date', label: 'Due Date', value: '2026-02-12' },
      ],
    },
  },
  project: {
    profile: {
      id: 'project_copilot',
      name: 'Project Copilot',
      slug: 'project',
      modelLabel: 'Claude',
      targetModel: 'project.project',
    },
    record: {
      id: 456,
      model: 'project.project',
      displayName: 'Scout v5 Development',
      icon: 'Pr',
      fields: [
        { key: 'manager', label: 'Manager', value: 'Jake Tolentino' },
        { key: 'status', label: 'Stage', value: 'In Progress' },
        { key: 'deadline', label: 'Deadline', value: '2026-03-31' },
        { key: 'budget', label: 'Budget', value: 'P 1,200,000' },
        { key: 'completion', label: 'Progress', value: '65%' },
      ],
    },
  },
  task: {
    profile: {
      id: 'task_copilot',
      name: 'Task Assistant',
      slug: 'task',
      modelLabel: 'GPT-4',
      targetModel: 'project.task',
    },
    record: {
      id: 789,
      model: 'project.task',
      displayName: 'Implement Copilot UI',
      icon: 'Ts',
      fields: [
        { key: 'assignee', label: 'Assignee', value: 'Claude Code' },
        { key: 'project', label: 'Project', value: 'Scout v5' },
        { key: 'priority', label: 'Priority', value: 'High' },
        { key: 'estimated_hours', label: 'Est. Hours', value: '8' },
        { key: 'stage', label: 'Stage', value: 'In Development' },
      ],
    },
  },
  expense: {
    profile: {
      id: 'expense_copilot',
      name: 'Expense Copilot',
      slug: 'expense',
      modelLabel: 'Claude',
      targetModel: 'hr.expense',
    },
    record: {
      id: 101,
      model: 'hr.expense',
      displayName: 'EXP/2026/0042',
      icon: 'Ex',
      fields: [
        { key: 'employee', label: 'Employee', value: 'Maria Santos' },
        { key: 'description', label: 'Description', value: 'Client Dinner - Manila' },
        { key: 'amount', label: 'Amount', value: 'P 12,500' },
        { key: 'category', label: 'Category', value: 'Meals & Entertainment' },
        { key: 'status', label: 'Status', value: 'Pending Approval' },
      ],
    },
  },
};

export default function CopilotDemoPage() {
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState<keyof typeof DEMO_RECORDS>('invoice');

  const { profile, record } = DEMO_RECORDS[selectedDemo];

  return (
    <div className="min-h-screen bg-surface-900 text-white">
      {/* Header */}
      <header className="border-b border-surface-700 bg-surface-800/95 backdrop-blur-sm sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">Copilot UI Demo</h1>
            <p className="text-sm text-surface-400">Fluent-style AI assistant for Odoo records</p>
          </div>
          <a
            href="/"
            className="text-sm text-surface-400 hover:text-white transition-colors"
          >
            Back to Home
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Demo Selection */}
        <section className="mb-12">
          <h2 className="text-lg font-semibold mb-4">Select a Record Type</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(DEMO_RECORDS).map(([key, { profile: p, record: r }]) => (
              <button
                key={key}
                onClick={() => setSelectedDemo(key as keyof typeof DEMO_RECORDS)}
                className={`p-4 rounded-xl border transition-all text-left ${
                  selectedDemo === key
                    ? 'bg-primary-500/20 border-primary-500 shadow-lg shadow-primary-500/10'
                    : 'bg-surface-800 border-surface-700 hover:border-surface-500'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-500 text-sm font-semibold">
                    {r.icon}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{p.name}</div>
                    <div className="text-xs text-surface-400">{r.model}</div>
                  </div>
                </div>
                <div className="text-xs text-surface-300 truncate">{r.displayName}</div>
              </button>
            ))}
          </div>
        </section>

        {/* Selected Record Preview */}
        <section className="mb-12">
          <h2 className="text-lg font-semibold mb-4">Current Record Context</h2>
          <div className="bg-surface-800 border border-surface-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-500 text-base font-semibold">
                  {record.icon}
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-surface-400">
                    {profile.name}
                  </div>
                  <div className="text-lg font-semibold">{record.displayName}</div>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-surface-700 text-xs font-medium text-surface-300 border border-surface-600">
                {profile.modelLabel}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {record.fields.map((field) => (
                <div key={field.key} className="bg-surface-700/50 rounded-lg p-3">
                  <div className="text-xs text-surface-400 uppercase tracking-wide mb-1">
                    {field.label}
                  </div>
                  <div className="text-sm font-medium truncate">
                    {field.value ?? '—'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Open Copilot CTA */}
        <section className="text-center">
          <button
            onClick={() => setCopilotOpen(true)}
            className="inline-flex items-center gap-3 px-8 py-4 bg-primary-500 hover:bg-primary-600 rounded-xl text-white font-semibold shadow-lg shadow-primary-500/30 transition-all hover:shadow-xl hover:shadow-primary-500/40"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Open Copilot
          </button>
          <p className="mt-4 text-sm text-surface-400">
            Click to open the Copilot panel for the selected record
          </p>
        </section>

        {/* Features */}
        <section className="mt-16">
          <h2 className="text-lg font-semibold mb-6 text-center">Copilot Features</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-surface-800 border border-surface-700 rounded-xl p-6">
              <h3 className="font-medium mb-2">Context-Aware</h3>
              <p className="text-sm text-surface-400">
                Copilot understands the current record context and provides relevant insights.
              </p>
            </div>
            <div className="bg-surface-800 border border-surface-700 rounded-xl p-6">
              <h3 className="font-medium mb-2">Quick Actions</h3>
              <p className="text-sm text-surface-400">
                Pre-built action templates for common tasks like summarizing, drafting emails, and planning.
              </p>
            </div>
            <div className="bg-surface-800 border border-surface-700 rounded-xl p-6">
              <h3 className="font-medium mb-2">Multi-Model</h3>
              <p className="text-sm text-surface-400">
                Supports multiple AI models (Claude, GPT-4, Gemini) configurable per profile.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Copilot Panel */}
      <CopilotPanel
        open={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        profile={profile}
        record={record}
      />
    </div>
  );
}
