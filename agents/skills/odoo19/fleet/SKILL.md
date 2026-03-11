---
name: fleet
description: "Manage company vehicles, drivers, contracts, services, accidents, and cost analysis."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Fleet — Odoo 19.0 Skill Reference

## Overview

The **Fleet** app manages a company's vehicle inventory, driver assignments, contracts (leases/purchases), scheduled and ad-hoc maintenance services, accident records, and cost analysis. Vehicles are organized by manufacturer and model with detailed specs (engine, fuel, emissions). The app integrates with Payroll (vehicle as employee benefit in Belgian localization), Employees (driver/mobility card), Contacts (drivers/vendors), and Purchase (RFQs for vehicles).

## Key Concepts

- **Vehicle** — A fleet record with model, license plate, driver, chassis/VIN number, odometer, and status. Default Kanban stages: New Request, To Order, Registered, Downgraded.
- **Manufacturer** — Vehicle make (e.g., BMW, Toyota). 67 preconfigured manufacturers ship with the app.
- **Model** — Specific vehicle model under a manufacturer (e.g., X2 under BMW). Must be created manually. Contains specs for engine, capacity, transmission, emissions.
- **Vehicle Type** — Fixed to Car or Bike only (not extensible, preserves Payroll integration).
- **Model Category** — User-defined grouping for organization (e.g., SUV, Sedan, Van). Not preconfigured.
- **Driver** — Person assigned to a vehicle. Stored as a Contact; does not need to be an Employee.
- **Future Driver** — Next assigned driver; Apply New Driver button triggers the changeover.
- **Contract** — Agreement for a vehicle (lease, purchase, insurance). Tracks responsible person, dates, and costs. End Date Contract Alert sends email N days before expiration.
- **Service** — Maintenance or repair record. Tracks service type, date, cost, vendor, vehicle, driver, odometer reading. Stages: New, Running, Done, Cancelled.
- **Service Type** — Category for services (Contract or Service). Only one default: Vendor Bill.
- **Accident** — Record of a vehicle incident.
- **Fleet Manager** — User assigned to oversee a vehicle.
- **Mobility Card** — Gas/expense card linked to an employee in the Employees app.

## Core Workflows

### 1. Add a Vehicle

1. Navigate to `Fleet → Fleet → Fleet`, click **New**.
2. Select or create **Model** (also creates manufacturer if needed).
3. Enter License Plate, Tags.
4. **Driver section**: Select Driver, Future Driver (optional), Assignment Date.
5. **Vehicle section**: Enter Category, Order Date, Registration Date, Chassis Number, Last Odometer, Fleet Manager, Location.
6. **Tax Info tab**: Enter Horsepower Taxation, Deductibility Rates, First Contract Date, Catalog Value, Purchase Value, Residual Value.
7. **Model tab**: Verify auto-populated specs; update Color, Trailer Hitch, etc.

### 2. Configure Manufacturers and Models

1. Navigate to `Fleet → Configuration → Manufacturers` to view/add manufacturers.
2. Navigate to `Fleet → Configuration → Models` to add models.
3. On model form: set Model Name, Manufacturer, Vehicle Type (Car/Bike), Category.
4. **Information tab**: fill Model specs (year, seats, doors, color) and Engine details (fuel type, range, CO2 emissions, transmission, power).
5. **Vendors tab**: link vendors for purchase RFQs.

### 3. Log a Service

1. Navigate to `Fleet → Fleet → Services`, click **New**.
2. Select Service Type (or create new: type name → Create and edit → set Category to Contract or Service).
3. Enter Date, Cost, Vendor, Vehicle (auto-fills Driver), Odometer Value.
4. Add Notes for details.

### 4. Manage Contracts

1. Navigate to `Fleet → Fleet → Contracts`.
2. Click on a contract to view: Responsible person, dates, costs.
3. Set **End Date Contract Alert** in `Fleet → Configuration → Settings` (number of days before expiration).

### 5. Track Costs

1. Navigate to `Fleet → Reporting → Cost Analysis`.
2. View aggregated costs by vehicle, service type, vendor, etc.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `fleet.vehicle` | Vehicle record |
| `fleet.vehicle.model` | Vehicle model |
| `fleet.vehicle.model.brand` | Manufacturer |
| `fleet.vehicle.model.category` | Model category |
| `fleet.vehicle.log.services` | Service/maintenance record |
| `fleet.vehicle.log.contract` | Vehicle contract |
| `fleet.vehicle.log.fuel` | Fuel log |
| `fleet.vehicle.odometer` | Odometer reading |
| `fleet.vehicle.tag` | Vehicle tag |

### Key Fields

- `fleet.vehicle`: `model_id`, `license_plate`, `driver_id`, `future_driver_id`, `vin_sn` (chassis/VIN), `odometer`, `state_id` (stage), `fleet_manager_id`, `company_id`, `tag_ids`
- `fleet.vehicle.model`: `name`, `brand_id` (manufacturer), `vehicle_type` (car/bike), `category_id`, `seats`, `doors`, `color`, `transmission`, `fuel_type`, `co2`, `power`, `horsepower`
- `fleet.vehicle.log.services`: `description`, `service_type_id`, `date`, `amount`, `vendor_id`, `vehicle_id`, `odometer_id`, `state` (new/running/done/cancelled)
- `fleet.vehicle.log.contract`: `name`, `vehicle_id`, `responsible_id`, `start_date`, `expiration_date`, `cost_generated`

### Important Menu Paths

- `Fleet → Fleet → Fleet` — vehicle Kanban
- `Fleet → Fleet → Contracts` — contract list
- `Fleet → Fleet → Services` — service records
- `Fleet → Configuration → Settings` — End Date Contract Alert, New Vehicle Request
- `Fleet → Configuration → Manufacturers`
- `Fleet → Configuration → Models`
- `Fleet → Configuration → Categories`
- `Fleet → Reporting → Cost Analysis`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Vehicle Type is fixed to Car and Bike; cannot be extended (preserves Payroll integration for employee benefits).
- Model categories are not preconfigured; all must be created by users.
- Models are not preconfigured; each new vehicle model must be added manually.
- Deductibility Rates on vehicles support date-ranged percentages for tax deduction.
- New Vehicle Request setting (Belgian localization only) controls when employees can request new cars via salary configurator.

## Common Pitfalls

- **Models must exist before adding vehicles.** The Model field is the only required field on the vehicle form; the model (and manufacturer) must be created first.
- **Vehicle Type cannot be extended.** Only Car and Bike are available to preserve the Payroll integration. Do not attempt to add new types.
- **Drivers are Contacts, not Employees.** Creating a new driver adds a contact, not an employee record. Link them via the Employees app if needed.
- **Service Types must be created from the service form.** There is no standalone menu for creating service types; use the Service Type field's "Create and edit" option.
- **End Date Contract Alert requires a Responsible person on the contract.** If no responsible person is assigned, no alert email is sent.
