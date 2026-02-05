/**
 * OCR Parallel Worker
 * 
 * This worker polls the Supabase ops-executor edge function for queued runs,
 * claims them atomically using SKIP LOCKED, and executes them in parallel.
 * 
 * Deploy this to:
 * - DigitalOcean App Platform
 * - Kubernetes (as a Deployment with replicas)
 * - GitHub Actions (long-running workflow)
 * - Local machine (dev mode)
 * 
 * Environment Variables:
 * - SUPABASE_FN_URL: https://<project-ref>.supabase.co/functions/v1/ops-executor
 * - SUPABASE_ANON: Your Supabase anon key
 * - WORKER_ID: Unique identifier for this worker (e.g., ocr-worker-1)
 * - CONCURRENCY: Number of parallel execution slots (default: 4)
 * - BATCH: Number of runs to claim per request (default: 1)
 */

// Node 18+ with ES modules
// npm install node-fetch

import fetch from "node-fetch";

const SUPABASE_FN_URL = process.env.SUPABASE_FN_URL;
const SUPABASE_ANON = process.env.SUPABASE_ANON;
const WORKER_ID = process.env.WORKER_ID || `worker-${Math.random().toString(16).slice(2, 8)}`;
const CONCURRENCY = Number(process.env.CONCURRENCY || 4);
const BATCH = Number(process.env.BATCH || 1);
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS || 800);

if (!SUPABASE_FN_URL || !SUPABASE_ANON) {
  console.error("Missing required environment variables:");
  console.error("  SUPABASE_FN_URL");
  console.error("  SUPABASE_ANON");
  process.exit(1);
}

async function claimAndRun() {
  const res = await fetch(`${SUPABASE_FN_URL}/claim`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${SUPABASE_ANON}`,
      "apikey": SUPABASE_ANON,
    },
    body: JSON.stringify({ worker_id: WORKER_ID, limit: BATCH }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  const json = await res.json();
  if (!json.ok) {
    throw new Error(json.error || "claim failed");
  }

  return json.claimed?.length || 0;
}

async function loop(slot: number) {
  for (;;) {
    try {
      const n = await claimAndRun();
      if (n === 0) {
        await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
      } else {
        console.log(`[slot ${slot}] claimed and executed ${n} run(s)`);
      }
    } catch (e) {
      console.error(`[slot ${slot}]`, e);
      await new Promise((r) => setTimeout(r, 1500));
    }
  }
}

(async () => {
  console.log(`OCR Worker ${WORKER_ID} starting`);
  console.log(`  Concurrency: ${CONCURRENCY}`);
  console.log(`  Batch size: ${BATCH}`);
  console.log(`  Poll interval: ${POLL_INTERVAL_MS}ms`);
  console.log(`  Target: ${SUPABASE_FN_URL}`);

  await Promise.all(Array.from({ length: CONCURRENCY }, (_, i) => loop(i)));
})();
