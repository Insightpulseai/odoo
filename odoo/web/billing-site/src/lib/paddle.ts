import crypto from 'crypto'

export interface PaddleWebhookEvent {
  event_id: string
  event_type: string
  occurred_at: string
  notification_id: string
  data: {
    id: string
    status: string
    customer_id: string
    address_id?: string
    business_id?: string
    currency_code: string
    items: Array<{
      price: {
        id: string
        product_id: string
        name: string
        unit_price: {
          amount: string
          currency_code: string
        }
      }
      quantity: number
    }>
    billing_period?: {
      starts_at: string
      ends_at: string
    }
    current_billing_period?: {
      starts_at: string
      ends_at: string
    }
    custom_data?: Record<string, string>
  }
}

export function verifyPaddleWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  if (!signature || !secret) {
    return false
  }

  // Paddle uses ts;h1=<signature> format
  const parts = signature.split(';')
  const timestampPart = parts.find(p => p.startsWith('ts='))
  const signaturePart = parts.find(p => p.startsWith('h1='))

  if (!timestampPart || !signaturePart) {
    return false
  }

  const timestamp = timestampPart.replace('ts=', '')
  const expectedSignature = signaturePart.replace('h1=', '')

  // Reconstruct the signed payload
  const signedPayload = `${timestamp}:${payload}`

  // Calculate HMAC
  const hmac = crypto.createHmac('sha256', secret)
  hmac.update(signedPayload)
  const calculatedSignature = hmac.digest('hex')

  // Constant-time comparison
  try {
    return crypto.timingSafeEqual(
      Buffer.from(calculatedSignature, 'hex'),
      Buffer.from(expectedSignature, 'hex')
    )
  } catch {
    return false
  }
}

export const PRICING_PLANS = {
  starter: {
    name: 'Starter',
    description: 'Perfect for small teams getting started',
    features: [
      'Up to 5 users',
      'Basic automation workflows',
      'Standard analytics dashboard',
      'Email support',
      'API access (1,000 calls/month)',
    ],
    monthly: {
      price: 49,
      priceId: process.env.NEXT_PUBLIC_PADDLE_PRICE_ID_STARTER_MONTHLY,
    },
    annual: {
      price: 39,
      priceId: process.env.NEXT_PUBLIC_PADDLE_PRICE_ID_STARTER_ANNUAL,
    },
  },
  pro: {
    name: 'Pro',
    description: 'For growing businesses that need more power',
    features: [
      'Up to 25 users',
      'Advanced automation workflows',
      'Custom analytics & reports',
      'Priority support',
      'API access (10,000 calls/month)',
      'Integrations (Slack, Teams, etc.)',
      'Custom branding',
    ],
    monthly: {
      price: 149,
      priceId: process.env.NEXT_PUBLIC_PADDLE_PRICE_ID_PRO_MONTHLY,
    },
    annual: {
      price: 119,
      priceId: process.env.NEXT_PUBLIC_PADDLE_PRICE_ID_PRO_ANNUAL,
    },
    popular: true,
  },
  enterprise: {
    name: 'Enterprise',
    description: 'For organizations that need the full platform',
    features: [
      'Unlimited users',
      'Enterprise automation suite',
      'Advanced BI & forecasting',
      'Dedicated support manager',
      'Unlimited API access',
      'All integrations',
      'SSO & advanced security',
      'Custom SLA',
      'On-premise deployment option',
    ],
    monthly: {
      price: null, // Contact sales
      priceId: null,
    },
    annual: {
      price: null,
      priceId: null,
    },
  },
} as const
