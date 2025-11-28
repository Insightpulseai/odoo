====================
IPAI Finance PPM
====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Production-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-jgtolentino%2Fodoo--ce-lightgray.png?logo=github
    :target: https://github.com/jgtolentino/odoo-ce/tree/main/addons/ipai_finance_ppm
    :alt: jgtolentino/odoo-ce

|badge1| |badge2| |badge3|

Finance Project Portfolio Management module providing Notion-like task tracking
and BIR compliance scheduling for Philippine businesses.

**Table of contents**

.. contents::
   :local:

Features
========

* **Directory Management**: Track finance team members, roles, and responsibilities
* **Monthly Task Templates**: Recurring monthly close tasks with status tracking
* **BIR Compliance Calendar**: Philippine tax filing deadlines and reminders
* **PPM Dashboard**: Visual overview of project portfolio status
* **Revenue Insights Search**: Natural language semantic search over monthly revenue data

Configuration
=============

1. Navigate to Finance PPM > Directory to set up team members
2. Configure monthly task templates under Finance PPM > Monthly Tasks
3. Import BIR schedule data for compliance tracking
4. Access the Revenue Insights search from the main menu

Usage
=====

Monthly Close Workflow
----------------------

1. At month start, tasks are automatically generated from templates
2. Assign tasks to team members via the Directory
3. Track progress on the PPM Dashboard
4. Mark tasks complete as they're finished

Revenue Insights Search
-----------------------

The semantic search feature allows natural language queries over revenue data:

* "Months with highest revenue growth"
* "Revenue dips in Q3"
* "Best performing months last year"

This feature requires the Supabase semantic query layer to be configured.

Technical Details
=================

Dependencies
------------

* ``base``: Odoo core
* ``mail``: Messaging and activity tracking
* ``project``: Project management features

External Services
-----------------

* **Supabase**: Vector embeddings for semantic search (optional)
* **OpenAI**: Text embeddings via ``text-embedding-3-small`` (optional)

Database Tables
---------------

* ``finance.person``: Team member directory
* ``finance.task.template``: Monthly task templates
* ``finance.task``: Task instances
* ``bir.form.schedule``: BIR compliance calendar

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/jgtolentino/odoo-ce/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
-------

* InsightPulseAI

Contributors
------------

* Jake Tolentino <jake@insightpulseai.net>

Maintainers
-----------

This module is maintained by InsightPulseAI.

.. image:: https://insightpulseai.net/logo.png
   :alt: InsightPulseAI
   :target: https://insightpulseai.net

Current maintainer:

* Jake Tolentino

This module is part of the `jgtolentino/odoo-ce <https://github.com/jgtolentino/odoo-ce/tree/main/addons/ipai_finance_ppm>`_ project on GitHub.
