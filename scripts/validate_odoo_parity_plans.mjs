/**
 * Validates catalog/odoo_parity_plans.yaml against catalog/odoo_parity_plans.schema.json
 * Requires: ajv, ajv-formats, yaml (npm install -D ajv ajv-formats yaml)
 */
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import YAML from "yaml";

const schemaPath = path.resolve("catalog/odoo_parity_plans.schema.json");
const dataPath = path.resolve("catalog/odoo_parity_plans.yaml");

if (!fs.existsSync(schemaPath)) throw new Error(`Missing ${schemaPath}`);
if (!fs.existsSync(dataPath)) throw new Error(`Missing ${dataPath}`);

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
const data = YAML.parse(fs.readFileSync(dataPath, "utf8"));

const ajv = new Ajv({ allErrors: true, strict: true });
addFormats(ajv);

const validate = ajv.compile(schema);
const ok = validate(data);

if (!ok) {
  console.error("Parity plan catalog validation failed:");
  for (const err of validate.errors ?? []) {
    console.error(`- ${err.instancePath} ${err.message}`);
  }
  process.exit(1);
}

console.log(`OK: catalog/odoo_parity_plans.yaml matches schema (${data.items?.length ?? 0} items, ${data.plans?.length ?? 0} plans)`);
