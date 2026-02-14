/**
 * Deterministic agent router (no LLM required).
 * - simple keyword routing
 * - returns agent ids + artifact hints
 */
import fs from "node:fs";
import path from "node:path";
import yaml from "yaml";

type RouterConfig = {
  version: number;
  routing: { match_any: string[]; primary: string; secondary?: string[] }[];
  defaults: { primary: string; secondary?: string[] };
};

export function loadConfig(configPath: string): RouterConfig {
  const raw = fs.readFileSync(configPath, "utf8");
  return yaml.parse(raw) as RouterConfig;
}

export function route(config: RouterConfig, input: string) {
  const text = input.toLowerCase();
  for (const rule of config.routing) {
    if (rule.match_any.some((k) => text.includes(k.toLowerCase()))) {
      return {
        primary_agent: rule.primary,
        secondary_agents: rule.secondary ?? [],
      };
    }
  }
  return {
    primary_agent: config.defaults.primary,
    secondary_agents: config.defaults.secondary ?? [],
  };
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const configPath =
    process.env.ROUTER_CONFIG ?? path.resolve("router/agent_router.yaml");
  const input = process.argv.slice(2).join(" ").trim();
  if (!input) {
    console.error('Usage: node router.ts "your request text"');
    process.exit(2);
  }
  const cfg = loadConfig(configPath);
  console.log(JSON.stringify(route(cfg, input), null, 2));
}
