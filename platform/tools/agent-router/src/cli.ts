import { route, listCapabilities, listAgentsForCapability } from "./router.js";

function readStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function parseArgs(argv: string[]) {
  const args: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v =
        argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[i + 1] : "true";
      args[k] = v;
      if (v !== "true") i++;
    }
  }
  return args;
}

async function main() {
  const cmd = process.argv[2];
  const args = parseArgs(process.argv.slice(3));

  if (!cmd || ["-h", "--help", "help"].includes(cmd)) {
    process.stdout.write(
      [
        "agent-router (CLI)",
        "",
        "Commands:",
        "  route                     Read JSON from stdin, output JSON",
        "  list-capabilities          Output all capability ids",
        "  list-agents --capability X Output agent mapping for capability",
        "",
        "Env overrides:",
        "  AGENT_ROUTER_TAXONOMY, AGENT_ROUTER_MATRIX, AGENT_ROUTER_PROMPTS_DIR",
        "",
      ].join("\n"),
    );
    process.exit(0);
  }

  if (cmd === "list-capabilities") {
    const caps = await listCapabilities();
    process.stdout.write(
      JSON.stringify({ capabilities: caps }, null, 2) + "\n",
    );
    return;
  }

  if (cmd === "list-agents") {
    const capability = args["capability"];
    if (!capability) throw new Error("Missing --capability");
    const agents = await listAgentsForCapability(capability);
    process.stdout.write(JSON.stringify({ mapping: agents }, null, 2) + "\n");
    return;
  }

  if (cmd === "route") {
    const raw = await readStdin();
    if (!raw.trim()) throw new Error("Expected JSON on stdin");
    const req = JSON.parse(raw);
    const res = await route(req);
    process.stdout.write(JSON.stringify(res, null, 2) + "\n");
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

main().catch((err) => {
  process.stderr.write(String(err?.stack || err?.message || err) + "\n");
  process.exit(1);
});
