#!/usr/bin/env node
// Test Email OTP Flow

import { createClient } from '@supabase/supabase-js'

const url = process.env.SUPABASE_URL
const anonKey = process.env.SUPABASE_ANON_KEY
const testEmail = process.env.TEST_EMAIL || 'test@insightpulseai.com'

if (!url || !anonKey) {
  console.error('❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY')
  process.exit(1)
}

const supabase = createClient(url, anonKey)

console.log('🔢 Testing Email OTP Flow...')
console.log(`→ Sending OTP to: ${testEmail}`)

// Send OTP
const { data, error } = await supabase.auth.signInWithOtp({
  email: testEmail,
  options: {
    shouldCreateUser: false
  }
})

if (error) {
  console.error('❌ OTP send failed:', error.message)
  process.exit(1)
}

console.log('✅ OTP sent successfully')
console.log('→ Check email inbox for 6-digit code')
console.log('→ Code expires in 5 minutes')
console.log('')
console.log('To verify OTP, run:')
console.log(`  node -e "import('@supabase/supabase-js').then(({createClient})=>{const s=createClient('${url}','${anonKey}');s.auth.verifyOtp({email:'${testEmail}',token:'123456',type:'email'}).then(console.log)})"`)
