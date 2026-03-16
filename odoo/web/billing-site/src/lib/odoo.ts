/**
 * Odoo JSON-RPC client for partner provisioning
 *
 * This module handles the creation/update of res.partner records in Odoo
 * when a new subscription is created via Paddle.
 */

interface OdooConfig {
  baseUrl: string
  db: string
  username: string
  password: string
}

interface OdooPartnerData {
  name: string
  email: string
  company_name?: string
  country_code?: string
  vat?: string
  phone?: string
  paddle_customer_id: string
  supabase_org_id: string
}

interface JsonRpcResponse<T = unknown> {
  jsonrpc: '2.0'
  id: number
  result?: T
  error?: {
    code: number
    message: string
    data: {
      name: string
      message: string
      debug: string
    }
  }
}

let sessionUid: number | null = null

async function jsonRpc<T>(
  url: string,
  method: string,
  params: Record<string, unknown>
): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'call',
      params: {
        service: method.split('.')[0],
        method: method.split('.')[1],
        args: params.args,
      },
    }),
  })

  const data: JsonRpcResponse<T> = await response.json()

  if (data.error) {
    throw new Error(`Odoo RPC Error: ${data.error.data?.message || data.error.message}`)
  }

  return data.result as T
}

async function authenticate(config: OdooConfig): Promise<number> {
  if (sessionUid) return sessionUid

  const result = await jsonRpc<number>(
    `${config.baseUrl}/jsonrpc`,
    'common.authenticate',
    {
      args: [config.db, config.username, config.password, {}],
    }
  )

  if (!result) {
    throw new Error('Odoo authentication failed')
  }

  sessionUid = result
  return result
}

async function execute<T>(
  config: OdooConfig,
  model: string,
  method: string,
  args: unknown[],
  kwargs: Record<string, unknown> = {}
): Promise<T> {
  const uid = await authenticate(config)

  const response = await fetch(`${config.baseUrl}/jsonrpc`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'call',
      params: {
        service: 'object',
        method: 'execute_kw',
        args: [config.db, uid, config.password, model, method, args, kwargs],
      },
    }),
  })

  const data: JsonRpcResponse<T> = await response.json()

  if (data.error) {
    throw new Error(`Odoo execute error: ${data.error.data?.message || data.error.message}`)
  }

  return data.result as T
}

/**
 * Create or update a partner in Odoo based on Paddle customer data
 * Idempotent: uses supabase_org_id as the unique key
 */
export async function provisionOdooPartner(
  partnerData: OdooPartnerData
): Promise<{ partnerId: number; created: boolean }> {
  const config: OdooConfig = {
    baseUrl: process.env.ODOO_BASE_URL!,
    db: process.env.ODOO_DB!,
    username: process.env.ODOO_USER!,
    password: process.env.ODOO_PASSWORD!,
  }

  // Search for existing partner by supabase_org_id (custom field)
  const existingPartners = await execute<number[]>(
    config,
    'res.partner',
    'search',
    [[['x_supabase_org_id', '=', partnerData.supabase_org_id]]]
  )

  const partnerValues: Record<string, unknown> = {
    name: partnerData.company_name || partnerData.name,
    email: partnerData.email,
    is_company: !!partnerData.company_name,
    phone: partnerData.phone,
    vat: partnerData.vat,
    x_paddle_customer_id: partnerData.paddle_customer_id,
    x_supabase_org_id: partnerData.supabase_org_id,
    customer_rank: 1,
  }

  // Set country if provided
  if (partnerData.country_code) {
    const countries = await execute<number[]>(
      config,
      'res.country',
      'search',
      [[['code', '=', partnerData.country_code.toUpperCase()]]]
    )
    if (countries.length > 0) {
      partnerValues.country_id = countries[0]
    }
  }

  if (existingPartners.length > 0) {
    // Update existing partner
    await execute<boolean>(
      config,
      'res.partner',
      'write',
      [[existingPartners[0]], partnerValues]
    )
    return { partnerId: existingPartners[0], created: false }
  } else {
    // Create new partner
    const partnerId = await execute<number>(
      config,
      'res.partner',
      'create',
      [partnerValues]
    )
    return { partnerId, created: true }
  }
}

/**
 * Get partner details from Odoo
 */
export async function getOdooPartner(
  supabaseOrgId: string
): Promise<Record<string, unknown> | null> {
  const config: OdooConfig = {
    baseUrl: process.env.ODOO_BASE_URL!,
    db: process.env.ODOO_DB!,
    username: process.env.ODOO_USER!,
    password: process.env.ODOO_PASSWORD!,
  }

  const partners = await execute<Array<Record<string, unknown>>>(
    config,
    'res.partner',
    'search_read',
    [[['x_supabase_org_id', '=', supabaseOrgId]]],
    {
      fields: ['id', 'name', 'email', 'phone', 'country_id', 'x_paddle_customer_id'],
      limit: 1,
    }
  )

  return partners[0] || null
}
