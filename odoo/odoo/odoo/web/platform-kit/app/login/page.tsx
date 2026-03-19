'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createBrowserClient } from '@/lib/supabase/browser'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle, Mail, Lock, Zap, Shield, BarChart3, FileCheck } from 'lucide-react'

// IPAI Design Tokens
const T = {
  brand: { navy: '#0F2A44', navyDeep: '#0A1E33', ink: '#0A1E33' },
  accent: { green: '#7BC043', teal: '#64B9CA', amber: '#F6C445' },
  surface: { bg: '#E7EDF5', bg2: '#E1E8F2', card: '#FFFFFF' },
  text: { primary: '#0B1F33', secondary: '#5E6B7C', onDark: '#FFFFFF' },
  border: { subtle: '#D7DDE6', hairline: 'rgba(0,0,0,0.08)' },
  radius: { card: 20, panel: 28, pill: 999 },
}

const LogoMark = ({ size = 40 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
    <defs>
      <linearGradient id="lg1" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor={T.brand.navy} />
        <stop offset="100%" stopColor={T.brand.navyDeep} />
      </linearGradient>
      <linearGradient id="lg2" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor={T.accent.green} />
        <stop offset="100%" stopColor={T.accent.teal} />
      </linearGradient>
    </defs>
    <rect width="40" height="40" rx="12" fill="url(#lg1)" />
    <polyline points="8,20 13,20 17,12 21,28 25,17 29,20 34,20" stroke="url(#lg2)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    <circle cx="34" cy="10" r="2.5" fill={T.accent.green} opacity="0.9" />
  </svg>
)

const features = [
  { icon: Shield, label: 'Bank-grade Security', desc: 'SOC 2 Type 2 certified' },
  { icon: Zap, label: 'Lightning Fast', desc: '99.9% uptime SLA' },
  { icon: BarChart3, label: 'Real-time Analytics', desc: 'Live dashboards & insights' },
  { icon: FileCheck, label: 'Full Compliance', desc: 'BIR & GDPR ready' },
]

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const supabase = createBrowserClient()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  const handleMagicLink = async () => {
    if (!email) {
      setError('Please enter your email address')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/dashboard`,
        },
      })

      if (error) throw error
      setError('Check your email for the magic link!')
    } catch (err: any) {
      setError(err.message || 'Failed to send magic link')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <div
        className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 relative overflow-hidden"
        style={{ background: `linear-gradient(165deg, ${T.brand.navy} 0%, ${T.brand.navyDeep} 100%)` }}
      >
        {/* Subtle noise texture */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          }}
        />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <LogoMark size={48} />
            <span className="text-2xl font-bold" style={{ color: T.text.onDark }}>
              InsightPulse AI
            </span>
          </div>

          <h1 className="text-4xl font-medium mb-4" style={{ color: T.text.onDark, letterSpacing: '-0.5px' }}>
            Welcome to the
            <br />
            <span style={{ color: T.accent.green }}>Control Plane</span>
          </h1>

          <p className="text-lg mb-12" style={{ color: 'rgba(255,255,255,0.6)' }}>
            Self-hosted enterprise ERP, BI & AI platform. Bank-grade security. Zero license fees.
          </p>

          <div className="space-y-6">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div key={feature.label} className="flex items-start gap-4">
                  <div
                    className="flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ background: 'rgba(123,192,67,0.1)', border: `1px solid rgba(123,192,67,0.2)` }}
                  >
                    <Icon className="w-6 h-6" style={{ color: T.accent.green }} />
                  </div>
                  <div>
                    <div className="font-medium mb-1" style={{ color: T.text.onDark }}>
                      {feature.label}
                    </div>
                    <div className="text-sm" style={{ color: 'rgba(255,255,255,0.5)' }}>
                      {feature.desc}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 text-sm" style={{ color: 'rgba(255,255,255,0.4)' }}>
            <span className="w-2 h-2 rounded-full" style={{ background: T.accent.green, boxShadow: `0 0 8px ${T.accent.green}` }} />
            <span>All systems operational</span>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8" style={{ background: T.surface.bg }}>
        <div className="w-full max-w-md">
          <div
            className="rounded-3xl p-8 shadow-xl"
            style={{
              background: T.surface.card,
              border: `1px solid ${T.border.subtle}`,
            }}
          >
            <div className="mb-8">
              <h2 className="text-2xl font-medium mb-2" style={{ color: T.brand.ink }}>
                Sign in to your account
              </h2>
              <p className="text-sm" style={{ color: T.text.secondary }}>
                Enter your credentials to access the platform
              </p>
            </div>

            {error && (
              <Alert variant={error.includes('Check your email') ? 'default' : 'destructive'} className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Label htmlFor="email" className="text-sm font-medium" style={{ color: T.brand.ink }}>
                  Email address
                </Label>
                <div className="relative mt-1.5">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" style={{ color: T.text.secondary }} />
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@company.com"
                    className="pl-10 h-12"
                    style={{
                      borderRadius: `${T.radius.card / 2}px`,
                      borderColor: T.border.subtle,
                    }}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password" className="text-sm font-medium" style={{ color: T.brand.ink }}>
                  Password
                </Label>
                <div className="relative mt-1.5">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" style={{ color: T.text.secondary }} />
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="pl-10 h-12"
                    style={{
                      borderRadius: `${T.radius.card / 2}px`,
                      borderColor: T.border.subtle,
                    }}
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="rounded" style={{ accentColor: T.accent.green }} />
                  <span style={{ color: T.text.secondary }}>Remember me</span>
                </label>
                <a href="#" className="font-medium hover:underline" style={{ color: T.accent.green }}>
                  Forgot password?
                </a>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 text-base font-semibold"
                style={{
                  background: T.accent.green,
                  color: T.brand.ink,
                  borderRadius: `${T.radius.pill}px`,
                  boxShadow: `0 4px 12px rgba(123,192,67,0.25)`,
                }}
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t" style={{ borderColor: T.border.subtle }} />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4" style={{ background: T.surface.card, color: T.text.secondary }}>
                  or continue with
                </span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={handleMagicLink}
              disabled={loading}
              className="w-full h-12 text-base font-medium"
              style={{
                borderRadius: `${T.radius.pill}px`,
                borderColor: T.accent.green,
                borderWidth: '2px',
                color: T.accent.green,
              }}
            >
              <Mail className="w-5 h-5 mr-2" />
              Email me a magic link
            </Button>

            <p className="mt-6 text-center text-sm" style={{ color: T.text.secondary }}>
              Need help?{' '}
              <a href="mailto:support@insightpulseai.com" className="font-medium hover:underline" style={{ color: T.accent.green }}>
                Contact support
              </a>
            </p>
          </div>

          <p className="mt-6 text-center text-xs" style={{ color: T.text.secondary }}>
            © 2026 InsightPulse AI. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  )
}
