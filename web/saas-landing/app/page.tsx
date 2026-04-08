'use client'

const ENTRA_TENANT = process.env.NEXT_PUBLIC_ENTRA_TENANT_ID || 'organizations'
const ENTRA_CLIENT_ID = process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID || ''
const REDIRECT_URI = process.env.NEXT_PUBLIC_REDIRECT_URI || 'https://erp.insightpulseai.com/auth/oidc/callback'

function getEntraLoginUrl() {
  const params = new URLSearchParams({
    client_id: ENTRA_CLIENT_ID,
    response_type: 'code',
    redirect_uri: REDIRECT_URI,
    scope: 'openid profile email User.Read',
    response_mode: 'query',
    prompt: 'select_account',
    domain_hint: 'insightpulseai.com',
  })
  return `https://login.microsoftonline.com/${ENTRA_TENANT}/oauth2/v2.0/authorize?${params.toString()}`
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0F2A44] to-[#1a3d5c] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <img src="/logo.png" alt="InsightPulse AI" className="w-16 h-16 mx-auto mb-4 rounded-xl" />
          <h1 className="text-4xl font-bold text-white mb-2">Odoo Copilot</h1>
          <p className="text-white/70">Sign in to the InsightPulse AI platform</p>
        </div>

        {/* Login Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 shadow-2xl">
          <div className="space-y-6">
            {/* Primary: Microsoft Entra SSO */}
            <a
              href={getEntraLoginUrl()}
              className="flex items-center justify-center gap-3 w-full py-3 px-4 bg-gradient-to-r from-[#7BC043] to-[#64B9CA] text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-[#7BC043]/30 transition-all duration-300 no-underline"
            >
              <svg className="w-5 h-5" viewBox="0 0 23 23" fill="currentColor">
                <path d="M0 0h11v11H0zM12 0h11v11H12zM0 12h11v11H0zM12 12h11v11H12z" />
              </svg>
              Sign in with Microsoft
            </a>

            <p className="text-center text-xs text-white/50">
              Uses your InsightPulse AI organizational account
            </p>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/20"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-transparent text-white/50">Or</span>
              </div>
            </div>

            {/* Fallback: Direct Odoo login (pre-Entra cutover) */}
            <a
              href="https://erp.insightpulseai.com/web/login"
              className="block w-full py-3 px-4 bg-white/10 border border-white/20 text-white font-medium rounded-xl hover:bg-white/20 transition-all duration-300 text-center no-underline"
            >
              Sign in with Odoo account
            </a>

            {/* Platform quick links */}
            <div className="grid grid-cols-3 gap-2 pt-2">
              <a
                href="https://plane.insightpulseai.com"
                className="text-center py-2 px-2 bg-white/5 border border-white/10 rounded-lg text-white/60 text-xs hover:bg-white/10 hover:text-white transition-all no-underline"
              >
                Plane
              </a>
              <a
                href="https://superset.insightpulseai.com"
                className="text-center py-2 px-2 bg-white/5 border border-white/10 rounded-lg text-white/60 text-xs hover:bg-white/10 hover:text-white transition-all no-underline"
              >
                Superset
              </a>
              <a
                href="https://n8n.insightpulseai.com"
                className="text-center py-2 px-2 bg-white/5 border border-white/10 rounded-lg text-white/60 text-xs hover:bg-white/10 hover:text-white transition-all no-underline"
              >
                n8n
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-white/50">
          &copy; 2026 InsightPulse AI. All rights reserved.
        </p>
      </div>
    </div>
  )
}
