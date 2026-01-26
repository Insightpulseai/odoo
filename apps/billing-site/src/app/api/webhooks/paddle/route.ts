import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase/server'
import { verifyPaddleWebhookSignature, type PaddleWebhookEvent } from '@/lib/paddle'
import { provisionOdooPartner } from '@/lib/odoo'

export async function POST(request: NextRequest) {
  const rawBody = await request.text()
  const signature = request.headers.get('paddle-signature')

  // Verify webhook signature
  const secret = process.env.PADDLE_WEBHOOK_SECRET
  if (!secret) {
    console.error('PADDLE_WEBHOOK_SECRET not configured')
    return NextResponse.json({ error: 'Webhook secret not configured' }, { status: 500 })
  }

  if (!signature || !verifyPaddleWebhookSignature(rawBody, signature, secret)) {
    console.error('Invalid webhook signature')
    return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
  }

  // Parse the event
  let event: PaddleWebhookEvent
  try {
    event = JSON.parse(rawBody)
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }

  const supabase = createServiceClient()

  // Log the webhook event for debugging/replay
  await supabase.from('billing.webhook_events').insert({
    event_id: event.event_id,
    event_type: event.event_type,
    payload: event,
    processed: false,
  })

  try {
    switch (event.event_type) {
      case 'customer.created':
      case 'customer.updated':
        await handleCustomerEvent(event, supabase)
        break

      case 'subscription.created':
      case 'subscription.activated':
        await handleSubscriptionCreated(event, supabase)
        break

      case 'subscription.updated':
        await handleSubscriptionUpdated(event, supabase)
        break

      case 'subscription.canceled':
        await handleSubscriptionCanceled(event, supabase)
        break

      case 'transaction.completed':
        await handleTransactionCompleted(event, supabase)
        break

      case 'transaction.paid':
        await handleTransactionPaid(event, supabase)
        break

      default:
        console.log(`Unhandled event type: ${event.event_type}`)
    }

    // Mark event as processed
    await supabase
      .from('billing.webhook_events')
      .update({ processed: true, processed_at: new Date().toISOString() })
      .eq('event_id', event.event_id)

    return NextResponse.json({ received: true })
  } catch (error) {
    console.error('Webhook processing error:', error)

    // Log error for debugging
    await supabase
      .from('billing.webhook_events')
      .update({ error: String(error) })
      .eq('event_id', event.event_id)

    return NextResponse.json({ error: 'Processing failed' }, { status: 500 })
  }
}

async function handleCustomerEvent(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event
  const customData = data.custom_data || {}

  await supabase.from('billing.customers').upsert(
    {
      paddle_customer_id: data.customer_id,
      email: customData.email || '',
      name: customData.name || null,
      company_name: customData.company_name || null,
      supabase_user_id: customData.supabase_user_id || null,
      updated_at: new Date().toISOString(),
    },
    { onConflict: 'paddle_customer_id' }
  )
}

async function handleSubscriptionCreated(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event
  const item = data.items?.[0]
  const customData = data.custom_data || {}

  // First, ensure customer exists
  const { data: customer } = await supabase
    .from('billing.customers')
    .select('id, supabase_user_id')
    .eq('paddle_customer_id', data.customer_id)
    .single()

  if (!customer) {
    // Create customer if doesn't exist
    const { data: newCustomer } = await supabase
      .from('billing.customers')
      .insert({
        paddle_customer_id: data.customer_id,
        email: customData.email || '',
        supabase_user_id: customData.supabase_user_id || null,
      })
      .select('id')
      .single()

    if (!newCustomer) throw new Error('Failed to create customer')
  }

  const customerId = customer?.id

  // Create subscription
  await supabase.from('billing.subscriptions').upsert(
    {
      paddle_subscription_id: data.id,
      customer_id: customerId,
      status: data.status,
      plan_name: item?.price?.name || 'Unknown',
      price_id: item?.price?.id || '',
      product_id: item?.price?.product_id || null,
      currency_code: data.currency_code,
      unit_price_amount: item?.price?.unit_price?.amount
        ? parseInt(item.price.unit_price.amount)
        : null,
      quantity: item?.quantity || 1,
      current_period_start: data.current_billing_period?.starts_at || null,
      current_period_end: data.current_billing_period?.ends_at || null,
      metadata: customData,
    },
    { onConflict: 'paddle_subscription_id' }
  )

  // Provision customer in Odoo (only on first subscription)
  if (customData.supabase_org_id) {
    try {
      await provisionOdooPartner({
        name: customData.name || customData.email || '',
        email: customData.email || '',
        company_name: customData.company_name,
        country_code: customData.country_code,
        paddle_customer_id: data.customer_id,
        supabase_org_id: customData.supabase_org_id,
      })
    } catch (error) {
      console.error('Failed to provision Odoo partner:', error)
      // Don't fail the webhook - Odoo provisioning is best-effort
    }
  }
}

async function handleSubscriptionUpdated(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event
  const item = data.items?.[0]

  await supabase
    .from('billing.subscriptions')
    .update({
      status: data.status,
      plan_name: item?.price?.name || 'Unknown',
      price_id: item?.price?.id || '',
      unit_price_amount: item?.price?.unit_price?.amount
        ? parseInt(item.price.unit_price.amount)
        : null,
      quantity: item?.quantity || 1,
      current_period_start: data.current_billing_period?.starts_at || null,
      current_period_end: data.current_billing_period?.ends_at || null,
      updated_at: new Date().toISOString(),
    })
    .eq('paddle_subscription_id', data.id)
}

async function handleSubscriptionCanceled(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event

  await supabase
    .from('billing.subscriptions')
    .update({
      status: 'canceled',
      canceled_at: event.occurred_at,
      updated_at: new Date().toISOString(),
    })
    .eq('paddle_subscription_id', data.id)
}

async function handleTransactionCompleted(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event

  // Get customer ID from our database
  const { data: customer } = await supabase
    .from('billing.customers')
    .select('id')
    .eq('paddle_customer_id', data.customer_id)
    .single()

  if (!customer) {
    console.error('Customer not found for transaction:', data.customer_id)
    return
  }

  // Create or update invoice record
  await supabase.from('billing.invoices').upsert(
    {
      paddle_transaction_id: data.id,
      customer_id: customer.id,
      status: data.status,
      currency_code: data.currency_code,
      billed_at: event.occurred_at,
    },
    { onConflict: 'paddle_transaction_id' }
  )
}

async function handleTransactionPaid(
  event: PaddleWebhookEvent,
  supabase: ReturnType<typeof createServiceClient>
) {
  const { data } = event

  await supabase
    .from('billing.invoices')
    .update({
      status: 'paid',
      paid_at: event.occurred_at,
      updated_at: new Date().toISOString(),
    })
    .eq('paddle_transaction_id', data.id)
}
