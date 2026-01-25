-- Unity Catalog Grants
-- Apply with appropriate admin permissions

-- Grant usage on catalog
GRANT USAGE ON CATALOG ${catalog} TO `data-engineers`;
GRANT USAGE ON CATALOG ${catalog} TO `data-analysts`;
GRANT USAGE ON CATALOG ${catalog} TO `platform-admins`;

-- Bronze schema: Engineers can write, analysts can read
GRANT USAGE ON SCHEMA ${catalog}.bronze TO `data-engineers`;
GRANT USAGE ON SCHEMA ${catalog}.bronze TO `data-analysts`;
GRANT CREATE TABLE ON SCHEMA ${catalog}.bronze TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.bronze TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.bronze TO `data-analysts`;
GRANT MODIFY ON SCHEMA ${catalog}.bronze TO `data-engineers`;

-- Silver schema: Engineers can write, analysts can read
GRANT USAGE ON SCHEMA ${catalog}.silver TO `data-engineers`;
GRANT USAGE ON SCHEMA ${catalog}.silver TO `data-analysts`;
GRANT CREATE TABLE ON SCHEMA ${catalog}.silver TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.silver TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.silver TO `data-analysts`;
GRANT MODIFY ON SCHEMA ${catalog}.silver TO `data-engineers`;

-- Gold schema: Both can read, only engineers write
GRANT USAGE ON SCHEMA ${catalog}.gold TO `data-engineers`;
GRANT USAGE ON SCHEMA ${catalog}.gold TO `data-analysts`;
GRANT CREATE TABLE ON SCHEMA ${catalog}.gold TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.gold TO `data-engineers`;
GRANT SELECT ON SCHEMA ${catalog}.gold TO `data-analysts`;
GRANT MODIFY ON SCHEMA ${catalog}.gold TO `data-engineers`;

-- Platform admins get full access
GRANT ALL PRIVILEGES ON CATALOG ${catalog} TO `platform-admins`;

-- Service principal for automated jobs
GRANT USAGE ON CATALOG ${catalog} TO `notion-ppm-service-principal`;
GRANT ALL PRIVILEGES ON SCHEMA ${catalog}.bronze TO `notion-ppm-service-principal`;
GRANT ALL PRIVILEGES ON SCHEMA ${catalog}.silver TO `notion-ppm-service-principal`;
GRANT ALL PRIVILEGES ON SCHEMA ${catalog}.gold TO `notion-ppm-service-principal`;
