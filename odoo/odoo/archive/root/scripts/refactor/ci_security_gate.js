const fs = require("fs");

function exit(msg, code=1){ console.error(msg); process.exit(code); }

const p = "out/refactor/npm-audit.json";
if (!fs.existsSync(p)) exit(`Missing ${p}. Run refactor-subagents first.`);

const audit = JSON.parse(fs.readFileSync(p, "utf8"));
const v = audit?.metadata?.vulnerabilities;
if (!v) exit("No vulnerabilities metadata found; audit output unexpected.");

const critical = v.critical || 0;
const high = v.high || 0;

console.log(`npm audit vulnerabilities: critical=${critical}, high=${high}, moderate=${v.moderate||0}, low=${v.low||0}`);

if (critical > 0 || high > 0) {
  exit("Failing CI: critical/high vulnerabilities present. Patch deps and re-run.", 2);
}
console.log("OK: no critical/high vulnerabilities.");
