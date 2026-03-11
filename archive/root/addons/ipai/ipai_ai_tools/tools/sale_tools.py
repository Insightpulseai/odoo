# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

"""Sale tools for AI agents.

These functions are called by the AI Agent tool executor.
"""

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def create_order(env, input_data, dry_run=False):
    """Create a new sale order.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - partner_id: Customer ID (required if partner_name not provided)
            - partner_name: Customer name (for lookup if ID not provided)
            - lines (required): List of order lines, each with:
                - product_id: Product ID (required if product_name not provided)
                - product_name: Product name (for lookup)
                - quantity: Quantity (default 1)
                - price_unit: Unit price (optional, uses product price if not set)
            - note: Order note
            - date_order: Order date
        dry_run: If True, validate but don't create

    Returns:
        dict with order_id, name, and message
    """
    SaleOrder = env["sale.order"]
    Partner = env["res.partner"]
    Product = env["product.product"]

    # Get partner
    partner_id = input_data.get("partner_id")
    if not partner_id and input_data.get("partner_name"):
        partner = Partner.search([("name", "ilike", input_data["partner_name"])], limit=1)
        if not partner:
            raise ValidationError(f"Customer not found: {input_data['partner_name']}")
        partner_id = partner.id

    if not partner_id:
        raise ValidationError("partner_id or partner_name is required.")

    partner = Partner.browse(partner_id)
    if not partner.exists():
        raise ValidationError(f"Partner {partner_id} not found.")

    # Validate lines
    lines = input_data.get("lines", [])
    if not lines:
        raise ValidationError("At least one order line is required.")

    # Prepare order lines
    order_lines = []
    for line in lines:
        product_id = line.get("product_id")
        if not product_id and line.get("product_name"):
            product = Product.search([("name", "ilike", line["product_name"])], limit=1)
            if not product:
                raise ValidationError(f"Product not found: {line['product_name']}")
            product_id = product.id

        if not product_id:
            raise ValidationError("Each line requires product_id or product_name.")

        product = Product.browse(product_id)
        if not product.exists():
            raise ValidationError(f"Product {product_id} not found.")

        quantity = line.get("quantity", 1)
        line_values = {
            "product_id": product_id,
            "product_uom_qty": quantity,
            "name": product.display_name,
        }

        if line.get("price_unit") is not None:
            line_values["price_unit"] = line["price_unit"]

        order_lines.append((0, 0, line_values))

    # Prepare order values
    values = {
        "partner_id": partner_id,
        "order_line": order_lines,
    }

    if input_data.get("note"):
        values["note"] = input_data["note"]
    if input_data.get("date_order"):
        values["date_order"] = input_data["date_order"]

    if dry_run:
        _logger.info(f"[DRY RUN] Would create sale order: {values}")
        return {
            "dry_run": True,
            "would_create": {
                "partner": partner.name,
                "line_count": len(order_lines),
            },
            "message": f"Would create sale order for: {partner.name}",
        }

    # Create the order
    order = SaleOrder.create(values)
    _logger.info(f"Created sale order {order.id}: {order.name}")

    return {
        "order_id": order.id,
        "name": order.name,
        "partner": order.partner_id.name,
        "amount_total": order.amount_total,
        "message": f"Successfully created sale order: {order.name}",
    }


def update_order(env, input_data, dry_run=False):
    """Update an existing sale order.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - order_id (required): ID of order to update
            - note: Updated note
            - add_lines: New lines to add
        dry_run: If True, validate but don't update

    Returns:
        dict with order_id and message
    """
    SaleOrder = env["sale.order"]
    Product = env["product.product"]

    order_id = input_data.get("order_id")
    if not order_id:
        raise ValidationError("order_id is required.")

    order = SaleOrder.browse(order_id)
    if not order.exists():
        raise ValidationError(f"Sale order {order_id} not found.")

    if order.state not in ("draft", "sent"):
        raise ValidationError(f"Cannot modify order in state: {order.state}")

    values = {}
    if input_data.get("note"):
        values["note"] = input_data["note"]

    # Handle adding new lines
    new_lines = []
    for line in input_data.get("add_lines", []):
        product_id = line.get("product_id")
        if not product_id and line.get("product_name"):
            product = Product.search([("name", "ilike", line["product_name"])], limit=1)
            if not product:
                raise ValidationError(f"Product not found: {line['product_name']}")
            product_id = product.id

        if product_id:
            product = Product.browse(product_id)
            quantity = line.get("quantity", 1)
            line_values = {
                "product_id": product_id,
                "product_uom_qty": quantity,
                "name": product.display_name,
            }
            if line.get("price_unit") is not None:
                line_values["price_unit"] = line["price_unit"]
            new_lines.append((0, 0, line_values))

    if new_lines:
        values["order_line"] = new_lines

    if not values:
        return {
            "order_id": order_id,
            "message": "No fields to update.",
        }

    if dry_run:
        _logger.info(f"[DRY RUN] Would update order {order_id}: {values}")
        return {
            "dry_run": True,
            "order_id": order_id,
            "would_add_lines": len(new_lines),
            "message": f"Would update order {order_id}",
        }

    order.write(values)
    _logger.info(f"Updated sale order {order_id}")

    return {
        "order_id": order_id,
        "name": order.name,
        "amount_total": order.amount_total,
        "message": f"Successfully updated order: {order.name}",
    }


def search_orders(env, input_data, dry_run=False):
    """Search for sale orders.

    Args:
        env: Odoo environment
        input_data: dict with keys:
            - query: Search query (searches name, partner name)
            - partner_id: Filter by customer
            - state: Filter by state (draft, sent, sale, done, cancel)
            - limit: Maximum results (default 10)
        dry_run: Ignored for search operations

    Returns:
        dict with orders list
    """
    SaleOrder = env["sale.order"]

    domain = []
    query = input_data.get("query", "")
    if query:
        domain = [
            "|",
            ("name", "ilike", query),
            ("partner_id.name", "ilike", query),
        ]

    if input_data.get("partner_id"):
        domain.append(("partner_id", "=", input_data["partner_id"]))
    if input_data.get("state"):
        domain.append(("state", "=", input_data["state"]))

    limit = min(input_data.get("limit", 10), 50)
    orders = SaleOrder.search(domain, limit=limit, order="date_order desc")

    return {
        "count": len(orders),
        "orders": [
            {
                "id": order.id,
                "name": order.name,
                "partner": order.partner_id.name,
                "state": order.state,
                "amount_total": order.amount_total,
                "date_order": str(order.date_order) if order.date_order else None,
            }
            for order in orders
        ],
    }
