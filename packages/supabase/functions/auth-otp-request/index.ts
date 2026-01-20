// Supabase Edge Function: Request Email OTP
// Purpose: Generate OTP, store in database, send via Mailgun
// POST /auth-otp-request { email: string }

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const MAILGUN_API_KEY = Deno.env.get('MAILGUN_API_KEY')!
const MAILGUN_DOMAIN = Deno.env.get('MAILGUN_DOMAIN') || 'mg.insightpulseai.net'
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface RequestOTPPayload {
  email: string
}

interface OTPResponse {
  success: boolean
  message?: string
  error?: string
  expires_in_seconds?: number
  requests_remaining?: number
  blocked_until?: string
  retry_after_seconds?: number
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Parse request body
    const { email }: RequestOTPPayload = await req.json()

    if (!email || typeof email !== 'string') {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'invalid_request',
          message: 'Email address is required'
        } as OTPResponse),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Validate email format
    const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/
    if (!emailRegex.test(email)) {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'invalid_email',
          message: 'Invalid email format'
        } as OTPResponse),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Get client IP and user agent for audit
    const clientIP = req.headers.get('x-forwarded-for')?.split(',')[0] ||
                     req.headers.get('x-real-ip') ||
                     'unknown'
    const userAgent = req.headers.get('user-agent') || 'unknown'

    // Create Supabase service role client
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    // Call database function to generate OTP
    const { data, error } = await supabase.rpc('request_otp', {
      p_email: email.toLowerCase().trim(),
      p_ip_address: clientIP,
      p_user_agent: userAgent
    })

    if (error) {
      console.error('Database error:', error)
      return new Response(
        JSON.stringify({
          success: false,
          error: 'database_error',
          message: 'Failed to generate OTP. Please try again.'
        } as OTPResponse),
        {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    // Check if rate limited
    if (!data.success && data.reason === 'rate_limited') {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'rate_limited',
          message: 'Too many requests. Please try again later.',
          blocked_until: data.blocked_until,
          retry_after_seconds: data.retry_after_seconds
        } as OTPResponse),
        {
          status: 429,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'Retry-After': data.retry_after_seconds?.toString() || '3600'
          }
        }
      )
    }

    if (!data.success && data.reason === 'rate_limit_exceeded') {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'rate_limit_exceeded',
          message: 'Rate limit exceeded. Your account is temporarily blocked.',
          blocked_until: data.blocked_until,
          retry_after_seconds: data.retry_after_seconds
        } as OTPResponse),
        {
          status: 429,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'Retry-After': data.retry_after_seconds?.toString() || '3600'
          }
        }
      )
    }

    // Send OTP via Mailgun
    const mailgunUrl = `https://api.mailgun.net/v3/${MAILGUN_DOMAIN}/messages`
    const mailgunAuth = `Basic ${btoa(`api:${MAILGUN_API_KEY}`)}`

    const emailBody = `
Your verification code is: ${data.otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

--
InsightPulse AI
https://insightpulseai.net
`.trim()

    const formData = new FormData()
    formData.append('from', `InsightPulse AI <noreply@${MAILGUN_DOMAIN}>`)
    formData.append('to', email)
    formData.append('subject', `Your verification code: ${data.otp_code}`)
    formData.append('text', emailBody)

    const mailgunResponse = await fetch(mailgunUrl, {
      method: 'POST',
      headers: {
        'Authorization': mailgunAuth
      },
      body: formData
    })

    if (!mailgunResponse.ok) {
      const errorText = await mailgunResponse.text()
      console.error('Mailgun error:', errorText)

      // OTP was generated but email failed - log this for manual intervention
      await supabase.from('auth_otp.audit_log').insert({
        email,
        action: 'mailgun_error',
        success: false,
        metadata: { error: errorText, otp_id: data.otp_id }
      })

      return new Response(
        JSON.stringify({
          success: false,
          error: 'email_send_failed',
          message: 'Failed to send verification email. Please try again.'
        } as OTPResponse),
        {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    console.log(`OTP sent to ${email}, expires at ${data.expires_at}`)

    // Return success (don't expose OTP code in response for security)
    return new Response(
      JSON.stringify({
        success: true,
        message: `Verification code sent to ${email}`,
        expires_in_seconds: 600, // 10 minutes
        requests_remaining: data.requests_remaining
      } as OTPResponse),
      {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (err) {
    console.error('Unexpected error:', err)
    return new Response(
      JSON.stringify({
        success: false,
        error: 'internal_error',
        message: 'An unexpected error occurred. Please try again.'
      } as OTPResponse),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
