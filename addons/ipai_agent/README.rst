IPAI Agent Orchestration
========================

This module provides the core integration points between Odoo CE and
the InsightPulse AI agent orchestration layer (IPAI).

Main features
-------------

* Registers IPAI agent metadata and configuration inside Odoo.
* Exposes hooks for task execution, logging, and monitoring.
* Designed to be extended by other IPAI ``ipai_*`` modules.

Configuration
-------------

* Install this module together with any dependent ``ipai_*`` modules.
* Configure the IPAI endpoint and credentials in the module settings if
  available.

Roadmap
-------

This README is intentionally minimal to satisfy OCA CI checks. It will
be extended as the agent orchestration features mature.
