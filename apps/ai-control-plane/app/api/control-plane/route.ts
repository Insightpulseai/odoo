import { NextRequest, NextResponse } from 'next/server';
import { ControlPlanePayloadSchema, ControlPlaneResponse } from '@/lib/types';
import { getSecret, botCanAccessSecret } from '@/lib/supabase';

const ALLOWED_PROXY_HOSTS = [
  'api.digitalocean.com',
  'api.vercel.com',
  'api.openai.com',
  'api.anthropic.com',
  'api.github.com',
];

/**
 * Control Plane API Route - Secret access and proxying
 *
 * Provides secure access to secrets stored in Supabase Vault.
 * Supports raw secret retrieval and proxied API calls.
 *
 * POST /api/control-plane
 */
export async function POST(req: NextRequest) {
  try {
    // Authenticate the request (check for bot auth header)
    const botId = req.headers.get('x-bot-id');
    const authToken = req.headers.get('x-control-plane-auth');

    // Validate auth token matches environment secret
    const expectedToken = process.env.CONTROL_PLANE_AUTH_TOKEN;
    if (expectedToken && authToken !== expectedToken) {
      return NextResponse.json(
        { ok: false, error: 'Unauthorized' } satisfies ControlPlaneResponse,
        { status: 401 }
      );
    }

    // Parse and validate request
    const json = await req.json();
    const payload = ControlPlanePayloadSchema.parse(json);

    // If botId is provided, check if bot can access the secret
    if (botId) {
      const canAccess = await botCanAccessSecret(botId, payload.secretName);
      if (!canAccess) {
        return NextResponse.json(
          { ok: false, error: `Bot ${botId} not authorized for secret ${payload.secretName}` } satisfies ControlPlaneResponse,
          { status: 403 }
        );
      }
    }

    // Get the secret
    const accessor = botId || 'anonymous';
    const secret = await getSecret(payload.secretName, accessor, payload.mode);

    if (!secret) {
      return NextResponse.json(
        { ok: false, error: `Secret ${payload.secretName} not found` } satisfies ControlPlaneResponse,
        { status: 404 }
      );
    }

    // Handle different modes
    switch (payload.mode) {
      case 'raw':
        // Return the raw secret value
        return NextResponse.json({
          ok: true,
          secretName: payload.secretName,
          value: secret,
        } satisfies ControlPlaneResponse);

      case 'proxy':
        // Proxy an API call using the secret
        if (!payload.proxyTarget) {
          return NextResponse.json(
            { ok: false, error: 'proxyTarget is required for proxy mode' } satisfies ControlPlaneResponse,
            { status: 400 }
          );
        }

        // Validate the proxy target host
        const targetUrl = new URL(payload.proxyTarget);
        if (!ALLOWED_PROXY_HOSTS.some((host) => targetUrl.host.includes(host))) {
          return NextResponse.json(
            { ok: false, error: `Proxy target host not allowed: ${targetUrl.host}` } satisfies ControlPlaneResponse,
            { status: 400 }
          );
        }

        // Make the proxied request
        const proxyResp = await fetch(payload.proxyTarget, {
          method: payload.proxyMethod || 'GET',
          headers: {
            Authorization: `Bearer ${secret}`,
            'Content-Type': 'application/json',
          },
          body: payload.proxyBody ? JSON.stringify(payload.proxyBody) : undefined,
        });

        const proxiedData = await proxyResp.json();

        return NextResponse.json({
          ok: proxyResp.ok,
          secretName: payload.secretName,
          proxiedResponse: proxiedData,
        } satisfies ControlPlaneResponse);

      case 'exchange':
        // Exchange the secret for a short-lived token (implementation depends on the secret type)
        // For now, just return the secret (could implement token exchange logic here)
        return NextResponse.json({
          ok: true,
          secretName: payload.secretName,
          value: secret,
        } satisfies ControlPlaneResponse);

      default:
        return NextResponse.json(
          { ok: false, error: `Unknown mode: ${payload.mode}` } satisfies ControlPlaneResponse,
          { status: 400 }
        );
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';

    console.error('Control Plane error:', err);

    return NextResponse.json(
      { ok: false, error: errorMessage } satisfies ControlPlaneResponse,
      { status: 500 }
    );
  }
}

/**
 * GET handler for listing available secrets (metadata only, not values)
 */
export async function GET(req: NextRequest) {
  try {
    const authToken = req.headers.get('x-control-plane-auth');
    const expectedToken = process.env.CONTROL_PLANE_AUTH_TOKEN;

    if (expectedToken && authToken !== expectedToken) {
      return NextResponse.json({ ok: false, error: 'Unauthorized' }, { status: 401 });
    }

    // Return the list of available secret names (not values)
    // This is a simplified version - in production, query the secret_index table
    const availableSecrets = [
      { name: 'DIGITALOCEAN_API_TOKEN', purpose: 'digitalocean_api' },
      { name: 'VERCEL_API_TOKEN', purpose: 'vercel_api' },
      { name: 'OPENAI_API_KEY', purpose: 'openai_api' },
      { name: 'GITHUB_TOKEN', purpose: 'github_api' },
      { name: 'SUPABASE_SERVICE_ROLE_KEY', purpose: 'supabase_api' },
    ];

    return NextResponse.json({
      ok: true,
      secrets: availableSecrets,
      timestamp: new Date().toISOString(),
    });
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ ok: false, error: errorMessage }, { status: 500 });
  }
}
