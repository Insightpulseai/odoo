export default function HomePage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">Workspace</h1>
      <p className="text-muted-foreground">System of Work — pages, knowledge databases, and docs.</p>
      <div className="mt-6 grid grid-cols-3 gap-4">
        {[
          { href: '/pages', label: 'Pages', desc: 'Wiki pages and docs', icon: '📄' },
          { href: '/databases', label: 'Databases', desc: 'Structured knowledge tables', icon: '🗃' },
          { href: '/search', label: 'Search', desc: 'Full-text search across workspace', icon: '🔍' },
        ].map(card => (
          <a key={card.href} href={card.href}
            className="block p-4 rounded-lg border border-border hover:border-primary hover:bg-accent/30 transition-colors">
            <div className="text-2xl mb-2">{card.icon}</div>
            <div className="font-medium">{card.label}</div>
            <div className="text-sm text-muted-foreground mt-1">{card.desc}</div>
          </a>
        ))}
      </div>
    </div>
  )
}
