#!/usr/bin/env python3
"""
Finance Directory Import Script
Imports the finance team directory into Odoo
"""

import csv
import psycopg2
import sys

# Database connection configuration
DB_CONFIG = {
    'host': '159.223.75.148',
    'port': 5432,
    'database': 'odoo',
    'user': 'odoo',
    'password': 'CHANGE_ME_STRONG_DB_PASSWORD'  # Replace with actual password
}

def import_finance_directory():
    """Import finance directory from CSV into Odoo"""
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("📊 Importing Finance Directory...")
        
        # Read CSV file
        with open('finance_directory.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                code = row['code']
                name = row['name']
                email = row['email']
                
                print(f"Processing: {code} - {name} ({email})")
                
                # Check if employee already exists
                cursor.execute("""
                    SELECT id FROM hr_employee 
                    WHERE work_email = %s OR name = %s
                """, (email, name))
                
                existing = cursor.fetchone()
                
                if existing:
                    print(f"  ⚠️  Employee already exists: {name}")
                    continue
                
                # Create new employee
                cursor.execute("""
                    INSERT INTO hr_employee 
                    (name, work_email, employee_code, active, create_uid, create_date, write_uid, write_date)
                    VALUES (%s, %s, %s, true, 2, NOW(), 2, NOW())
                    RETURNING id
                """, (name, email, code))
                
                employee_id = cursor.fetchone()[0]
                
                # Create user account if email exists
                if email:
                    cursor.execute("""
                        INSERT INTO res_users 
                        (login, password, name, active, company_id, partner_id, create_uid, create_date, write_uid, write_date)
                        VALUES (%s, %s, %s, true, 1, %s, 2, NOW(), 2, NOW())
                        RETURNING id
                    """, (email, 'CHANGE_ME_PASSWORD', name, employee_id))
                    
                    user_id = cursor.fetchone()[0]
                    
                    # Link employee to user
                    cursor.execute("""
                        UPDATE hr_employee SET user_id = %s WHERE id = %s
                    """, (user_id, employee_id))
                
                print(f"  ✅ Created: {name} (ID: {employee_id})")
        
        # Commit changes
        conn.commit()
        print("✅ Finance directory import completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def verify_import():
    """Verify the imported data"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying imported data...")
        
        # Count imported employees
        cursor.execute("SELECT COUNT(*) FROM hr_employee WHERE employee_code IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"Total employees with codes: {count}")
        
        # List imported employees
        cursor.execute("""
            SELECT employee_code, name, work_email 
            FROM hr_employee 
            WHERE employee_code IS NOT NULL 
            ORDER BY employee_code
        """)
        
        print("\n📋 Imported Employees:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} - {row[2]}")
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Finance Directory Import Tool")
    print("=" * 40)
    
    import_finance_directory()
    verify_import()
    
    print("\n🎉 Import process completed!")
