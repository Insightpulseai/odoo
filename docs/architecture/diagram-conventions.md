# Diagram Conventions

## Purpose

Define the canonical diagram layering and source format for platform architecture.

## Source of truth

- store editable source diagrams as `.drawio`
- export deterministic PNG and/or SVG artifacts for docs
- keep overview, high-level, and low-level diagrams separate

## Diagram layers

### 1. Overview diagrams
Show:
- the six planes
- major truth planes
- major system boundaries
- major ingress and tenant boundaries

Do not show:
- every resource
- detailed networking
- CI/CD internals

### 2. High-level diagrams
Show:
- major Azure services
- resource groups and environments
- shared vs workload boundaries
- regional and HA/DR structure where relevant
- monitoring/backup/recovery placement

### 3. Low-level diagrams
Show:
- implementation detail
- CI/CD and release wiring
- exact service interactions
- identity and private networking detail
- runtime topology details

## Shape conventions

- use Azure shape libraries for Azure services
- use rectangles and grouping for region/environment boundaries
- use repeated substructures consistently
- separate shared/platform from workload/application areas visually

## Environment coloring

- shared/platform plane = neutral
- development = one consistent color
- staging = one consistent color
- production = one consistent color
- DR/secondary = one consistent color

## Export rules

- export PNG for quick docs embedding
- export SVG when scalability/editability is preferred
- keep filenames deterministic
- fail CI when exported artifact drifts from source, if/when diagram CI is enabled

## Required diagrams

- platform-overview.drawio
- target-platform-architecture.drawio
- tenant-model.drawio
- control-plane-vs-data-plane.drawio
- domain-workbench-map.drawio

---

*Last updated: 2026-03-17*
