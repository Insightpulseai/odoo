import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Page() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header - Odoo Style */}
      <header className="bg-[#714B67] text-white border-b border-gray-700">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="text-xl font-bold">InsightPulse.ai</div>
            <nav className="hidden md:flex gap-6 text-sm">
              <a href="#" className="hover:text-gray-300 transition-colors">HOME</a>
              <a href="#features" className="hover:text-gray-300 transition-colors">FEATURES</a>
              <a href="#pricing" className="hover:text-gray-300 transition-colors">PRICING</a>
              <a href="#buy" className="hover:text-gray-300 transition-colors">BUY</a>
              <a href="#faq" className="hover:text-gray-300 transition-colors">F.A.Q.</a>
              <a href="#docs" className="hover:text-gray-300 transition-colors">DOCUMENTATION</a>
            </nav>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <a href="#" className="hover:text-gray-300">@insightpulse</a>
          </div>
        </div>
      </header>

      {/* Hero Section - Odoo.sh Style with Dark City Background */}
      <section
        className="relative min-h-[600px] flex items-center justify-center text-white overflow-hidden"
        style={{
          background: 'linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url("data:image/svg+xml,%3Csvg width=\'1920\' height=\'600\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Crect width=\'1920\' height=\'600\' fill=\'%23000\'/%3E%3C/svg%3E")',
          backgroundColor: '#0a0a0a'
        }}
      >
        {/* Simulated city lights effect */}
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255, 200, 100, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(100, 200, 255, 0.3) 0%, transparent 50%), radial-gradient(circle at 50% 80%, rgba(255, 150, 100, 0.3) 0%, transparent 50%)',
          backgroundSize: 'cover'
        }} />

        <div className="relative z-10 container mx-auto px-4 text-center">
          <h1 className="text-6xl md:text-7xl font-light mb-8 tracking-tight">
            The InsightPulse <span className="font-semibold">Cloud Platform</span>
          </h1>

          <div className="flex items-center justify-center gap-4 text-xl mb-12 font-light">
            <span>Development</span>
            <span className="text-[#00A09D]">➜</span>
            <span>Staging</span>
            <span className="text-[#00A09D]">➜</span>
            <span>Deployment</span>
          </div>

          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-[#00A09D] hover:bg-[#008B88] text-white font-semibold text-base px-10 py-6 h-auto"
            >
              DEPLOY YOUR PLATFORM
            </Button>
          </Link>
        </div>
      </section>

      {/* Platform Screenshot Section */}
      <section className="bg-[#F8F9FA] py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <Card className="shadow-2xl overflow-hidden">
              <div className="bg-gray-800 px-4 py-2 flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="ml-4 text-sm text-gray-400">insightpulse.ai/dashboard</span>
              </div>
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 p-8 min-h-[400px]">
                <div className="grid grid-cols-5 gap-6 h-full">
                  {/* Sidebar */}
                  <div className="col-span-1 space-y-4">
                    <div className="text-[#00A09D] text-sm font-semibold">PROJECTS</div>
                    <div className="space-y-2 text-sm text-gray-400">
                      <div className="flex items-center gap-2 text-white">
                        <span className="w-2 h-2 bg-[#00A09D] rounded-full"></span>
                        Production
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                        Staging
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                        Development
                      </div>
                    </div>
                    <div className="text-[#00A09D] text-sm font-semibold mt-8">BUILDS</div>
                    <div className="space-y-2 text-sm text-gray-400">
                      <div>Build #156</div>
                      <div>Build #155</div>
                      <div>Build #154</div>
                    </div>
                  </div>

                  {/* Main Content */}
                  <div className="col-span-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl text-white font-semibold mb-1">master branch</h3>
                        <p className="text-sm text-gray-400">Last deployed 2 hours ago</p>
                      </div>
                      <Button className="bg-[#00A09D] hover:bg-[#008B88] text-sm">
                        Deploy Now
                      </Button>
                    </div>

                    <div className="bg-gray-900/50 rounded-lg p-4 space-y-3">
                      <div className="flex items-start gap-3 text-sm">
                        <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-xs">
                          MC
                        </div>
                        <div className="flex-1">
                          <div className="text-white mb-1">feat: Add BIR compliance module</div>
                          <div className="text-gray-400 text-xs">by Michael Campbell • 3 hours ago</div>
                        </div>
                        <span className="text-xs text-[#00A09D] bg-[#00A09D]/10 px-2 py-1 rounded">
                          Ready
                        </span>
                      </div>

                      <div className="flex items-start gap-3 text-sm">
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-xs">
                          JS
                        </div>
                        <div className="flex-1">
                          <div className="text-white mb-1">fix: Update invoice processing logic</div>
                          <div className="text-gray-400 text-xs">by John Smith • 5 hours ago</div>
                        </div>
                        <span className="text-xs text-green-500 bg-green-500/10 px-2 py-1 rounded">
                          Success
                        </span>
                      </div>

                      <div className="flex items-start gap-3 text-sm">
                        <div className="w-8 h-8 rounded-full bg-orange-600 flex items-center justify-center text-xs">
                          AB
                        </div>
                        <div className="flex-1">
                          <div className="text-white mb-1">chore: Update dependencies</div>
                          <div className="text-gray-400 text-xs">by Alice Brown • 1 day ago</div>
                        </div>
                        <span className="text-xs text-green-500 bg-green-500/10 px-2 py-1 rounded">
                          Success
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-light mb-4">
            Everything You Need for <span className="font-semibold">Business Growth</span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A complete platform to develop, test, and deploy your applications
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="border-t-4 border-t-[#00A09D] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#00A09D]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <CardTitle className="text-xl">Instant Deployment</CardTitle>
              <CardDescription>Deploy your changes in seconds</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 leading-relaxed">
                Push your code and watch it deploy automatically. No complex configurations,
                no waiting times. Just instant deployments.
              </p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#714B67] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#714B67]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔄</span>
              </div>
              <CardTitle className="text-xl">Staging Environments</CardTitle>
              <CardDescription>Test before you deploy</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 leading-relaxed">
                Every branch gets its own staging environment. Test features
                in isolation before merging to production.
              </p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#00A09D] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#00A09D]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <CardTitle className="text-xl">Real-time Monitoring</CardTitle>
              <CardDescription>Track your application health</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 leading-relaxed">
                Monitor performance, errors, and resource usage in real-time.
                Get alerts when something needs attention.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section className="bg-[#F8F9FA] py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-light mb-4">
              Built on <span className="font-semibold">Modern Technology</span>
            </h2>
            <p className="text-lg text-gray-600">
              Enterprise-grade infrastructure and tools
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="text-4xl mb-4">🐍</div>
                <div className="font-semibold">Python</div>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="text-4xl mb-4">🐘</div>
                <div className="font-semibold">PostgreSQL</div>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="text-4xl mb-4">⚛️</div>
                <div className="font-semibold">React</div>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="text-4xl mb-4">🐳</div>
                <div className="font-semibold">Docker</div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-[#714B67] to-[#00A09D] text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-light mb-6">
            Ready to <span className="font-semibold">Deploy Your Platform?</span>
          </h2>
          <p className="text-xl mb-8 text-gray-100 max-w-2xl mx-auto font-light">
            Get started today with InsightPulse Cloud Platform
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/dashboard">
              <Button size="lg" className="bg-white text-[#714B67] hover:bg-gray-100 font-semibold text-lg px-10">
                Start Free Trial
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 font-semibold text-lg px-10">
              View Documentation
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#2B2B2B] text-gray-400 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-white font-bold text-lg mb-4">InsightPulse.ai</div>
              <p className="text-sm">
                Cloud platform for modern business applications
              </p>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-[#00A09D]">Features</a></li>
                <li><a href="#" className="hover:text-[#00A09D]">Pricing</a></li>
                <li><a href="#" className="hover:text-[#00A09D]">Documentation</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-[#00A09D]">About Us</a></li>
                <li><a href="#" className="hover:text-[#00A09D]">Blog</a></li>
                <li><a href="#" className="hover:text-[#00A09D]">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-[#00A09D]">Terms of Service</a></li>
                <li><a href="#" className="hover:text-[#00A09D]">Privacy Policy</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 pt-8 text-center text-sm">
            <p>© 2026 InsightPulse AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
