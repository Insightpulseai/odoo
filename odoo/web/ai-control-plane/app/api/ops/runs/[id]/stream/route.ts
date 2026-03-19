import { NextRequest } from 'next/server';
import { createOpsClient } from '@/lib/supabase-ops';

export const dynamic = 'force-dynamic';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const supabase = createOpsClient();

      const channel = supabase
        .channel(`run:${params.id}`)
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'ops',
            table: 'run_events',
            filter: `run_id=eq.${params.id}`
          },
          (payload) => {
            const data = `data: ${JSON.stringify(payload.new)}\n\n`;
            controller.enqueue(encoder.encode(data));
          }
        )
        .subscribe();

      req.signal.addEventListener('abort', () => {
        supabase.removeChannel(channel);
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  });
}
