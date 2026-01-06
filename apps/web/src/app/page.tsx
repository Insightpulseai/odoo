import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="solution-heading mb-4">
          <span className="gradient-text">InsightPulse AI</span>
        </h1>
        <p className="solution-subheading mb-8">
          Secure, compliant collaboration for regulated industries
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/solutions/financial-services"
            className="inline-flex items-center px-6 py-3 rounded-ipai bg-ipai-primary text-ipai-bg font-semibold hover:bg-ipai-primary2 transition-colors"
          >
            Financial Services Solutions
          </Link>
        </div>
      </div>
    </main>
  );
}
