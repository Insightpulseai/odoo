#!/usr/bin/env node
/**
 * Visio-DrawIO Export CLI
 *
 * Converts Visio diagrams to DrawIO format with PNG/SVG export
 */

import { Command } from 'commander';
import { glob } from 'glob';
import { parseVisio } from './parse.js';
import { convertToDrawio } from './convert.js';
import { exportImages } from './export.js';
import { validateDrawio } from './validate.js';
import { visualDiff } from './diff.js';
import fs from 'fs/promises';
import path from 'path';

const program = new Command();

program
  .name('visio-drawio-export')
  .description('Export Visio diagrams to DrawIO with PNG/SVG previews')
  .version('1.0.0');

program
  .option('-i, --input <path>', 'Input Visio file path')
  .option('-g, --input-glob <pattern>', 'Glob pattern for input files')
  .option('-o, --outdir <path>', 'Output directory', 'artifacts/diagrams')
  .option('-f, --formats <formats>', 'Output formats (comma-separated)', 'drawio,png,svg')
  .option('-v, --validate <level>', 'Validation level (none, basic, strict)', 'basic')
  .option('--min-shapes <count>', 'Minimum shape count for validation', '0')
  .option('--scale <factor>', 'PNG export scale factor', '2.0')
  .option('--diff', 'Run visual regression comparison')
  .option('--baseline <path>', 'Baseline directory for visual diff')
  .option('--current <path>', 'Current directory for visual diff', 'artifacts/diagrams')
  .option('--diff-threshold <value>', 'Diff threshold (0-1)', '0.003')
  .option('--json', 'Output results as JSON')
  .action(async (options) => {
    try {
      const results = {
        success: true,
        files: [],
        errors: [],
        warnings: [],
      };

      // Visual diff mode
      if (options.diff) {
        if (!options.baseline) {
          throw new Error('--baseline is required for visual diff');
        }
        const diffResult = await runVisualDiff(options);
        results.diff = diffResult;
        results.success = diffResult.passed;
      } else {
        // Export mode
        const inputFiles = await getInputFiles(options);

        if (inputFiles.length === 0) {
          throw new Error('No input files found');
        }

        // Ensure output directory exists
        await fs.mkdir(options.outdir, { recursive: true });

        const formats = options.formats.split(',').map((f) => f.trim());

        for (const inputFile of inputFiles) {
          try {
            const fileResult = await processFile(inputFile, options.outdir, formats, options);
            results.files.push(fileResult);

            if (fileResult.errors?.length) {
              results.errors.push(...fileResult.errors);
            }
            if (fileResult.warnings?.length) {
              results.warnings.push(...fileResult.warnings);
            }
          } catch (err) {
            results.errors.push({
              file: inputFile,
              error: err.message,
            });
            results.success = false;
          }
        }
      }

      // Output results
      if (options.json) {
        console.log(JSON.stringify(results, null, 2));
      } else {
        printResults(results);
      }

      process.exit(results.success ? 0 : 1);
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  });

async function getInputFiles(options) {
  if (options.input) {
    return [options.input];
  }
  if (options.inputGlob) {
    return await glob(options.inputGlob, { nodir: true });
  }
  return [];
}

async function processFile(inputFile, outdir, formats, options) {
  const result = {
    input: inputFile,
    outputs: [],
    errors: [],
    warnings: [],
  };

  const baseName = path.basename(inputFile, path.extname(inputFile));
  const ext = path.extname(inputFile).toLowerCase();

  let drawioContent;

  // Parse input
  if (ext === '.vsdx' || ext === '.vsd') {
    // Parse Visio and convert to DrawIO
    console.log(`Parsing Visio: ${inputFile}`);
    const visioData = await parseVisio(inputFile);
    drawioContent = await convertToDrawio(visioData);
  } else if (ext === '.drawio') {
    // Already DrawIO, just read it
    drawioContent = await fs.readFile(inputFile, 'utf-8');
  } else {
    throw new Error(`Unsupported input format: ${ext}`);
  }

  // Save DrawIO if requested
  if (formats.includes('drawio')) {
    const drawioPath = path.join(outdir, `${baseName}.drawio`);
    await fs.writeFile(drawioPath, drawioContent);
    result.outputs.push({ format: 'drawio', path: drawioPath });
    console.log(`Saved: ${drawioPath}`);
  }

  // Validate if requested
  if (options.validate !== 'none') {
    const validation = await validateDrawio(drawioContent, {
      strict: options.validate === 'strict',
      minShapes: parseInt(options.minShapes, 10),
    });

    result.validation = validation;

    if (!validation.valid) {
      result.errors.push(...validation.errors);
    }
    result.warnings.push(...validation.warnings);
  }

  // Export images
  const tempDrawio = path.join(outdir, `${baseName}.drawio`);
  if (!formats.includes('drawio')) {
    await fs.writeFile(tempDrawio, drawioContent);
  }

  if (formats.includes('png') || formats.includes('svg')) {
    const imageOutputs = await exportImages(tempDrawio, outdir, {
      formats: formats.filter((f) => f === 'png' || f === 'svg'),
      scale: parseFloat(options.scale),
    });
    result.outputs.push(...imageOutputs);
  }

  // Clean up temp file if not keeping drawio
  if (!formats.includes('drawio')) {
    await fs.unlink(tempDrawio);
  }

  return result;
}

async function runVisualDiff(options) {
  console.log('Running visual regression...');

  const baselineFiles = await glob('**/*.png', { cwd: options.baseline, nodir: true });
  const threshold = parseFloat(options.diffThreshold);

  const results = {
    passed: true,
    comparisons: [],
    threshold,
  };

  for (const file of baselineFiles) {
    const baselinePath = path.join(options.baseline, file);
    const currentPath = path.join(options.current, file);

    try {
      const diff = await visualDiff(baselinePath, currentPath, { threshold });
      results.comparisons.push({
        file,
        ...diff,
      });

      if (!diff.match) {
        results.passed = false;
        console.log(`FAIL: ${file} (${(diff.diffPercentage * 100).toFixed(3)}% different)`);
      } else {
        console.log(`PASS: ${file}`);
      }
    } catch (err) {
      results.comparisons.push({
        file,
        error: err.message,
        match: false,
      });
      results.passed = false;
      console.log(`ERROR: ${file} - ${err.message}`);
    }
  }

  return results;
}

function printResults(results) {
  console.log('\n=== Export Results ===\n');

  if (results.files) {
    for (const file of results.files) {
      console.log(`Input: ${file.input}`);
      for (const output of file.outputs) {
        console.log(`  -> ${output.format}: ${output.path}`);
      }
      if (file.validation) {
        console.log(`  Validation: ${file.validation.valid ? 'PASSED' : 'FAILED'}`);
        console.log(`    Shapes: ${file.validation.shapeCount}, Connectors: ${file.validation.connectorCount}`);
      }
    }
  }

  if (results.diff) {
    console.log(`\nVisual Regression: ${results.diff.passed ? 'PASSED' : 'FAILED'}`);
    console.log(`Threshold: ${(results.diff.threshold * 100).toFixed(3)}%`);
  }

  if (results.errors.length > 0) {
    console.log('\nErrors:');
    for (const err of results.errors) {
      console.log(`  - ${err.file || 'general'}: ${err.error || err}`);
    }
  }

  if (results.warnings.length > 0) {
    console.log('\nWarnings:');
    for (const warn of results.warnings) {
      console.log(`  - ${warn}`);
    }
  }

  console.log(`\nStatus: ${results.success ? 'SUCCESS' : 'FAILURE'}`);
}

program.parse();
