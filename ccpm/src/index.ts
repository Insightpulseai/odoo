import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";

type Cmd = "init" | "ingest" | "trace";

function usage() {
  console.log(`ccpm <command>

Commands:
  init
  ingest <specPath>
  trace <reqKey>   # search ledger for a requirement
`);
}

function ensureDir(p: string) {
  if (!existsSync(p)) mkdirSync(p, { recursive: true });
}

function init() {
  ensureDir("ccpm_state");
  ensureDir("ccpm_state/ledger");
  const ledgerPath = join("ccpm_state/ledger", "events.jsonl");
  if (!existsSync(ledgerPath)) writeFileSync(ledgerPath, "");
  console.log("OK: initialized ccpm_state/ledger/events.jsonl");
}

function appendEvent(action: string, payload: unknown) {
  ensureDir("ccpm_state/ledger");
  const ledgerPath = join("ccpm_state/ledger", "events.jsonl");
  const evt = { ts: new Date().toISOString(), action, payload };
  writeFileSync(ledgerPath, JSON.stringify(evt) + "\n", { flag: "a" });
}

function ingest(specPath: string) {
  const content = readFileSync(specPath, "utf8");
  appendEvent("spec.ingested", { specPath, bytes: content.length });
  console.log(`OK: ingested ${specPath} (${content.length} bytes)`);
}

function trace(reqKey: string) {
  const ledgerPath = join("ccpm_state/ledger", "events.jsonl");
  if (!existsSync(ledgerPath)) {
    console.log(JSON.stringify({ reqKey, hits: [] }, null, 2));
    return;
  }
  const lines = readFileSync(ledgerPath, "utf8").split("\n").filter(Boolean);
  const hits = lines
    .map((l) => JSON.parse(l))
    .filter((e: unknown) => JSON.stringify(e).includes(reqKey));
  console.log(JSON.stringify({ reqKey, hits }, null, 2));
}

const args = process.argv.slice(2);
const cmd = (args[0] || "") as Cmd;

if (!cmd) usage();
else if (cmd === "init") init();
else if (cmd === "ingest") ingest(args[1] || "spec/prd.md");
else if (cmd === "trace") trace(args[1] || "R-1");
else usage();
