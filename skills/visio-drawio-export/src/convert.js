/**
 * DrawIO Converter
 *
 * Converts parsed Visio data to DrawIO XML format
 */

/**
 * Convert parsed Visio data to DrawIO XML
 * @param {Object} visioData - Parsed Visio data
 * @returns {string} DrawIO XML content
 */
export async function convertToDrawio(visioData) {
  const pages = visioData.pages || [];

  // Build mxGraphModel for each page
  const pageXml = pages
    .map((page, index) => convertPage(page, index))
    .join('\n');

  // Wrap in DrawIO format
  const drawio = `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="visio-drawio-export" modified="${new Date().toISOString()}" agent="visio-drawio-export/1.0.0" version="24.0.0" type="device">
${pageXml}
</mxfile>`;

  return drawio;
}

function convertPage(page, pageIndex) {
  const shapes = page.shapes || [];
  const connects = page.connects || [];

  // Convert shapes to mxCells
  let cellId = 2; // 0 and 1 are reserved for root and default parent
  const cells = [];
  const shapeIdMap = new Map(); // Map Visio shape IDs to mxCell IDs

  for (const shape of shapes) {
    const mxCell = convertShape(shape, cellId, shapeIdMap);
    cells.push(mxCell);
    shapeIdMap.set(shape.id, cellId);
    cellId++;

    // Handle sub-shapes
    for (const subShape of shape.subShapes || []) {
      const subMxCell = convertShape(subShape, cellId, shapeIdMap, shapeIdMap.get(shape.id));
      cells.push(subMxCell);
      shapeIdMap.set(subShape.id, cellId);
      cellId++;
    }
  }

  // Convert connections to edges
  for (const connect of connects) {
    const edge = convertConnect(connect, cellId, shapeIdMap);
    if (edge) {
      cells.push(edge);
      cellId++;
    }
  }

  return `  <diagram id="page-${pageIndex}" name="Page ${pageIndex + 1}">
    <mxGraphModel dx="1000" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
${cells.join('\n')}
      </root>
    </mxGraphModel>
  </diagram>`;
}

function convertShape(shape, cellId, shapeIdMap, parentId = 1) {
  const cells = shape.cells || {};

  // Extract geometry
  const x = parseFloat(cells.PinX || 0) * 72; // Convert inches to points
  const y = parseFloat(cells.PinY || 0) * 72;
  const width = parseFloat(cells.Width || 1) * 72;
  const height = parseFloat(cells.Height || 1) * 72;

  // Extract style
  const style = buildStyle(shape, cells);

  // Build mxCell
  const value = escapeXml(shape.text || shape.name || '');

  return `        <mxCell id="${cellId}" value="${value}" style="${style}" vertex="1" parent="${parentId}">
          <mxGeometry x="${Math.round(x)}" y="${Math.round(y)}" width="${Math.round(width)}" height="${Math.round(height)}" as="geometry"/>
        </mxCell>`;
}

function convertConnect(connect, cellId, shapeIdMap) {
  const sourceId = shapeIdMap.get(connect.fromSheet);
  const targetId = shapeIdMap.get(connect.toSheet);

  if (!sourceId || !targetId) {
    return null;
  }

  const style = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;';

  return `        <mxCell id="${cellId}" style="${style}" edge="1" parent="1" source="${sourceId}" target="${targetId}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>`;
}

function buildStyle(shape, cells) {
  const parts = ['rounded=0', 'whiteSpace=wrap', 'html=1'];

  // Fill color
  const fillColor = cells.FillForegnd;
  if (fillColor) {
    parts.push(`fillColor=${normalizeColor(fillColor)}`);
  }

  // Stroke color
  const lineColor = cells.LineColor;
  if (lineColor) {
    parts.push(`strokeColor=${normalizeColor(lineColor)}`);
  }

  // Line weight
  const lineWeight = cells.LineWeight;
  if (lineWeight) {
    parts.push(`strokeWidth=${Math.round(parseFloat(lineWeight) * 72)}`);
  }

  // Shape type
  const shapeType = determineShapeType(shape);
  if (shapeType) {
    parts.push(shapeType);
  }

  return parts.join(';') + ';';
}

function normalizeColor(color) {
  if (!color) return '#FFFFFF';

  // Handle Visio color formats
  if (color.startsWith('RGB(')) {
    const match = color.match(/RGB\((\d+),(\d+),(\d+)\)/);
    if (match) {
      const r = parseInt(match[1]).toString(16).padStart(2, '0');
      const g = parseInt(match[2]).toString(16).padStart(2, '0');
      const b = parseInt(match[3]).toString(16).padStart(2, '0');
      return `#${r}${g}${b}`;
    }
  }

  // Already hex
  if (color.startsWith('#')) {
    return color;
  }

  return '#FFFFFF';
}

function determineShapeType(shape) {
  const name = (shape.name || '').toLowerCase();

  if (name.includes('rectangle') || name.includes('box')) {
    return 'shape=mxgraph.basic.rect';
  }
  if (name.includes('ellipse') || name.includes('circle')) {
    return 'ellipse';
  }
  if (name.includes('diamond') || name.includes('decision')) {
    return 'rhombus';
  }
  if (name.includes('triangle')) {
    return 'triangle';
  }
  if (name.includes('cylinder') || name.includes('database')) {
    return 'shape=cylinder3';
  }

  return null;
}

function escapeXml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
