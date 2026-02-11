'use client'

import Link from "next/link";

function TerminalBlock() {
  return (
    <div className="rounded-2xl border bg-neutral-950 text-neutral-100 overflow-hidden shadow-2xl">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-neutral-800">
        <div className="flex gap-2">
          <span className="h-3 w-3 rounded-full bg-red-500/80" />
          <span className="h-3 w-3 rounded-full bg-yellow-500/80" />
          <span className="h-3 w-3 rounded-full bg-green-500/80" />
        </div>
        <div className="text-xs text-neutral-400 font-mono">platform-manager • workflow</div>
      </div>

      <div className="grid grid-cols-12 min-h-[220px]">
        <div className="col-span-4 border-r border-neutral-800 bg-neutral-950/60 p-2">
          <div className="px-3 py-2 text-[10px] uppercase tracking-wider font-bold text-neutral-500">Deploy environments</div>
          <div className="space-y-1">
            {[
              "Production",
              "Launch a Staging Server",
              "Test Your Developments",
              "Install Community Modules",
            ].map((t, i) => (
              <div
                key={t}
                className={[
                  "px-3 py-2 rounded-lg text-xs transition-colors cursor-default",
                  i === 0 ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "text-neutral-500 hover:text-neutral-300",
                ].join(" ")}
              >
                {t}
              </div>
            ))}
          </div>
        </div>

        <div className="col-span-8 p-6 font-mono text-xs leading-relaxed">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-neutral-500">$</span>
            <span className="text-neutral-300">git branch</span>
          </div>
          <div className="pl-4 text-neutral-400">feature-X</div>
          <div className="pl-4 text-emerald-400 flex items-center gap-2">
            <span>*</span>
            <span>production</span>
          </div>
          <div className="pl-4 text-neutral-400">staging-1</div>

          <div className="mt-4 flex items-center gap-2 mb-1">
            <span className="text-neutral-500">$</span>
            <span className="text-neutral-300">git merge staging-1</span>
          </div>
          <div className="pl-4 text-neutral-500 italic">Merge made by the 'ort' strategy.</div>

          <div className="mt-4 flex items-center gap-2 mb-1">
            <span className="text-neutral-500">$</span>
            <span className="text-neutral-300">git push</span>
          </div>
          <div className="pl-4 text-neutral-300">
            To git@github.com:insightpulseai/platform.git
          </div>
          <div className="pl-4 text-neutral-400">
            * b70ca1f..7a0aa41 production -{">"} production
          </div>
          <div className="mt-2 text-emerald-500/80 animate-pulse font-bold"># Production server being updated...</div>
        </div>
      </div>
    </div>
  );
}

function FeatureGrid() {
  const features = [
    { title: "Database", desc: "Tables, columns, indexes, RLS, and safe browsing via admin RPCs." },
    { title: "Staging / Preview", desc: "Preview schema + policies before promoting to production." },
    { title: "Backups", desc: "Automate snapshots and retention policies (SQL + scheduled jobs)." },
    { title: "Automated checks", desc: "Run policy lint + migration verification in CI." },
    { title: "SSH-free ops", desc: "Everything via Supabase + Edge Functions + GitHub Actions." },
    { title: "DNS & routes", desc: "Route manager UI behind your existing app domain." },
    { title: "Email gateways", desc: "Outbox table + provider adapters (Zoho/SMTP) via Edge." },
    { title: "Logs & audit", desc: "Admin-only logs with retention and queryable metadata." },
    { title: "AI Suggestions", desc: "Metadata-driven checks + optional LLM layer (toggleable)." },
    { title: "Runbook workflow", desc: "Promote staging → production using Git commits/migrations." },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {features.map((f) => (
        <div key={f.title} className="rounded-2xl border p-5 bg-white/50 backdrop-blur-sm group hover:border-emerald-500/30 transition-all hover:shadow-md">
          <div className="font-bold text-neutral-900 group-hover:text-emerald-600 transition-colors">{f.title}</div>
          <div className="text-sm text-neutral-500 mt-1 leading-snug">{f.desc}</div>
        </div>
      ))}
    </div>
  );
}

export function OdooStyleLanding({ onOpenManager }: { onOpenManager: () => void }) {
  return (
    <main className="min-h-screen bg-neutral-50 selection:bg-emerald-200">
      {/* Hero */}
      <section className="relative overflow-hidden bg-neutral-950 px-6 py-20 lg:py-32">
        <div
          className="absolute inset-0 opacity-40"
          style={{
            background:
              "radial-gradient(1200px 500px at 50% 10%, rgba(16, 185, 129, 0.15), transparent 80%)," +
              "radial-gradient(800px 400px at 10% 80%, rgba(59, 130, 246, 0.1), transparent 80%)," +
              "radial-gradient(800px 400px at 90% 80%, rgba(245, 158, 11, 0.1), transparent 80%)",
          }}
        />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>

        <div className="relative mx-auto max-w-6xl">
          <div className="flex items-center justify-between mb-16">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 bg-emerald-500 rounded-md flex items-center justify-center font-black text-neutral-900 italic text-xs">IP</div>
              <div className="text-sm font-bold tracking-tight text-neutral-100 lowercase">
                insightpulseai<span className="text-emerald-500">.platform</span>
              </div>
            </div>
            <div className="flex gap-6">
              <button
                className="text-sm font-medium text-neutral-400 hover:text-neutral-100 transition-colors"
                onClick={onOpenManager}
              >
                Open Manager
              </button>
              <a
                className="text-sm font-medium text-neutral-400 hover:text-neutral-100 transition-colors"
                href="https://supabase.com"
                target="_blank"
                rel="noreferrer"
              >
                Supabase Dashboard
              </a>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <div className="text-left">
              <h1 className="text-5xl lg:text-7xl font-black tracking-tighter text-white leading-[0.9]">
                The Backend <br />
                <span className="text-emerald-500 italic">Control Plane.</span>
              </h1>
              <p className="mt-8 text-lg text-neutral-400 max-w-lg font-medium leading-relaxed">
                Deploy, monitor, and scale your Supabase infra with a Git-driven workflow.
                Built for mission-critical Odoo 19 SaaS delivery.
              </p>

              <div className="mt-10 flex flex-wrap items-center gap-4">
                <button
                  onClick={onOpenManager}
                  className="rounded-full px-8 py-4 text-sm font-bold bg-emerald-500 text-neutral-950 hover:bg-emerald-400 transition-all hover:scale-105 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                >
                  Launch Manager
                </button>
                <Link
                  href="/docs"
                  className="rounded-full px-8 py-4 text-sm font-bold border border-neutral-700 text-neutral-100 hover:bg-white/5 transition-colors"
                >
                  View Blueprint
                </Link>
              </div>

              <div className="mt-12 flex items-center gap-8 border-t border-neutral-800 pt-8">
                <div>
                  <div className="text-2xl font-black text-white leading-none">100%</div>
                  <div className="text-[10px] uppercase tracking-widest font-bold text-neutral-500 mt-1">GitOps Managed</div>
                </div>
                <div>
                  <div className="text-2xl font-black text-white leading-none">Zero</div>
                  <div className="text-[10px] uppercase tracking-widest font-bold text-neutral-500 mt-1">Manual Config</div>
                </div>
              </div>
            </div>

            <div className="relative">
               <div className="absolute -inset-4 bg-emerald-500/20 blur-3xl opacity-20"></div>
               <TerminalBlock />
            </div>
          </div>
        </div>
      </section>

      {/* Value Prop */}
      <section className="mx-auto max-w-6xl px-6 py-24 lg:py-32">
        <div className="grid lg:grid-cols-12 gap-16 lg:gap-24 items-start">
          <div className="lg:col-span-5">
            <h2 className="text-4xl font-black tracking-tight text-neutral-900 leading-tight">
              A Platform Built <br />
              <span className="text-emerald-600 italic">for Engineers.</span>
            </h2>
            <p className="mt-6 text-lg text-neutral-500 font-medium leading-relaxed">
              Ditch the manual dashboard clicks. Our platform kit brings everything into your version-controlled repo.
              Promote changes with PRs, not button pushes.
            </p>
            <div className="mt-10 space-y-4">
              {[
                { label: "Branch Parity", desc: "Unlimited ephemeral staging envs for every PR." },
                { label: "Atomic Migrations", desc: "Schema changes validated in CI before merge." },
                { label: "Signed Evidence", desc: "Every deploy produces a verfied audit bundle." },
                { label: "AI Assisted Ops", desc: "Non-authoritative SQL and policy suggestions." },
              ].map((t) => (
                <div key={t.label} className="flex gap-4 group">
                  <div className="mt-1 h-5 w-5 rounded-full bg-emerald-100 border border-emerald-200 flex items-center justify-center shrink-0 group-hover:bg-emerald-500 transition-colors">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-600 group-hover:bg-white" />
                  </div>
                  <div>
                    <div className="font-bold text-neutral-900 text-sm">{t.label}</div>
                    <div className="text-xs text-neutral-400 mt-0.5">{t.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-7">
            <FeatureGrid />
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-neutral-900 py-16 px-6">
        <div className="mx-auto max-w-6xl flex flex-col md:flex-row items-center justify-between gap-8">
          <div>
             <div className="text-2xl lg:text-3xl font-black text-white tracking-tight">System Operational.</div>
             <div className="text-neutral-400 mt-2 font-medium">All services connected via Management API. Ready for tenant provisioning.</div>
          </div>
          <button
            onClick={onOpenManager}
            className="rounded-full px-10 py-5 text-sm font-black bg-white text-neutral-950 hover:bg-neutral-200 transition-all active:scale-95 shadow-xl shrink-0"
          >
            Access Control Plane
          </button>
        </div>
      </section>
    </main>
  );
}
