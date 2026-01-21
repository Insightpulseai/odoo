// Supabase Edge Function: sync-odoo-modules
// Purpose: Sync Odoo installed modules to Supabase catalog
// Trigger: Called by CI/CD or scheduled cron

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface OdooModule {
  name: string
  shortdesc?: string
  category?: string
  category_id?: [number, string]
  license?: string
  installed_version?: string
}

interface SyncRequest {
  modules?: OdooModule[]
  odoo_url?: string
  odoo_database?: string
  odoo_password?: string
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const body: SyncRequest = await req.json()
    let modules: OdooModule[] = body.modules || []

    // If no modules provided, fetch from Odoo
    if (modules.length === 0 && body.odoo_url) {
      modules = await fetchOdooModules(
        body.odoo_url,
        body.odoo_database || 'odoo_core',
        body.odoo_password || 'admin'
      )
    }

    if (modules.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No modules provided and could not fetch from Odoo' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Classify and upsert modules
    const moduleData = modules.map((m: OdooModule) => ({
      module_name: m.name,
      display_name: m.shortdesc || m.name,
      category: m.category_id ? m.category_id[1] : (m.category || 'Uncategorized'),
      source: classifySource(m.name, m.license),
      installed_version: m.installed_version || '',
      is_installed: true,
      last_synced_at: new Date().toISOString(),
    }))

    const { data, error } = await supabase
      .from('odoo_modules')
      .upsert(moduleData, { onConflict: 'module_name' })

    if (error) {
      console.error('Supabase error:', error)
      throw error
    }

    // Check for EE modules (should not exist)
    const eeModules = modules.filter(m => m.license === 'OEEL-1')
    const hasEE = eeModules.length > 0

    return new Response(
      JSON.stringify({
        success: true,
        count: modules.length,
        sources: {
          ce: moduleData.filter(m => m.source === 'ce').length,
          oca: moduleData.filter(m => m.source === 'oca').length,
          ipai: moduleData.filter(m => m.source === 'ipai').length,
          community: moduleData.filter(m => m.source === 'community').length,
        },
        warnings: hasEE ? [`EE modules detected: ${eeModules.map(m => m.name).join(', ')}`] : [],
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    console.error('Sync error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

function classifySource(name: string, license?: string): string {
  if (name.startsWith('ipai_')) return 'ipai'
  if (license === 'OEEL-1') return 'ee' // Should never happen in CE deployment
  if (name.includes('oca') || name.endsWith('_oca')) return 'oca'

  // Known OCA modules
  const ocaModules = [
    'account_financial_report', 'mis_builder', 'account_reconcile_oca',
    'project_timeline', 'hr_timesheet_sheet', 'helpdesk_mgmt',
    'mail_tracking', 'attachment_s3', 'base_report_to_printer',
    'web_responsive', 'fieldservice', 'mrp_multi_level', 'quality_control',
  ]
  if (ocaModules.includes(name)) return 'oca'

  // Assume CE for standard modules
  return 'ce'
}

async function fetchOdooModules(url: string, database: string, password: string): Promise<OdooModule[]> {
  const response = await fetch(`${url}/jsonrpc`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute_kw',
        args: [
          database,
          2, // Admin UID
          password,
          'ir.module.module',
          'search_read',
          [[['state', '=', 'installed']]],
          {
            fields: ['name', 'shortdesc', 'category_id', 'license', 'installed_version'],
          },
        ],
      },
      id: 1,
    }),
  })

  const data = await response.json()
  return data.result || []
}
