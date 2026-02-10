#!/usr/bin/env node
// Test Magic Link Flow

import { createClient } from '@supabase/supabase-js'

const url = process.env.SUPABASE_URL
const anonKey = process.env.SUPABASE_ANON_KEY
const testEmail = process.env.TEST_EMAIL || 'test@insightpulseai.com'

if (!url || !anonKey) {
  console.error('❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY')
  process.exit(1)
}

const supabase = createClient(url, anonKey)

console.log('🔗 Testing Magic Link Flow...')
console.log(`→ Sending magic link to: ${testEmail}`)

const { data, error } = await supabase.auth.signInWithOtp({
  email: testEmail,
  options: {
    emailRedirectTo: 'https://erp.insightpulseai.com/auth/callback'
  }
})

if (error) {
  console.error('❌ Magic Link failed:', error.message)
  process.exit(1)
}

console.log('✅ Magic Link sent successfully')
console.log('→ Check email inbox for magic link')
console.log('→ Link expires in 24 hours')
