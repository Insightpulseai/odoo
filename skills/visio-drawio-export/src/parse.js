/**
 * Visio Parser
 *
 * Parses .vsdx files and extracts shapes, connections, and metadata
 */

import JSZip from 'jszip';
import { parseStringPromise } from 'xml2js';
import fs from 'fs/promises';

/**
 * Parse a Visio file and extract its structure
 * @param {string} filePath - Path to .vsdx file
 * @returns {Object} Parsed Visio data
 */
export async function parseVisio(filePath) {
  const data = await fs.readFile(filePath);
  const zip = await JSZip.loadAsync(data);

  const result = {
    pages: [],
    masters: [],
    styles: {},
    metadata: {},
  };

  // Parse document properties
  const docPropsFile = zip.file('docProps/core.xml');
  if (docPropsFile) {
    const docProps = await docPropsFile.async('string');
    result.metadata = await parseDocProps(docProps);
  }

  // Parse pages
  const pagesDir = zip.folder('visio/pages');
  if (pagesDir) {
    const pageFiles = Object.keys(zip.files).filter(
      (f) => f.startsWith('visio/pages/page') && f.endsWith('.xml')
    );

    for (const pageFile of pageFiles.sort()) {
      const pageContent = await zip.file(pageFile).async('string');
      const page = await parsePage(pageContent);
      result.pages.push(page);
    }
  }

  // Parse masters (stencils/shapes)
  const mastersFile = zip.file('visio/masters/masters.xml');
  if (mastersFile) {
    const mastersContent = await mastersFile.async('string');
    result.masters = await parseMasters(mastersContent);
  }

  // Parse styles
  const stylesFile = zip.file('visio/document.xml');
  if (stylesFile) {
    const stylesContent = await stylesFile.async('string');
    result.styles = await parseStyles(stylesContent);
  }

  return result;
}

async function parseDocProps(xml) {
  try {
    const parsed = await parseStringPromise(xml);
    const props = parsed['cp:coreProperties'] || {};
    return {
      title: props['dc:title']?.[0] || '',
      creator: props['dc:creator']?.[0] || '',
      created: props['dcterms:created']?.[0]?._ || '',
      modified: props['dcterms:modified']?.[0]?._ || '',
    };
  } catch {
    return {};
  }
}

async function parsePage(xml) {
  const parsed = await parseStringPromise(xml);
  const pageContents = parsed.PageContents || {};

  const page = {
    shapes: [],
    connects: [],
    layers: [],
  };

  // Extract shapes
  const shapes = pageContents.Shapes?.[0]?.Shape || [];
  for (const shape of shapes) {
    page.shapes.push(parseShape(shape));
  }

  // Extract connections
  const connects = pageContents.Connects?.[0]?.Connect || [];
  for (const connect of connects) {
    page.connects.push({
      fromSheet: connect.$.FromSheet,
      toSheet: connect.$.ToSheet,
      fromCell: connect.$.FromCell,
      toCell: connect.$.ToCell,
    });
  }

  return page;
}

function parseShape(shape) {
  const attrs = shape.$ || {};

  const result = {
    id: attrs.ID,
    name: attrs.Name || attrs.NameU || '',
    type: attrs.Type,
    master: attrs.Master,
    cells: {},
    text: '',
    subShapes: [],
  };

  // Parse cells (properties)
  const cells = shape.Cell || [];
  for (const cell of cells) {
    const name = cell.$.N;
    const value = cell.$.V;
    if (name && value !== undefined) {
      result.cells[name] = value;
    }
  }

  // Parse text
  if (shape.Text) {
    result.text = extractText(shape.Text[0]);
  }

  // Parse sub-shapes
  const subShapes = shape.Shapes?.[0]?.Shape || [];
  for (const subShape of subShapes) {
    result.subShapes.push(parseShape(subShape));
  }

  return result;
}

function extractText(textNode) {
  if (typeof textNode === 'string') {
    return textNode;
  }
  if (textNode._) {
    return textNode._;
  }
  if (textNode.cp) {
    return textNode.cp.map((cp) => cp._ || '').join('');
  }
  return '';
}

async function parseMasters(xml) {
  try {
    const parsed = await parseStringPromise(xml);
    const masters = parsed.Masters?.Master || [];

    return masters.map((master) => ({
      id: master.$.ID,
      name: master.$.Name || master.$.NameU,
      uniqueId: master.$.UniqueID,
    }));
  } catch {
    return [];
  }
}

async function parseStyles(xml) {
  try {
    const parsed = await parseStringPromise(xml);
    const styleSheets = parsed.VisioDocument?.StyleSheets?.[0]?.StyleSheet || [];

    const styles = {};
    for (const sheet of styleSheets) {
      const id = sheet.$.ID;
      const name = sheet.$.Name || sheet.$.NameU;
      styles[id] = { id, name };
    }
    return styles;
  } catch {
    return {};
  }
}
