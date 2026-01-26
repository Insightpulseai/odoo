'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { PricingCard } from '@/components/PricingCard'
import { PricingToggle } from '@/components/PricingToggle'
import { usePaddleCheckout } from '@/components/PaddleCheckout'
import { PRICING_PLANS } from '@/lib/paddle'

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('annual')
  const { openCheckout } = usePaddleCheckout()
  const router = useRouter()

  const handleSelectPlan = (priceId: string) => {
    if (priceId) {
      openCheckout({
        priceId,
        onSuccess: () => {
          router.push('/billing/success')
        },
      })
    } else {
      // Enterprise - redirect to contact
      router.push('/contact?plan=enterprise')
    }
  }

  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Simple, transparent pricing
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Choose the plan that fits your needs. All plans include a 14-day free trial.
          </p>
          <PricingToggle billingPeriod={billingPeriod} onChange={setBillingPeriod} />
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 items-start max-w-5xl mx-auto">
          <PricingCard
            name={PRICING_PLANS.starter.name}
            description={PRICING_PLANS.starter.description}
            features={PRICING_PLANS.starter.features}
            price={PRICING_PLANS.starter[billingPeriod].price}
            priceId={PRICING_PLANS.starter[billingPeriod].priceId || null}
            billingPeriod={billingPeriod}
            onSelectPlan={handleSelectPlan}
          />
          <PricingCard
            name={PRICING_PLANS.pro.name}
            description={PRICING_PLANS.pro.description}
            features={PRICING_PLANS.pro.features}
            price={PRICING_PLANS.pro[billingPeriod].price}
            priceId={PRICING_PLANS.pro[billingPeriod].priceId || null}
            billingPeriod={billingPeriod}
            popular
            onSelectPlan={handleSelectPlan}
          />
          <PricingCard
            name={PRICING_PLANS.enterprise.name}
            description={PRICING_PLANS.enterprise.description}
            features={PRICING_PLANS.enterprise.features}
            price={PRICING_PLANS.enterprise[billingPeriod].price}
            priceId={PRICING_PLANS.enterprise[billingPeriod].priceId}
            billingPeriod={billingPeriod}
            onSelectPlan={() => router.push('/contact?plan=enterprise')}
          />
        </div>

        {/* FAQ Section */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Frequently asked questions
          </h2>
          <div className="space-y-6">
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Can I change plans later?</h3>
              <p className="text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately,
                and we'll prorate the difference.
              </p>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, American Express), PayPal, and bank transfers
                for annual enterprise plans.
              </p>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Is there a free trial?</h3>
              <p className="text-gray-600">
                Yes, all plans include a 14-day free trial with full access to all features.
                No credit card required to start.
              </p>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Do you offer refunds?</h3>
              <p className="text-gray-600">
                Yes, we offer a 30-day money-back guarantee. If you're not satisfied, contact us for a full refund.
              </p>
            </div>
          </div>
        </div>

        {/* Enterprise CTA */}
        <div className="mt-20 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Need a custom solution?
          </h2>
          <p className="text-gray-600 mb-6">
            Our enterprise team can help you build a solution tailored to your organization's needs.
          </p>
          <a
            href="mailto:business@insightpulseai.com?subject=Enterprise%20Inquiry"
            className="btn btn-primary"
          >
            Contact Sales
          </a>
        </div>
      </div>
    </div>
  )
}
