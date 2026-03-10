#!/usr/bin/env python3
"""
Schema to Draw.io ERD Renderer

Converts schema.json to a native .drawio file that can be opened
in diagrams.net or VS Code Draw.io Integration extension.

Usage:
    export SCHEMA_JSON=docs/data_model/schema.json
    export OUT_DRAWIO=docs/data_model/erd.drawio
    python3 tools/odoo_schema/schema_to_drawio.py

Output:
    docs/data_model/erd.drawio
"""
import json
import os
import sys
import html
from collections import defaultdict


def esc(s: str) -> str:
    """HTML escape for XML attributes."""
    return html.escape(s, quote=True)


def mx_cell(
    id_,
    value="",
    style="",
    parent="1",
    vertex=False,
    edge=False,
    source=None,
    target=None,
    x=0,
    y=0,
    w=160,
    h=80,
):
    """Generate an mxCell XML element."""
    parts = [f'<mxCell id="{id_}"']
    if value != "":
        parts.append(f' value="{esc(value)}"')
    if style != "":
        parts.append(f' style="{esc(style)}"')
    if parent is not None:
        parts.append(f' parent="{parent}"')
    if vertex:
        parts.append(' vertex="1"')
    if edge:
        parts.append(' edge="1"')
    if source:
        parts.append(f' source="{source}"')
    if target:
        parts.append(f' target="{target}"')
    parts.append(">")
    if vertex or edge:
        parts.append(
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry">'
        )
        if edge:
            parts.append('<mxPoint x="0" y="0" as="sourcePoint"/>')
            parts.append('<mxPoint x="0" y="0" as="targetPoint"/>')
        parts.append("</mxGeometry>")
    parts.append("</mxCell>")
    return "".join(parts)


def render_drawio():
    """Main render function."""
    schema_path = os.environ.get("SCHEMA_JSON", "docs/data_model/schema.json")
    out_path = os.environ.get("OUT_DRAWIO", "docs/data_model/erd.drawio")
    anchors = set(
        os.environ.get(
            "ANCHORS",
            "res.partner,res.users,res.company,crm.lead,sale.order,"
            "purchase.order,stock.picking,account.move,project.task,"
            "account.analytic.account,account.analytic.line",
        ).split(",")
    )

    if not os.path.exists(schema_path):
        print(f"Schema file not found: {schema_path}")
        print("Run export_schema.py first.")
        return 1

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # Keep only anchor models + any directly connected to anchors (1 hop)
    edges = schema.get("edges", [])
    neighbors = defaultdict(set)
    for e in edges:
        neighbors[e["from"]].add(e["to"])
        neighbors[e["to"]].add(e["from"])

    nodes = set(anchors)
    for a in list(anchors):
        for b in neighbors.get(a, []):
            nodes.add(b)

    # Build node boxes content (top N fields)
    model_map = {m["model"]: m for m in schema.get("models", [])}
    nodes = [n for n in nodes if n in model_map]
    nodes.sort()

    # Layout grid
    cols = 4
    gapx, gapy = 40, 40
    boxw, boxh = 280, 180

    def pos(i):
        r = i // cols
        c = i % cols
        x = 40 + c * (boxw + gapx)
        y = 40 + r * (boxh + gapy)
        return x, y

    # drawio document
    cells = []
    cells.append(
        '<mxGraphModel dx="1200" dy="1200" grid="1" gridSize="10" guides="1" '
        'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        'pageWidth="1654" pageHeight="1169" math="0" shadow="0">'
    )
    cells.append("<root>")
    cells.append('<mxCell id="0"/>')
    cells.append('<mxCell id="1" parent="0"/>')

    node_id = {}
    next_id = 2

    # Node style (entity box)
    style_box = (
        "rounded=1;whiteSpace=wrap;html=1;align=left;spacingLeft=10;"
        "spacingTop=8;strokeWidth=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    )

    for i, mname in enumerate(nodes):
        mid = str(next_id)
        next_id += 1
        node_id[mname] = mid
        m = model_map[mname]
        fields = m.get("fields", [])
        top = []
        for fld in fields:
            t = fld.get("type")
            nm = fld.get("field")
            rel = fld.get("relation")
            if t in ("many2one", "one2many", "many2many") and rel:
                top.append(f"<b>{nm}</b>: {t} → {rel}")
            else:
                top.append(f"{nm}: {t}")
            if len(top) >= 12:
                break
        label = f"<b>{mname}</b><hr/>" + "<br/>".join(top)
        x, y = pos(i)
        cells.append(
            mx_cell(
                mid, label, style_box, parent="1", vertex=True, x=x, y=y, w=boxw, h=boxh
            )
        )

    # Edge style (relationship arrow)
    style_edge = (
        "endArrow=block;html=1;rounded=1;strokeWidth=1;"
        "strokeColor=#82b366;fontColor=#82b366;"
    )

    for e in edges:
        a, b = e["from"], e["to"]
        if a in node_id and b in node_id:
            eid = str(next_id)
            next_id += 1
            lbl = f"{e.get('field')} ({e.get('rel')})"
            cells.append(
                mx_cell(
                    eid,
                    lbl,
                    style_edge,
                    parent="1",
                    edge=True,
                    source=node_id[a],
                    target=node_id[b],
                    x=0,
                    y=0,
                    w=0,
                    h=0,
                )
            )

    cells.append("</root>")
    cells.append("</mxGraphModel>")

    # Build final XML
    diagram_content = "".join(cells)

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net" modified="true" '
        'agent="odoo_schema_tools" version="20.8.16">\n'
        '  <diagram id="ERD" name="Odoo ERD">\n'
        f"    {diagram_content}\n"
        "  </diagram>\n"
        "</mxfile>\n"
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"Wrote: {out_path}")
    print(f"Open in diagrams.net or VS Code Draw.io Integration extension")
    return 0


if __name__ == "__main__":
    sys.exit(render_drawio())
