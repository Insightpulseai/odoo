import { NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';

export async function GET() {
  try {
    const client = getDatabricksClient();
    const jobs = await client.getJobs();

    return NextResponse.json({ jobs });
  } catch (error) {
    console.error('Failed to fetch jobs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch jobs' },
      { status: 500 }
    );
  }
}
