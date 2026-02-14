'use client'

import Image from 'next/image'

export function ClientLogos() {
  return (
    <div className="block-content block-r21-client-logos view-white block-r21-client-logos--slim with-copy copy-left py-12 lg:py-16">
      <div className="container px-6 lg:px-16">
        <div className="row">
          <div className="col-12">
            <div className="logo-row flex flex-col lg:flex-row items-center gap-8">
              <div className="copy lg:flex-shrink-0">
                <p className="text-gray-600 text-sm lg:text-base">
                  Deployed by the world's leading organizations
                </p>
              </div>

              <div className="logo-block flex flex-wrap items-center justify-center lg:justify-start gap-8 lg:gap-12">
                <div className="single-logo" style={{ width: '65px' }}>
                  <Image
                    src="https://mattermost.com/wp-content/uploads/2021/10/AIG_color.svg"
                    alt="AIG"
                    width={65}
                    height={40}
                    className="w-full h-auto"
                  />
                </div>

                <div className="single-logo" style={{ width: '140px' }}>
                  <Image
                    src="https://mattermost.com/wp-content/uploads/2021/08/bnp-paribas-logo-1.webp"
                    alt="BNP Paribas"
                    width={345}
                    height={74}
                    className="w-full h-auto"
                  />
                </div>

                <div className="single-logo" style={{ width: '110px' }}>
                  <Image
                    src="https://mattermost.com/wp-content/uploads/2024/05/Worldline-Logo-Cropped.webp"
                    alt="Worldline"
                    width={244}
                    height={47}
                    className="w-full h-auto"
                  />
                </div>

                <div className="single-logo" style={{ width: '130px' }}>
                  <Image
                    src="https://mattermost.com/wp-content/uploads/2021/08/PNC_Bank-1.webp"
                    alt="PNC Bank"
                    width={301}
                    height={64}
                    className="w-full h-auto"
                  />
                </div>

                <div className="single-logo" style={{ width: '110px' }}>
                  <Image
                    src="https://mattermost.com/wp-content/uploads/2021/08/deloitte-logo-1.webp"
                    alt="Deloitte"
                    width={244}
                    height={50}
                    className="w-full h-auto"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
