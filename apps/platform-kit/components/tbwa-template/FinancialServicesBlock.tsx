'use client'

import Image from 'next/image'

export function FinancialServicesBlock() {
  return (
    <section className="block-content block-r24-large-app-screen-preview view-two-column block-padding-below-none camo-section relative py-20 lg:py-32">
      <div className="app-screen-contents">
        {/* Background Pattern */}
        <div className="bg-pattern absolute inset-0 opacity-10">
          <Image
            src="https://mattermost.com/wp-content/uploads/2025/01/r2024-camo-pattern-bg-4x.webp"
            alt=""
            fill
            className="object-cover"
          />
        </div>

        <div className="container relative z-10 px-6 lg:px-16">
          <div className="intro-contents row mb-12">
            <div className="col col-12 mb-4">
              <span className="subtitle-intro-above-main-title text-sm uppercase tracking-wider text-gray-600">
                Financial Services
              </span>
            </div>

            <div className="col col-12 lg:col-6 left-column mb-6 lg:mb-0">
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900">
                Modernize Your Financial Workflow Without Losing Oversight
              </h2>
            </div>

            <div className="col col-12 lg:col-6 right-column">
              <p className="text-lg text-gray-700 leading-relaxed">
                From global banks to fintech startups, Mattermost unifies secure collaboration across teams, tools, and time zones – helping you meet audit requirements, enforce governance policies, and accelerate response in high-pressure environments.
              </p>
            </div>
          </div>
        </div>

        {/* Phone-Desktop App Images */}
        <div className="phone-desktop-pairs relative mt-16">
          <div className="image-contents relative max-w-7xl mx-auto px-6 lg:px-16">
            {/* Desktop Image */}
            <div className="desktop-image relative z-10">
              <Image
                src="https://mattermost.com/wp-content/uploads/2025/02/r2024-financial-services-app-desktop.webp"
                alt="financial services chat app for communication and collaboration"
                width={1822}
                height={926}
                className="w-full h-auto"
              />
            </div>

            {/* Phone Image - Overlapping */}
            <div className="phone-image absolute bottom-0 right-8 lg:right-24 z-20 w-1/4 max-w-[300px]">
              <Image
                src="https://mattermost.com/wp-content/uploads/2025/02/r2024-financial-services-app-phone.webp"
                alt="financial services chat app for communication and collaboration"
                width={516}
                height={774}
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>

        {/* Gradient Overlay at Bottom */}
        <div className="app-screen-gradient absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent"></div>
      </div>
    </section>
  )
}
