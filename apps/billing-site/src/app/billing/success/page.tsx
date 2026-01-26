import Link from 'next/link'
import { CheckCircle } from 'lucide-react'

export default function BillingSuccessPage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center py-20">
      <div className="max-w-md mx-auto px-4 text-center">
        <div className="mb-6">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to InsightPulse AI!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Your subscription has been activated. You're all set to start transforming your business.
        </p>
        <div className="space-y-4">
          <Link href="/account" className="btn btn-primary w-full">
            Go to Your Account
          </Link>
          <Link href="/docs/getting-started" className="btn btn-secondary w-full">
            Read Getting Started Guide
          </Link>
        </div>
        <p className="mt-8 text-sm text-gray-500">
          Need help? Contact us at{' '}
          <a href="mailto:business@insightpulseai.com" className="text-primary-600 hover:underline">
            business@insightpulseai.com
          </a>
        </p>
      </div>
    </div>
  )
}
