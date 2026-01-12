After installing the module:

1. Navigate to **Platform > Tenants**
2. Review seed tenants:

   * **platform** → Internal operations (odoo_platform, public schema)
   * **tbwa** → TBWA Philippines (odoo_tbwa, tbwa schema)
   * **scout** → Scout Retail Intelligence (odoo_platform, scout schema)

3. Create additional tenants as needed

Environment Variables
=====================

Required for automated provisioning:

.. code-block:: bash

    # Supabase Connection
    export POSTGRES_URL='postgres://postgres.spdtwktxdalcfigzeqrz:PASSWORD@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require'
    export SUPABASE_SERVICE_ROLE_KEY='eyJ...'

    # Odoo Configuration
    export ODOO_ADMIN_PASSWORD='secure_password'
    export ODOO_URL='http://localhost:8069'  # Optional, defaults to localhost

    # GitHub Integration (for cross-repo CI)
    export GH_PAT_SUPERSET='ghp_...'  # Personal Access Token with repo scope
