export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>AI Control Plane</h1>
      <p>BugBot, Vercel Bot, and infrastructure automation via Vercel AI Gateway + Supabase Vault</p>

      <h2>Endpoints</h2>
      <ul>
        <li>
          <strong>POST /api/bugbot</strong> - AI SRE &amp; debugging assistant
        </li>
        <li>
          <strong>POST /api/vercel-bot</strong> - Deployment SRE
        </li>
        <li>
          <strong>POST /api/control-plane</strong> - Secret access and proxying
        </li>
      </ul>

      <h2>Health Checks</h2>
      <ul>
        <li>
          <a href="/api/bugbot">GET /api/bugbot</a>
        </li>
        <li>
          <a href="/api/vercel-bot">GET /api/vercel-bot</a>
        </li>
        <li>
          <a href="/api/control-plane">GET /api/control-plane</a>
        </li>
      </ul>

      <h2>Configuration</h2>
      <p>Set the following environment variables:</p>
      <pre style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
{`# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI Gateway (optional - uses direct OpenAI if not set)
AI_GATEWAY_URL=https://gateway.ai.cloudflare.com/v1/...
OPENAI_API_KEY=sk-...

# Control Plane Auth
CONTROL_PLANE_AUTH_TOKEN=your-auth-token

# Fallback tokens (if not using Vault)
VERCEL_TOKEN=your-vercel-token
DIGITALOCEAN_API_TOKEN=your-do-token`}
      </pre>
    </main>
  );
}
