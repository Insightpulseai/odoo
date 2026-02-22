export default function RunbooksPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Runbooks</h1>
        <p className="text-sm text-muted-foreground">
          Render docs/ops runbooks (read-only).
        </p>
      </div>

      <div className="rounded-lg border p-4">
        <div className="text-sm font-medium">Coming online</div>
        <ul className="mt-2 list-disc pl-5 text-sm text-muted-foreground">
          <li>Promotion checklist</li>
          <li>Rollback playbook</li>
          <li>Odoo.sh-equivalent runbook</li>
        </ul>
      </div>
    </div>
  )
}
