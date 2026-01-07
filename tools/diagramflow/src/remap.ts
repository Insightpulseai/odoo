/**
 * Azure to Target Stack Remapper
 *
 * Reads a draw.io XML file and remaps Azure services to target stack
 * (DigitalOcean, Supabase, Kubernetes, Odoo, etc.) based on a YAML mapping.
 *
 * Usage:
 *   node dist/remap.js diagram.drawio mapping.yaml
 */

import fs from "node:fs";
import { XMLParser, XMLBuilder } from "fast-xml-parser";
import YAML from "yaml";

export interface ServiceMapping {
  label: string;
  icon?: string;
  icon_style?: string;
  fillColor?: string;
  strokeColor?: string;
  description?: string;
}

export interface MappingConfig {
  mappings: Record<string, ServiceMapping>;
  defaults?: {
    style?: string;
  };
}

export interface RemapOptions {
  /** Path to the draw.io file */
  drawioPath: string;
  /** Path to the mapping YAML file */
  mappingPath: string;
  /** Output path (defaults to input path, overwriting) */
  outputPath?: string;
  /** Dry run - don't write, just report changes */
  dryRun?: boolean;
}

export interface RemapResult {
  changed: boolean;
  mappedNodes: number;
  unmappedNodes: string[];
  output?: string;
}

// XML parser options for draw.io format
const PARSER_OPTIONS = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  allowBooleanAttributes: true,
  parseAttributeValue: false,
};

const BUILDER_OPTIONS = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  format: true,
  indentBy: "  ",
  suppressBooleanAttributes: false,
};

export function loadMapping(mappingPath: string): MappingConfig {
  const content = fs.readFileSync(mappingPath, "utf8");
  return YAML.parse(content) as MappingConfig;
}

export function remapDrawio(options: RemapOptions): RemapResult {
  const { drawioPath, mappingPath, outputPath, dryRun = false } = options;

  // Load files
  const xml = fs.readFileSync(drawioPath, "utf8");
  const config = loadMapping(mappingPath);
  const { mappings } = config;

  // Parse XML
  const parser = new XMLParser(PARSER_OPTIONS);
  const doc = parser.parse(xml);

  // Navigate to root cells
  const mxfile = doc.mxfile;
  if (!mxfile) {
    throw new Error("Invalid draw.io file: missing mxfile root");
  }

  const diagram = mxfile.diagram;
  if (!diagram) {
    throw new Error("Invalid draw.io file: missing diagram element");
  }

  const graphModel = diagram.mxGraphModel;
  if (!graphModel) {
    throw new Error("Invalid draw.io file: missing mxGraphModel");
  }

  const root = graphModel.root;
  if (!root) {
    throw new Error("Invalid draw.io file: missing root element");
  }

  // Get cells array
  let cells = root.mxCell;
  if (!Array.isArray(cells)) {
    cells = cells ? [cells] : [];
  }

  let mappedNodes = 0;
  const unmappedNodes: string[] = [];

  // Process each cell
  for (const cell of cells) {
    // Only process vertex (shape) cells
    if (cell["@_vertex"] !== "1") continue;

    const value = cell["@_value"] || "";
    const style = cell["@_style"] || "";

    // Look for service tag in value or style
    // Convention: value contains "svc=azure.xxx" or "| svc=azure.xxx |"
    const svcMatch = String(value).match(/svc=([a-z0-9_.-]+)/i);
    if (!svcMatch) {
      // Try to detect Azure services by style patterns
      const azureStyle = detectAzureService(style, value);
      if (azureStyle && !mappings[azureStyle]) {
        unmappedNodes.push(`${cell["@_id"]}: ${value.slice(0, 50)} (detected: ${azureStyle})`);
      }
      continue;
    }

    const svcId = svcMatch[1];
    const mapping = mappings[svcId];

    if (!mapping) {
      unmappedNodes.push(`${cell["@_id"]}: ${svcId}`);
      continue;
    }

    // Apply mapping
    mappedNodes++;

    // Update label (remove svc= tag, add new label)
    const cleanValue = value.replace(/\s*\|?\s*svc=[a-z0-9_.-]+\s*\|?\s*/gi, "").trim();
    cell["@_value"] = mapping.label || cleanValue;

    // Update style
    if (mapping.icon_style) {
      cell["@_style"] = mapping.icon_style;
    } else {
      let newStyle = style;

      // Update fill color
      if (mapping.fillColor) {
        newStyle = updateStyleProperty(newStyle, "fillColor", mapping.fillColor);
      }

      // Update stroke color
      if (mapping.strokeColor) {
        newStyle = updateStyleProperty(newStyle, "strokeColor", mapping.strokeColor);
      }

      // Update icon/image
      if (mapping.icon) {
        // If using an image shape
        if (newStyle.includes("shape=image") || mapping.icon.startsWith("data:") || mapping.icon.endsWith(".svg") || mapping.icon.endsWith(".png")) {
          newStyle = `shape=image;image=${mapping.icon};aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;`;
        }
      }

      cell["@_style"] = newStyle;
    }
  }

  // Build output XML
  const builder = new XMLBuilder(BUILDER_OPTIONS);
  const output = builder.build(doc);

  // Write output
  if (!dryRun) {
    const outPath = outputPath || drawioPath;
    fs.writeFileSync(outPath, output, "utf8");
  }

  return {
    changed: mappedNodes > 0,
    mappedNodes,
    unmappedNodes,
    output: dryRun ? output : undefined,
  };
}

function updateStyleProperty(style: string, property: string, value: string): string {
  const regex = new RegExp(`${property}=[^;]*;?`, "g");
  if (style.match(regex)) {
    return style.replace(regex, `${property}=${value};`);
  }
  // Append property
  return style.endsWith(";") ? `${style}${property}=${value};` : `${style};${property}=${value};`;
}

function detectAzureService(style: string, value: string): string | null {
  // Common Azure shape patterns in draw.io
  const patterns: Record<string, RegExp> = {
    "azure.app_service": /azure.*app.*service|webapp|azureWebApp/i,
    "azure.functions": /azure.*function|azureFunction/i,
    "azure.storage_account": /azure.*storage|azureBlob|azureStorage/i,
    "azure.sql_database": /azure.*sql|azureSQL/i,
    "azure.cosmos_db": /azure.*cosmos|cosmosDB/i,
    "azure.aks": /azure.*kubernetes|aks|azureAKS/i,
    "azure.key_vault": /azure.*key.*vault|azureKeyVault/i,
    "azure.event_hub": /azure.*event.*hub|azureEventHub/i,
    "azure.service_bus": /azure.*service.*bus|azureServiceBus/i,
    "azure.api_management": /azure.*api.*management|azureAPIM/i,
    "azure.container_registry": /azure.*container.*registry|acr|azureACR/i,
    "azure.virtual_network": /azure.*vnet|virtual.*network|azureVNet/i,
    "azure.load_balancer": /azure.*load.*balancer|azureLB/i,
    "azure.application_gateway": /azure.*app.*gateway|azureAppGateway/i,
    "azure.redis_cache": /azure.*redis|azureRedis/i,
  };

  const combined = `${style} ${value}`;
  for (const [service, pattern] of Object.entries(patterns)) {
    if (pattern.test(combined)) {
      return service;
    }
  }

  // Check for mxgraph Azure shapes
  if (style.includes("mxgraph.azure") || style.includes("azure.")) {
    const match = style.match(/mxgraph\.(azure\.[a-z_]+)|shape=(azure\.[a-z_]+)/i);
    if (match) {
      return match[1] || match[2];
    }
  }

  return null;
}

/**
 * Generate a mapping template from an existing draw.io file
 */
export function generateMappingTemplate(drawioPath: string): MappingConfig {
  const xml = fs.readFileSync(drawioPath, "utf8");
  const parser = new XMLParser(PARSER_OPTIONS);
  const doc = parser.parse(xml);

  const cells = doc.mxfile?.diagram?.mxGraphModel?.root?.mxCell || [];
  const cellArray = Array.isArray(cells) ? cells : [cells];

  const detectedServices = new Set<string>();

  for (const cell of cellArray) {
    if (cell["@_vertex"] !== "1") continue;

    const value = cell["@_value"] || "";
    const style = cell["@_style"] || "";

    // Look for svc= tags
    const svcMatch = String(value).match(/svc=([a-z0-9_.-]+)/i);
    if (svcMatch) {
      detectedServices.add(svcMatch[1]);
      continue;
    }

    // Try auto-detection
    const detected = detectAzureService(style, value);
    if (detected) {
      detectedServices.add(detected);
    }
  }

  // Generate template
  const mappings: Record<string, ServiceMapping> = {};
  for (const svc of Array.from(detectedServices).sort()) {
    mappings[svc] = {
      label: `TODO: ${svc}`,
      description: `Replace Azure ${svc} with equivalent service`,
    };
  }

  return { mappings };
}
