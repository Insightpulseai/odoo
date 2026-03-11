export default function DigitalOceanPlatformLoading() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Header skeleton */}
      <div className="space-y-2">
        <div className="h-8 w-56 bg-black/5 rounded-lg" />
        <div className="h-4 w-80 bg-black/5 rounded" />
      </div>

      {/* Summary cards skeleton */}
      <div className="grid gap-4 md:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="glass-card rounded-xl p-5">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-black/5" />
              <div className="space-y-2">
                <div className="h-3 w-24 bg-black/5 rounded" />
                <div className="h-7 w-10 bg-black/5 rounded" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Table skeleton */}
      <div className="space-y-3">
        <div className="h-4 w-24 bg-black/5 rounded" />
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-black/5">
            <div className="h-3 w-full max-w-lg bg-black/5 rounded" />
          </div>
          {[0, 1, 2].map((i) => (
            <div key={i} className="px-4 py-3 border-b border-black/5 last:border-0">
              <div className="h-4 w-full bg-black/5 rounded" />
            </div>
          ))}
        </div>
      </div>

      {/* Second table skeleton */}
      <div className="space-y-3">
        <div className="h-4 w-36 bg-black/5 rounded" />
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-black/5">
            <div className="h-3 w-full max-w-lg bg-black/5 rounded" />
          </div>
          {[0, 1].map((i) => (
            <div key={i} className="px-4 py-3 border-b border-black/5 last:border-0">
              <div className="h-4 w-full bg-black/5 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
