/**
 * Visual Diff
 *
 * Compares images for visual regression testing
 */

import pixelmatch from 'pixelmatch';
import { PNG } from 'pngjs';
import fs from 'fs/promises';
import path from 'path';

/**
 * Compare two images for visual differences
 * @param {string} baselinePath - Path to baseline image
 * @param {string} currentPath - Path to current image
 * @param {Object} options - Comparison options
 * @returns {Object} Diff result
 */
export async function visualDiff(baselinePath, currentPath, options = {}) {
  const { threshold = 0.003, outputPath = null } = options;

  // Check files exist
  try {
    await fs.access(baselinePath);
  } catch {
    throw new Error(`Baseline not found: ${baselinePath}`);
  }

  try {
    await fs.access(currentPath);
  } catch {
    throw new Error(`Current image not found: ${currentPath}`);
  }

  // Load images
  const baselineBuffer = await fs.readFile(baselinePath);
  const currentBuffer = await fs.readFile(currentPath);

  const baseline = PNG.sync.read(baselineBuffer);
  const current = PNG.sync.read(currentBuffer);

  // Check dimensions match
  if (baseline.width !== current.width || baseline.height !== current.height) {
    return {
      match: false,
      error: `Image dimensions differ: baseline ${baseline.width}x${baseline.height} vs current ${current.width}x${current.height}`,
      diffPercentage: 1.0,
      diffPixels: baseline.width * baseline.height,
    };
  }

  // Create diff image
  const { width, height } = baseline;
  const diff = new PNG({ width, height });

  // Compare pixels
  const numDiffPixels = pixelmatch(
    baseline.data,
    current.data,
    diff.data,
    width,
    height,
    {
      threshold: 0.1, // Per-pixel sensitivity
      includeAA: true, // Include anti-aliased pixels
    }
  );

  const totalPixels = width * height;
  const diffPercentage = numDiffPixels / totalPixels;
  const match = diffPercentage <= threshold;

  // Save diff image if requested
  if (outputPath && numDiffPixels > 0) {
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, PNG.sync.write(diff));
  }

  return {
    match,
    diffPercentage,
    diffPixels: numDiffPixels,
    totalPixels,
    threshold,
    dimensions: { width, height },
  };
}

/**
 * Run visual regression for all images in a directory
 * @param {string} baselineDir - Baseline directory
 * @param {string} currentDir - Current directory
 * @param {Object} options - Comparison options
 * @returns {Object} Results summary
 */
export async function visualDiffDirectory(baselineDir, currentDir, options = {}) {
  const { threshold = 0.003, diffDir = null, pattern = '**/*.png' } = options;

  const { glob } = await import('glob');
  const files = await glob(pattern, { cwd: baselineDir, nodir: true });

  const results = {
    passed: true,
    total: files.length,
    matched: 0,
    failed: 0,
    missing: 0,
    comparisons: [],
  };

  for (const file of files) {
    const baselinePath = path.join(baselineDir, file);
    const currentPath = path.join(currentDir, file);
    const diffPath = diffDir ? path.join(diffDir, file) : null;

    try {
      const diff = await visualDiff(baselinePath, currentPath, {
        threshold,
        outputPath: diffPath,
      });

      results.comparisons.push({
        file,
        ...diff,
      });

      if (diff.match) {
        results.matched++;
      } else {
        results.failed++;
        results.passed = false;
      }
    } catch (err) {
      results.comparisons.push({
        file,
        error: err.message,
        match: false,
      });

      if (err.message.includes('not found')) {
        results.missing++;
      } else {
        results.failed++;
      }
      results.passed = false;
    }
  }

  return results;
}
