import fs from "fs";
import path from "path";
import crypto from "crypto";
import YAML from "yaml";
import { getGoogleAuth } from "./lib/google_auth.mjs";
import { exportDocToMarkdown } from "./lib/export_doc_markdown.mjs";

const ROOT = process.cwd();
const MANIFEST_PATH = path.join(ROOT, "scripts/drive_sync/drive_manifest.yml");
const MODE = (process.env.DRIVE_SYNC_MODE || "pr").toLowerCase(); // pr|verify|dry-run|push
const LOG_PATH = path.join(ROOT, "scripts/drive_sync", "sync.log.json");

function ensureDir(p) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
}

function sha256(s) {
  return crypto.createHash("sha256").update(s, "utf8").digest("hex");
}

function stableFrontmatter(obj) {
  // stable key ordering
  const ordered = {};
  for (const k of ["title", "tags", "owner", "source_url", "drive_file_id", "drive_modified_time", "checksum"]) {
    if (obj[k] !== undefined && obj[k] !== null) ordered[k] = obj[k];
  }
  // include any other keys deterministically
  for (const k of Object.keys(obj).sort()) {
    if (!(k in ordered) && obj[k] !== undefined && obj[k] !== null) ordered[k] = obj[k];
  }
  const y = YAML.stringify(ordered).trimEnd();
  return `---\n${y}\n---\n\n`;
}

function loadManifest() {
  const raw = fs.readFileSync(MANIFEST_PATH, "utf8");
  const doc = YAML.parse(raw);
  const defaults = doc.defaults || {};
  const entries = doc.documents || [];
  return { defaults, entries, raw };
}

async function run() {
  const { defaults, entries, raw: manifestRaw } = loadManifest();
  const auth = await getGoogleAuth();

  const log = {
    startedAt: new Date().toISOString(),
    mode: MODE,
    manifestSha: sha256(manifestRaw),
    processed: [],
    skipped: [],
    errors: []
  };

  for (const e of entries) {
    const enabled = e.enabled ?? defaults.enabled ?? true;
    if (!enabled) {
      log.skipped.push({ id: e.id, reason: "disabled" });
      continue;
    }

    const type = (e.type ?? defaults.type ?? "doc").toLowerCase();
    if (type !== "doc") {
      log.skipped.push({ id: e.id, reason: `unsupported_type:${type}` });
      continue;
    }

    try {
      const repoPath = e.repo_path;
      if (!repoPath) throw new Error("Missing repo_path in manifest entry.");

      const { markdown, metadata } = await exportDocToMarkdown({ auth, fileId: e.id });

      const fm = {
        ...(defaults.frontmatter || {}),
        ...(e.frontmatter || {}),
        source_url: metadata.webViewLink || `https://docs.google.com/document/d/${e.id}/edit`,
        drive_file_id: e.id,
        drive_modified_time: metadata.modifiedTime,
        checksum: metadata.rawChecksum
      };

      const out = stableFrontmatter(fm) + markdown;

      const absOut = path.join(ROOT, repoPath);
      if (MODE !== "dry-run") {
        ensureDir(absOut);
        fs.writeFileSync(absOut, out, "utf8");
      }

      log.processed.push({
        id: e.id,
        repo_path: repoPath,
        modifiedTime: metadata.modifiedTime,
        checksum: metadata.rawChecksum,
        bytes: Buffer.byteLength(out, "utf8")
      });
    } catch (err) {
      log.errors.push({ id: e.id, message: err?.message || String(err) });
    }
  }

  ensureDir(LOG_PATH);
  fs.writeFileSync(LOG_PATH, JSON.stringify(log, null, 2) + "\n", "utf8");

  if (log.errors.length) {
    console.error("Drive sync completed with errors:", log.errors);
    process.exit(2);
  }

  console.log(`Drive sync complete. Processed: ${log.processed.length}, Skipped: ${log.skipped.length}`);
}

await run();
