import SupabaseManagerClient from './supabase-manager-client'

export default function DatabasePage() {
  const projectRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF ?? ''
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold">Database</h2>
      </div>
      <SupabaseManagerClient projectRef={projectRef} />
    </div>
  )
}
