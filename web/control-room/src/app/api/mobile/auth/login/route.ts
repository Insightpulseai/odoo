import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
  device_id: z.string().optional(),
  device_name: z.string().optional(),
  platform: z.enum(['ios', 'android', 'web']).optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = loginSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { email, password, device_id, device_name, platform } = parsed.data;

    // TODO: Authenticate against Supabase or Odoo
    // For now, return mock tokens

    // Mock authentication (replace with real auth)
    if (email === 'admin@example.com' && password === 'admin') {
      const accessToken = generateMockJWT({ email, exp: Date.now() + 3600000 });
      const refreshToken = generateMockJWT({ email, exp: Date.now() + 86400000 * 30 });

      // TODO: Register device for push notifications
      // await registerDevice(userId, device_id, device_name, platform);

      return NextResponse.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 3600,
        user: {
          id: '1',
          email: email,
          name: 'Admin User',
        },
      });
    }

    return NextResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

function generateMockJWT(payload: Record<string, unknown>): string {
  // Mock JWT generation - replace with real JWT library
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify(payload));
  const signature = btoa('mock-signature');
  return `${header}.${body}.${signature}`;
}
