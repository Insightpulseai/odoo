import { redirect } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/server'
import { CreditCard, User, Building2, Settings, LogOut } from 'lucide-react'

export default async function AccountPage() {
  const supabase = createClient()

  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/auth/signin')
  }

  // Get subscription info
  const { data: subscription } = await supabase
    .rpc('billing.get_current_subscription')
    .single()

  // Get customer info
  const { data: customer } = await supabase
    .from('billing.customers')
    .select('*')
    .eq('supabase_user_id', user.id)
    .single()

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Account</h1>
          <p className="text-gray-600 mt-1">Manage your account settings and subscription</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Sidebar */}
          <div className="md:col-span-1">
            <nav className="space-y-1">
              <Link
                href="/account"
                className="flex items-center gap-3 px-4 py-3 bg-primary-50 text-primary-700 rounded-lg font-medium"
              >
                <User className="w-5 h-5" />
                Overview
              </Link>
              <Link
                href="/account/billing"
                className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
              >
                <CreditCard className="w-5 h-5" />
                Billing
              </Link>
              <Link
                href="/account/organization"
                className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
              >
                <Building2 className="w-5 h-5" />
                Organization
              </Link>
              <Link
                href="/account/settings"
                className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg"
              >
                <Settings className="w-5 h-5" />
                Settings
              </Link>
              <form action="/auth/signout" method="post">
                <button
                  type="submit"
                  className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-50 rounded-lg w-full text-left"
                >
                  <LogOut className="w-5 h-5" />
                  Sign out
                </button>
              </form>
            </nav>
          </div>

          {/* Main Content */}
          <div className="md:col-span-2 space-y-6">
            {/* Profile Card */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500">Email</label>
                  <p className="text-gray-900">{user.email}</p>
                </div>
                {customer?.company_name && (
                  <div>
                    <label className="text-sm text-gray-500">Company</label>
                    <p className="text-gray-900">{customer.company_name}</p>
                  </div>
                )}
                <div>
                  <label className="text-sm text-gray-500">Account created</label>
                  <p className="text-gray-900">{formatDate(user.created_at)}</p>
                </div>
              </div>
            </div>

            {/* Subscription Card */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Subscription</h2>
                <Link href="/account/billing" className="text-sm text-primary-600 hover:text-primary-700">
                  Manage billing
                </Link>
              </div>

              {subscription ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xl font-bold text-gray-900">{subscription.plan_name}</span>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        subscription.status === 'active'
                          ? 'bg-green-100 text-green-700'
                          : subscription.status === 'trialing'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {subscription.status}
                    </span>
                  </div>
                  {subscription.current_period_end && (
                    <p className="text-sm text-gray-600">
                      {subscription.status === 'trialing' ? 'Trial ends' : 'Renews'} on{' '}
                      {formatDate(subscription.current_period_end)}
                    </p>
                  )}
                </div>
              ) : (
                <div>
                  <p className="text-gray-600 mb-4">You don't have an active subscription.</p>
                  <Link href="/pricing" className="btn btn-primary">
                    View pricing plans
                  </Link>
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <Link
                  href="/docs/getting-started"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Getting Started</p>
                    <p className="text-sm text-gray-500">Read the documentation</p>
                  </div>
                </Link>
                <a
                  href="mailto:business@insightpulseai.com"
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Contact Support</p>
                    <p className="text-sm text-gray-500">Get help from our team</p>
                  </div>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
