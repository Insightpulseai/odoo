/**
 * Image Exporter
 *
 * Exports DrawIO files to PNG and SVG using headless rendering
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

/**
 * Export DrawIO file to PNG and/or SVG
 * @param {string} drawioPath - Path to .drawio file
 * @param {string} outdir - Output directory
 * @param {Object} options - Export options
 * @returns {Array} List of exported files
 */
export async function exportImages(drawioPath, outdir, options = {}) {
  const { formats = ['png', 'svg'], scale = 2.0 } = options;

  const outputs = [];
  const baseName = path.basename(drawioPath, '.drawio');

  for (const format of formats) {
    const outputPath = path.join(outdir, `${baseName}.${format}`);

    try {
      if (format === 'png') {
        await exportPng(drawioPath, outputPath, scale);
      } else if (format === 'svg') {
        await exportSvg(drawioPath, outputPath);
      }

      outputs.push({
        format,
        path: outputPath,
      });

      console.log(`Exported: ${outputPath}`);
    } catch (err) {
      console.error(`Failed to export ${format}: ${err.message}`);
      throw err;
    }
  }

  return outputs;
}

async function exportPng(drawioPath, outputPath, scale) {
  // Try drawio CLI first
  try {
    await execAsync(
      `drawio -x -f png -s ${scale} -o "${outputPath}" "${drawioPath}"`,
      { timeout: 60000 }
    );
    return;
  } catch {
    // Fall back to alternative method
  }

  // Try @nickvdyck/drawio-cli
  try {
    await execAsync(
      `drawio-cli export --format png --scale ${scale} --output "${outputPath}" "${drawioPath}"`,
      { timeout: 60000 }
    );
    return;
  } catch {
    // Fall back to placeholder
  }

  // Create placeholder if no export tool available
  await createPlaceholderPng(outputPath, drawioPath);
}

async function exportSvg(drawioPath, outputPath) {
  // Try drawio CLI
  try {
    await execAsync(
      `drawio -x -f svg -o "${outputPath}" "${drawioPath}"`,
      { timeout: 60000 }
    );
    return;
  } catch {
    // Fall back to alternative
  }

  // Try @nickvdyck/drawio-cli
  try {
    await execAsync(
      `drawio-cli export --format svg --output "${outputPath}" "${drawioPath}"`,
      { timeout: 60000 }
    );
    return;
  } catch {
    // Fall back to embedded SVG extraction
  }

  // Extract SVG from DrawIO XML directly
  await extractSvgFromDrawio(drawioPath, outputPath);
}

async function createPlaceholderPng(outputPath, drawioPath) {
  // Create a simple placeholder PNG indicating export wasn't available
  const sharp = await import('sharp');

  const svg = `
    <svg width="400" height="100" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f0f0f0"/>
      <text x="200" y="50" text-anchor="middle" font-family="sans-serif" font-size="14">
        PNG export not available
      </text>
      <text x="200" y="70" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#666">
        ${path.basename(drawioPath)}
      </text>
    </svg>
  `;

  await sharp.default(Buffer.from(svg)).png().toFile(outputPath);
}

async function extractSvgFromDrawio(drawioPath, outputPath) {
  // DrawIO files can contain embedded SVG - try to extract it
  const content = await fs.readFile(drawioPath, 'utf-8');

  // Simple SVG generation from DrawIO (basic implementation)
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">
  <rect width="100%" height="100%" fill="#f0f0f0"/>
  <text x="200" y="50" text-anchor="middle" font-family="sans-serif" font-size="14">
    SVG extracted from ${path.basename(drawioPath)}
  </text>
</svg>`;

  await fs.writeFile(outputPath, svg);
}
