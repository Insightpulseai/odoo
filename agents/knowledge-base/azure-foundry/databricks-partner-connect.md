# What is Databricks Partner Connect?

Partner Connect lets you create trial accounts with select Databricks technology partners and connect your Databricks workspace to partner solutions from the Databricks UI. This allows you to try partner solutions using your data in the Databricks lakehouse, then adopt the solutions that best meet your business needs.

Partner Connect simplifies integration by provisioning the required Databricks resources on your behalf, then passing resource details to the partner. These resources might include:
- Databricks SQL warehouse (formerly Databricks SQL endpoint)
- Service principal
- Personal access token

## Requirements
- Databricks account must be on the Premium plan or above.
- To create new connections, you must sign in as a Workspace Admin.
- For other tasks, you need Workspace access entitlement (and SQL access entitlement if working with SQL warehouses).

## Quickstart
1. Ensure requirements are met.
2. In the sidebar, click Marketplace.
3. In Partner Connect integrations, click View all.
4. Click the tile for the partner you want to connect to. Follow on-screen directions.

## Common Tasks 

### Allow users to access partner-generated databases and tables
Partner solutions in the Data Ingestion category can create databases and tables. These are owned by the associated service principal. Use the SQL `GRANT` statement to allow other users to access them. Use `SHOW GRANTS` to get access details.

### Create an access token
Databricks partner solutions require you to provide a personal access token.
- **Cloud-based solutions**: Partner Connect automatically creates the token and a Databricks service principal associated with it, sharing the value with the partner.
- **Desktop-based solutions**: You must create the token manually and share it with the partner.

*Security Best Practice*: Use OAuth tokens for automated tools and scripts. If using personal access tokens, use tokens belonging to service principals instead of workspace users.
