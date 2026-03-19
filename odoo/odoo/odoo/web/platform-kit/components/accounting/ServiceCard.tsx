'use client'

import Link from 'next/link'
import { ReactNode } from 'react'

interface ServiceCardProps {
  title: string
  description: string
  icon: ReactNode
  links: Array<{
    label: string
    href: string
  }>
  variant?: 'mint' | 'white'
}

export function ServiceCard({
  title,
  description,
  icon,
  links,
  variant = 'mint'
}: ServiceCardProps) {
  const bgClass = variant === 'mint'
    ? 'bg-gradient-to-br from-mint-100 to-mint-50'
    : 'bg-white'

  return (
    <div className={`${bgClass} rounded-2xl p-8 md:p-10 lg:p-12 shadow-sm hover:shadow-md transition-shadow`}>
      <div className="grid md:grid-cols-2 gap-8 items-center">
        {/* Content */}
        <div className="space-y-6 order-2 md:order-1">
          <h3 className="text-2xl md:text-3xl font-bold text-forest-900">
            {title}
          </h3>
          <p className="text-base md:text-lg text-forest-700 leading-relaxed">
            {description}
          </p>
          <div className="flex flex-wrap gap-3">
            {links.map((link, index) => (
              <Link
                key={index}
                href={link.href}
                className="inline-flex items-center justify-center px-5 py-2.5 bg-white text-forest-700 font-medium rounded-full hover:bg-forest-50 transition-colors border border-forest-200 text-sm"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Icon/Illustration */}
        <div className="flex justify-center md:justify-end order-1 md:order-2">
          <div className="w-48 h-48 md:w-56 md:h-56 lg:w-64 lg:h-64 flex items-center justify-center">
            {icon}
          </div>
        </div>
      </div>
    </div>
  )
}
