---
description: Create deterministic database seed scripts for development and testing
---

# Database Seeding Workflow

## Goal

Create a deterministic seed script for dev/test environments with realistic data and proper foreign key ordering.

## Steps

### 1. Analyze Schema

Identify tables, relationships, and constraints:

- Primary keys
- Foreign keys (dependency order)
- Unique constraints
- Required fields vs optional
- Data types and validation

**For Odoo**:

- Models and their dependencies
- `_sql_constraints`
- Required fields (`required=True`)
- Related fields (`many2one`, `one2many`, `many2many`)

### 2. Determine Insert Order

Respect foreign key dependencies:

```
1. Independent tables (no FK dependencies)
   - res.country
   - res.currency

2. First-level dependencies
   - res.partner (depends on country)
   - res.users (depends on partner)

3. Second-level dependencies
   - sale.order (depends on partner, user)
   - sale.order.line (depends on order, product)
```

### 3. Generate Realistic Records

Use faker library with **stable seed** for reproducibility:

```python
from faker import Faker
fake = Faker()
Faker.seed(12345)  # Deterministic data

# Generate users
users = []
for i in range(10):
    users.append({
        'name': fake.name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'created_at': fake.date_time_this_year()
    })
```

**Data quality**:

- Realistic names, emails, addresses
- Valid phone numbers, dates
- Proper relationships (orders belong to real users)
- Edge cases (empty strings, nulls where allowed)

### 4. Create Seed Script

**SQL Example**:

```sql
-- seed.sql
BEGIN;

-- Clear existing data (dev/test only!)
TRUNCATE users, orders, order_items CASCADE;

-- Reset sequences
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE orders_id_seq RESTART WITH 1;

-- Insert users
INSERT INTO users (name, email, phone, created_at) VALUES
('John Doe', 'john@example.com', '+1-555-0100', '2024-01-15 10:30:00'),
('Jane Smith', 'jane@example.com', '+1-555-0101', '2024-01-16 14:20:00'),
-- ... more users

-- Insert orders
INSERT INTO orders (user_id, total, status, created_at) VALUES
(1, 99.99, 'completed', '2024-02-01 09:15:00'),
(1, 149.50, 'pending', '2024-02-10 16:45:00'),
(2, 75.00, 'completed', '2024-02-05 11:30:00');
-- ... more orders

COMMIT;
```

**Python/ORM Example (Odoo)**:

```python
# seed_data.py
from odoo import api, SUPERUSER_ID

def seed_database(env):
    """Seed database with test data"""

    # Clear existing data (dev only!)
    env['sale.order'].search([]).unlink()
    env['res.partner'].search([('is_company', '=', False)]).unlink()

    # Create partners
    partners = []
    for i in range(10):
        partner = env['res.partner'].create({
            'name': f'Customer {i+1}',
            'email': f'customer{i+1}@example.com',
            'phone': f'+1-555-{i:04d}',
            'is_company': False,
        })
        partners.append(partner)

    # Create orders
    for partner in partners[:5]:
        env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': '2024-02-01',
            'order_line': [(0, 0, {
                'product_id': env.ref('product.product_product_1').id,
                'product_uom_qty': 2,
                'price_unit': 50.00,
            })],
        })

    env.cr.commit()
    print(f"Seeded {len(partners)} partners and 5 orders")

# Run with: odoo-bin shell -d mydb --no-http
# >>> from seed_data import seed_database
# >>> seed_database(env)
```

### 5. Create Reset Script (Optional)

```bash
#!/bin/bash
# reset_db.sh

set -euo pipefail

DB_NAME="myapp_dev"

echo "⚠️  This will DELETE ALL DATA in $DB_NAME"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted"
    exit 1
fi

# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Run migrations
python manage.py migrate

# Seed data
psql -U postgres -d $DB_NAME -f seed.sql

echo "✅ Database reset and seeded"
```

### 6. Provide Verification Queries

```sql
-- Verify row counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;

-- Verify foreign key integrity
SELECT o.id, o.user_id, u.name
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;
-- Should return 0 rows

-- Verify data quality
SELECT * FROM users WHERE email NOT LIKE '%@%';
-- Should return 0 rows
```

## Output Format

### Seed Script

- `seed.sql` or `seed_data.py`
- Deterministic (same data every run)
- Respects FK constraints
- Includes realistic data

### Reset Script (Optional)

- `reset_db.sh`
- Drops and recreates database
- Runs migrations
- Seeds data

### Verification Queries

- Row count checks
- FK integrity checks
- Data quality checks

### Usage Documentation

````markdown
## Database Seeding

### Quick Start

```bash
# SQL approach
psql -U postgres -d myapp_dev -f seed.sql

# Python/Odoo approach
odoo-bin shell -d mydb --no-http
>>> from seed_data import seed_database
>>> seed_database(env)
```
````

### Reset Database (Dev Only!)

```bash
./reset_db.sh
```

### Verify

```bash
psql -U postgres -d myapp_dev -f verify.sql
```

### Seed Data Summary

- 10 users
- 5 orders
- 15 order items
- All FK relationships valid
- Deterministic (Faker seed: 12345)

```

## Verification
- [ ] Seed script respects FK order
- [ ] Data is deterministic (same every run)
- [ ] Realistic data (not just "test1", "test2")
- [ ] Verification queries provided
- [ ] Usage documentation included
- [ ] Reset script (if applicable)
- [ ] Tested on clean database
```
