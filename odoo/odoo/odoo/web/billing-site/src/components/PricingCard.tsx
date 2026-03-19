'use client'

import { Check } from 'lucide-react'
import clsx from 'clsx'

interface PricingCardProps {
  name: string
  description: string
  features: string[]
  price: number | null
  priceId: string | null
  billingPeriod: 'monthly' | 'annual'
  popular?: boolean
  onSelectPlan: (priceId: string) => void
}

export function PricingCard({
  name,
  description,
  features,
  price,
  priceId,
  billingPeriod,
  popular,
  onSelectPlan,
}: PricingCardProps) {
  const isEnterprise = price === null

  return (
    <div
      className={clsx(
        'relative rounded-2xl p-8 flex flex-col',
        popular
          ? 'bg-primary-600 text-white shadow-xl scale-105 z-10'
          : 'bg-white shadow-sm border border-gray-100'
      )}
    >
      {popular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="bg-accent-500 text-white text-sm font-medium px-4 py-1 rounded-full">
            Most Popular
          </span>
        </div>
      )}

      <div className="mb-6">
        <h3 className={clsx('text-xl font-bold', !popular && 'text-gray-900')}>{name}</h3>
        <p className={clsx('text-sm mt-1', popular ? 'text-primary-100' : 'text-gray-500')}>
          {description}
        </p>
      </div>

      <div className="mb-8">
        {isEnterprise ? (
          <div className={clsx('text-3xl font-bold', !popular && 'text-gray-900')}>Custom</div>
        ) : (
          <>
            <span className={clsx('text-4xl font-bold', !popular && 'text-gray-900')}>
              ${price}
            </span>
            <span className={clsx('text-sm', popular ? 'text-primary-100' : 'text-gray-500')}>
              /user/{billingPeriod === 'annual' ? 'month (billed annually)' : 'month'}
            </span>
          </>
        )}
      </div>

      <ul className="space-y-3 mb-8 flex-grow">
        {features.map((feature) => (
          <li key={feature} className="flex items-start gap-3">
            <Check
              className={clsx(
                'w-5 h-5 flex-shrink-0 mt-0.5',
                popular ? 'text-primary-200' : 'text-primary-500'
              )}
            />
            <span className={clsx('text-sm', popular ? 'text-primary-50' : 'text-gray-600')}>
              {feature}
            </span>
          </li>
        ))}
      </ul>

      <button
        onClick={() => priceId && onSelectPlan(priceId)}
        className={clsx(
          'w-full py-3 px-6 rounded-lg font-medium transition-all',
          isEnterprise
            ? 'bg-primary-600 text-white hover:bg-primary-700'
            : popular
            ? 'bg-white text-primary-600 hover:bg-primary-50'
            : 'bg-primary-600 text-white hover:bg-primary-700'
        )}
      >
        {isEnterprise ? 'Contact Sales' : 'Get Started'}
      </button>
    </div>
  )
}
