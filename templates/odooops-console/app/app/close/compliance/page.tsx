import { createClient } from "@/lib/supabase/server";

interface TaxForm {
  id: string;
  formCode: string;
  formName: string;
  frequency: "monthly" | "quarterly";
  deadline: string;
  status: "draft" | "for_review" | "for_payment" | "filed" | "paid";
  payableAmount: string;
  filedAt?: string;
  paidAt?: string;
}

export default async function CompliancePage() {
  const supabase = await createClient();

  // In production, call tax.ui_filings_board(p_org_id, p_period)
  const forms: TaxForm[] = [
    {
      id: "1",
      formCode: "1601-C",
      formName: "Withholding Tax on Compensation",
      frequency: "monthly",
      deadline: "Feb 10, 2026",
      status: "filed",
      payableAmount: "₱45,230",
      filedAt: "Feb 8, 2026",
      paidAt: "Feb 9, 2026",
    },
    {
      id: "2",
      formCode: "0619-E",
      formName: "Expanded Withholding Tax",
      frequency: "monthly",
      deadline: "Feb 10, 2026",
      status: "for_payment",
      payableAmount: "₱12,890",
      filedAt: "Feb 7, 2026",
    },
    {
      id: "3",
      formCode: "2550M",
      formName: "VAT Monthly Declaration",
      frequency: "monthly",
      deadline: "Feb 25, 2026",
      status: "for_review",
      payableAmount: "₱89,450",
    },
    {
      id: "4",
      formCode: "2550Q",
      formName: "VAT Quarterly Declaration",
      frequency: "quarterly",
      deadline: "Apr 25, 2026",
      status: "draft",
      payableAmount: "₱268,340",
    },
    {
      id: "5",
      formCode: "SLSP",
      formName: "Schedule of Laptops, Sales & Purchases",
      frequency: "quarterly",
      deadline: "Apr 25, 2026",
      status: "draft",
      payableAmount: "N/A",
    },
  ];

  const statusConfig = {
    draft: {
      bg: "bg-gray-100",
      text: "text-gray-800",
      label: "Draft",
      nextAction: "Complete form",
    },
    for_review: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      label: "For Review",
      nextAction: "Review & approve",
    },
    for_payment: {
      bg: "bg-orange-100",
      text: "text-orange-800",
      label: "For Payment",
      nextAction: "Process payment",
    },
    filed: {
      bg: "bg-blue-100",
      text: "text-blue-800",
      label: "Filed",
      nextAction: "Confirm payment",
    },
    paid: {
      bg: "bg-green-100",
      text: "text-green-800",
      label: "Paid",
      nextAction: "Complete",
    },
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">BIR Compliance</h1>
        <p className="text-sm text-gray-600 mt-1">
          Philippines BIR tax form board and filing tracker
        </p>
      </div>

      {/* Compliance Summary */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: "Forms Due", value: "3", color: "text-red-600" },
          { label: "Filed (Unpaid)", value: "1", color: "text-orange-600" },
          { label: "Fully Compliant", value: "1", color: "text-green-600" },
          { label: "Total Payable", value: "₱147,570", color: "text-gray-900" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white border border-gray-200 rounded-lg p-4"
          >
            <div className="text-sm text-gray-600 mb-1">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Forms Board */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Tax Forms (Feb 2026)</h2>
        </div>

        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Form Code
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Frequency
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Deadline
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Amount
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Next Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {forms.map((form) => {
              const statusInfo = statusConfig[form.status];
              const isOverdue = new Date(form.deadline) < new Date();

              return (
                <tr key={form.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-semibold text-sm">
                        {form.formCode}
                      </span>
                      {isOverdue && form.status !== "paid" && (
                        <span className="text-red-600 text-xs">⚠️ Overdue</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {form.formName}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    <span className="capitalize">{form.frequency}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {form.deadline}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${statusInfo.bg} ${statusInfo.text}`}
                    >
                      {statusInfo.label}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {form.payableAmount}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                      {statusInfo.nextAction}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Filing History */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Recent Filings</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {forms
            .filter((f) => f.filedAt)
            .map((form) => (
              <div key={form.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-mono font-semibold">
                        {form.formCode}
                      </span>
                      <span className="text-sm text-gray-700">
                        {form.formName}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                      <span>Filed: {form.filedAt}</span>
                      {form.paidAt && <span>Paid: {form.paidAt}</span>}
                      <span>Amount: {form.payableAmount}</span>
                    </div>
                  </div>
                  <span
                    className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${
                      statusConfig[form.status].bg
                    } ${statusConfig[form.status].text}`}
                  >
                    {statusConfig[form.status].label}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* KPI Alerts */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-yellow-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-yellow-900">
              Compliance Alerts
            </h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-yellow-800 mt-2">
              <li>2550M VAT return due in 3 days (Feb 25)</li>
              <li>0619-E payment pending confirmation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
