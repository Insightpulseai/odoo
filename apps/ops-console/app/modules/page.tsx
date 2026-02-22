export default function ModulesPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Modules</h1>
        <p className="text-sm text-muted-foreground">
          Wave status + allowlisted OCA modules (read-only).
        </p>
      </div>

      <div className="rounded-lg border p-4">
        <div className="text-sm font-medium">Coming online</div>
        <ul className="mt-2 list-disc pl-5 text-sm text-muted-foreground">
          <li>Wave tabs (Wave 1–4) sourced from SSOT</li>
          <li>Installed vs allowlisted diff per environment</li>
          <li>Evidence artifact links (module_status_*.txt)</li>
        </ul>
      </div>
    </div>
  )
}
