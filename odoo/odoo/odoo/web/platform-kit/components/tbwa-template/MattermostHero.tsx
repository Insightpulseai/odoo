'use client'

export function MattermostHero() {
  return (
    <section className="block-content block-r24-marquee-masthead view-left-short block-padding-below-none">
      <div className="masthead-wrapper relative">
        {/* Video Background */}
        <div className="video-bg absolute inset-0 w-full h-full overflow-hidden">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover"
          >
            <source src="https://mattermost.com/wp-content/uploads/2025/01/Industry_Finance.webm" type="video/webm" />
            <source src="https://mattermost.com/wp-content/uploads/2025/01/Industry_Finance.mp4" type="video/mp4" />
          </video>
        </div>

        {/* Dual Overlay Filters */}
        <div className="video-overlay-filter absolute inset-0 bg-black/40"></div>
        <div className="video-overlay-filter-2 absolute inset-0 bg-gradient-to-b from-black/20 to-black/60"></div>

        {/* Content Overlay */}
        <div className="container relative z-10 px-6 lg:px-16">
          <div className="row">
            <div className="col col-12 masthead-content py-32 lg:py-48">
              <div className="copy-content max-w-3xl">
                <h1 className="h1 text-5xl lg:text-7xl font-bold text-white mb-6">
                  Move Fast, Stay Compliant, Reduce Risk
                </h1>

                <p className="text-xl lg:text-2xl text-white/90 mb-8">
                  Compliant communication that moves fast, integrates seamlessly, and keeps every message traceable, secure, and audit-ready.
                </p>
              </div>

              <div className="masthead-button">
                <a
                  className="inline-block px-8 py-4 bg-transparent border-2 border-white text-white font-semibold hover:bg-white hover:text-gray-900 transition-all duration-300"
                  href="https://mattermost.com/contact-sales/"
                >
                  Contact Sales
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
