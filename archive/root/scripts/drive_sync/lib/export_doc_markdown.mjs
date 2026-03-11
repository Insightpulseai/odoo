import crypto from "crypto";
import { google } from "googleapis";
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";
import { normalizeMarkdown } from "./normalize_markdown.mjs";

export async function exportDocToMarkdown({ auth, fileId }) {
  const drive = google.drive({ version: "v3", auth });

  // 1) Fetch metadata (stable "modifiedTime" used for determinism)
  const meta = await drive.files.get({
    fileId,
    fields: "id,name,mimeType,modifiedTime,owners(displayName,emailAddress),webViewLink"
  });

  // 2) Export HTML (Google's most stable cross-doc format)
  const res = await drive.files.export(
    { fileId, mimeType: "text/html" },
    { responseType: "arraybuffer" }
  );

  const html = Buffer.from(res.data).toString("utf8");
  const rawChecksum = sha256(html);

  // 3) HTML -> Markdown
  const td = new TurndownService({
    codeBlockStyle: "fenced",
    headingStyle: "atx",
    bulletListMarker: "-",
    emDelimiter: "_"
  });
  td.use(gfm);

  // Minor rules for stability
  td.addRule("removeEmptyAnchors", {
    filter: (node) => node.nodeName === "A" && !node.textContent?.trim(),
    replacement: () => ""
  });

  let md = td.turndown(html);
  md = normalizeMarkdown(md);

  return {
    markdown: md,
    metadata: {
      id: meta.data.id,
      name: meta.data.name,
      modifiedTime: meta.data.modifiedTime,
      webViewLink: meta.data.webViewLink,
      owner:
        meta.data.owners?.[0]?.emailAddress ||
        meta.data.owners?.[0]?.displayName ||
        null,
      rawChecksum
    }
  };
}

function sha256(s) {
  return crypto.createHash("sha256").update(s, "utf8").digest("hex");
}
