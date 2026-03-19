import fs from "node:fs/promises";
import path from "node:path";

const TEMPLATE = "spec/platforms/platform-capabilities.template.md";
const OUT_DIR = "docs/runbooks";

async function main() {
  const src = await fs.readFile(TEMPLATE, "utf8");

  const platforms = ["supabase", "vercel", "digitalocean", "superset", "figma-sites"];

  await fs.mkdir(OUT_DIR, { recursive: true });

  for (const p of platforms) {
    const out = [
      `# Runbook: ${p}`,
      ``,
      `## Scope`,
      `This runbook is generated from ${TEMPLATE}.`,
      ``,
      `## Required Secrets`,
      `- TODO: list secrets for ${p}`,
      ``,
      `## Apply`,
      `\`\`\`bash`,
      `# TODO: apply commands for ${p}`,
      `\`\`\``,
      ``,
      `## Test / Verify`,
      `\`\`\`bash`,
      `# TODO: verification commands for ${p}`,
      `\`\`\``,
      ``,
      `## Deploy / Rollback`,
      `\`\`\`bash`,
      `# TODO: deploy`,
      `# TODO: rollback`,
      `\`\`\``,
      ``,
      `## Production Validation`,
      `\`\`\`bash`,
      `# TODO: health checks + logs`,
      `\`\`\``,
      ``,
      `## Notes / Risks`,
      `- TODO`,
      ``,
      `---`,
      ``,
      `## Template (reference)`,
      `\n` + src,
    ].join("\n");

    await fs.writeFile(path.join(OUT_DIR, `${p}.md`), out, "utf8");
  }

  console.log(`Generated runbooks to ${OUT_DIR}/`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
