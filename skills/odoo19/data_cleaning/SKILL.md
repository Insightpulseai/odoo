---
name: data_cleaning
description: Data integrity tools for deduplication, record recycling, and field formatting standardization
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# data_cleaning -- Odoo 19.0 Skill Reference

## Overview

The Odoo Data Cleaning app maintains data integrity and consistency through three core features: deduplication (merge/remove duplicate records), recycling (archive/delete outdated records), and field cleaning (standardize text formatting). Customizable rules ensure data stays up-to-date, streamlined, and consistently formatted. The base Data Recycle module is available in Community edition; Data Cleaning and Data Merge require Enterprise.

## Key Concepts

- **Deduplication**: Finds similar/duplicate records based on configurable rules and merges them into a master record.
- **Recycle Records**: Identifies outdated records based on time-field criteria and archives or deletes them.
- **Field Cleaning**: Standardizes text data by trimming spaces, setting case, formatting phone numbers, or scrapping HTML.
- **Master Record**: The base record into which duplicates are merged. One master per grouping.
- **Similarity Rating**: Percentage score (0-100%) indicating how similar two records are.
- **Deduplication Rules**: Configuration defining which model fields to compare and how (Exact Match or Case/Accent Insensitive Match).
- **Recycle Record Rules**: Configuration defining which model, time field, delta, and action (archive/delete) to apply.
- **Field Cleaning Rules**: Configuration defining which model fields to clean and what action to apply.
- **Merge Mode**: Manual (user reviews each grouping) or Automatic (auto-merges above similarity threshold).
- **Cleaning Mode**: Manual (user validates each change) or Automatic (auto-applies formatting).
- **Merge Action Manager**: Enables/disables the Merge action in the Actions menu for specific models (requires Developer Mode).

## Core Workflows

1. **Deduplicate Records**
   1. Navigate to Data Cleaning > Deduplication.
   2. Select a rule in the RULE sidebar to filter duplicates.
   3. Review grouped records; set one as Master (Is Master checkbox).
   4. Click Merge to combine records, then Ok to confirm.
   5. Merge details logged in master record's chatter.

2. **Configure a Deduplication Rule**
   1. Go to Data Cleaning > Configuration > Deduplication.
   2. Click New or select an existing rule.
   3. Select Model, configure Domain filter.
   4. Set Duplicate Removal (Archive or Delete) and Merge Mode (Manual or Automatic).
   5. Add Deduplication Rules: select Unique ID Field and Match If condition (Exact Match or Case/Accent Insensitive Match).
   6. Enable Active toggle. Save.
   7. Optionally click Deduplicate to run immediately.

3. **Recycle Outdated Records**
   1. Navigate to Data Cleaning > Recycle Records.
   2. Select a rule in the RECYCLE RULES sidebar.
   3. Click Validate on records to recycle (archive/delete).

4. **Configure a Recycle Record Rule**
   1. Go to Data Cleaning > Configuration > Recycle Records, click New.
   2. Select Model, configure Filter.
   3. Set Time Field, Delta (number), Delta Unit (Days/Weeks/Months/Years).
   4. Set Recycle Mode (Manual or Automatic) and Recycle Action (Archive or Delete).
   5. Save. Optionally click Run Now to run immediately.

5. **Clean Field Formatting**
   1. Navigate to Data Cleaning > Field Cleaning.
   2. Select a rule in the CLEANING RULES sidebar.
   3. Review Current vs. Suggested values.
   4. Click Validate to apply formatting changes.

6. **Configure a Field Cleaning Rule**
   1. Go to Data Cleaning > Configuration > Field Cleaning, click New.
   2. Select Model.
   3. Add Rules: select Field To Clean and Action (Trim Spaces, Set Type Case, Format Phone, Scrap HTML).
   4. Set Cleaning Mode (Manual or Automatic). Save.
   5. Optionally click Clean to run immediately.

## Technical Reference

- **Modules**:
  - `data_recycle` (Community): Base recycle feature
  - `data_cleaning` (Enterprise): Field cleaning
  - `data_merge` (Enterprise): Deduplication/merge
  - App-specific: `data_merge_crm`, `data_merge_helpdesk`, `data_merge_project`, `data_merge_utm`, `data_merge_stock_account`
- **Key Models**: `data.merge.rule`, `data.merge.group`, `data.merge.record`, `data.recycle.rule`, `data.recycle.record`, `data.cleaning.rule`, `data.cleaning.record`
- **Deduplication Rule Fields**: `model_id`, `domain`, `duplicate_removal` (archive/delete), `merge_mode` (manual/automatic), `similarity_threshold`, `suggestion_threshold` (Developer Mode), `cross_company`, `active`
- **Recycle Rule Fields**: `model_id`, `filter_domain`, `time_field_id`, `delta`, `delta_unit`, `recycle_mode`, `recycle_action`, `include_archived`
- **Field Cleaning Actions**: Trim Spaces (All Spaces / Superfluous Spaces), Set Type Case (First Letters Uppercase / All Uppercase / All Lowercase), Format Phone (international format), Scrap HTML (to plain text)
- **Scheduled Actions (Crons)**:
  - `Data Merge: Find Duplicate Records` (daily)
  - `Data Recycle: Clean Records` (daily)
  - `Data Cleaning: Clean Records` (daily)
- **Merge Action Manager**: Data Cleaning > Configuration > Merge Action Manager (requires Developer Mode). Toggle `Can Be Merged` per model.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs -->

## Common Pitfalls

- At least one Deduplication Rule (Unique ID Field + Match If) must be set for duplicates to be detected.
- If no master record is selected during merge, Odoo picks one at random.
- Discarded groupings are archived, not deleted; they can be found via the Discarded filter.
- Phone formatting converts to international format based on the country of the contact; ensure country data is correct.
- The `data_merge_stock_account` module creates warnings when merging products that may affect inventory valuation.
