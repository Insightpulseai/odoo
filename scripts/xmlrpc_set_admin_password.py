#!/usr/bin/env python3
"""
XML-RPC utility to set Odoo admin password
Usage: python3 xmlrpc_set_admin_password.py <DATABASE> <NEW_PASSWORD>
"""

import sys
import xmlrpc.client
import os


def set_admin_password(db_name, new_password, url="http://localhost:8069"):
    """Set admin user password via XML-RPC"""

    try:
        # Connect to XML-RPC
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

        # Authenticate as superuser
        uid = common.authenticate(db_name, "admin", "admin", {})

        if not uid:
            print(f"❌ Failed to authenticate as admin (using default password)")
            print(f"ℹ️  This is normal for new databases - setting password directly")

            # For new databases, use SQL approach
            import subprocess

            postgres_url = os.environ.get("POSTGRES_URL")
            if not postgres_url:
                print("❌ POSTGRES_URL not set")
                return False

            # Hash password (bcrypt)
            try:
                import bcrypt

                password_hash = bcrypt.hashpw(
                    new_password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")

                # Update via SQL
                cmd = [
                    "psql",
                    postgres_url,
                    "-c",
                    f"UPDATE res_users SET password = '{password_hash}' WHERE login = 'admin' AND id = 2;",
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ Admin password set successfully via SQL")
                return True

            except ImportError:
                print("❌ bcrypt module not found - install with: pip install bcrypt")
                return False

        # If authentication succeeded, update password via XML-RPC
        models.execute_kw(
            db_name,
            uid,
            "admin",
            "res.users",
            "write",
            [[2], {"password": new_password}],  # User ID 2 is admin
        )

        print(f"✅ Admin password updated successfully for database '{db_name}'")
        return True

    except Exception as e:
        print(f"❌ Error setting admin password: {e}")
        return False


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 xmlrpc_set_admin_password.py <DATABASE> <NEW_PASSWORD>")
        sys.exit(1)

    db_name = sys.argv[1]
    new_password = sys.argv[2]

    odoo_url = os.environ.get("ODOO_URL", "http://localhost:8069")

    success = set_admin_password(db_name, new_password, odoo_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
