import { NextResponse } from 'next/server';
import { createServerClient, type MCPJob, type MCPJobStats } from '@/lib/supabase';

export async function GET(request: Request) {
  try {
    const supabase = createServerClient();
    const { searchParams } = new URL(request.url);

    const source = searchParams.get('source');
    const status = searchParams.get('status');
    const jobType = searchParams.get('jobType');
    const limit = parseInt(searchParams.get('limit') || '50');

    let query = supabase
      .from('jobs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (source) query = query.eq('source', source);
    if (status) query = query.eq('status', status);
    if (jobType) query = query.eq('job_type', jobType);

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching jobs:', error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data as MCPJob[]);
  } catch (error) {
    console.error('MCP Jobs API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const supabase = createServerClient();
    const body = await request.json();

    const { source, jobType, payload, priority = 5 } = body;

    if (!source || !jobType) {
      return NextResponse.json(
        { error: 'source and jobType are required' },
        { status: 400 }
      );
    }

    // Call the enqueue_job RPC
    const { data, error } = await supabase.rpc('enqueue_job', {
      p_source: source,
      p_job_type: jobType,
      p_payload: payload || {},
      p_priority: priority,
    });

    if (error) {
      console.error('Error enqueueing job:', error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ jobId: data, status: 'queued' });
  } catch (error) {
    console.error('MCP Jobs API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
