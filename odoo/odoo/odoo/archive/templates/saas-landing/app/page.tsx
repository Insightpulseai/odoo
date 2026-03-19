"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// UI Variant Selector Component
function VariantSelector({ variant, setVariant }: { variant: string; setVariant: (v: string) => void }) {
  return (
    <div className="fixed top-4 right-4 z-50 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-3">
      <div className="text-xs font-semibold mb-2 text-gray-700">UI Variant</div>
      <Tabs value={variant} onValueChange={setVariant} className="w-[200px]">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="original">Odoo</TabsTrigger>
          <TabsTrigger value="modern">Modern</TabsTrigger>
          <TabsTrigger value="minimal">Minimal</TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  )
}

// Original Odoo-style variant
function OriginalVariant() {
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

      {/* Hero Section */}
      <section
        className="relative min-h-[600px] flex items-center justify-center text-white overflow-hidden"
        style={{
          background: 'linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url("data:image/svg+xml,%3Csvg width=\'1920\' height=\'600\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Crect width=\'1920\' height=\'600\' fill=\'%23000\'/%3E%3C/svg%3E")',
          backgroundColor: '#0a0a0a'
        }}
      >
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255, 200, 100, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(100, 200, 255, 0.3) 0%, transparent 50%), radial-gradient(circle at 50% 80%, rgba(255, 150, 100, 0.3) 0%, transparent 50%)',
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
            <Button size="lg" className="bg-[#00A09D] hover:bg-[#008B88] text-white font-semibold text-base px-10 py-6 h-auto">
              DEPLOY YOUR PLATFORM
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-light mb-4">
            Everything You Need for <span className="font-semibold">Business Growth</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="border-t-4 border-t-[#00A09D] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#00A09D]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <CardTitle className="text-xl">Instant Deployment</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Push your code and watch it deploy automatically. No complex configurations.
              </p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#714B67] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#714B67]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔄</span>
              </div>
              <CardTitle className="text-xl">Staging Environments</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Every branch gets its own staging environment.
              </p>
            </CardContent>
          </Card>

          <Card className="border-t-4 border-t-[#00A09D] hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="w-12 h-12 bg-[#00A09D]/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <CardTitle className="text-xl">Real-time Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Monitor performance, errors, and resource usage in real-time.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}

// Modern SaaS-style variant
function ModernVariant() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      {/* Modern Header */}
      <header className="sticky top-0 z-40 backdrop-blur-lg bg-white/80 border-b border-slate-200">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              InsightPulse
            </div>
            <nav className="hidden md:flex gap-6 text-sm font-medium text-slate-600">
              <a href="#" className="hover:text-blue-600 transition-colors">Product</a>
              <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
              <a href="#pricing" className="hover:text-blue-600 transition-colors">Pricing</a>
              <a href="#docs" className="hover:text-blue-600 transition-colors">Docs</a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="text-sm">Sign In</Button>
            <Button className="bg-blue-600 hover:bg-blue-700 text-sm">Get Started</Button>
          </div>
        </div>
      </header>

      {/* Modern Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <Badge className="mb-6 bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200">
          🚀 Now with AI-powered deployments
        </Badge>

        <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-slate-900 via-blue-800 to-slate-900 bg-clip-text text-transparent leading-tight">
          Ship faster with
          <br />
          <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
            intelligent infrastructure
          </span>
        </h1>

        <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto font-light">
          The all-in-one platform that developers love. Deploy, monitor, and scale your applications with confidence.
        </p>

        <div className="flex gap-4 justify-center mb-8">
          <Link href="/dashboard">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-base px-8">
              Start Building →
            </Button>
          </Link>
          <Button size="lg" variant="outline" className="text-base px-8">
            View Demo
          </Button>
        </div>

        <div className="flex items-center justify-center gap-6 text-sm text-slate-500">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>All systems operational</span>
          </div>
          <span>•</span>
          <span>99.99% uptime SLA</span>
          <span>•</span>
          <span>24/7 support</span>
        </div>
      </section>

      {/* Modern Features Grid */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-slate-100 text-slate-700 hover:bg-slate-200">
            Platform Features
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-slate-900">
            Everything you need to scale
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            From development to production, we've got you covered
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {[
            { icon: "⚡", title: "Lightning Fast", desc: "Deploy in seconds, not hours", color: "blue" },
            { icon: "🔐", title: "Secure by Default", desc: "Enterprise-grade security built-in", color: "green" },
            { icon: "📊", title: "Real-time Analytics", desc: "Monitor every request, every metric", color: "purple" },
            { icon: "🌍", title: "Global CDN", desc: "Deliver content at edge locations", color: "orange" },
            { icon: "🔄", title: "Auto Scaling", desc: "Scale automatically based on demand", color: "cyan" },
            { icon: "💬", title: "Team Collaboration", desc: "Work together seamlessly", color: "pink" },
          ].map((feature, idx) => (
            <Card key={idx} className="border-0 shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 bg-white/50 backdrop-blur">
              <CardHeader>
                <div className={`w-14 h-14 bg-${feature.color}-50 rounded-2xl flex items-center justify-center mb-4 text-3xl`}>
                  {feature.icon}
                </div>
                <CardTitle className="text-xl font-semibold">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600">{feature.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Modern CTA */}
      <section className="container mx-auto px-4 py-20">
        <Card className="border-0 bg-gradient-to-br from-blue-600 via-blue-700 to-cyan-600 text-white shadow-2xl">
          <CardContent className="p-16 text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to build something amazing?
            </h2>
            <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
              Join thousands of developers shipping faster with InsightPulse
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/dashboard">
                <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 font-semibold px-8">
                  Get Started Free
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 px-8">
                Talk to Sales
              </Button>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}

// Minimal/Clean variant
function MinimalVariant() {
  return (
    <div className="min-h-screen bg-white">
      {/* Minimal Header */}
      <header className="border-b border-gray-100">
        <div className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="text-xl font-light tracking-tight">InsightPulse</div>
          <nav className="flex items-center gap-8 text-sm">
            <a href="#features" className="text-gray-600 hover:text-black transition-colors">Features</a>
            <a href="#pricing" className="text-gray-600 hover:text-black transition-colors">Pricing</a>
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="font-normal">
                Sign In →
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Minimal Hero */}
      <section className="container mx-auto px-4 py-32 text-center">
        <h1 className="text-6xl md:text-8xl font-light mb-8 tracking-tight text-black max-w-5xl mx-auto leading-[1.1]">
          Platform for
          <br />
          <span className="italic font-extralight">modern teams</span>
        </h1>

        <p className="text-xl text-gray-500 mb-12 max-w-xl mx-auto font-light">
          Deploy, monitor, scale. Everything you need, nothing you don't.
        </p>

        <Link href="/dashboard">
          <Button className="bg-black hover:bg-gray-800 text-white rounded-full px-8 py-6 text-base font-normal">
            Start Building
          </Button>
        </Link>
      </section>

      {/* Minimal Features */}
      <section id="features" className="container mx-auto px-4 py-20 border-t border-gray-100">
        <div className="grid md:grid-cols-2 gap-16 max-w-4xl mx-auto">
          <div className="space-y-6">
            <div className="text-sm font-medium text-gray-400 uppercase tracking-wider">Deploy</div>
            <h3 className="text-3xl font-light">Ship in seconds</h3>
            <p className="text-gray-600 leading-relaxed">
              Push code and watch it go live instantly. No configuration, no waiting. Just seamless deployments.
            </p>
          </div>

          <div className="space-y-6">
            <div className="text-sm font-medium text-gray-400 uppercase tracking-wider">Monitor</div>
            <h3 className="text-3xl font-light">Know everything</h3>
            <p className="text-gray-600 leading-relaxed">
              Real-time insights into performance, errors, and usage. See what's happening as it happens.
            </p>
          </div>

          <div className="space-y-6">
            <div className="text-sm font-medium text-gray-400 uppercase tracking-wider">Scale</div>
            <h3 className="text-3xl font-light">Grow effortlessly</h3>
            <p className="text-gray-600 leading-relaxed">
              From zero to millions of users. Infrastructure that scales automatically with your success.
            </p>
          </div>

          <div className="space-y-6">
            <div className="text-sm font-medium text-gray-400 uppercase tracking-wider">Collaborate</div>
            <h3 className="text-3xl font-light">Build together</h3>
            <p className="text-gray-600 leading-relaxed">
              Team features designed for modern workflows. Review, approve, and ship as a team.
            </p>
          </div>
        </div>
      </section>

      {/* Minimal CTA */}
      <section className="container mx-auto px-4 py-32 border-t border-gray-100">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-5xl font-light mb-8 text-black">
            Start building today
          </h2>
          <p className="text-xl text-gray-500 mb-12 font-light">
            No credit card required. Deploy your first project in minutes.
          </p>
          <Link href="/dashboard">
            <Button className="bg-black hover:bg-gray-800 text-white rounded-full px-10 py-6 text-lg font-normal">
              Get Started →
            </Button>
          </Link>
        </div>
      </section>

      {/* Minimal Footer */}
      <footer className="border-t border-gray-100 py-12">
        <div className="container mx-auto px-4 text-center text-sm text-gray-400">
          <p>© 2026 InsightPulse AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

// Main Page Component with Variant Switching
export default function Page() {
  const [variant, setVariant] = useState<string>("original")

  return (
    <>
      <VariantSelector variant={variant} setVariant={setVariant} />

      {variant === "original" && <OriginalVariant />}
      {variant === "modern" && <ModernVariant />}
      {variant === "minimal" && <MinimalVariant />}
    </>
  )
}
