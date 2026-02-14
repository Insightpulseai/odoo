'use client'

import clsx from 'clsx'

interface PricingToggleProps {
  billingPeriod: 'monthly' | 'annual'
  onChange: (period: 'monthly' | 'annual') => void
}

export function PricingToggle({ billingPeriod, onChange }: PricingToggleProps) {
  return (
    <div className="flex items-center justify-center gap-4">
      <span
        className={clsx(
          'text-sm font-medium transition-colors cursor-pointer',
          billingPeriod === 'monthly' ? 'text-gray-900' : 'text-gray-500'
        )}
        onClick={() => onChange('monthly')}
      >
        Monthly
      </span>
      <button
        onClick={() => onChange(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
        className="relative w-14 h-8 bg-gray-200 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        aria-label="Toggle billing period"
      >
        <div
          className={clsx(
            'absolute top-1 w-6 h-6 bg-primary-600 rounded-full transition-transform',
            billingPeriod === 'annual' ? 'translate-x-7' : 'translate-x-1'
          )}
        />
      </button>
      <span
        className={clsx(
          'text-sm font-medium transition-colors cursor-pointer flex items-center gap-2',
          billingPeriod === 'annual' ? 'text-gray-900' : 'text-gray-500'
        )}
        onClick={() => onChange('annual')}
      >
        Annual
        <span className="text-xs text-primary-600 font-semibold bg-primary-50 px-2 py-0.5 rounded-full">
          Save 20%
        </span>
      </span>
    </div>
  )
}
