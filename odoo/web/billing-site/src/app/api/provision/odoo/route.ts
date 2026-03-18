import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase/server'
import { provisionOdooPartner, getOdooPartner } from '@/lib/odoo'
import { z } from 'zod'

const ProvisionRequestSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  company_name: z.string().optional(),
  country_code: z.string().length(2).optional(),
  vat: z.string().optional(),
  phone: z.string().optional(),
  paddle_customer_id: z.string().min(1),
  supabase_org_id: z.string().uuid(),
})

/**
 * POST /api/provision/odoo
 *
 * Creates or updates a customer (res.partner) in Odoo.
 * This endpoint is called after a successful Paddle subscription.
 *
 * Authentication: Requires service role key in Authorization header
 */
export async function POST(request: NextRequest) {
  // Verify service role authentication
  const authHeader = request.headers.get('authorization')
  const expectedAuth = `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`

  if (!authHeader || authHeader !== expectedAuth) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Parse and validate request body
  let body: z.infer<typeof ProvisionRequestSchema>
  try {
    const json = await request.json()
    body = ProvisionRequestSchema.parse(json)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      )
    }
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  // Check if Odoo credentials are configured
  if (!process.env.ODOO_BASE_URL || !process.env.ODOO_USER || !process.env.ODOO_PASSWORD) {
    return NextResponse.json(
      { error: 'Odoo integration not configured' },
      { status: 503 }
    )
  }

  try {
    // Provision partner in Odoo
    const result = await provisionOdooPartner(body)

    // Update Supabase customer with Odoo partner ID
    const supabase = createServiceClient()
    await supabase
      .from('billing.customers')
      .update({ odoo_partner_id: result.partnerId })
      .eq('paddle_customer_id', body.paddle_customer_id)

    return NextResponse.json({
      success: true,
      odoo_partner_id: result.partnerId,
      created: result.created,
    })
  } catch (error) {
    console.error('Odoo provisioning error:', error)
    return NextResponse.json(
      { error: 'Provisioning failed', message: String(error) },
      { status: 500 }
    )
  }
}

/**
 * GET /api/provision/odoo?org_id=<uuid>
 *
 * Gets the Odoo partner record for a given organization.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const orgId = searchParams.get('org_id')

  if (!orgId) {
    return NextResponse.json({ error: 'org_id is required' }, { status: 400 })
  }

  // Verify service role authentication
  const authHeader = request.headers.get('authorization')
  const expectedAuth = `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`

  if (!authHeader || authHeader !== expectedAuth) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Check if Odoo credentials are configured
  if (!process.env.ODOO_BASE_URL || !process.env.ODOO_USER || !process.env.ODOO_PASSWORD) {
    return NextResponse.json(
      { error: 'Odoo integration not configured' },
      { status: 503 }
    )
  }

  try {
    const partner = await getOdooPartner(orgId)

    if (!partner) {
      return NextResponse.json({ error: 'Partner not found' }, { status: 404 })
    }

    return NextResponse.json({ partner })
  } catch (error) {
    console.error('Odoo query error:', error)
    return NextResponse.json(
      { error: 'Query failed', message: String(error) },
      { status: 500 }
    )
  }
}
