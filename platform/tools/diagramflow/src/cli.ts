#!/usr/bin/env node
/**
 * diagramflow CLI
 *
 * Deterministic diagram pipeline:
 * - Mermaid → BPMN 2.0 XML → draw.io
 * - Azure → target stack remapping
 * - CI drift checking
 *
 * Commands:
 *   build   Convert Mermaid files to BPMN and draw.io
 *   remap   Remap Azure services to target stack
 *   check   Verify diagrams are up-to-date (CI mode)
 */

import fs from "node:fs";
import path from "node:path";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";
import { parseMermaid, validateModel } from "./parseMermaid.js";
import { toBpmnXml } from "./toBpmn.js";
import { toDrawioXml } from "./toDrawio.js";
import { remapDrawio, generateMappingTemplate } from "./remap.js";

interface BuildArgs {
  input: string;
  output: string;
  check: boolean;
  bpmn: boolean;
  drawio: boolean;
  validate: boolean;
}

interface RemapArgs {
  file: string;
  mapping: string;
  output?: string;
  dryRun: boolean;
  template: boolean;
}

async function main() {
  await yargs(hideBin(process.argv))
    .scriptName("diagramflow")
    .usage("$0 <command> [options]")

    // Build command
    .command<BuildArgs>(
      "build",
      "Convert Mermaid files to BPMN and draw.io",
      (yargs) =>
        yargs
          .option("input", {
            alias: "i",
            type: "string",
            default: "docs/diagrams",
            description: "Input directory containing .mmd/.mermaid files",
          })
          .option("output", {
            alias: "o",
            type: "string",
            default: "docs/diagrams",
            description: "Output directory for generated files",
          })
          .option("check", {
            alias: "c",
            type: "boolean",
            default: false,
            description: "Check mode: fail if outputs differ (for CI)",
          })
          .option("bpmn", {
            type: "boolean",
            default: true,
            description: "Generate BPMN 2.0 XML files",
          })
          .option("drawio", {
            type: "boolean",
            default: true,
            description: "Generate draw.io XML files",
          })
          .option("validate", {
            alias: "v",
            type: "boolean",
            default: true,
            description: "Validate BPMN compliance",
          }),
      async (argv) => {
        await buildCommand(argv);
      }
    )

    // Remap command
    .command<RemapArgs>(
      "remap",
      "Remap Azure services to target stack",
      (yargs) =>
        yargs
          .option("file", {
            alias: "f",
            type: "string",
            demandOption: true,
            description: "Path to draw.io file to remap",
          })
          .option("mapping", {
            alias: "m",
            type: "string",
            default: "docs/diagrams/mappings/azure_to_stack.yaml",
            description: "Path to mapping YAML file",
          })
          .option("output", {
            alias: "o",
            type: "string",
            description: "Output path (defaults to overwriting input)",
          })
          .option("dry-run", {
            alias: "d",
            type: "boolean",
            default: false,
            description: "Show changes without writing",
          })
          .option("template", {
            alias: "t",
            type: "boolean",
            default: false,
            description: "Generate mapping template from file",
          }),
      async (argv) => {
        await remapCommand(argv);
      }
    )

    // Check command (alias for build --check)
    .command(
      "check",
      "Verify diagrams are up-to-date (CI mode)",
      (yargs) =>
        yargs
          .option("input", {
            alias: "i",
            type: "string",
            default: "docs/diagrams",
            description: "Input directory containing .mmd/.mermaid files",
          }),
      async (argv) => {
        await buildCommand({
          input: argv.input as string,
          output: argv.input as string,
          check: true,
          bpmn: true,
          drawio: true,
          validate: true,
        });
      }
    )

    .demandCommand(1, "You must specify a command")
    .strict()
    .help()
    .alias("h", "help")
    .version("1.0.0")
    .parse();
}

async function buildCommand(argv: BuildArgs) {
  const { input, output, check, bpmn, drawio, validate } = argv;

  const inputDir = path.resolve(input);
  const outputDir = path.resolve(output);

  // Find Mermaid files
  const files = fs.readdirSync(inputDir).filter((f) => f.endsWith(".mmd") || f.endsWith(".mermaid"));

  if (files.length === 0) {
    console.log(`No Mermaid files found in ${inputDir}`);
    process.exit(0);
  }

  console.log(`Processing ${files.length} Mermaid file(s)...`);

  let hasErrors = false;
  let hasDrift = false;

  for (const file of files) {
    const name = file.replace(/\.(mmd|mermaid)$/, "");
    const srcPath = path.join(inputDir, file);
    const src = fs.readFileSync(srcPath, "utf8");

    console.log(`\n→ ${file}`);

    // Parse Mermaid
    const model = parseMermaid(src);
    console.log(`  Parsed: ${model.nodes.length} nodes, ${model.edges.length} edges, ${model.pools.length} pools`);

    // Validate
    if (validate) {
      const errors = validateModel(model);
      if (errors.length > 0) {
        console.log(`  ⚠ Validation warnings:`);
        errors.forEach((e) => console.log(`    - ${e}`));
        if (!check) {
          // Non-fatal in build mode
        }
      }
    }

    // Generate BPMN
    if (bpmn) {
      const bpmnPath = path.join(outputDir, `${name}.bpmn`);
      const bpmnXml = toBpmnXml(model, { processId: `Process_${name}` });

      if (check) {
        if (fs.existsSync(bpmnPath)) {
          const existing = fs.readFileSync(bpmnPath, "utf8");
          if (existing !== bpmnXml) {
            console.log(`  ✗ BPMN file differs: ${bpmnPath}`);
            hasDrift = true;
          } else {
            console.log(`  ✓ BPMN up-to-date`);
          }
        } else {
          console.log(`  ✗ BPMN file missing: ${bpmnPath}`);
          hasDrift = true;
        }
      } else {
        fs.writeFileSync(bpmnPath, bpmnXml, "utf8");
        console.log(`  → Generated: ${name}.bpmn`);
      }
    }

    // Generate draw.io
    if (drawio) {
      const drawioPath = path.join(outputDir, `${name}.drawio`);
      const drawioXml = toDrawioXml(model, { diagramName: name });

      if (check) {
        if (fs.existsSync(drawioPath)) {
          const existing = fs.readFileSync(drawioPath, "utf8");
          // Compare ignoring timestamps
          const existingNorm = normalizeDrawio(existing);
          const newNorm = normalizeDrawio(drawioXml);
          if (existingNorm !== newNorm) {
            console.log(`  ✗ draw.io file differs: ${drawioPath}`);
            hasDrift = true;
          } else {
            console.log(`  ✓ draw.io up-to-date`);
          }
        } else {
          console.log(`  ✗ draw.io file missing: ${drawioPath}`);
          hasDrift = true;
        }
      } else {
        fs.writeFileSync(drawioPath, drawioXml, "utf8");
        console.log(`  → Generated: ${name}.drawio`);
      }
    }
  }

  if (hasDrift) {
    console.log("\n✗ Diagram artifacts out of date.");
    console.log("  Run: npm --prefix tools/diagramflow run diagram:build");
    process.exit(1);
  }

  if (hasErrors) {
    console.log("\n✗ Build completed with errors.");
    process.exit(1);
  }

  console.log("\n✓ Build complete.");
}

async function remapCommand(argv: RemapArgs) {
  const { file, mapping, output, dryRun, template } = argv;

  const filePath = path.resolve(file);

  // Generate template mode
  if (template) {
    console.log(`Generating mapping template from ${filePath}...`);
    const config = generateMappingTemplate(filePath);

    const YAML = await import("yaml");
    const yaml = YAML.stringify(config);

    const templatePath = mapping.replace(".yaml", ".template.yaml");
    fs.writeFileSync(templatePath, yaml, "utf8");
    console.log(`Template written to: ${templatePath}`);
    return;
  }

  // Remap mode
  const mappingPath = path.resolve(mapping);

  if (!fs.existsSync(mappingPath)) {
    console.error(`Mapping file not found: ${mappingPath}`);
    console.log("Tip: Use --template to generate a mapping template first");
    process.exit(1);
  }

  console.log(`Remapping ${filePath}...`);
  console.log(`Using mapping: ${mappingPath}`);

  const result = remapDrawio({
    drawioPath: filePath,
    mappingPath,
    outputPath: output ? path.resolve(output) : undefined,
    dryRun,
  });

  console.log(`\nMapped ${result.mappedNodes} node(s)`);

  if (result.unmappedNodes.length > 0) {
    console.log(`\nUnmapped services (${result.unmappedNodes.length}):`);
    result.unmappedNodes.forEach((n) => console.log(`  - ${n}`));
  }

  if (dryRun) {
    console.log("\n[Dry run - no changes written]");
  } else {
    console.log(`\n✓ Remap complete`);
  }
}

/**
 * Normalize draw.io XML for comparison (remove timestamps, etc.)
 */
function normalizeDrawio(xml: string): string {
  return xml
    .replace(/modified="[^"]*"/g, 'modified=""')
    .replace(/host="[^"]*"/g, 'host=""')
    .replace(/agent="[^"]*"/g, 'agent=""')
    .trim();
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
