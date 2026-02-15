# SKILL: drawio_diagramming

## Intent

Create and edit diagrams using the Draw.io / diagrams.net format (XML/mxGraphModel).

## Inputs

- **prompt:** Description of the diagram content (e.g., "ERD for Odoo Sales", "Flowchart of Approval Process").
- **title:** (Optional) Title of the diagram.
- **template:** (Optional) Starting template (default: blank).

## Preconditions

- The agent must be able to generate valid XML.
- `mxGraphModel` structure must be adhered to.

## Procedure

1.  **Analyze Request:** Understand the nodes, edges, and layout required.
2.  **Generate XML:** Construct the `<mxGraphModel>` payload within a standard Draw.io XML envelope.
    - Use `<mxGeometry>` for positioning.
    - Use `<mxCell>` for nodes and edges.
    - Assign unique IDs to every cell.
    - **Advanced:** Use `style` attributes to define shape types (e.g., `shape=umlActor`, `shape=cylinder3`).
3.  **Save File:** Write the XML to `docs/evidence/<YYYY-MM-DD>/drawio/<title>.drawio`.
4.  **Generate Link:** Construct a viewer URL.
    - Base: `https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1`
    - **Refinement:** Append `&ui=min` for cleaner embedded view, or `&lightbox=1` for focus.
    - Append `#R<URL_ENCODED_XML>` (or compressed).
    - _Note:_ Since URL encoding large XML is inefficient, refer the user to the local file for complex diagrams.
5.  **Output:** Return the file path and the viewer link.

## Advanced Patterns

- **ERD:** Use `shape=swimlane` for tables and `endArrow=ER*` for relationships.
- **BPMN:** Use the `bpmn` shape library styles.
- **Mockups:** Use `mockup` container shapes for UI design.

## Evidence Outputs

- `*.drawio` file (the diagram source).

## Escalation

- If XML syntax is invalid, retry generation.
- If layout is too complex, simplify to a basic graph or suggest using a dedicated layout tool first.
