/**
 * App Platform management tools
 */

import { DigitalOceanClient } from "../do-client.js";

export async function listApps(client: DigitalOceanClient): Promise<unknown> {
  return client.listApps();
}

export async function getApp(
  client: DigitalOceanClient,
  id: string
): Promise<unknown> {
  return client.getApp(id);
}

export async function getAppLogs(
  client: DigitalOceanClient,
  appId: string,
  deploymentId?: string,
  component?: string,
  lines?: number
): Promise<unknown> {
  return client.getAppLogs(appId, deploymentId, component, lines);
}

export async function deployApp(
  client: DigitalOceanClient,
  id: string,
  forceBuild: boolean = false
): Promise<unknown> {
  return client.deployApp(id, forceBuild);
}

export async function createAppFromSpec(
  client: DigitalOceanClient,
  spec: unknown
): Promise<unknown> {
  return client.createApp(spec);
}
