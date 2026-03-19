/**
 * DrawIO Validator
 *
 * Validates DrawIO file structure and content
 */

import { parseStringPromise } from 'xml2js';

/**
 * Validate DrawIO content
 * @param {string} content - DrawIO XML content
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export async function validateDrawio(content, options = {}) {
  const { strict = false, minShapes = 0 } = options;

  const result = {
    valid: true,
    errors: [],
    warnings: [],
    shapeCount: 0,
    connectorCount: 0,
    pageCount: 0,
  };

  try {
    // Parse XML
    const parsed = await parseStringPromise(content);

    // Check root element
    if (!parsed.mxfile) {
      result.errors.push('Invalid DrawIO file: missing mxfile root element');
      result.valid = false;
      return result;
    }

    // Check diagrams
    const diagrams = parsed.mxfile.diagram || [];
    result.pageCount = diagrams.length;

    if (diagrams.length === 0) {
      result.errors.push('DrawIO file contains no diagrams');
      result.valid = false;
      return result;
    }

    // Analyze each diagram
    for (let i = 0; i < diagrams.length; i++) {
      const diagram = diagrams[i];
      const diagramResult = analyzeDiagram(diagram, i);

      result.shapeCount += diagramResult.shapes;
      result.connectorCount += diagramResult.connectors;
      result.warnings.push(...diagramResult.warnings);

      if (diagramResult.errors.length > 0) {
        result.errors.push(...diagramResult.errors);
        result.valid = false;
      }
    }

    // Check minimum shapes
    if (minShapes > 0 && result.shapeCount < minShapes) {
      const msg = `Diagram has ${result.shapeCount} shapes, minimum required is ${minShapes}`;
      if (strict) {
        result.errors.push(msg);
        result.valid = false;
      } else {
        result.warnings.push(msg);
      }
    }

    // Strict mode checks
    if (strict) {
      if (result.shapeCount === 0) {
        result.errors.push('Diagram is empty (no shapes)');
        result.valid = false;
      }

      if (result.shapeCount > 0 && result.connectorCount === 0) {
        result.warnings.push('Diagram has shapes but no connectors');
      }
    }
  } catch (err) {
    result.errors.push(`Failed to parse DrawIO XML: ${err.message}`);
    result.valid = false;
  }

  return result;
}

function analyzeDiagram(diagram, index) {
  const result = {
    shapes: 0,
    connectors: 0,
    errors: [],
    warnings: [],
  };

  try {
    // Diagrams can have content directly or compressed
    const mxGraphModel = diagram.mxGraphModel?.[0];

    if (!mxGraphModel) {
      // May be compressed - would need decompression
      result.warnings.push(`Diagram ${index + 1}: content may be compressed`);
      return result;
    }

    const root = mxGraphModel.root?.[0];
    if (!root) {
      result.errors.push(`Diagram ${index + 1}: missing root element`);
      return result;
    }

    const cells = root.mxCell || [];

    for (const cell of cells) {
      const attrs = cell.$ || {};

      // Skip root cells (id 0 and 1)
      if (attrs.id === '0' || attrs.id === '1') {
        continue;
      }

      if (attrs.edge === '1') {
        result.connectors++;

        // Validate edge has source/target
        if (!attrs.source || !attrs.target) {
          result.warnings.push(
            `Edge ${attrs.id} in diagram ${index + 1} missing source or target`
          );
        }
      } else if (attrs.vertex === '1') {
        result.shapes++;

        // Check for geometry
        const geometry = cell.mxGeometry;
        if (!geometry) {
          result.warnings.push(
            `Shape ${attrs.id} in diagram ${index + 1} missing geometry`
          );
        }
      }
    }
  } catch (err) {
    result.errors.push(`Failed to analyze diagram ${index + 1}: ${err.message}`);
  }

  return result;
}

/**
 * Validate DrawIO file from path
 * @param {string} filePath - Path to .drawio file
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export async function validateDrawioFile(filePath, options = {}) {
  const fs = await import('fs/promises');
  const content = await fs.readFile(filePath, 'utf-8');
  return validateDrawio(content, options);
}
