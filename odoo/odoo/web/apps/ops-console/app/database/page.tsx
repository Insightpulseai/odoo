import SupabaseManagerClient from './supabase-manager-client'
import { IntegrationBadges } from '@/components/platform/IntegrationBadges'

export const dynamic = "force-dynamic"

export default function DatabasePage() {
  const projectRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF ?? ''
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold">Database</h2>
          <div className="mt-2">
            <IntegrationBadges />
          </div>
        </div>
      </div>
      <SupabaseManagerClient projectRef={projectRef} />
    </div>
  )
}
