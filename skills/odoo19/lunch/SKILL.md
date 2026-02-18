---
name: lunch
description: "Employee lunch ordering system with vendor management, product catalog, alerts, and account balances."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Lunch — Odoo 19.0 Skill Reference

## Overview

The **Lunch** app provides an internal meal ordering system. Employees browse available food products from configured vendors, place orders, and pay from a pre-funded lunch account. Managers configure vendors, products, locations, alerts, and manage order fulfillment. The app supports multiple locations, future-date ordering, product extras, and account overdraft limits.

## Key Concepts

- **Vendor** — A food supplier with availability schedule (days of week, operating hours, order cutoff time), delivery location, and email for order transmission.
- **Product** — A food item from a vendor, with name, price, description, category, and optional "New" tag. Displayed on the Order Your Lunch dashboard.
- **Product Category** — Grouping for products (e.g., Pizza, Salad, Drinks). Used for filtering.
- **Extras** — Additional options for a product (toppings, sides, drinks). Can be required or optional per vendor.
- **Location** — A delivery site (e.g., HQ Office). Default: HQ Office. Must match where the employee wants food delivered.
- **Alert** — Notification displayed in-app or sent via Discuss chat. Configurable per day-of-week, location, and recipient group.
- **Lunch Account** — Per-employee balance. Funded by administrators. Products are debited on order. Overdraft up to a configurable limit.
- **Overdraft Limit** — Maximum negative balance allowed (set in Settings).
- **Reception Notification** — Discuss message sent when food arrives (default: "Your lunch has been delivered. Enjoy your meal!").
- **Order Status** — To Order → Ordered → Sent → Received (or Cancelled).

## Core Workflows

### 1. Initial Setup

1. Navigate to `Lunch → Configuration → Settings`.
2. Set **Lunch Overdraft** maximum amount.
3. Set **Reception Notification** message text.
4. Configure **Locations**: `Lunch → Configuration → Locations`. Add addresses for each delivery site.

### 2. Configure Vendors and Products

1. Navigate to `Lunch → Configuration → Vendors`, click **New**.
2. Enter vendor name, phone, email, address, and availability (days, hours, order cutoff).
3. Navigate to `Lunch → Configuration → Products`, click **New**.
4. Enter Product name, vendor, category, price, description, and photo.
5. Configure extras per vendor if needed.

### 3. Set Up Alerts

1. Navigate to `Lunch → Configuration → Alerts`, click **New**.
2. Enter Alert Name, Display type (Alert in app / Chat notification).
3. For chat: select Recipients (Everyone / ordered last week/month/year).
4. Set Location(s), Show Until date, Notification Time (days, time).
5. Enter the alert Message.

### 4. Place a Lunch Order (Employee)

1. Open `Lunch` app (or `Lunch → My Lunch → New Order`).
2. Verify Location and Date on the right panel.
3. Browse products (filter by Category or Vendor).
4. Click a product → Configure Your Order popup: select Extras, add Notes (allergies, special requests).
5. Click **Add To Cart**. Repeat for additional items.
6. Review **Your Order** summary on the right panel (adjust quantities with +/- buttons).
7. Click **Order Now** to submit. Balance is debited.

### 5. Manage Orders (Administrator)

1. Navigate to `Lunch → Management → Today's Orders`.
2. Review orders. Send orders to vendors.
3. When food arrives, click **Confirm** to mark as Received — triggers reception notification to employees.

### 6. Manage Employee Accounts

1. Navigate to `Lunch → Management → Cash Moves` to add funds to employee accounts.
2. View account summaries per employee.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `lunch.order` | Individual lunch order line |
| `lunch.product` | Food product |
| `lunch.product.category` | Product category |
| `lunch.supplier` | Vendor/supplier |
| `lunch.location` | Delivery location |
| `lunch.alert` | Alert/notification |
| `lunch.cashmove` | Account transaction (credit/debit) |
| `lunch.topping` | Extra/topping option |

### Key Fields

- `lunch.order`: `product_id`, `user_id`, `date`, `state` (new/confirmed/ordered/sent/received/cancelled), `price`, `topping_ids_1/2/3`, `note`, `lunch_location_id`
- `lunch.product`: `name`, `supplier_id`, `category_id`, `price`, `description`, `new_until`
- `lunch.supplier`: `name`, `phone`, `email`, `available_location_ids`, `send_by` (email), `automatic_email_time`
- `lunch.alert`: `name`, `display` (alert/chat), `location_ids`, `until`, `message`, `notification_time`, `notification_moment`

### Important Menu Paths

- `Lunch` — Order Your Lunch dashboard
- `Lunch → My Lunch → New Order`
- `Lunch → My Lunch → My Order History`
- `Lunch → My Lunch → My Account History`
- `Lunch → Management → Today's Orders`
- `Lunch → Management → Cash Moves`
- `Lunch → Configuration → Settings`
- `Lunch → Configuration → Vendors`
- `Lunch → Configuration → Products`
- `Lunch → Configuration → Product Categories`
- `Lunch → Configuration → Locations`
- `Lunch → Configuration → Alerts`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Future-date ordering allows employees to schedule meals for upcoming days.
- Translation support for multilingual databases on settings and forms.
- Vendor availability includes both operating hours and order email cutoff time.
- Reception notification uses Discuss app for real-time delivery alerts.

## Common Pitfalls

- **Insufficient funds block orders.** The Add To Cart button is hidden if the product price exceeds the user's available balance. Contact a lunch manager to add funds.
- **Vendor order cutoff.** If the order window has closed for a vendor, products display "The orders for this vendor have already been sent." Users must choose another vendor.
- **Location must be set correctly.** The location determines which vendors/products are available. All locations are visible to all users regardless of their work location.
- **Required Extras cause validation errors.** If a vendor has mandatory extras (e.g., "choose a free beverage"), users must select one or the order fails with a Validation Error.
- **Cancelled orders can be reset.** The Reset button on cancelled orders changes status back to Ordered, but funds are re-debited from the account.
