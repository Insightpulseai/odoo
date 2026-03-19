/**
 * Droplet management tools
 */

import { DigitalOceanClient } from "../do-client.js";

export async function listDroplets(
  client: DigitalOceanClient,
  tag?: string
): Promise<unknown> {
  return client.listDroplets(tag);
}

export async function getDroplet(
  client: DigitalOceanClient,
  id: number
): Promise<unknown> {
  return client.getDroplet(id);
}

export async function rebootDroplet(
  client: DigitalOceanClient,
  id: number
): Promise<unknown> {
  return client.dropletAction(id, "reboot");
}

export async function powerCycleDroplet(
  client: DigitalOceanClient,
  id: number
): Promise<unknown> {
  return client.dropletAction(id, "power_cycle");
}
