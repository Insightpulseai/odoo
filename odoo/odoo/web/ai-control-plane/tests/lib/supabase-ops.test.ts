import { describe, it, expect } from 'vitest';
import { createOpsClient } from '@/lib/supabase-ops';

describe('Supabase Ops Client', () => {
  it('should create client with environment variables', () => {
    const client = createOpsClient();
    expect(client).toBeDefined();
  });

  it('should throw error if env vars missing', () => {
    const originalUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const originalKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    
    delete process.env.NEXT_PUBLIC_SUPABASE_URL;
    delete process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    expect(() => createOpsClient()).toThrow('Missing Supabase environment variables');

    process.env.NEXT_PUBLIC_SUPABASE_URL = originalUrl;
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = originalKey;
  });
});
