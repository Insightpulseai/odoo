/**
 * DigitalOcean source for Ops Advisor
 *
 * Fetches droplet health and bandwidth metrics via the DO API.
 * Requires: DIGITALOCEAN_API_TOKEN env var
 */

const DO_API = "https://api.digitalocean.com/v2";

export interface Droplet {
  id: number;
  name: string;
  status: string;
  networks: { v4: Array<{ ip_address: string; type: string }> };
}

export interface BandwidthMetrics {
  inbound_bytes_30d: number;
  outbound_bytes_30d: number;
  limit_bytes_30d: number;
}

export async function getDroplet(
  token: string,
  dropletId: number
): Promise<Droplet | null> {
  const res = await fetch(`${DO_API}/droplets/${dropletId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`DO getDroplet failed: ${res.status}`);
  const data = await res.json();
  return data.droplet ?? null;
}

export async function getDropletByTag(
  token: string,
  tag: string
): Promise<Droplet[]> {
  const res = await fetch(`${DO_API}/droplets?tag_name=${encodeURIComponent(tag)}&per_page=5`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`DO getDropletByTag failed: ${res.status}`);
  const data = await res.json();
  return data.droplets ?? [];
}

export async function getBandwidthUsage(
  _token: string,
  _dropletId: number
): Promise<BandwidthMetrics | null> {
  // TODO: Use DO Monitoring API /v2/monitoring/metrics/droplet/bandwidth
  // Returning null until the monitoring endpoint is integrated.
  return null;
}
