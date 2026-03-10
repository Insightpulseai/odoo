import fs from "fs";
import path from "path";
import matter from "gray-matter";

// Paths
// Paths
const REPO_ROOT = path.resolve(process.cwd(), "../.."); // Assuming running from templates/odooops-console
const OVERRIDES_DIR = path.join(
  process.cwd(),
  "src/content/docs/upstream_overrides",
);
const DEPLOYED_DIR = path.join(process.cwd(), "src/content/docs/stack");
const UPSTREAM_DIR = path.resolve(REPO_ROOT, "docs/kb/odoo19/upstream");

export interface DocMetadata {
  layer: "override" | "deployed" | "upstream";
  sourcePath: string;
  canonicalId: string;
  pinnedSha?: string; // Only for upstream
  [key: string]: any;
}

export interface DocPage {
  slug: string;
  title: string;
  content: string;
  meta: DocMetadata;
}

export async function getDocPage(slugParts: string[]): Promise<DocPage | null> {
  const slugPath = slugParts.join("/");

  // 1. Check Overrides (Highest Priority)
  const overridePath = path.join(OVERRIDES_DIR, `${slugPath}.md`);
  if (fs.existsSync(overridePath)) {
    return loadFile(overridePath, slugPath, "override");
  } else {
    // Check for index file in directory
    const overrideIndexPath = path.join(OVERRIDES_DIR, slugPath, "index.md");
    if (fs.existsSync(overrideIndexPath)) {
      return loadFile(overrideIndexPath, slugPath, "override");
    }
  }

  // 2. Check Deployed Stack (Middle Priority)
  const deployedPath = path.join(DEPLOYED_DIR, `${slugPath}.md`);
  if (fs.existsSync(deployedPath)) {
    return loadFile(deployedPath, slugPath, "deployed");
  }

  // 3. Check Upstream (Lowest Priority)
  const upstreamContentDir = path.join(UPSTREAM_DIR, "content");

  // Check for MD/MDX first
  let upstreamPath = path.join(upstreamContentDir, `${slugPath}.md`);
  if (fs.existsSync(upstreamPath)) {
    return loadFile(upstreamPath, slugPath, "upstream");
  }

  // Check for RST
  upstreamPath = path.join(upstreamContentDir, `${slugPath}.rst`);
  if (fs.existsSync(upstreamPath)) {
    return loadFile(upstreamPath, slugPath, "upstream");
  }

  // Check for index (MD then RST)
  const upstreamIndexMd = path.join(upstreamContentDir, slugPath, "index.md");
  if (fs.existsSync(upstreamIndexMd)) {
    return loadFile(upstreamIndexMd, slugPath, "upstream");
  }
  const upstreamIndexRst = path.join(upstreamContentDir, slugPath, "index.rst");
  if (fs.existsSync(upstreamIndexRst)) {
    return loadFile(upstreamIndexRst, slugPath, "upstream");
  }

  return null;
}

function loadFile(
  filePath: string,
  slug: string,
  layer: "override" | "deployed" | "upstream",
): DocPage {
  const fileContent = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(fileContent);

  // Canonical ID: kb://odoo19/<slug>
  // This ID is stable regardless of which layer serves the content.
  const canonicalId = `kb://odoo19/${slug}`;

  // For upstream, we could read PIN file, but that might differ if verifying pin.
  // We'll leave pinnedSha undefined for now or inject it if needed by UI.

  const meta: DocMetadata = {
    ...data,
    layer,
    sourcePath: filePath,
    canonicalId,
  };

  return {
    slug,
    title: data.title || slug.split("/").pop() || "Untitled",
    content,
    meta,
  };
}
