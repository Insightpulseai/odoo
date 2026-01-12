Provision New Tenant
====================

**Via Command Line** (recommended):

.. code-block:: bash

    cd /path/to/odoo-ce
    export ODOO_ADMIN_PASSWORD='secure_password'
    export POSTGRES_URL='postgres://postgres.spdtwktxdalcfigzeqrz:...'
    make provision-tenant CODE=tbwa

**Via Odoo UI**:

1. Create tenant record: **Platform > Tenants > Create**
2. Set required fields:

   * Code: ``tbwa`` (lowercase alphanumeric)
   * DB Name: ``odoo_tbwa``
   * Supabase Schema: ``tbwa``
   * Primary Domain: ``tbwa.erp.insightpulseai.net``

3. Click **Provision Supabase Schema** button
4. Run provisioning script to complete setup

Access Tenant Data
==================

**In Odoo**:

* Access via domain: ``https://tbwa.erp.insightpulseai.net``
* Or filter: ``https://erp.insightpulseai.net?db=odoo_tbwa``

**In Superset**:

1. Click **Open Superset** button on tenant record
2. Access tenant-specific dashboards in workspace folder
