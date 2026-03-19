# -*- coding: utf-8 -*-
"""
IPAI ADE - Agentic Document Extraction Engine.

A config-driven, multi-step document extraction pipeline that runs:
classify -> extract -> validate -> correct -> re-check -> finalize

Uses YAML pipelines to define extraction flows per document type.
"""
from . import core
