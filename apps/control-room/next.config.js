/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    DATABRICKS_HOST: process.env.DATABRICKS_HOST,
    DATABRICKS_TOKEN: process.env.DATABRICKS_TOKEN,
    DATABRICKS_CATALOG: process.env.DATABRICKS_CATALOG,
    NOTION_TOKEN: process.env.NOTION_TOKEN,
    NOTION_ACTIONS_DB_ID: process.env.NOTION_ACTIONS_DB_ID,
  },
};

module.exports = nextConfig;
