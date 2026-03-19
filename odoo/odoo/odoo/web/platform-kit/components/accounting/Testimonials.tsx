'use client'

import Image from 'next/image'

interface Testimonial {
  quote: string
  author: string
  role: string
  company: string
  rating: number
}

const testimonials: Testimonial[] = [
  {
    quote: "Managing my taxes as a freelancer used to be overwhelming, but Noble Finance made it effortless.",
    author: "Sarah J.",
    role: "Freelance Photographer",
    company: "27 years old",
    rating: 5,
  },
]

export function Testimonials() {
  return (
    <section className="py-16 md:py-20 lg:py-24 bg-white">
      <div className="container mx-auto px-6 md:px-8 lg:px-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-forest-900 mb-4">
            Hear From Our Happy Clients
          </h2>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Testimonial Card */}
            <div className="bg-forest-700 text-white rounded-2xl p-8 md:p-10 shadow-xl">
              <div className="space-y-6">
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className="w-5 h-5 text-yellow-400 fill-current"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                    </svg>
                  ))}
                </div>

                <p className="text-lg md:text-xl leading-relaxed">
                  "{testimonials[0].quote}"
                </p>

                <div className="pt-4 border-t border-forest-600">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-forest-600 rounded-full flex items-center justify-center text-lg font-bold">
                      {testimonials[0].author[0]}
                    </div>
                    <div>
                      <p className="font-semibold">{testimonials[0].author}</p>
                      <p className="text-sm text-forest-300">{testimonials[0].role}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Image */}
            <div className="relative h-64 md:h-96 rounded-2xl overflow-hidden shadow-xl">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-100 to-amber-200" />
              {/* Placeholder for professional image */}
              <div className="absolute inset-0 flex items-center justify-center text-forest-700 font-medium">
                Professional workspace
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
